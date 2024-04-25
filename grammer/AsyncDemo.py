import asyncio
import time
import requests
from datetime import datetime


class AsyncDemo:
    """
    参考文档：https://blog.csdn.net/lady_killer9/article/details/128891256

    基本概念：
    举个例子：假设有1个洗衣房，里面有10台洗衣机，有一个洗衣工在负责这10台洗衣机。那么洗衣房就相当于1个进程，洗衣工就相当1个线程。如果有10个洗衣工，就相当于10个线程，1个进程是可以开多线程的。这就是多线程！
    那么协程呢？先不急。大家都知道，洗衣机洗衣服是需要等待时间的，如果10个洗衣工，1人负责1台洗衣机，这样效率肯定会提高，但是不觉得浪费资源吗？明明1 个人能做的事，却要10个人来做。只是把衣服放进去，打开开关，就没事做了，等衣服洗好再拿出来就可以了。
    就算很多人来洗衣服，1个人也足以应付了，开好第一台洗衣机，在等待的时候去开第二台洗衣机，再开第三台，……直到有衣服洗好了，就回来把衣服取出来，接着再取另一台的（哪台洗好先就取哪台，所以协程是无序的）。这就是计算机的协程！洗衣机就是执行的方法。
    当你程序中方法需要等待时间的话，就可以用协程，效率高，消耗资源少。
    缺点：只有这个洗衣工处理完当前的洗衣机时，它才能处理下一个，本质上它还是串行处理所有任务，所以如果这些任务都是非常耗时，则处理的延迟也越多。
    总结：进程就是一个应用程序，线程就是这个应用程序可以同时执行多项任务，但是如果这多项任务需要等待，则有些浪费资源了，所以出现了协程，一个可以中断等待的函数，并且在一个线程中可以创建多个协程。
    总结1：Asyncio 为抢占式任务处理提供了一种更安全的替代方法，从而避免了再复杂的多线程应用中经常发生的错误，竞争条件等危险。

    重点函数：（先定义协程函数，调用协程函数返回协程对象，只有将多个协程对象转换为协程任务，放入到事件循环中，才能做到程序并发执行）
    协程函数：coroutine function，定义形式为 async def 的函数。
    协程对象：coroutine object，调用协程函数返回的对象。
    事件循环：event loop，并发执行任务的大脑，判断哪些任务已处于可执行状态，并执行。
    协程任务：coroutine task，事件循环调度的最小单位，可由协程对象转化，只有这样调度才能让协程对象并发执行。
    asyncio.run()
    asyncio.create_task()

    廖雪峰：https://www.liaoxuefeng.com/wiki/1016959663602400/1017968846697824
    看起来A、B的执行有点像多线程，但协程的特点在于是一个线程执行，那和多线程比，协程有何优势？
    最大的优势就是协程极高的执行效率。因为子程序切换不是线程切换，而是由程序自身控制，因此，没有线程切换的开销，和多线程比，线程数量越多，协程的性能优势就越明显。
    第二大优势就是不需要多线程的锁机制，因为只有一个线程，也不存在同时写变量冲突，在协程中控制共享资源不加锁，只需要判断状态就好了，所以执行效率比多线程高很多。
    因为协程是一个线程执行，那怎么利用多核CPU呢？最简单的方法是多进程+协程，既充分利用多核，又充分发挥协程的高效率，可获得极高的性能。

    问：Asyncio 使线程变的多余？
    当然不，线程的真正价值在于能够编写多 CPU 程序，其中不同的计算任务可以共享内存，所以我们才需要加锁释放锁。
    协程的核心，是以线程逻辑来维护上下文，以极低的成本来实现高并发。单从性能上讲，协程相比传统异步模型并没有优势，开发效率的革命性提升，这才是关键。
    这里我们必须要指出，在并发量方面，使用「协程」的方式并不优于「非阻塞+回调」的方式，而我们之所以选择协程是因为它的编程模型更简单，类似于同步，也就是可以让我们使用同步的方式编写异步的代码。
    「非阻塞+回调」这种方式非常考验编程技巧，一旦出现错误，不好定位问题，容易陷入回调地狱、栈撕裂等困境。

    协程英文名：coroutine

    资料1：https://blog.csdn.net/cainiao_python/article/details/125056926


    """

    '''
    python 3.5 之前的语法
    '''
    @asyncio.coroutine
    def hello_one(self):
        print("Hello world!")
        r = yield from asyncio.sleep(1)
        print("Hello again!")

    '''
    python 3.5 之后的语法
    从广义上讲，协程是一种轻量级的并发模型，说的比较高大上。但从狭义上讲，协程就是调用一个可以暂停并切换的函数。像我们使用 async def 定义的就是一个协程函数，本质上也是个函数，而调用协程函数就会得到一个协程。
    将协程丢进事件循环，由事件循环驱动执行，一旦发生阻塞，便将执行权主动交给事件循环，事件循环再驱动其它协程执行。所以自始至终都只有一个线程，而协程只不过是我们参考线程的结构，在用户态模拟出来的。
    所以调用一个普通函数，会一直将内部的代码逻辑全部执行完；而调用一个协程函数，在内部出现了阻塞，那么会切换到其它的协程。
    但是协程出现阻塞能够切换有一个重要的前提，就是这个阻塞不能涉及任何的系统调用，比如 time.sleep、同步的 socket 等等。这些都需要内核参与，而内核一旦参与了，那么造成的阻塞就不单单是阻塞某个协程那么简单了
    （OS 也感知不到协程），而是会使线程阻塞。线程一旦阻塞，在其之上的所有协程都会阻塞，由于协程是以线程作为载体的，实际执行的肯定是线程，如果每个协程都会使得线程阻塞，那么此时不就相当于串行了吗？
    '''
    async def hello_two(self):
        print("Hello world!")
        r = await asyncio.sleep(1)
        print("Hello again!")

    '''
    知识点1：阻塞，切换
    1、回到上面那个协程的例子中，我们一共发了 10 个请求，并在可能阻塞的地方加上了 await。意思就是，在执行某个协程 await 后面的代码时如果阻塞了，那么该协程会主动将执行权交给事件循环，
    然后事件循环再选择其它的协程执行。并且协程本质上也是个单线程，虽然协程可以有多个，但是背后的线程只有一个。
    由此可见，协程就是用户态的线程。然而，为了保证所有切换都在用户态进行，协程必须重新封装所有的阻塞系统调用，否则一旦协程触发了线程切换，会导致这个线程进入休眠状态，进而其上的所有协程都得不到执行。
    比如普通的 sleep 函数会让当前线程休眠，由内核来唤醒线程，而协程化改造后，sleep 只会让当前协程休眠，由协程框架在指定时间后唤醒协程，所以在 Python 的协程里面我们不能写 time.sleep，而是应该写 asyncio.sleep。
    再比如，线程间的互斥锁是使用信号量实现的，而信号量也会导致线程休眠，协程化改造互斥锁后，同样由框架来协调、同步各协程的执行。
    2、协程出现阻塞能够切换有一个重要的前提，就是这个阻塞不能涉及任何的系统调用，比如 time.sleep、同步的 socket 等等。这些都需要内核参与，而内核一旦参与了，那么造成的阻塞就不单单是阻塞某个协程那么简单了
    （OS 也感知不到协程），而是会使线程阻塞。线程一旦阻塞，在其之上的所有协程都会阻塞，由于协程是以线程作为载体的，实际执行的肯定是线程，如果每个协程都会使得线程阻塞，那么此时不就相当于串行了吗？
    index1 会导致整个线程阻塞，无法进行协程的切换，验证阻塞的协程并发的执行，index2不会阻塞，只会导致协程的切换

    '''
    async def index1(self):
        time.sleep(30)
        return "index1"

    async def index2(self):
        await asyncio.sleep(30)
        return "index1"
    '''
    知识点2：await
    调用 async 异步函数，必须使用 await，使用 await 必须在 异步函数内，就是一个套娃。
    最外层可以使用：asyncio.run(AsyncDemo.A())

    '''

    '''
    asyncio.create_task 调用函数，需要使用 await 进行等待，否则程序会直接结束，通过 create_task 创建的任务会并行执行
    注意：如果只对某些协程任务添加了 await，则只会等待到最长时间的任务结束，程序即结束了，所以最好还是将所有的异步任务都添加 await
    '''
    async def main(self):
        startTime = datetime.now()
        print("开始时间：%s" % startTime)
        task_lady = asyncio.create_task(self.async_test(3, "lady"))
        task_killer = asyncio.create_task(self.async_test(6, "killer9"))
        await task_lady
        middleTime = datetime.now()
        print("lady耗时：%s" % middleTime)
        await task_killer
        endTime = datetime.now()
        print("开始时间：%s, 结束时间：%s, 总共耗时耗时：%s" % (startTime, endTime, (endTime - startTime)))

    '''
    在一个异步函数中，多次调用 await，则是串行执行
    '''
    async def async_test(self, delay: int, content):
        print(delay)
        await asyncio.sleep(delay)
        print(content)

    '''
    压力测试，看看性能如何
    '''
    async def async_pressure_test_main(self):
        startTime = datetime.now()
        for i in range(1000):
            asyncio.create_task(self.async_pressure_test(i))

        task = asyncio.create_task(self.async_pressure_test('end'))
        await task
        endTime = datetime.now()
        print("开始时间：%s, 结束时间：%s, 总共耗时耗时：%s" % (startTime, endTime, (endTime - startTime)))

    async def async_pressure_test(self, index):
        print(f"协程：{index}， 开始运行")
        temp = []
        for i in range(25):
            await asyncio.sleep(1)
            for j in range(10000):
                temp.append("abcd")
        print(f"协程：{index}， 结束运行")

    async def A(self):
        print("1")
        print("2")
        print("3")
        try:
            await self.B()
        except:
            print("4")
        print(5)

    async def B(self):
        print("a")
        print("b")
        print("c")
        raise Exception("报错了")
        print("d")

if __name__ == '__main__':
    AsyncDemo = AsyncDemo()
    # 可以作为最高层级的入口点，如果不用这个，直接调用异步的函数，会报： RuntimeWarning: coroutine 'main' was never awaited，且直接调用并不会真正执行
    # 注意，main 函数由于加了关键字，已经是协程函数，直接调用(AsyncDemo.main())会返回协程对象，并不会执行函数内的代码，执行协程代码需要使用(asyncio.run)
    print("开始")
    asyncio.run(AsyncDemo.A())
    print("结束")
    print(datetime.now())
