import threading
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import *
from multiprocessing import Manager
import sys,ast,multiprocessing,os,csv,json
from multiprocessing import Process, Value, Array

def MultiProcess():
    # 创建 Manager 对象
    with Manager() as manager:
        # 创建 ListProxy 对象
        shared_list = manager.list([1, 2, 3, 4, 5])

        # 读取 ListProxy 中的值
        values = list(shared_list)
        print("Values in ListProxy:", values)

def modify_shared_data(shared_value, shared_array):
    shared_value.value = 42
    shared_array[0] = 99

def MultiProcessArray():
    shared_value = Value('i', 0)
    shared_array = Array('i', [0, 0, 0])

    p = Process(target=modify_shared_data, args=(shared_value, shared_array))
    p.start()
    p.join()

    print("Shared Value:", shared_value.value)
    print("Shared Array:", shared_array[:])

def worker_process(process_id):
    print(f"Worker Process {process_id} started.")
    time.sleep(2)
    print(f"Worker Process {process_id} finished.")

def CreateMultiProcess():
    # 创建两个子进程
    process1 = multiprocessing.Process(target=worker_process, args=(1,))
    process2 = multiprocessing.Process(target=worker_process, args=(2,))

    # 启动子进程
    process1.start()
    process2.start()

    # 等待子进程完成
    process1.join()
    process2.join()

    print("Main Process finished.")

def worker():
    """工作函数"""
    pid = os.getpid()
    # core_id = int(pid) % multiprocessing.cpu_count()  # 使用进程的 PID 来决定绑定的 CPU 核心
    core_id = 150
    os.system(f"taskset -p -c {core_id} {pid}")  # 使用 taskset 命令将进程绑定到指定的 CPU 核心
    print(f"Worker function, process {pid} bound to CPU core {core_id}")
    i  = 0
    while True:
        i += 1
        print(i)


def multi_process():
     # 设置启动方法为 "spawn"
    multiprocessing.set_start_method('spawn')

    # 创建多个进程
    num_processes = 1
    processes = []
    for _ in range(num_processes):
        process = multiprocessing.Process(target=worker)
        processes.append(process)
        process.start()

    # 等待所有进程结束
    for process in processes:
        process.join()

    print("All processes have finished")

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

def task_function():
    # 模拟一个耗时的任务
    time.sleep(3)
    print("Task completed")
def createThreadFour():
    # 使用 ProcessPoolExecutor 创建进程池
    with ProcessPoolExecutor() as executor:
        # 提交任务给进程池
        future = executor.submit(task_function)

        # 判断任务是否已经结束
        while not future.done():
            print("Task is still running...")
            time.sleep(1)

        # 获取任务的结果
        # result = future.result()
        # print("Task result:", result)


if __name__ == '__main__':
    multi_process()