from controller import version_controller, quote_controller, kline_controller, ticket_info_controller, contract_daily_info_controller
from GmaxQuantUtil import SqliteUtil
from datetime import datetime

class GmaxQuantReal_V_3:

    def monit_quote_info(self):
        sqliteUtil = SqliteUtil.SqliteUtil()
        self.DIRECT_SELL = 'SELL'
        self.DIRECT_BUY = 'BUY'

        his_version = 0
        while True:
            # 1、查询版本是否有改变，改变后查询所有 quote 进行开仓条件判断
            curr_version = version_controller.query_max_version()
            if curr_version != his_version:
                start_time = datetime.now()
                print("版本更新：%s" % curr_version)
                # 更新
                his_version = curr_version
                ticket_df = ticket_info_controller.query_all()
                ticket_df = ticket_df[:50]
                contract_df = contract_daily_info_controller.query_all()

                start_time = datetime.now()
                quote_df = quote_controller.query_columns()
                end_time = datetime.now()
                print("quote_df数据库查询，开始时间：%s, 结束时间：%s, 耗时：%s" % (start_time, end_time, (end_time-start_time)))

                start_time = datetime.now()
                kline_df = kline_controller.query_columns()
                end_time = datetime.now()
                print("quote_df数据库查询，开始时间：%s, 结束时间：%s, 耗时：%s" % (start_time, end_time, (end_time-start_time)))

                start_time = datetime.now()
                for index, row in ticket_df.iterrows():
                    # 1、查询这两个合约的下单信息
                    tableName = 'tickets_{}_{}'.format(row['instrument_id_1'].split('.')[1], row['instrument_id_2'].split('.')[1])
                    sqliteUtil.CreateTableIfNotExist(tableName)
                    results = sqliteUtil.GetAllData(tableName)
                    ticket_len_sell, ticket_len_buy = self.ticket_len(results, self.DIRECT_SELL, self.DIRECT_BUY)

                    # 2、查询两个合约的quote信息 和 K线信息
                    quote1 = quote_df
                    quote2 = quote_df
                    kline = kline_df
                    if quote1.shape[0] == 0 or quote2.shape[0] == 0 or kline.shape[0] == 0:
                        continue

                    # 3、计算价差
                    SellPrice = quote1.iloc[0]['bid_price1'] - quote2.iloc[0]['ask_price1']
                    BuyPrice = quote1.iloc[0]['ask_price1'] - quote2.iloc[0]['bid_price1']

                    # 4、计算交易机会 0没有机会 1开仓做空机会 2开仓做多机会 3做空平仓机会 4做多平仓机会
                    trade_opt = 0
                    if ticket_len_sell == 0 and SellPrice > 100 and SellPrice > kline.iloc[0]['five_min_upper']:
                        trade_opt = 1
                    elif ticket_len_buy == 0 and BuyPrice < 100 and BuyPrice < kline.iloc[0]['five_min_lower']:
                        trade_opt = 2
                    else:
                        for result in results:
                            if ticket_len_sell > 0 and result['diff_direct'] == self.DIRECT_SELL and BuyPrice < result['pd_price'] - row['stop_profit'] * kline.iloc[0]['group_value']:
                                trade_opt = 3
                                break
                            elif ticket_len_buy > 0 and result['diff_direct'] == self.DIRECT_BUY and SellPrice > result['pd_price'] + row['stop_profit'] * kline.iloc[0]['group_value']:
                                trade_opt = 4
                                break

                    #5、如果有交易机会，再检查是否符合条件
                    if trade_opt > 0:
                        # 检查当前价格是否到达涨跌停价，并且在交易时间
                        is_not_limit = self.check_not_limit(quote1, contract_df) or self.check_not_limit(quote2, contract_df)
                        is_trade_time = self.trade_time()

                        if is_not_limit and is_trade_time:
                            ticket_info_controller.update_trade_opt(row['instrument_id_1'], row['instrument_id_2'], trade_opt)

                end_time = datetime.now()
                print("数据计算开始时间：%s, 结束时间：%s, 耗时：%s" % (start_time, end_time, (end_time-start_time)))

    def ticket_len(self, results, diff_direct1, diff_direct2):
            len_ticket1 = 0
            len_ticket2 = 0
            for result in results:
                if result['diff_direct'] == diff_direct1:
                    len_ticket1 += 1
                elif result['diff_direct'] == diff_direct2:
                    len_ticket2 += 1
            return len_ticket1, len_ticket2

    def check_not_limit(self, quote, contract_df):
        contract_info = contract_df[contract_df['instrument_id'] == quote.iloc[0]['instrument_id']]
        if quote.iloc[0]['last_price'] == contract_info.iloc[0]['upper_limit'] or quote.iloc[0]['last_price'] == contract_info.iloc[0]['lower_limit']:
            return False
        return True

    def trade_time(self):
        now = datetime.now().time()
        start_time1 = datetime.strptime('9:00:00', '%H:%M:%S').time()
        end_time1 = datetime.strptime('11:30:00', '%H:%M:%S').time()
        start_time2 = datetime.strptime('13:30:00', '%H:%M:%S').time()
        end_time2 = datetime.strptime('15:00:00', '%H:%M:%S').time()
        start_time3 = datetime.strptime('21:00:00', '%H:%M:%S').time()
        end_time3 = datetime.strptime('23:59:59', '%H:%M:%S').time()
        start_time4 = datetime.strptime('00:00:00', '%H:%M:%S').time()
        end_time4 = datetime.strptime('2:30:00', '%H:%M:%S').time()

        if (now >= start_time1 and now <= end_time1) \
            or (now >= start_time2 and now <= end_time2) \
            or (now >= start_time3 and now <= end_time3) \
            or (now >= start_time4 and now <= end_time4):
            return True
        return False

if __name__ == '__main__':
    GmaxQuantReal_V_3().monit_quote_info()