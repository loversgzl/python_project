import pandas as pd
from datetime import datetime

'''
 pandas is built on top of NumPy;
 The two primary data structures of pandas, Series and DataFrame;
 Each column in a DataFrame is a Series;
 
 
 优势：
 1、容易处理空值
 2、O（1）时间的插入和删除数据
 3、可以很容易的将不同的数据结构转为 DataFrame 数据结构
 4、很容易处理大数据量
 
 
'''
data = {'Name': ['Alice', 'Bob', 'Charlie'], 'Age': [25, 30, 35], 'City': ['New York', 'San Francisco', 'Los Angeles']}
df = pd.DataFrame(data)

def file_dataFrame():
    # 读取csv, excel, sql, json, parquet，以 read_ 开头 （the first and last 5 rows will be shown by default:）
    # titanic = pd.read_csv("titanic.csv")
    # titanic = pd.read_excel("titanic.xlsx", sheet_name="passengers")
    # 读取前10行，后10行
    # print(titanic_data.head(10))
    # print(titanic_data.tail(10))
    # 写入数据
    # titanic.to_excel("titanic.xlsx", sheet_name="passengers", index=False)
    print("")
def SelectDataFrame():

    # 查询：获取数量([rows, columns])
    print("查询：获取数量([rows, columns])")
    print(df.shape)

    # 查询：获取前 2 行(head默认是5)
    print("查询：获取前 2 行，获取后 2 行")
    print(df.head(2))
    print(df.tail(2))

    # 查询：行的范围 列的范围（索引从0开始的）
    print("查询：行的范围 列的范围")
    print(df.iloc[1, 2])
    print(df.iloc[1:2, 1:2])

    # 查询：获取每个列的数据类型（The data types in this DataFrame are integers (int64), floats (float64) and strings (object).）
    print("查询：获取所有列")
    print(df.columns)

    # 查询：获取每个列的数据类型（The data types in this DataFrame are integers (int64), floats (float64) and strings (object).）
    print("查询：获取每个列的数据类型")
    print(df.dtypes)

    # 查询：选择最大值
    print("查询：选择最大值")
    print(df['Age'].max())

    # 查询：计算平均值
    print("查询：计算平均值")
    print(df['Age'].mean())

    # 查询：选择多列
    print("查询：选择多列")
    print(df[['Name', 'City']])

    # 查询：选择年龄大于等于 30 的行
    print("查询：选择年龄大于等于 30 的行")
    print(df[df['Age'] >= 30])

    # 查询：选择年龄大于等于 30 的人的姓名
    print("查询：选择年龄大于等于 30 的人的姓名")
    print(df.loc[df['Age'] >= 30, "Name"])

    # 查询：多条件，筛选
    print("查询：多条件，筛选")
    print(df[df['Age'].isin([25, 30])])

    # 查询：过滤空值
    print("查询：过滤空值")
    print(df[df['Age'].notna()])


def update_dataFrame():
    # 修改：一个字段排序，两个字段倒序排序
    print("修改：一个字段排序，两个字段倒序排序")
    print(df.sort_values(by="Age"))
    print(df.sort_values(by=['Age', 'City'], ascending=False))

def add_dataFrame():
    # 新增：增加一列
    print("新增：增加一列")
    df['new_column'] = df['Age'] + 1
def violence_test_column():
    age_list = [item for item in range(1000)]
    data = {}
    for i in range(10000000):
        column_name = "new_column_{}".format(i)
        data[column_name] = age_list

    start_time = datetime.now()
    df = pd.DataFrame(data)
    end_time = datetime.now()
    print("初始化dataFrame：开始时间：%s, 结束时间：%s，耗时：%s" % (start_time, end_time, (end_time-start_time)))

    start_time = datetime.now()
    print(df.iloc[1]['new_column_1'])
    print(df.iloc[2]['new_column_1'])
    print(df.iloc[3]['new_column_1'])
    end_time = datetime.now()
    print("查询：开始时间：%s, 结束时间：%s，耗时：%s" % (start_time, end_time, (end_time-start_time)))

if __name__ == '__main__':
    SelectDataFrame()







