'''
1、PEP8（Python Enhacement Proposal #8 《8 号 Python 增强规范》）
2、《Google Python 风格规范》（Google Python Style Guide），以下简称 Google Style，这是源自 Google 内部的风格规范。公开发布的社区版本，是为了让 Google 旗下所有 Python 开源项目的编程风格统一。
（http://google.github.io/styleguide/pyguide.html）

'''

'''
1、 == 和 is 区别
看起来 is 是比较内存地址，那么两个结果应该都是一样的，可是实际上打印出来的，却分别是 True 和 False！
原因是在 CPython（Python 的 C 实现）的实现中，把 -5 到 256 的整数做成了 singleton，也就是说，这个区间里的数字都会引用同一块内存区域，所以上面的 27 和下面的 27 会指向同一个地址，运行结果为 True。
但是 -5 到 256 之外的数字，会因为你的重新定义而被重新分配内存，所以两个 721 会指向不同的内存地址，结果也就是 False 了。
所以，即使你已经清楚，is 比较对象的内存地址，你也应该在代码风格中，避免去用 is 比较两个 Python 整数的地址。

'''
# 错误示例
x = 27
y = 27
print(x is y)

x = 721
y = 721
print(x is y)


'''
1、range 在版本二中，一次性生成，如果太大会导致内存占用过多，所有二有 Xrange这个函数，版本三改进了，废弃了 xrange这个函数，将其功能内置到 range 中了，迭代生成，不怕数字太大
2、keys() 方法会在遍历前生成一个临时的列表，导致上面的代码消耗大量内存并且运行缓慢。正确的方式，是使用默认的 iterator。默认的 iterator 不会分配新内存，也就不会造成上面的性能问题:
正确示例： for key in adict:

'''
adict = {i: i * 2 for i in range(10000000)}
for key in adict.keys():
    print("{0} = {1}".format(key, adict[key]))

















