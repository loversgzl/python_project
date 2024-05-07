import ast
import csv

'''
读取文件中的参数，并转为相应的数据结构，而不是字符串
'''
def read_file():
    param_list = []
    param_file_path = 'param.txt'
    with open(param_file_path, 'r') as paramFile:
        for param in paramFile:
            if len(param.strip()) > 0:
                param_list.append(ast.literal_eval(param.strip()))
    print(param_list)

'''
将数据写入CSV文件
'''
def write_to_csvfile(dataList, path):
    with open(path, 'a', newline='') as file:
        csv_writer = csv.writer(file)
        # 逐行写入数据
        for row in dataList:
            csv_writer.writerow(row)

if __name__ == '__main__':
   read_file()