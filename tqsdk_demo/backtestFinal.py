import math
import re
from datetime import datetime, time, date, timedelta
from tqsdk import TqApi, TqAuth, TqKq, tafunc, TqAccount, TqSim, TqBacktest, TargetPosTask
import numpy as np
import pandas as pd
import logging
import time
import sys,ast,multiprocessing,os,csv
from tqsdk.tools import DataDownloader
import json
import asyncio

class InitStrategy:
    def InitLog(self,last_log_name):
        # 根据时间生成文件名
        # current_datetime = datetime.now()
        # date = f"{current_datetime.year}_{current_datetime.month}_{current_datetime.day}_{current_datetime.hour}_{current_datetime.minute}"
        # 配置日志记录
        logging.basicConfig(
            level=logging.INFO,  # 设置记录的最低级别为 INFO
            format='%(asctime)s - %(levelname)s - %(message)s',  # 设置日志的格式
            filename = f'/home/log/{last_log_name}.log'  # 将日志写入文件
            # filename = f'../log/strategytwo{date}.log'  # 将日志写入文件
        )

    def InitParam(self, param):
        startTime = datetime.now()
        logging.info("下载并清洗数据开始时间：%s", startTime)

        # 保存输入的参数（SMA均线）
        # 远程使用 /home
        self.paramMap = param

        # 本地使用 /home
        # self.paramMap = {'symbol1': 'SHFE.hc2301', 'symbol2': 'SHFE.hc2304', 'concurrentNum': 100, 'windowSizeStart': 100, 'windowSizeEnd': 1000, 'windowSizeStep': 100, 'groupSizeStart': 30, 'groupSizeEnd': 150, 'groupSizeStep': 30, 'timesStart': 1, 'timesEnd': 10, 'timesStep': 1, 'stopProfitStart': 1, 'stopProfitEnd': 5, 'stopProfitStep': 0.5, 'dStart': 0.5, 'dEnd': 2, 'dStep': 0.5}
        logging.info("参数列表：%s", self.paramMap)

        # 登录天勤账户
        self.sim = TqSim()
        self.api = TqApi(self.sim, auth=TqAuth("13057302291", "ivy123456"))

        # 1、下载数据
        self.DownloadData()

        # 2、初始化文件信息
        self.InitContractData()

        # 3、TICK：清洗TICK数据，读取出来，清洗完成后再写回
        self.WashTickDataInMemoryLoadFast()

        # 4、TICK：计算清洗后数据的价差，并保存到文件中；TICK：预处理TICK数据，取5min中最大值和最小值
        self.TickPriceDiff()

        # 5、Kline：预处理SMA均线，标准差周期
        self.PreprocessKlineData(self.paramMap['symbol1'], self.paramMap['symbol2'], self.paramMap['cleanKlineFileName'], self.paramMap["klineFile"])

        # 5、PreKline：清理上一年K线数据
        self.PreprocessKlineData(self.paramMap['preSymbol1'], self.paramMap['preSymbol2'], self.paramMap['cleanPreKlineFileName'], self.paramMap["preKlineFile"])

        # 6、计算全局标准差
        self.WholeUpperAndLower()

        # 关闭接口
        self.api.close()

        endTime = datetime.now()
        logging.info("下载并清洗数据结束时间：%s,  结束时间：%s, 一共耗时：%s", startTime, endTime, (endTime - startTime))

    ##################### 下载，清洗数据开始 #####################
    def DownloadData(self):
        # 记录下载开始时间
        startTime = datetime.now()
        logging.info("1、下载数据开始，时间：%s", startTime)
        # 初始化文件名
        symbol1 = self.paramMap["symbol1"]
        symbol2 = self.paramMap["symbol2"]
        pre_year_symbol1 = self.PreYearContract(symbol1)
        pre_year_symbol2 = self.PreYearContract(symbol2)
        if symbol1 > symbol2:
            symbol1, symbol2 = symbol2, symbol1
        if pre_year_symbol1 > pre_year_symbol2:
            pre_year_symbol1, pre_year_symbol2 = pre_year_symbol2, pre_year_symbol1

        # 保存合约信息
        self.paramMap["symbol1"] = symbol1
        self.paramMap["symbol2"] = symbol2
        self.paramMap["preSymbol1"] = pre_year_symbol1
        self.paramMap["preSymbol2"] = pre_year_symbol2

        # 初始化下载文件的文件名
        filePath = "/home/csvfiles/"
        # filePath = "../csvfiles/"
        klineFileName = "%s_%s_%s_%s_kline.csv" % (symbol1.split('.')[0], symbol1.split('.')[1], symbol2.split('.')[0], symbol2.split('.')[1])
        preKlineFileName = "%s_%s_%s_%s_kline.csv" % (pre_year_symbol1.split('.')[0], pre_year_symbol1.split('.')[1], pre_year_symbol2.split('.')[0], pre_year_symbol2.split('.')[1])
        tick1FileName = "%s_%s_tick.csv" % (symbol1.split('.')[0], symbol1.split('.')[1])
        tick2FileName = "%s_%s_tick.csv" % (symbol2.split('.')[0], symbol2.split('.')[1])
        logging.info("K线文件名称：%s, 盘口1数据文件名称：%s, 盘口2数据文件名称：%s", klineFileName, tick1FileName, tick2FileName)
        # 保存文件名称
        self.paramMap["klineFileName"] = klineFileName
        self.paramMap["preKlineFileName"] = preKlineFileName
        self.paramMap["tick1FileName"] = tick1FileName
        self.paramMap["tick2FileName"] = tick2FileName
        self.paramMap["klineFile"] = filePath + klineFileName
        self.paramMap["preKlineFile"] = filePath + preKlineFileName
        self.paramMap["tick1File"] = filePath + tick1FileName
        self.paramMap["tick2File"] = filePath + tick2FileName

        # 获取天勤量化交易接口数据
        global klineData, quoteData1, quoteData2

        # 判断文件是否存在
        isExistKline = os.path.exists(filePath + klineFileName)
        isExistPreKline = os.path.exists(filePath + preKlineFileName)
        isExistTickFileOne = os.path.exists(filePath + tick1FileName)
        isExistTickFileTwo = os.path.exists(filePath + tick2FileName)

        # 下载数据显示进度
        if not isExistKline:
            logging.info("K线不存在，开始下载 %s,%s 的K线", symbol1, symbol2)
            # 下载所有的（一年）K线数据，K线周期为5分钟
            klineData = DataDownloader(self.api, symbol_list=[symbol1, symbol2], dur_sec=300, start_dt=datetime(2000, 1, 1, 0, 0, 0), end_dt=datetime(2026, 1, 1, 0, 0, 0),
                                       csv_file_name=filePath + klineFileName)
            while not klineData.is_finished():
                self.api.wait_update()
                logging.info("progress: kline: %.2f%%", klineData.get_progress())
        # 上一年的K线数据是否存在
        if not isExistPreKline:
            logging.info("上一年K线不存在，开始下载 %s,%s 的K线", pre_year_symbol1, pre_year_symbol2)
            # 下载所有的（一年）K线数据，K线周期为5分钟
            klineData = DataDownloader(self.api, symbol_list=[pre_year_symbol1, pre_year_symbol2], dur_sec=300, start_dt=datetime(2000, 1, 1, 0, 0, 0), end_dt=datetime(2026, 1, 1, 0, 0, 0),
                                       csv_file_name=filePath + preKlineFileName)
            while not klineData.is_finished():
                self.api.wait_update()
                logging.info("progress: pre_kline: %.2f%%", klineData.get_progress())
        if not isExistTickFileOne:
            logging.info("%s盘口数据不存在，开始下载盘口数据", symbol1)
            # 下载这个合约的所有盘口Tick数据
            quoteData1 = DataDownloader(self.api, symbol_list=symbol1, dur_sec=0, start_dt=datetime(2000, 1, 1), end_dt=datetime(2026, 1, 1), csv_file_name=filePath + tick1FileName)
            while not quoteData1.is_finished():
                self.api.wait_update()
                logging.info("progress: tick1:%.2f%%", quoteData1.get_progress())
        if not isExistTickFileTwo:
            logging.info("%s盘口数据不存在，开始下载盘口数据", symbol2)
            quoteData2 = DataDownloader(self.api, symbol_list=symbol2, dur_sec=0, start_dt=datetime(2000, 1, 1), end_dt=datetime(2026, 1, 1), csv_file_name=filePath + tick2FileName)
            while not quoteData2.is_finished():
                self.api.wait_update()
                logging.info("progress: tick2:%.2f%%", quoteData2.get_progress())
        endTime = datetime.now()
        logging.info("1、下载数据结束，开始时间：%s，结束时间：%s，下载数据时长：，%s", startTime, endTime, endTime-startTime)
    def PreYearContract(self, symbol):  # 获取换月合约代码
        match = re.search(r'\d', symbol)
        num = symbol[match.start():]
        num = int(num) - 100
        pre_year_symbol = symbol[:match.start()] + str(num)
        return pre_year_symbol
    def InitContractData(self):
        logging.info("2、初始化合约数据")

        # 初始化参数信息
        symbol1Name = self.paramMap['symbol1']
        symbol2Name = self.paramMap['symbol2']
        preSymbol1Name = self.paramMap['preSymbol1']
        preSymbol2Name = self.paramMap['preSymbol2']

        # 1、获取合约1手的单位
        self.quoteVolume1 = self.api.get_quote(symbol1Name).get("volume_multiple")
        self.quoteVolume2 = self.api.get_quote(symbol2Name).get("volume_multiple")
        self.paramMap["quoteVolume1"] = self.quoteVolume1
        self.paramMap["quoteVolume2"] = self.quoteVolume2
        logging.info("合约一的一手单位为 %d，合约二的一手单位为 %d", self.quoteVolume1, self.quoteVolume2)

        # 2、获取合约的手续费
        self.serviceCharge1 = self.sim.get_commission(symbol1Name)
        self.serviceCharge2 = self.sim.get_commission(symbol2Name)
        self.paramMap["serviceCharge1"] = self.serviceCharge1
        self.paramMap["serviceCharge2"] = self.serviceCharge2
        logging.info("合约一的手续费为 %d，合约二的手续费为 %d", self.serviceCharge1, self.serviceCharge2)

        # 3、获取最小变动单位
        price_tick = self.api.get_quote(symbol1Name).get("price_tick")
        self.paramMap["priceTick"] = price_tick

        # 路径和文件名初始化 /home
        self.paramMap['outFilePath'] = "/home/clean_csvfiles/"
        # self.paramMap['outFilePath'] = "../clean_csvfiles/"
        #DCE
        exchange_code=symbol1Name.split('.')[0]
        #v2307
        s1_code=symbol1Name.split('.')[1]
        #v2308
        s2_code=symbol2Name.split('.')[1]
        self.paramMap['cleanTick1FileName'] = "%s_%s_clean_tick_for_%s_%s.csv" % (exchange_code, s1_code,s1_code,s2_code)
        self.paramMap['cleanTick2FileName'] = "%s_%s_clean_tick_for_%s_%s.csv" % (exchange_code, s2_code,s1_code,s2_code)
        self.paramMap['tickPriceDiffFileName'] = "%s_%s_%s_%s_tick_price_diff.csv" % (exchange_code, s1_code, exchange_code, s2_code)
        self.paramMap['maxMinTickFileName'] = "%s_%s_%s_%s_max_min_tick_price.csv" % (exchange_code, s1_code, exchange_code, s2_code)
        self.paramMap['cleanKlineFileName'] = "%s_%s_%s_%s_clean_kline.csv" % (exchange_code, s1_code, exchange_code, s2_code)
        self.paramMap['cleanPreKlineFileName'] = "%s_%s_%s_%s_clean_kline.csv" % (preSymbol1Name.split('.')[0], preSymbol1Name.split('.')[1], preSymbol2Name.split('.')[0], preSymbol2Name.split('.')[1])

        # 保存订单文件夹位置
        order_name = '{}_{}_{}_{}_order_detail.json'.format(self.paramMap['symbol1'].split('.')[0], self.paramMap['symbol1'].split('.')[1],self.paramMap['symbol2'].split('.')[0], self.paramMap['symbol2'].split('.')[1])
        self.order_path = '/home/order_detail/{}'.format(order_name)

    def WashTickDataInMemoryLoadFast(self):
        logging.info("3、开始清洗并保存数据")
        # 0、预处理数据
        tick_time_moning = datetime.strptime('09:00:00',"%H:%M:%S").time()
        tick_time_afternoon = datetime.strptime('15:00:00',"%H:%M:%S").time()
        tick_time_night = datetime.strptime('21:00:00',"%H:%M:%S").time()

        # 1、判断是否已经清洗过tick数据了
        outFilePath = self.paramMap['outFilePath']
        cleanTick1FileName = self.paramMap['cleanTick1FileName']
        cleanTick2FileName = self.paramMap['cleanTick2FileName']
        isCleanTick1Data = os.path.exists(outFilePath + cleanTick1FileName)
        isCleanTick2Data = os.path.exists(outFilePath + cleanTick2FileName)

        # 如果存在，则重新清洗
        if isCleanTick1Data:
            os.remove(outFilePath + cleanTick1FileName)
            isCleanTick1Data = False
        if isCleanTick2Data:
            os.remove(outFilePath + cleanTick2FileName)
            isCleanTick2Data = False

        # 如果两个tick数据没有清洗，则清洗两边的数据，如果只有单边，则后面运行报错处理
        if not isCleanTick1Data and not isCleanTick2Data:
            tick1File = self.paramMap['tick1File']
            tick2File = self.paramMap['tick2File']
            klineFile = self.paramMap["klineFile"]

            # 0、读取K线数据
            logging.info("开始读取K线")
            klineIndex = 0
            klineDataList = []
            with open(klineFile, 'r') as file:
                reader = csv.reader(file)
                # 不要标题行
                header = next(reader)
                for row in reader:
                    # datetime，SHFE.rb2203.high，SHFE.rb2204.high
                    if row[3] != '#N/A' and row[10] != '#N/A':
                        klineDataList.append([row[0], float(row[3]), float(row[10])])
            klineTotalRow = len(klineDataList)

            # 1、加载并清洗tick1数据
            start = datetime.now()
            logging.info("加载并清洗tick1数据开始时间：%s", start)
            pre_row = [0,0,0]
            tick1DataList = []
            to_csv_num = 0
            total_num = 0
            with open(tick1File, 'r') as file:
                reader = csv.reader(file)
                # 不要标题行
                header = next(reader)
                for row in reader:
                    str_time = row[0]
                    input_datetime = datetime.strptime(str_time[11:19], "%H:%M:%S")
                    tick_time = input_datetime.time()

                    # 清洗tick1数据（1-相邻一样的tick数据去除；2-不在交易范围内的tick去除；）
                    if (pre_row[1] != row[9] or pre_row[2] != row[11]) and row[9] != 'nan' and row[11] != 'nan' and not (tick_time < tick_time_moning or tick_time_afternoon < tick_time < tick_time_night) :
                        # 获取当前tick的K线，58min的tick，需要对比 55min的K线的high
                        while klineIndex + 1 < klineTotalRow:
                            leftKlineDatetime = klineDataList[klineIndex][0]
                            rightKlineDatetime = klineDataList[klineIndex+1][0]
                            if leftKlineDatetime <= row[0] < rightKlineDatetime or row[0] < leftKlineDatetime:
                                break
                            klineIndex += 1

                        # 判断tick是否跑到对应的K线中了
                        if row[0] < leftKlineDatetime:
                            continue
                        if klineIndex + 1 >= klineTotalRow:
                            break
                        if klineDataList[klineIndex][1] >= float(row[9]):
                            tick1DataList.append([row[0], row[9], row[11]])
                            pre_row = [row[0], row[9], row[11]]

                            # 每10万条，保存一次
                            to_csv_num += 1
                            total_num += 1
                            if to_csv_num >= 100000:
                                self.AppendToCsv(tick1DataList, outFilePath + cleanTick1FileName)
                                tick1DataList = []
                                to_csv_num = 0
                # 剩余数据也写入到文件中
                if len(tick1DataList) > 0:
                    self.AppendToCsv(tick1DataList, outFilePath + cleanTick1FileName)

            end = datetime.now()
            logging.info("加载并清洗tick1数据结束时间：%s，耗费时间：%s", end, (end-start))
            logging.info("tick1清洗后数据总量：%s", total_num)

            # 2、加载并清洗tick2数据
            start = datetime.now()
            logging.info("加载并清洗tick2数据开始时间：%s", start)
            # 读取K线数据
            total_num = 0
            klineIndex = 0
            pre_row = [0,0,0]
            tick2DataList = []
            to_csv_num = 0
            with open(tick2File, 'r') as file:
                reader = csv.reader(file)
                # 不要标题行
                header = next(reader)
                for row in reader:
                    str_time = row[0]
                    input_datetime = datetime.strptime(str_time[11:19], "%H:%M:%S")
                    tick_time = input_datetime.time()

                    # 清洗tick2数据（1-相邻一样的tick数据去除；2-不在交易范围内的tick去除；）
                    if (pre_row[1] != row[9] or pre_row[2] != row[11]) and row[9] != 'nan' and row[11] != 'nan' and not (tick_time < tick_time_moning or tick_time_afternoon < tick_time < tick_time_night):
                        # 获取当前tick的K线，58min的tick，需要对比 55min的K线
                        while klineIndex + 1 < klineTotalRow:
                            leftKlineDatetime = klineDataList[klineIndex][0]
                            rightKlineDatetime = klineDataList[klineIndex+1][0]
                            if leftKlineDatetime < row[0] < rightKlineDatetime or row[0] < leftKlineDatetime:
                                break
                            klineIndex += 1

                        # 判断tick是否跑到对应的K线中了
                        if row[0] < leftKlineDatetime:
                            continue
                        if klineIndex + 1 >= klineTotalRow:
                            break
                        # 判断tick是否大于K线的最大值
                        if klineDataList[klineIndex][2] >= float(row[9]):
                            tick2DataList.append([row[0], row[9], row[11]])
                            pre_row = [row[0], row[9], row[11]]

                            # 每10万条，保存一次
                            to_csv_num += 1
                            total_num += 1
                            if to_csv_num == 100000:
                                self.AppendToCsv(tick2DataList, outFilePath + cleanTick2FileName)
                                tick2DataList = []
                                to_csv_num = 0
                # 剩余数据也写入到文件中
                if len(tick2DataList) > 0:
                    self.AppendToCsv(tick2DataList, outFilePath + cleanTick2FileName)
            end = datetime.now()
            logging.info("加载并清洗tick2数据结束，时间：%s，耗费时间：%s", end, (end-start))
            logging.info("tick2清洗后数据总量：%s", total_num)
            logging.info("3、结束清洗并保存数据")
    def AppendToCsv(self, dataList, path):
        with open(path, 'a', newline='') as file:
            csv_writer = csv.writer(file)
            # 逐行写入数据
            for row in dataList:
                csv_writer.writerow(row)
    def TickPriceDiff(self):
        logging.info("4、开始计算并保存价差")
        # 1、初始化数据
        outFilePath = self.paramMap['outFilePath']
        tickPriceDiffFileName = self.paramMap['tickPriceDiffFileName']
        maxMinTickFileName = self.paramMap['maxMinTickFileName']
        cleanTick1FileName = self.paramMap['cleanTick1FileName']
        cleanTick2FileName = self.paramMap['cleanTick2FileName']
        isExistCleanTick1Data = os.path.exists(outFilePath + tickPriceDiffFileName)
        isExistCleanTick2Data = os.path.exists(outFilePath + maxMinTickFileName)

        # 2、开始加载数据，如果不存在则开始生成
        if not isExistCleanTick1Data or not isExistCleanTick2Data:

            # 1、加载tick1数据时间
            start = datetime.now()
            logging.info("加载tick1数据开始时间：%s", start)
            tick1DataList = []
            with open(outFilePath + cleanTick1FileName, 'r') as file:
                reader = csv.reader(file)
                for row in reader:
                    tick1DataList.append([row[0], float(row[1]), float(row[2])])
            end = datetime.now()
            logging.info("加载tick1数据结束，时间：%s，耗费时间：%s", end, (end-start))

            # 2、加载tick2数据时间
            start = datetime.now()
            logging.info("加载tick2数据开始时间：%s", start)
            tick2DataList = []
            with open(outFilePath + cleanTick2FileName, 'r') as file:
                reader = csv.reader(file)
                for row in reader:
                    tick2DataList.append([row[0], float(row[1]), float(row[2])])
            end = datetime.now()
            logging.info("加载tick2数据结束，时间：%s，耗费时间：%s", end, (end-start))

            # 3、将tick1数据日期往前取，一定要大于tick2的数据，这样后续计算找tick2的数据就不会有问题
            tick1Date = tick1DataList[0][0]
            tick2Date = tick2DataList[0][0]
            if tick1Date < tick2Date:
                while tick1Date < tick2Date:
                    tick1DataList = tick1DataList[1000:]
                    tick1Date = tick1DataList[0][0]

            # 4、开始计算tick1，tick2数据的价差
            start = datetime.now()
            logging.info("开始计算tick1，2价差开始时间：%s", start)
            tick1StartIndex = 0
            tick2StartIndex = 0
            priceDiffList = []
            tick1TotalRow = len(tick1DataList)
            tick2TotalRow = len(tick2DataList)

            while tick1StartIndex < tick1TotalRow:
                tick1IndexData = tick1DataList[tick1StartIndex]
                # 获取tick2数据
                while tick2StartIndex < tick2TotalRow:
                    tick2IndexData = tick2DataList[tick2StartIndex]
                    if tick2IndexData[0] > tick1IndexData[0]:
                        break
                    tick2StartIndex += 1
                # 如果tick2数据没有了，则结束计算
                if tick2StartIndex == tick2TotalRow:
                    break
                # 计算保存价差
                tick2IndexData = tick2DataList[tick2StartIndex-1]
                priceDiffList.append([tick1IndexData[0], tick1IndexData[1] - tick2IndexData[2], tick1IndexData[2] - tick2IndexData[1], tick1IndexData[1], tick1IndexData[2], tick2IndexData[1], tick2IndexData[2]])

                # tick1的索引自增
                tick1StartIndex += 1

                # 计算tick2是否有多余的tick需要计算
                if tick1StartIndex == tick1TotalRow:
                    break
                nextTick1IndexData = tick1DataList[tick1StartIndex]
                while tick2StartIndex < tick2TotalRow:
                    tick2IndexData = tick2DataList[tick2StartIndex]
                    if tick2IndexData[0] >= nextTick1IndexData[0]:
                        break
                    priceDiffList.append([tick2IndexData[0], tick1IndexData[1] - tick2IndexData[2], tick1IndexData[2] - tick2IndexData[1], tick1IndexData[1], tick1IndexData[2], tick2IndexData[1], tick2IndexData[2]])
                    tick2StartIndex += 1
            end = datetime.now()
            logging.info("结束计算tick1，2价差结束时间：%s，耗费时间：%s", end, (end-start))

            # 4、计算最大最小值的价差
            start = datetime.now()
            logging.info("开始计算最大最小值，开始时间：%s", start)
            param = {}
            klineTickMaxMinPriceDiff = []
            totalRowPriceDiff = len(priceDiffList)
            i = 0
            leftTime = 0
            leftTimeStr = ''
            rightTime = 0
            rightTimeStr = ''
            while i < totalRowPriceDiff:
                # 构造左右边界
                maxSellPrice = priceDiffList[i][1]
                minBuyPrice = priceDiffList[i][2]
                leftTime = math.floor(int(priceDiffList[i][0][14:16])/5)*5
                if leftTime == int(priceDiffList[i][0][14:16]):
                    rightTime = leftTime + 5
                else:
                    rightTime = math.ceil(int(priceDiffList[i][0][14:16])/5)*5
                if leftTime < 10:
                    leftTimeStr = '0{}:00'.format(leftTime)
                else:
                    leftTimeStr = '{}:00'.format(leftTime)
                if rightTime < 10:
                    rightTimeStr = '0{}:00'.format(rightTime)
                else:
                    rightTimeStr = '{}:00'.format(rightTime)

                # 开始计算最大最小值
                while i < totalRowPriceDiff:
                    if leftTimeStr <= priceDiffList[i][0][14:19] < rightTimeStr:
                        maxSellPrice = priceDiffList[i][1] if priceDiffList[i][1] > maxSellPrice else maxSellPrice
                        minBuyPrice = priceDiffList[i][2] if priceDiffList[i][2] < minBuyPrice else minBuyPrice
                    else:
                        # 遇到整点，时需要+1
                        if rightTime == 60:
                            param['datetime'] = priceDiffList[i-1][0][:11] + str(int(priceDiffList[i-1][0][11:13])+1) + ':00:00'
                        else:
                            param['datetime'] = priceDiffList[i-1][0][:14] + rightTimeStr
                        param['max_sell_price'] = maxSellPrice
                        param['min_buy_price'] = minBuyPrice
                        klineTickMaxMinPriceDiff.append(param.copy())
                        break
                    i += 1

            # 5、保存价差数据到文件
            columns = ['datetime', "sell_price", "buy_price", "tick1_bid_price", "tick1_ask_price", "tick2_bid_price", "tick2_ask_price"]
            tick1DataFrame = pd.DataFrame(priceDiffList, columns=columns)
            tick1DataFrame.to_csv(outFilePath + tickPriceDiffFileName)
            logging.info("保存价差数据到文件完成")

            # 6、保存最大最小值数据到文件中
            columns = ['datetime', "max_sell_price", "min_buy_price"]
            klineTickDataFrame = pd.DataFrame(klineTickMaxMinPriceDiff, columns=columns)
            klineTickDataFrame.to_csv(outFilePath + maxMinTickFileName)
            end = datetime.now()
            logging.info("结束计算最大最小值时间：%s，耗费时间：%s", end, (end-start))
            logging.info("4、结束计算并保存价差")
    def PreprocessKlineData(self, symbol1Name, symbol2Name, cleanKlineFileName, klineFile):
        # 1、准备参数
        start = datetime.now()
        logging.info("5、预处理K线数据开始时间：%s", start)
        outFilePath = self.paramMap['outFilePath']
        isExistKline = os.path.exists(outFilePath + cleanKlineFileName)

        # 如果存在，则需要删除，因为每次参数修改后，预处理的均值和方差都有区别
        if isExistKline:
            os.remove(outFilePath + cleanKlineFileName)

        # 2、每次跑合约需要重新清洗K线
        # 0、删除冗余列
        klineDataFrame = pd.read_csv(klineFile)
        klineDataFrame.drop(columns=['datetime_nano', symbol1Name+'.open', symbol1Name+'.high', symbol1Name+'.low', symbol1Name+'.volume', symbol1Name+'.open_oi', symbol1Name+'.close_oi'], axis=1, inplace=True)
        klineDataFrame.drop(columns=[symbol2Name+'.open', symbol2Name+'.high', symbol2Name+'.low', symbol2Name+'.volume', symbol2Name+'.open_oi', symbol2Name+'.close_oi'], axis=1, inplace=True)

        # 1、加载K线数据
        start = datetime.now()
        logging.info("加载K线数据开始时间：%s", start)
        klineDataList = []
        with open(klineFile, 'r') as file:
            reader = csv.reader(file)
            # 不要标题行
            header = next(reader)
            i = 0
            for row in reader:
                if row[5] != '#N/A' and row[12] != '#N/A':
                    klineDataList.append([row[0], float(row[5]), float(row[12])])
                else:
                    klineDataFrame.drop(i, inplace=True)
                i += 1
        end = datetime.now()
        logging.info("加载K线数据结束时间：%s，耗费时间：%s", end, (end-start))

        # 2、计算K线的价差
        priceDiff = []
        i = 0
        klineDataTotalRows = len(klineDataList)
        while i < klineDataTotalRows:
            priceDiff.append(klineDataList[i][1] - klineDataList[i][2])
            i += 1
        klineDataFrame['price_diff'] = priceDiff

        # 3、预处理K线的SMA均值，和标准差周期
        # 参数1：SMA_100 - 1000 均线
        smaStart = int(self.paramMap['windowSizeStart'])
        smaEnd = int(self.paramMap['windowSizeEnd'])
        smaStep = int(self.paramMap['windowSizeStep'])
        for num in range(smaStart, smaEnd+1, smaStep):
            smaListName = 'sma_{}'.format(num)
            smaList = [0]*(num-1)
            i = (num-1)
            while i < klineDataTotalRows:
                startIndex = i + 1 - num
                endIndex = i + 1
                SMATotal = sum(priceDiff[startIndex:endIndex])
                PriceDiff_SMA = SMATotal / num
                smaList.append(PriceDiff_SMA)
                i += 1
            # 添加到dataFrame中
            klineDataFrame[smaListName] = smaList.copy()

        # 参数2：dev_30 - 300 标准差周期
        devStart = int(self.paramMap['groupSizeStart'])
        devEnd = int(self.paramMap['groupSizeEnd'])
        devStep = int(self.paramMap['groupSizeStep'])
        for num in range(devStart, devEnd+1, devStep):
            devListName = 'dev_{}'.format(num)
            devList = [0]*(num-1)
            i = (num-1)
            while i < klineDataTotalRows:
                startIndex = i + 1 - num
                endIndex = i + 1
                PriceDiff_Dev = np.std(priceDiff[startIndex:endIndex])
                devList.append(PriceDiff_Dev)
                i += 1
            # 添加到dataFrame中
            klineDataFrame[devListName] = devList.copy()

        # 4、将处理后的数据写入文件中
        klineDataFrame.to_csv(outFilePath + cleanKlineFileName, index=False)
        end = datetime.now()
        logging.info("5、预处理K线数据结束时间：%s, 耗时：%s", end, (end-start))
    def WholeUpperAndLower(self):
        # 1、加载K线数据
        start = datetime.now()
        logging.info("6、计算全局标准差开始时间：%s", start)
        outFilePath = self.paramMap['outFilePath']
        cleanKlineFileName = self.paramMap['cleanKlineFileName']
        cleanPreKlineFileName = self.paramMap['cleanPreKlineFileName']
        prePriceDiffDatetime = []
        prePriceDiff = []
        priceDiffDatetime = []
        priceDiff = []
        # 读取去年合约的K线
        with open(outFilePath + cleanPreKlineFileName, 'r') as file:
            reader = csv.reader(file)
            header = next(reader)
            for row in reader:
                prePriceDiffDatetime.append(row[0])
                prePriceDiff.append(float(row[3]))
        # 读取今年合约的K线
        with open(outFilePath + cleanKlineFileName, 'r') as file:
            reader = csv.reader(file)
            header = next(reader)
            for row in reader:
                priceDiffDatetime.append(row[0])
                priceDiff.append(float(row[3]))
        end = datetime.now()
        print("加载K线数据结束时间：%s，耗费时间：%s" % (end, (end-start)))

        # 2、计算去年一年的K线和前一个月的K线价差的SMA和DEV，一共计算12次
        whole_sma_list = [0]*20
        whole_dev_list = [0]*20
        pre_month = int(priceDiffDatetime[0][5:7])
        whole_sma_list[pre_month] = sum(prePriceDiff) / len(prePriceDiff)
        whole_dev_list[pre_month] = np.std(prePriceDiff)

        # 每一个月计算一次
        for i in range(len(priceDiffDatetime)):
            if int(priceDiffDatetime[i][5:7]) != pre_month:
                pre_month = int(priceDiffDatetime[i][5:7])
                whole_sma_list[pre_month] = sum(prePriceDiff) / len(prePriceDiff)
                whole_dev_list[pre_month] = np.std(prePriceDiff)
            else:
                prePriceDiff.append(priceDiff[i])

        # 保存结果
        self.paramMap["whole_sma_list"] = whole_sma_list
        self.paramMap["whole_dev_list"] = whole_dev_list

        end = datetime.now()
        logging.info("6、计算全局标准差结束时间：%s", end)
    ##################### 下载，清洗数据结束 #####################
    def CreateParams(self):
        start = datetime.now()
        logging.info("7、开始组合并处理开始时间：%s", start)
        # SMA均线
        windowSizeStart = int(self.paramMap["windowSizeStart"])
        windowSizeEnd = int(self.paramMap["windowSizeEnd"])
        windowSizeStep = int(self.paramMap["windowSizeStep"])
        windowSizeKind = (windowSizeEnd - windowSizeStart)/windowSizeStep + 1

        # 标准差周期
        groupSizeStart = int(self.paramMap["groupSizeStart"])
        groupSizeEnd = int(self.paramMap["groupSizeEnd"])
        groupSizeStep = int(self.paramMap["groupSizeStep"])
        groupSizeKind = (groupSizeEnd - groupSizeStart)/groupSizeStep + 1

        # N倍标准差
        timesStart = float(self.paramMap["timesStart"])
        timesEnd = float(self.paramMap["timesEnd"])
        timesStep = float(self.paramMap["timesStep"])
        timesKind = (timesEnd - timesStart)/timesStep + 1

        # 止盈倍数
        stopProfitStart = float(self.paramMap["stopProfitStart"])
        stopProfitEnd = float(self.paramMap["stopProfitEnd"])
        stopProfitStep = float(self.paramMap["stopProfitStep"])
        stopProfitKind = (stopProfitEnd - stopProfitStart)/stopProfitStep + 1

        # 止损倍数
        # stopLossStart = int(self.paramMap["stopLossStart"])
        # stopLossEnd = int(self.paramMap["stopLossEnd"])
        # stopLossStep = int(self.paramMap["stopLossStep"])
        # stopLossKind = (stopLossEnd - stopLossStart)/stopLossStep + 1
        stopLossStart = 10000
        stopLossEnd = 10000
        stopLossStep = 1
        stopLossKind = (stopLossEnd - stopLossStart)/stopLossStep + 1

        # 全局价差控制指标
        dStart = float(self.paramMap["dStart"])
        dEnd = float(self.paramMap["dEnd"])
        dStep = float(self.paramMap["dStep"])
        dKind = (dEnd - dStart)/dStep + 1

        # 判断参数是否超过1000个线程
        totalKind = math.ceil(windowSizeKind * groupSizeKind * timesKind * stopProfitKind * stopLossKind * dKind)
        logging.info("总参数数量：%s", totalKind)
        # 创建多进程共享的列表
        manager = multiprocessing.Manager()
        self.jsonSharedList = manager.list([[0]]*totalKind)

        # 保存订单详情
        self.orderDetailDict = manager.dict()
        for i in range(int(self.paramMap['concurrentNum'])):
            self.orderDetailDict[i] = manager.list([])

        self.thread_id = 0
        finishParamNum = 0
        param = {}
        paramList = []
        # 均值从第四位开始
        param["windowSizeIndex"] = 3
        groupSizeIndex = (windowSizeEnd - windowSizeStart)/windowSizeStep + 4
        for windowSize in range(windowSizeStart, windowSizeEnd+1, windowSizeStep):
            param["windowSizeIndex"] = int(param["windowSizeIndex"]) + 1
            # 方差从第14位开始
            param["groupSizeIndex"] = groupSizeIndex
            for groupSize in range(groupSizeStart, groupSizeEnd+1, groupSizeStep):
                param["groupSizeIndex"] = int(param["groupSizeIndex"]) + 1
                for timesIndex in np.arange(timesStart, timesEnd+1, timesStep):
                    for stopProfitIndex in np.arange(stopProfitStart, stopProfitEnd+stopProfitStep, stopProfitStep):
                        for stopLossIndex in range(stopLossStart, stopLossEnd+stopLossStep, stopLossStep):
                            for dIndex in np.arange(dStart, dEnd+dStep, dStep):
                                finishParamNum += 1
                                param["windowSize"] = windowSize
                                param["groupSize"] = groupSize
                                param["times"] = timesIndex
                                param["stopProfit"] = stopProfitIndex
                                param["stopLoss"] = stopLossIndex
                                param["d"] = dIndex
                                paramList.append(param.copy())
                                if len(paramList) >= int(self.paramMap['concurrentNum']):
                                    logging.info("参数组合数量达到要求，开始发送请求")
                                    try:
                                        self.CreateMultiProcess(paramList)
                                    except Exception as e:
                                        logging.info("合约运行这组参数有问题，终止位置：%s， 错误：%s", finishParamNum, e)
                                    paramList.clear()
                                    time.sleep(5)
                                if finishParamNum % 1000 == 0:
                                    logging.info("运行一千种策略，当前一共运行策略组合：%s", finishParamNum)

        # 开始写入JSON结果
        logging.info("开始写入结果")
        dateSuffix = "{}_{}".format(self.paramMap["symbol1"], self.paramMap["symbol2"])
        # /home
        resultFilePath = f"/home/result/result_{dateSuffix}.json"
        # resultFilePath = f"../result/result_{dateSuffix}.json"
        json_data = json.dumps(list(self.jsonSharedList), indent=2)

        # 将列表数据写入 JSON 文件
        with open(resultFilePath, "w") as json_file:
            json_file.write(json_data)
        logging.info("结束写入结果")

        # 关闭共享资源
        manager.shutdown()
        end = datetime.now()
        logging.info("7、结束组合并处理结束时间：%s， 耗时：%s", end, (end-start))
    def CreateMultiProcess(self, paramList):
        # 1、创建线程
        start = datetime.now()
        logging.info("线程执行开始时间：%s，开始线程ID：%s， 线程数量：%s", start, self.thread_id, len(paramList))
        processes = []
        for param in paramList:
            self.paramMap["windowSize"] = param["windowSize"]
            self.paramMap["windowSizeIndex"] = param["windowSizeIndex"]
            self.paramMap["groupSize"] = param["groupSize"]
            self.paramMap["groupSizeIndex"] = param["groupSizeIndex"]
            self.paramMap["times"] = param["times"]
            self.paramMap["stopProfit"] = param["stopProfit"]
            self.paramMap["stopLoss"] = param["stopLoss"]
            self.paramMap["d"] = param["d"]
            self.paramMap["threadId"] = self.thread_id
            process = multiprocessing.Process(target=StrategyTwo().exec, args=(self.paramMap, self.jsonSharedList, self.orderDetailDict,))
            processes.append(process)
            process.start()
            self.thread_id += 1
        for process in processes:
            process.join()

        # 保存订单详情的结果
        self.AppendToOrderDetail()

        end = datetime.now()
        logging.info("线程执行开始时间：%s, 结束时间：%s, 耗时：%s", start, end, (end-start))
    def AppendToOrderDetail(self):
        with open(self.order_path, 'a') as file:
            # 逐行写入数据
            for i in range(int(self.paramMap['concurrentNum'])):
                for row in self.orderDetailDict[i]:
                    json.dump(row, file)
                    file.write('\n')
                # 写完结果，情况dict
                self.orderDetailDict[i][:] = []

