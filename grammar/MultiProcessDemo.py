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

if __name__ == '__main__':
    multi_process()