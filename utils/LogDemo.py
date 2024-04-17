import datetime
import logging

def init_log():
    # 创建两个日志记录器
    logger1 = logging.getLogger('logger1')
    logger2 = logging.getLogger('logger2')

    # 创建文件处理程序，指定日志文件名
    file_handler1 = logging.FileHandler('../log_file1.txt', encoding='utf-8')
    file_handler2 = logging.FileHandler('../log_file2.txt', encoding='utf-8')

    # 创建格式化器，定义日志记录的格式
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    # 将格式化器添加到处理程序
    file_handler1.setFormatter(formatter)
    file_handler2.setFormatter(formatter)

    # 将处理程序添加到日志记录器
    logger1.addHandler(file_handler1)
    logger2.addHandler(file_handler2)

    # 设置日志级别
    logger1.setLevel(logging.INFO)
    logger2.setLevel(logging.WARNING)

    # 记录一些信息到两个不同的日志
    logger1.info('This is an informational message for logger1.')
    logger2.warning('This is a warning message for logger2.')
    logger1.info(datetime.datetime.now())

if __name__ == '__main__':
    init_log()