class StrategyTwo:
    def InitLog(self, threadId):
        # 根据时间生成文件名
        current_datetime = datetime.now()
        date = f"{current_datetime.year}_{current_datetime.month}_{current_datetime.day}_{current_datetime.hour}_{current_datetime.minute}"
        # 配置日志记录
        logging.basicConfig(
            level=logging.INFO,  # 设置记录的最低级别为 INFO
            format='%(asctime)s - %(levelname)s - %(message)s',  # 设置日志的格式
            filename = f'/home/log/strategytwo{date}_{threadId}.log'  # 将日志写入文件
            # filename = f'../log/strategytwo{date}_{threadId}.log'  # 将日志写入文件
        )
    def exec(self, paramMap, resultList, orderDetailDict):
        # 创建日志文件
        # self.InitLog(paramMap["threadId"])

        startTime = datetime.now()
        # print("进入策略，线程：%d，开始执行多线程策略，时间：%s" % (paramMap["threadId"], startTime))

        # 初始化数据
        self.InitThreadData(paramMap, orderDetailDict)

        # 过滤出有成交的五分钟tick区间
        self.FilterValidTickDatetime()

        # 开平仓
        self.OpenCloseTrade()

        # 保存利润
        resultList[paramMap["threadId"]] = [paramMap["threadId"], paramMap['symbol1'], paramMap['symbol2'], paramMap['windowSize'], paramMap['groupSize'], paramMap['times'], paramMap['stopProfit'], paramMap['stopLoss'], paramMap['d'], paramMap['serviceCharge1'], paramMap['serviceCharge2'], paramMap['quoteVolume1'], paramMap['quoteVolume2'], self.profitTotal, self.totalOrderNum]

