import threading
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import *
from multiprocessing import Manager
import sys,ast,multiprocessing,os,csv,json
from multiprocessing import Process, Value, Array

class MultiThread():

    '''
    在 Python 中，多线程在 Linux 中通常是串行的，而不是并行的。这是由于 Python 的全局解释器锁（Global Interpreter Lock，GIL）的存在。
    全局解释器锁是 Python 解释器中的一个机制，它限制了同时只能有一个线程执行 Python 字节码。即使你在多线程程序中创建了多个线程，但是这些线程在同一时刻只能有一个被执行，因为 GIL 会锁住解释器，防止多线程同时执行 Python 字节码。
    虽然多线程在 Python 中无法实现真正的并行执行，但在某些情况下，多线程仍然能够提升程序的性能。例如，当线程在等待 I/O 操作（如网络请求、文件读写）时，解释器会释放 GIL，允许其他线程执行。这样的情况下，多线程可以提高程序的效率，因为不同的线程可以在等待 I/O 操作的同时执行其他计算任务。
    需要注意的是，在涉及 CPU 密集型任务的情况下，多线程并不会提高程序的性能，因为多个线程无法同时执行 Python 字节码。对于 CPU 密集型任务，你可能需要考虑使用多进程或者异步编程来实现并行执行。
    如果你希望实现真正的并行执行，可以考虑使用多进程或者其他并行计算的技术。在 Linux 中，多进程可以实现真正的并行执行，因为每个进程都有自己独立的 Python 解释器进程，不受 GIL 的限制。


    创建多个进程可以实现真正的并行执行，因为每个进程都有自己独立的 Python 解释器进程，不受全局解释器锁（GIL）的限制。
    在 Python 中，你可以使用 multiprocessing 模块来创建多个进程。以下是一个简单的示例，演示了如何使用 multiprocessing 模块创建多个进程：

    '''
    def createMultiThread(self):
        self.threads = []
        startTime = datetime.now()

        # 创建和启动十个线程
        for i in range(10):
            thread = threading.Thread(target=self.worker, args=(i,))
            self.threads.append(thread)
            thread.start()

        # 等待所有线程执行完成
        for thread in self.threads:
            thread.join()

        endTime = datetime.now()
        print("开始时间：%s, 结束时间：%s, 总共耗时耗时：%s" % (startTime, endTime, (endTime - startTime)))

    def worker(self, thread_id):
        print(f"线程：{thread_id}，休息 5 秒")
        for i in range(5):
            time.sleep(1)

    def createThreadTwo(self):
        # 创建 ThreadPoolExecutor，并指定线程数（可以根据需求调整）
        with ThreadPoolExecutor(max_workers=4) as executor:
            # 提交任务给线程池
            # 这里提交了十万个任务，每个任务执行 my_function 函数
            futures = [executor.submit(self.worker, i) for i in range(10000)]

            # 等待所有任务完成
            for future in futures:
                future.result()

        print("All threads have finished")
    def process_data(self, data):
        # Your processing logic here
        return data * 2
    def createThreadThree(self):
        # 创建 ProcessPoolExecutor，并指定进程数（可以根据需求调整）
        with ProcessPoolExecutor(max_workers=4) as executor:
            # 提交任务给进程池
            # 这里提交了十个任务，每个任务执行 process_data 函数
            data_to_process = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
            futures = [executor.submit(self.worker, item) for item in data_to_process]
            while True:
                isDone = True
                for future in futures:
                    if not future.done():
                        isDone = False
                if isDone:
                    break
                print("还未结束，休息一分钟后继续扫描")
                time.sleep(60)


            # 使用 as_completed 迭代已完成的任务
            # for future in as_completed(futures):
            #     # result = future.result()
            #     print(future)

        print("All threads have finished")

    def task_function(self):
        # 模拟一个耗时的任务
        time.sleep(3)
        print("Task completed")
    def createThreadFour(self):
        # 使用 ProcessPoolExecutor 创建进程池
        with ProcessPoolExecutor() as executor:
            # 提交任务给进程池
            future = executor.submit(self.task_function)

            # 判断任务是否已经结束
            while not future.done():
                print("Task is still running...")
                time.sleep(1)

            # 获取任务的结果
            # result = future.result()
            # print("Task result:", result)

# def MultiThread():
#     list_size = 100
#     paramList = []
#     with ThreadPoolExecutor(max_workers=list_size) as executor:
#         futures = []
#
#         for i in range(list_size):
#             if (i + 1) == pool_list:
#                 array_list = band_casting_users[i * list_size:]
#             else:
#                 array_list = band_casting_users[i * list_size: (i + 1) * list_size]
#
#             futures.append(executor.submit(process_chunk, array_list, new_list))
#
#         # 等待所有线程完成
#         wait(futures)
#
#     print("数据大小:", len(band_casting_users))



if __name__ == '__main__':
    MultiThread = MultiThread()
    MultiThread.createMultiThread()


