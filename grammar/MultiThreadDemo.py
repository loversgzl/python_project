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

        # for循环创建和启动十个线程
        for i in range(1000):
            thread = threading.Thread(target=self.worker, args=(i,))
            self.threads.append(thread)
            thread.start()

        # 等待所有线程执行完成
        for thread in self.threads:
            thread.join()

        endTime = datetime.now()
        print("开始时间：%s, 结束时间：%s, 总共耗时耗时：%s" % (startTime, endTime, (endTime - startTime)))

    def worker(self, thread_id):
        print(f"线程：{thread_id}，开始计算")
        temp = 0
        for i in range(10000000):
            temp += i


    def createThreadTwo(self):
        # 创建 ThreadPoolExecutor，并指定线程数（可以根据需求调整）
        with ThreadPoolExecutor(max_workers=1000) as executor:
            # 提交任务给线程池
            # 这里提交了十万个任务，每个任务执行 my_function 函数
            futures = [executor.submit(self.worker, i) for i in range(10000)]

            # 等待所有任务完成
            for future in futures:
                future.result()

        print("All threads have finished")



if __name__ == '__main__':
    MultiThread = MultiThread()
    MultiThread.createThreadTwo()