#         print("将利润写入list中：%s" % resultList[paramMap["threadId"]])
#         print("线程：%d，利润为：%d" % (paramMap["threadId"], self.profitTotal))
        endTime = datetime.now()
#         print("线程：%d，结束执行多线程策略，开始时间：%s，结束时间：%s, 耗时：%s" % (paramMap["threadId"], startTime, endTime, (endTime-startTime)))

    def InitThreadData(self, paramMap, orderDetailDict):
#         print("初始化参数：")
        # 1、初始化参数
        self.paramMap = paramMap
        self.sma_name = 'sma_{}'.format(paramMap["windowSize"])
        self.dev_name = 'dev_{}'.format(paramMap["groupSize"])
        self.sma_index = int(paramMap["windowSizeIndex"])
        self.dev_index = int(paramMap["groupSizeIndex"])
        self.orderList = []
        self.totalOrderNum = 0
        self.profitTotal = 0

        # 2、订单类型
        self.sellType = "SELL"
        self.buyType = "BUY"

        # 3、保存下单信息
        self.open_close_info = [paramMap["threadId"]]
        self.order_detail_list = orderDetailDict[paramMap["threadId"]%100]

    def FilterValidTickDatetime(self):
#         print("筛选出符合条件的五分钟tick数据：")

        # 1、预处理参数
        outFilePath = self.paramMap['outFilePath']
        maxMinTickFileName = self.paramMap['maxMinTickFileName']
        cleanKlineFileName = self.paramMap['cleanKlineFileName']

        # 2、寻找突破上下轨道的时间，上轨：找最小的那一根（均值min + 方差min） 下轨：找最大的那一根（均值max - 方差min）
        # 2、初始化参数
        self.point_list = []

        # 五分钟最大最小价差文件
        maxMinTickDataFrame = pd.read_csv(outFilePath + maxMinTickFileName)
        # 均值方差十组数据
        klineCleanDataFrame = pd.read_csv(outFilePath + cleanKlineFileName)
        klineTickRows = maxMinTickDataFrame.shape[0]
        klineCleanRows = klineCleanDataFrame.shape[0]

        # 3、开始寻找符合条件的值
        i = 0
        j = 0
        while i < klineTickRows:
            klineTickRow = maxMinTickDataFrame.iloc[i]
            while j < klineCleanRows:
                klineCleanRow = klineCleanDataFrame.iloc[j]
                if klineCleanRow.get('datetime')[:19] == klineTickRow.get('datetime'):
                    sma = klineCleanRow.get(self.sma_name)
                    dev = klineCleanRow.get(self.dev_name)
                    if sma == 0.0 or dev == 0.0:
                        j += 1
                        break
                    upper_track = sma + dev*self.paramMap['times']
                    lower_track = sma - dev*self.paramMap['times']
                    if klineTickRow[2] > upper_track or klineTickRow[3] < lower_track:
                        self.point_list.append(klineTickRow[1])
                elif klineCleanRow.get('datetime')[:19] > klineTickRow.get('datetime'):
                    break
                j += 1
            i += 1
    def OpenCloseTrade(self):
        # 1、初始化数据
        self.symbol1 = self.paramMap['symbol1']
        self.symbol2 = self.paramMap['symbol2']
        self.serviceCharge1 = self.paramMap['serviceCharge1']
        self.serviceCharge2 = self.paramMap['serviceCharge2']
        self.quoteVolume1 = self.paramMap['quoteVolume1']
        self.quoteVolume2 = self.paramMap['quoteVolume2']
        self.whole_sma_list = self.paramMap["whole_sma_list"]
        self.whole_dev_list = self.paramMap["whole_dev_list"]
        outFilePath = self.paramMap['outFilePath']
        tickPriceDiffFileName = self.paramMap['tickPriceDiffFileName']
        cleanKlineFileName = self.paramMap['cleanKlineFileName']

        # 预处理第一条符合条件的五分钟tick数据，获取左右边界
        point_index = 0
        rightDatetime = self.point_list[point_index]
        leftDatetime = self.GetLeftDateTime(rightDatetime)

        # 2、开始遍历价差，进行开平仓
        start = datetime.now()
