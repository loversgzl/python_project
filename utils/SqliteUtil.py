import sqlite3
from datetime import datetime
import uuid

class SqliteUtil:

    def __init__(self):
        # 连接到 SQLite 数据库（如果不存在则创建）
        dbFile = '../GmaxQuantDB/gmaxdata.db'
        self.conn = sqlite3.connect(dbFile)
        # 创建一个游标对象，用于执行 SQL 语句
        self.cursor = self.conn.cursor()
        # print("连接数据库结束")

    def CloseDB(self):
        self.cursor.close()

    def DropTableIfExist(self, tableName):
        # 如果表存在，则删除表格
        self.cursor.execute(f"DROP TABLE IF EXISTS '{tableName}'")
        # 提交更改
        self.conn.commit()
        print("删除表格结束")

    def CreateTableIfNotExist(self, tableName):
        # 如果表不存在，则创建表格
        self.cursor.execute(f"CREATE TABLE IF NOT EXISTS '{tableName}' (id INTEGER PRIMARY KEY AUTOINCREMENT, ticket_id INTEGER, order_id TEXT, diff_direct TEXT, symbol TEXT, direction TEXT, volume INTEGER, price_cost REAL, pd_price REAL, sl REAL, tp REAL, insert_time TEXT, is_delete INTEGER, project_num TEXT);")
        # 提交更改
        self.conn.commit()
        # print("创建表格结束")

    def add_column(self, tableName, column_name, default_value):
        update_sql = f"ALTER TABLE {tableName} ADD COLUMN {column_name} TEXT DEFAULT {default_value};"
        self.cursor.execute(update_sql)
        # 提交更改
        self.conn.commit()

    def get_all_tableName(self):
        self.cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table';")
        results = self.cursor.fetchall()
        return results

    def get_table_column(self, tableName):
        # 执行查询
        self.cursor.execute(f"PRAGMA table_info({tableName});")

        # 获取结果
        table_info = self.cursor.fetchall()

        # 打印表结构信息
        for column in table_info:
            print(column)

############################  数据处理  ####################################

    def DeleteData(self, tableName, id):
        update_sql = f"UPDATE {tableName} SET is_delete = 1 WHERE id = ?"
        data_to_update = (id, )
        self.cursor.execute(update_sql, data_to_update)
        # 提交更改
        self.conn.commit()

    def InsertData(self, tableName, record1, record2, m, min_change, project_num):
        print("aaa:%s" % record1)
        print("aaa:%s" % record2)
        uid = str(uuid.uuid4())
        pd_price = record1['trade_price'] - record2['trade_price']
        tp_price = record1['trade_price'] - record2['trade_price'] - m * min_change
        self._AddRecord(tableName, record1, uid, pd_price, tp_price, project_num)
        self._AddRecord(tableName, record2, uid, pd_price, tp_price, project_num)
        self.conn.commit()
        print("插入两条数据成功")

    def _AddRecord(self, tableName, record, uid, pd_price, tp_price, project_num):
        ticketParam = {}
        ticketParam['ticket_id'] = uid
        ticketParam['diff_direct'] = record['direction']
        ticketParam['symbol'] = record['instrument_id']
        ticketParam['order_id'] = record['order_id']
        ticketParam['direction'] = record['direction']
        ticketParam['volume'] = record['volume_orign'] - record['volume_left']
        ticketParam['price_cost'] = record['trade_price']
        ticketParam['pd_price'] = pd_price
        ticketParam['tp'] = tp_price
        ticketParam['sl'] = 0 #默认值
        ticketParam['project_num'] = project_num
        insert_sql = f"INSERT INTO {tableName} (ticket_id, order_id, diff_direct, symbol, direction, volume, price_cost, pd_price, sl, tp, insert_time, is_delete, project_num) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
        data_to_insert = (ticketParam['ticket_id'], ticketParam['order_id'], ticketParam['diff_direct'], ticketParam['symbol'], ticketParam['direction'], ticketParam['volume'], ticketParam['price_cost'], ticketParam['pd_price'], ticketParam['sl'], ticketParam['tp'], datetime.now(), 0, ticketParam['project_num'])
        self.cursor.execute(insert_sql, data_to_insert)

    def GetAllData(self, tableName):
        self.cursor.execute(f"SELECT * FROM {tableName} WHERE is_delete = 0")
        results = self.cursor.fetchall()
        returnResults = []
        ticketParam = {}
        for result in results:
            ticketParam['id'] = result[0]
            ticketParam['ticket_id'] = result[1]
            ticketParam['order_id'] = result[2]
            ticketParam['diff_direct'] = result[3]
            ticketParam['symbol'] = result[4]
            ticketParam['direction'] = result[5]
            ticketParam['volume'] = result[6]
            ticketParam['price_cost'] = result[7]
            ticketParam['pd_price'] = result[8]
            ticketParam['sl'] = result[9]
            ticketParam['tp'] = result[10]
            ticketParam['insert_time'] = result[11]
            ticketParam['project_num'] = result[13]
            returnResults.append(ticketParam.copy())
        return returnResults

    def update_data(self, tableName, updateColumnName, updateColumnValue, conditionColumnName, conditionColumnValue):
        update_sql = f"UPDATE {tableName} SET {updateColumnName} = ? where {conditionColumnName} = ?;"
        self.cursor.execute(update_sql, (updateColumnValue, conditionColumnValue))

        # 提交更改
        self.conn.commit()



if __name__ == '__main__':
    # 创建表格
    sqlite = SqliteUtil()

    # sqlite.get_table_column('tickets_ag2410_ag2501')

    # 插入一列
    # tableNameList = sqlite.get_all_tableName()
    # for tableName in tableNameList:
    #     if tableName[0] != 'sqlite_sequence':
    #         sqlite.add_column(tableName[0], 'project_num', 'R1')
    #         print(tableName[0])

    # 更新数据
    tableNameList = ['tickets_ag2412_ag2501']
    for tableName in tableNameList:
        sqlite.update_data(tableName, 'volume', 5, 'id', 1)

    # 查询数据
    # tableNameList = ['tickets_ag2410_ag2501', 'tickets_ag2412_ag2501', 'tickets_al2406_al2407']
    tableName = 'tickets_ag2412_ag2501'
    results = sqlite.GetAllData(tableName)
    for result in results:
        print(result)

















