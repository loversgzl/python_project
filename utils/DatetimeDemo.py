from datetime import datetime
from zoneinfo import ZoneInfo  # Python 3.9 及以上版本

def datetime_demo():
    curr_time = datetime.now()
    print(curr_time)

    # 字符串转时间戳，带毫秒
    datetimeStr = "2024-04-18 15:35:54.672082"
    curr_time = datetime.strptime(datetimeStr, '%Y-%m-%d %H:%M:%S.%f')
    print(curr_time)

    # 时间戳转时间（毫秒就除以1000），增加时区
    timestamp = 1681875167.465
    utc_dt = datetime.fromtimestamp(timestamp, tz=ZoneInfo('UTC'))
    # 将 UTC 时间转换为中国标准时间
    cst_dt = utc_dt.astimezone(ZoneInfo('Asia/Shanghai'))
    print(cst_dt)

    # 时间相加减
    curr_one = datetime.now()
    curr_two = datetime.now()
    print(curr_one - curr_one)
    print(curr_one.timestamp() - curr_two.timestamp())

if __name__ == '__main__':
        datetime_demo()







