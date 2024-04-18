
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


# 性能