#         print("开仓平仓开始时间：%s" % start)
        with open(outFilePath + tickPriceDiffFileName, 'r') as file1:
            with open(outFilePath + cleanKlineFileName, 'r') as file2:
                reader1 = csv.reader(file1)
                reader2 = csv.reader(file2)
                header1 = next(reader1)
                header2 = next(reader2)

                # 预处理和第一条五分钟tick对齐的的K线
                for cleanKlineRow in reader2:
                    if cleanKlineRow[0][:19] >= rightDatetime:
                        self.currentKline = cleanKlineRow
                        sma = float(self.currentKline[self.sma_index])
                        dev = float(self.currentKline[self.dev_index])
                        if sma == 0.0 or dev == 0.0:
                            point_index += 1
                            rightDatetime = self.point_list[point_index]
                            leftDatetime = self.GetLeftDateTime(rightDatetime)
                            continue
                        self.Bolling_Upper = sma + dev*self.paramMap['times']
                        self.Bolling_Lower = sma - dev*self.paramMap['times']
                        break

                # 循环处理tick数据
                for priceDiffRow in reader1:
                    # 如果没有开仓，调整到下一个五分钟区间
                    if priceDiffRow[1] >= rightDatetime:
                        point_index += 1
                        if point_index < len(self.point_list):
                            rightDatetime = self.point_list[point_index]
                            leftDatetime = self.GetLeftDateTime(rightDatetime)
                        else:
                            # 符合开仓条件的数据结束，跳出循环
                            break
                        # 寻找对应的K线
                        for cleanKlineRow in reader2:
                            if cleanKlineRow[0][:19] >= rightDatetime:
                                self.currentKline = cleanKlineRow
                                sma = float(self.currentKline[self.sma_index])
                                dev = float(self.currentKline[self.dev_index])
                                if sma == 0.0 or dev == 0.0:
                                    point_index += 1
                                    rightDatetime = self.point_list[point_index]
                                    leftDatetime = self.GetLeftDateTime(rightDatetime)
                                    continue
                                self.Bolling_Upper = sma + dev*self.paramMap['times']
                                self.Bolling_Lower = sma - dev*self.paramMap['times']
                                break

                    # 如果有开仓，则进行止盈止损判断；或者符合开仓条件
                    if len(self.orderList) > 0 or leftDatetime <= priceDiffRow[1] < rightDatetime:
                        self.currentPriceDiff = priceDiffRow
                        self.SellPrice = float(priceDiffRow[2])
                        self.BuyPrice = float(priceDiffRow[3])
                        self.ComputeOrder()
        end = datetime.now()
