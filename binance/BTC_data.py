import datetime


def ReadJson():
        # 读取数据
        param_list = []
        for i in range(1, 17):
            date_str = str(i).zfill(2)
            param_file_path = f'csv_file/BTCUSDT-trades-2024-04-{date_str}.csv'

            with open(param_file_path, 'r', encoding='utf-8') as paramFile:
                for param in paramFile:
                    if len(param.strip()) > 0:
                        param_list.append(param.strip().split(','))

        # 分析数据
        # for i in range(20):
        #     print(param_list[i])
        #     time = datetime.datetime.fromtimestamp(int(param_list[i][4])/1000)
        #     print(time)
        strategy2(param_list)

def strategy1(param_list):
    upper_price = float(param_list[0][1])
    lower_price = float(param_list[0][1])
    stop_upper = upper_price * (1 + 0.015)
    stop_lower = lower_price * (1 - 0.015)
    print("开仓价格：%s，上轨：%s，下轨：%s" % (upper_price, stop_upper, stop_lower))

    first_order = True
    second_order = False
    direct = 0
    max_loss_price = 0

    for param in param_list[1:]:
        curr_price = float(param[1])
        if first_order:
            # 先平做多的单子，等待做空单子回归
            if curr_price >= stop_upper:
                lower_price = (lower_price + curr_price)/2
                direct = 1
                first_order = False
                second_order = True
                print("第一单：先平做多的单子，价格：%s，等待做空单子回归" % curr_price)
            # 先平做空的单子，等待做多单子回归
            elif curr_price <= stop_lower:
                upper_price = (upper_price + curr_price)/2
                direct = 2
                first_order = False
                second_order = True
                print("第一单：先平做空的单子，价格：%s，等待做多单子回归" % curr_price)

        if second_order:
            if direct == 1:
                gap = curr_price - lower_price
                if gap <= 0:
                    print("第二单：平做空的单子，价格：%s，最大价差：%s" % (param, max_loss_price))
                    return
                if gap > max_loss_price:
                    max_loss_price = gap
            if direct == 2:
                gap = upper_price - curr_price
                if gap <= 0:
                    print("第二单：平做多的单子，价格：%s，最大价差：%s" % (param, max_loss_price))
                    return
                if gap > max_loss_price:
                    max_loss_price = gap

    # 结束
    print("行情结束，未能平掉所有单，最大价差：%s" % max_loss_price)

def strategy2(param_list):
    open_price = float(param_list[0][1])
    stop_profit = open_price * (1 - 0.02)
    add_position_price = open_price * (1 + 0.015)
    position = 1
    print("开仓价格：%s，做空止盈价格：%s，第一次价差价格：%s" % (open_price, stop_profit, add_position_price))

    for param in param_list[1:]:
        curr_price = float(param[1])
        if curr_price <= stop_profit:
            print("止盈：平做空的单子，价格：%s，逐仓数量：%s" % (param, position))
            stop_profit = curr_price * (1 - 0.02)
            add_position_price = curr_price * (1 + 0.015)
            position = 0
        # 是否到达逐仓的位置
        elif curr_price >= add_position_price:
            position += 1
            add_position_price = curr_price * (1 + 0.015)
            print("逐仓价格：%s，当前数量：%s" % (curr_price, position))

    # 结束
    print("行情结束，未能平掉做空的单子，最大逐仓：%s" % position)

if __name__ == "__main__":
    ReadJson()


