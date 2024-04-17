
def Verify():
    # 打开文件并读取内容
    file_path = 'record/log_file2.txt'

    with open(file_path, 'r', encoding='gbk') as file:
        # 使用迭代器逐行读取文件
        file_iterator = iter(file)

        order_num = 0

        for line in file_iterator:
            if line.strip() == '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~':
                try:
                    # 获取全局价差
                    whole_pricediff_line = next(file_iterator)
                    whole_lower = float(whole_pricediff_line.split('：')[1].split('~~')[0].strip())
                    whole_upper = float(whole_pricediff_line.split('：')[1].split('~~')[1].strip())

                    # 无效行
                    next(file_iterator)

                    # 布林上轨
                    bulling_upper_line = next(file_iterator)
                    bulling_upper = float(bulling_upper_line.split('：')[1].split('-----------------')[0].strip())

                    # 做空价差
                    sell_pricediff_line = next(file_iterator)
                    sell_pricediff = float(sell_pricediff_line.split('：')[1].strip())

                    # 无效行
                    next(file_iterator)

                    # 做多价差
                    buy_pricediff_line = next(file_iterator)
                    buy_pricediff = float(buy_pricediff_line.split('：')[1].strip())

                    # 布林下轨
                    bulling_lower_line = next(file_iterator)
                    bulling_lower = float(bulling_lower_line.split('：')[1].split('-----------------')[0].strip())

                    # 无效行
                    next(file_iterator)

                    # 有无开仓(0未开仓，1开仓)
                    open_trade_line = next(file_iterator)
                    open_trade = int(open_trade_line.split('=')[1].strip())

                    # 持仓数量
                    keep_trade_line = next(file_iterator)
                    keep_trade = 0
                    if(len(keep_trade_line.split('=')) > 1):
                        keep_trade = int(open_trade_line.split('=')[1].strip())
                    else:
                        keep_trade = int(keep_trade_line.split('：')[2].strip())

                    if sell_pricediff > bulling_upper and sell_pricediff > whole_upper and open_trade+keep_trade == 0:
                        print("异常，该做空时未做空，布林轨道上轨价格为：%s" % bulling_upper)
                    if buy_pricediff < bulling_lower and buy_pricediff < whole_lower and open_trade+keep_trade == 0:
                        print("异常，该做多时未做多，布林轨道下轨价格为：%s" % bulling_lower)

                    # 订单数
                    order_num += 1
                    if order_num % 100 == 0:
                        print("订单数量：%s" % order_num)


                except StopIteration:
                    # 处理到文件末尾时，可能会引发 StopIteration 异常
                    print("已到达文件末尾")

    # 文件已在 with 语句块结束时自动关闭


if __name__ == '__main__':
    Verify()