#         print("下单数量：%s" % self.totalOrderNum)
#         print("开仓平仓结束时间：%s，耗费时间：%s" % (end, (end-start)))
    def GetLeftDateTime(self, rightDatetime):
        # 将字符串转换为 datetime 对象
        original_datetime = datetime.strptime(rightDatetime, '%Y-%m-%d %H:%M:%S')
        # 减少五分钟
        new_datetime = original_datetime - timedelta(minutes=5)
        # 将结果转换为字符串
        leftDatetime = new_datetime.strftime('%Y-%m-%d %H:%M:%S')
        return leftDatetime
    def ComputeOrder(self):
        if len(self.orderList) == 0:
            # 开仓
            month_index = int(self.currentPriceDiff[1][5:7])
            self.Whole_Upper = self.whole_sma_list[month_index] + self.whole_dev_list[month_index] * self.paramMap["d"]
            self.Whole_Lower = self.whole_sma_list[month_index] - self.whole_dev_list[month_index] * self.paramMap["d"]
            self.OpenTrade()
        elif self.orderList[0][0] == self.sellType:
            # 如果是做空的单子，则进行对应的止盈止损
            self.CloseSellProfitAndLoss()
        else:
            # 如果是做多的单子，则进行对应的止盈止损
            self.CloseBuyProfitAndLoss()
    def OpenTrade(self):
        if self.SellPrice > self.Bolling_Upper and self.SellPrice > self.Whole_Upper:
            self.totalOrderNum += 1
            order1 = [self.sellType, self.symbol1, float(self.currentPriceDiff[4]), self.SellPrice]
            order2 = [self.buyType, self.symbol2, float(self.currentPriceDiff[7]), self.SellPrice]
            self.orderList.append(order1)
            self.orderList.append(order2)
            open1_info = [self.currentPriceDiff[1], self.sellType, self.symbol1, self.currentPriceDiff[4], self.SellPrice, self.Bolling_Upper, self.Bolling_Lower, self.currentKline[self.sma_index], self.currentKline[self.dev_index], self.Whole_Upper, self.Whole_Lower]
            open2_info = [self.currentPriceDiff[1], self.buyType, self.symbol2, self.currentPriceDiff[7], self.SellPrice, self.Bolling_Upper, self.Bolling_Lower, self.currentKline[self.sma_index], self.currentKline[self.dev_index], self.Whole_Upper, self.Whole_Lower]
            self.open_close_info.append(open1_info)
            self.open_close_info.append(open2_info)
