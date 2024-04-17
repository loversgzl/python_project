import schedule
import time
from datetime import datetime


'''
schedule.run_pending() 是 schedule 库中的一个方法，用于运行已经被安排但还没有执行的任务。
当你在程序中使用 schedule.every().xxx.do(job) 来安排定时任务时，这些任务并不会立即执行，而是需要通过 run_pending() 方法来触发执行。
一般将 schedule.run_pending() 放在一个 while 循环中，它会检查是否有已经到了执行时间的任务，如果有就执行。如果不调用这个方法，即使任务的执行时间到了，它们也不会被执行。
这种设计允许你在程序中维护一个定时任务列表，而不需要在每个任务的执行逻辑中包含复杂的定时控制逻辑。
'''

def minute_job():
    now = datetime.now().replace(microsecond=0)
    print("当前时间：%s，分钟定时任务执行了！" % now)

def second_job():
    now = datetime.now().replace(microsecond=0)
    print("当前时间：%s，秒钟定时任务执行了！" % now)

def schedules():
        # 每隔一分钟执行一次任务
        schedule.every(1).minutes.do(minute_job)

        # 每隔15秒执行一次任务
        schedule.every(15).seconds.do(second_job)

        while True:
            now = datetime.now().replace(microsecond=0)
            print("当前时间：%s" % now)
            print("每隔5秒检查一下，当前是否有到时间，需要执行的定时任务")
            time.sleep(5)
            schedule.run_pending()
if __name__ == '__main__':
        schedules()
