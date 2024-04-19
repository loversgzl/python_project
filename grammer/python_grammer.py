import operator
# 问题
'''
问：py2 和 py3 的区别有哪些？



'''

# 报错
'''
#错误：par = range(len(edges)+2)—‘range’object does not support item assignment
报错原因：python3.x range返回的是range对象，不返回数组对象

#错误：TypeError: 'str' object does not support item assignment
报错原因：（字符串）start[i:i+2] = 'LX'

#错误：SyntaxError: 'return' outside function
报错原因：函数中的缩进格式有误，第3行之后的缩进格式不正确

#错误：TypeError: 'int' object is not subscriptable
报错原因：int类型当做列表用了

#错误：RecursionError: maximum recursion depth exceeded in comparison
报错原因：递归没写好，造成无限递归了

#超时：写代码的过程中调用了很多sum函数，而用一个变量tempsum记录总和可以加快运行
#超时：不要在循环语句里面调用函数，尽量在外面调用，在里面用结果就好了。


'''


# 其它操作
def other_opt():
    a, b, c = 1, 2, 3
    print("变量追加到后面", type(a))
    print("变量：%s，可以插入到不同位置" % type(a))


# LIST(什么元素都能存，包括数字，字符串，对象)
def list_demo():
    nums = [0, 1, 2, '3']
    # 查
    print(nums[0])
    print(nums[1:3])
    print(nums[-1])

    # 增
    nums.append(4)
    nums.append([5, 6, 7])
    nums.extend([5, 6, 7])
    nums += [8, 9, 10]
    print(nums)

    # 删
    del nums[3]
    del nums[4]
    print(nums)

    # 改
    nums[0] = 1
    print(nums)

    # 操作：比较两个list中的元素是否相同；
    operator.eq(nums, [1, 2, 3])
    print(len(nums)) # 长度；
    print(max(nums)) # 最大值；
    print(min(nums)) # 最小值；
    print(nums.index(10)) # 查询第一个匹配的索引
    print(nums.count(1)) #某个元素出现的次数；
    nums.remove(1) # 删除某个元素
    nums.sort(reverse=True) # 原地排序，没有返回值
    print(nums)
    print(nums.clear()) # 清空列表

def dict_demo():
    tinydict = {'name': 'runoob', 'likes': 123, 'url': 'www.runoob.com'}
    tinydict['name'] = 'TOM'
    print(tinydict['name']) # 如果不存在key则会报错
    print(tinydict.get('name1'))
    print(tinydict)
    print('name' in tinydict)
    print(list(tinydict.keys())) # 返回一个可迭代的视图对象，需要转换
    print(tinydict.values())

# TUPLE（Python 的元组与列表类似，不同之处在于元组的元素不能修改）
def tuple_demo():
    # 只有一个元素时需要添加逗号，否则会被认为是括号
    tup = (1, 2, 3, 4)
    tup = 1, 2, 3, 4
    print(tup)

    # 不能修改，包括删除，但是可以进行组合
    tup1 = (12, 34.56)
    tup2 = ('abc', 'xyz')
    tup3 = tup1 + tup2
    print(tup3)

# 函数中引用生效
def quote_demo():
    total_list = []
    for i in range(10):
        temp = [i] # 每次会生成一个新的LIST，地址也是不同的
        total_list.append(temp.copy())
        temp.clear() # 这里不行，上一个引用还在列表中，不能对当前引用进行清空，可以使用copy对地址进行复制
    print(total_list)


# 进阶：Python 推导式
def advance():
    num_list = [i for i in range(30) if i % 3 == 0]
    print(num_list)
    num_dict = {x: x**2 for x in (2, 4, 6)}
    print(num_dict)

if __name__ == '__main__':
    advance()