#             print("符合做空条件，开始做空，第 %s 单" % self.totalOrderNum)
#             print("tick时间：%s, 符合做空条件，开始做空，价差：%d，布林轨道上轨：%s, 布林轨道下轨：%s, 全局上轨：%s, 全局下轨：%s，SMA：%s, dev方差：%s" % (self.currentPriceDiff[1], self.SellPrice, self.Bolling_Upper, self.Bolling_Lower, self.Whole_Upper, self.Whole_Lower, self.currentKline[self.sma_index], self.currentKline[self.dev_index]))
#             print("做空下单：%s" % self.orderList)
            # logging.info("符合做空条件，开始做空，第 %s 单", self.totalOrderNum)
            # logging.info("tick时间：%s, 符合做空条件，开始做空，价差：%d，布林轨道上轨：%s, 布林轨道下轨：%s, 全局上轨：%s, 全局下轨：%s，SMA：%s, dev方差：%s", self.currentPriceDiff[1], self.SellPrice, self.Bolling_Upper, self.Bolling_Lower, self.Whole_Upper, self.Whole_Lower, self.currentKline[self.sma_index], self.currentKline[self.dev_index])
            # logging.info("做空下单：%s", self.orderList)

        # 符合条件下单（价差小于布林上轨，同时小于全局价差）
        elif self.BuyPrice < self.Bolling_Lower and self.BuyPrice < self.Whole_Lower:
            self.totalOrderNum += 1
            order1 = [self.buyType, self.symbol1, float(self.currentPriceDiff[5]), self.BuyPrice]
            order2 = [self.sellType, self.symbol2, float(self.currentPriceDiff[6]), self.BuyPrice]
            self.orderList.append(order1)
            self.orderList.append(order2)
            open1_info = [self.currentPriceDiff[1], self.buyType, self.symbol1, self.currentPriceDiff[5], self.BuyPrice, self.Bolling_Upper, self.Bolling_Lower, self.currentKline[self.sma_index], self.currentKline[self.dev_index], self.Whole_Upper, self.Whole_Lower]
            open2_info = [self.currentPriceDiff[1], self.sellType, self.symbol2, self.currentPriceDiff[6], self.BuyPrice, self.Bolling_Upper, self.Bolling_Lower, self.currentKline[self.sma_index], self.currentKline[self.dev_index], self.Whole_Upper, self.Whole_Lower]
            self.open_close_info.append(open1_info)
            self.open_close_info.append(open2_info)
#             print("符合做多条件，开始做多，第 %s 单" % self.totalOrderNum)
#             print("tick时间：%s, 价差：%d，布林轨道上轨：%s, 布林轨道下轨：%s, 全局上轨：%s, 全局下轨：%s，SMA：%s, dev方差：%s" % (self.currentPriceDiff[1], self.BuyPrice, self.Bolling_Upper, self.Bolling_Lower, self.Whole_Upper, self.Whole_Lower, self.currentKline[self.sma_index], self.currentKline[self.dev_index]))
#             print("做多下单：%s" % self.orderList)
            # logging.info("符合做多条件，开始做多，第 %s 单", self.totalOrderNum)
            # logging.info("tick时间：%s, 价差：%d，布林轨道上轨：%s, 布林轨道下轨：%s, 全局上轨：%s, 全局下轨：%s，SMA：%s, dev方差：%s", self.currentPriceDiff[1], self.BuyPrice, self.Bolling_Upper, self.Bolling_Lower, self.Whole_Upper, self.Whole_Lower, self.currentKline[self.sma_index], self.currentKline[self.dev_index])
            # logging.info("做多下单：%s", self.orderList)
    def CloseSellProfitAndLoss(self):
        # 符合做空的止盈条件
        dev = float(self.currentKline[self.dev_index])
        # dev = float(self.paramMap['priceTick'])
        PD_Sell = self.orderList[0][3]

        if self.BuyPrice <= (PD_Sell - dev*self.paramMap['stopProfit']) or self.BuyPrice > PD_Sell + dev*self.paramMap['stopLoss']:
            priceDiff1 = self.orderList[0][2] - float(self.currentPriceDiff[5])
            profitSymbol1 = priceDiff1 * self.quoteVolume1 - self.serviceCharge1*2
            priceDiff2 = float(self.currentPriceDiff[6]) - self.orderList[1][2]
            profitSymbol2 = priceDiff2 * self.quoteVolume2 - self.serviceCharge2*2
            self.orderList.clear()
            closeOrder1 = [self.buyType, self.symbol1, self.currentPriceDiff[5], self.BuyPrice, profitSymbol1]
            closeOrder2 = [self.sellType, self.symbol2, self.currentPriceDiff[6], self.BuyPrice, profitSymbol2]
            self.profitTotal += profitSymbol1
            self.profitTotal += profitSymbol2
            # 保存开平仓信息
            close1_info = [self.currentPriceDiff[1], self.buyType, self.symbol1, self.currentPriceDiff[5], self.BuyPrice, profitSymbol1, dev, self.quoteVolume1, self.serviceCharge1]
            close2_info = [self.currentPriceDiff[1], self.sellType, self.symbol2, self.currentPriceDiff[6], self.BuyPrice, profitSymbol2, dev, self.quoteVolume2, self.serviceCharge2]
            self.open_close_info.append(close1_info)
            self.open_close_info.append(close2_info)
            self.order_detail_list.append(self.open_close_info.copy())
            self.open_close_info = [self.paramMap["threadId"]]

            # if self.BuyPrice < (PD_Sell - dev*int(self.paramMap['stopProfit'])):
                #止盈条件，现在的价差 小于 （做空价差 - stopProfit*标准差），就是超过最大目标盈利了
                #盈利计算：拿合约的卖价 - 买价 就是盈利
#                 print("符合止盈条件做空平仓")
#                 print("止盈平仓后利润 %d，净值：%s" % ((profitSymbol1+profitSymbol2), self.profitTotal))
#                 print("tick时间：%s, 止盈价差：%s，做空价差：%s, 方差：%s" % (self.currentPriceDiff[1], self.BuyPrice, PD_Sell, dev))
#                 print("第一单：%s, 第二单：%s" % (closeOrder1, closeOrder2))
#                 print("-----------------------------------------------------------------------------------------------------------------")

                # logging.info("符合止盈条件做空平仓")
                # logging.info("止盈平仓后利润 %d，净值：%s", (profitSymbol1+profitSymbol2), self.profitTotal)
                # logging.info("tick时间：%s, 止盈价差：%s，做空价差：%s, 方差：%s", self.currentPriceDiff[1], self.BuyPrice, PD_Sell, dev)
                # logging.info("第一单：%s, 第二单：%s", closeOrder1, closeOrder2)
                # logging.info("-----------------------------------------------------------------------------------------------------------------")
            # else:
                #止损条件，现在的价差 大于 （做空价差 + stopProfit*标准差），就是超过最大承受的损失了
                #损失计算：拿合约的卖价 - 买价 就是亏损
#                 print("符合止损条件做空平仓")
#                 print("止损平仓后亏损 %d，净值：%s" % ((profitSymbol1+profitSymbol2), self.profitTotal))
#                 print("tick时间：%s, 止损价差：%s，做空价差：%s, 方差：%s" % (self.currentPriceDiff[1], self.BuyPrice, PD_Sell, dev))
#                 print("第一单：%s, 第二单：%s" % (closeOrder1, closeOrder2))
#                 print("-----------------------------------------------------------------------------------------------------------------")
                # logging.info("符合止损条件做空平仓")
                # logging.info("止损平仓后亏损 %d，净值：%s", (profitSymbol1+profitSymbol2), self.profitTotal)
                # logging.info("tick时间：%s, 止损价差：%s，做空价差：%s, 方差：%s", self.currentPriceDiff[1], self.BuyPrice, PD_Sell, dev)
                # logging.info("第一单：%s, 第二单：%s", closeOrder1, closeOrder2)
                # logging.info("-----------------------------------------------------------------------------------------------------------------")
    def CloseBuyProfitAndLoss(self):
        # 符合做多的止盈条件
        dev = float(self.currentKline[self.dev_index])
        # dev = float(self.paramMap['priceTick'])
        PD_Buy = self.orderList[0][3]
        if self.SellPrice >= (PD_Buy + dev*self.paramMap['stopProfit']) or self.SellPrice < (PD_Buy - dev*self.paramMap['stopLoss']):
            priceDiff1 = float(self.currentPriceDiff[4]) - self.orderList[0][2]
            # 因为下单的手续费没算，所以平仓算利润的时候一起算上
            profitSymbol1 = priceDiff1 * self.quoteVolume1 - self.serviceCharge1*2
            priceDiff2 = self.orderList[1][2] - float(self.currentPriceDiff[7])
            profitSymbol2 = priceDiff2 * self.quoteVolume2 - self.serviceCharge2*2
            self.orderList.clear()
            closeOrder1 = [self.sellType, self.symbol1, self.currentPriceDiff[4], self.SellPrice, profitSymbol1]
            closeOrder2 = [self.buyType, self.symbol2, self.currentPriceDiff[7], self.SellPrice, profitSymbol2]
            self.profitTotal += profitSymbol1
            self.profitTotal += profitSymbol2
            # 保存开平仓信息
            close1_info = [self.currentPriceDiff[1], self.sellType, self.symbol1, self.currentPriceDiff[4], self.SellPrice, profitSymbol1, dev, self.quoteVolume1, self.serviceCharge1]
            close2_info = [self.currentPriceDiff[1], self.buyType, self.symbol2, self.currentPriceDiff[7], self.SellPrice, profitSymbol2, dev, self.quoteVolume2, self.serviceCharge2]
            self.open_close_info.append(close1_info)
            self.open_close_info.append(close2_info)
            self.order_detail_list.append(self.open_close_info.copy())
            self.open_close_info = [self.paramMap["threadId"]]

            # if self.SellPrice > (PD_Buy + dev*int(self.paramMap['stopProfit'])):
#                 print("符合止盈条件做多平仓")
#                 print("止盈平仓后利润 %d，净值：%s" % ((profitSymbol1+profitSymbol2), self.profitTotal))
#                 print("tick时间：%s, 止盈价差：%s，做多价差：%s, 方差：%s" % (self.currentPriceDiff[1], self.SellPrice, PD_Buy, dev))
#                 print("第一单：%s, 第二单：%s" % (closeOrder1, closeOrder2))
#                 print("-----------------------------------------------------------------------------------------------------------------")

                # logging.info("符合止盈条件做多平仓")
                # logging.info("止盈平仓后利润 %d，净值：%s", (profitSymbol1+profitSymbol2), self.profitTotal)
                # logging.info("tick时间：%s, 止盈价差：%s，做多价差：%s, 方差：%s", self.currentPriceDiff[1], self.SellPrice, PD_Buy, dev)
                # logging.info("第一单：%s, 第二单：%s", closeOrder1, closeOrder2)
                # logging.info("-----------------------------------------------------------------------------------------------------------------")
            # else:
                #止损条件，现在的价差 小于 （做空价差 - stopLoss*标准差），就是超过最大承受的损失了
                #损失计算：拿合约的卖价 - 买价 就是亏损
#                 print("符合止损条件做多平仓")
#                 print("止损平仓后亏损 %d，净值：%s" % ((profitSymbol1+profitSymbol2), self.profitTotal))
#                 print("tick时间：%s, 止损价差：%s，做空价差：%s, 方差：%s" % (self.currentPriceDiff[1], self.SellPrice, PD_Buy, dev))
#                 print("第一单：%s, 第二单：%s" % (closeOrder1, closeOrder2))
#                 print("-----------------------------------------------------------------------------------------------------------------")

                # logging.info("符合止损条件做多平仓")
                # logging.info("止损平仓后亏损 %d，净值：%s", (profitSymbol1+profitSymbol2), self.profitTotal)
                # logging.info("tick时间：%s, 止损价差：%s，做空价差：%s, 方差：%s", self.currentPriceDiff[1], self.SellPrice, PD_Buy, dev)
                # logging.info("第一单：%s, 第二单：%s", closeOrder1, closeOrder2)
                # logging.info("-----------------------------------------------------------------------------------------------------------------")


if __name__ == '__main__':
    InitStrategy = InitStrategy()



    paramMap = ast.literal_eval(sys.argv[1])
    symbolList = ast.literal_eval(sys.argv[2])
    last_log_name = sys.argv[3]
    # 定义日志
    InitStrategy.InitLog(last_log_name)

    for symbol in symbolList:
        dateSuffix = "{}_{}".format(symbol[0], symbol[1])
        resultFilePath = f"/home/result/result_{dateSuffix}.json"
        if os.path.exists(resultFilePath):
            logging.info(f"{dateSuffix}已运算完成无需处理")
            continue
        try:
            symbolStartTime = datetime.now()
            logging.info("计算合约对开始：%s，开始时间：%s" % (symbol, symbolStartTime))

            # 预处理数据
            paramMap['symbol1'] = symbol[0]
            paramMap['symbol2'] = symbol[1]

            # 清洗数据，生成预处理文件
            InitStrategy.InitParam(paramMap)

            # 多线程处理多组参数
            InitStrategy.CreateParams()

            symbolEndTime = datetime.now()
            logging.info("计算合约对结束：%s，结束时间：%s，耗时：%s" % (symbol, symbolEndTime, (symbolEndTime - symbolStartTime)))
        except Exception as e:
            logging.info("合约对运行出错了：%s, %s", symbol, e)

        # 跑完一组休息一分钟
        time.sleep(60)
