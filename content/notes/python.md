+++
title = 'python'
date = '2026-09-28T12:00:00+08:00'
draft = false
summary = ''
tags = []
showtoc = true
+++
本来要学安卓的 怎么跑这里来了。

看漫宿的博客和菜鸟学习的，

写笔记也可以看作是强制让自己完整不加遗漏地看一遍并且进行思考吧 主要也是很久没有手搓过代码了 想到python也没有系统学习 现在就把窟窿填上吧

[Python3 教程 \| 菜鸟教程](https://www.runoob.com/python3)

## 运算

比较基础 可以复习一下

## 字符串

### 转义字符

```Python
print("hello,,\rworldd")
```

输出`world,`

经过测试，这个替换会**先跳过符号，优先去取代字符串**，如果前面的字符串不够，就会往后取代符号。



实现百分比进度

```Python
import time

for i in range(101):
    print("\r{:3}%".format(i),end=' ')
    time.sleep(0.05)
```

这段代码实现了一个在同一行动态刷新的百分比进度条，运行效果是**从 0% 走到 100%**，共耗时约 5 秒，最后只会得到1个数字。

> - `\r`：把光标退回到当前行的最开头。这样后续打印的内容会直接覆盖原来的内容。
> 
> - `{:3}`：格式化占位符，表示数字占据 3 个字符宽度，右对齐（不足的用空格补齐）。例如 `0` 变成 `" 0"`，`100` 就是 `"100"`。这一点非常重要，因为它保证了每次输出的字符串长度完全一致（固定为4个字符的百分比\+1个空格），不会出现上一个问题里“覆盖不全留下多余逗号”的情况。
> 
> - **`format(i)`****：把当前的进度数字塞进占位符。**
> 
> - **`end=' '`****：默认 ****`print()`**** 会换行（****`\n`****），这里改成 ****`end=' '`**** 意味着不换行，并在末尾加上一个空格（总长度变成 5 个字符，覆盖时刚好能把上一次的内容完全抹掉）。**
> 
> 

所有转义字符：

### 字符串运算符

### 字符串格式化

类似于C语言的吧

```Python
import time
for i in range(101):
    print("%d%%"% i)
    time.sleep(0.01)
```

> **字符串里面的两个 ****`%`****：****`"%d%%"`**
> 
> 这两个百分号在引号内部，属于“模板”。
> 
> - 第一个 `%d`：这是占位符。`%` 是特殊指令的开头，`d` 代表整数（decimal）。它挖了一个坑，等着外面的变量 `i` 填进来。
> 
> - 第二个 `%%`：这是**转义字符**。在 % 格式化语法里，因为单独的 `%` 已经被“征用”去当占位符的开头了（比如 `%d`, `%s`），那如果程序员真的想原样输出一个百分号符号怎么办？必须连写两个 `%%`，Python 才会把它当成一个普通的 `%` 打印出来。
> 
> 字符串外面的一个 `%`：`% i`
> 
> 这个引号外面的 `%`，是**格式化操作符**。它的意思是：**“把右边的变量 ****`i`****，塞进左边字符串的占位符里”。**
> 
> 

其实可以直接写成

```Python
print(f"{i}%")
```

刚刚的进度条代码也可以直接写成

```Python
print(f"\r{i:3}%", end=' ')
```

也就是我们一会要讲的 算是一种引入吧

### f\-string

f\-string 是 python3\.6 之后版本添加的，称之为**字面量格式化字符串**，是新的格式化字符串的语法。

之前我们习惯用百分号 \(%\):

f\-string 格式化字符串**以 f 开头，后面跟着字符串，字符串中的表达式用大括号 \{\} 包起来**，**它会将变量或表达式计算后的值替换进去**，实例如下：

```Python
>>> w = {'name': 'Runoob', 'url': 'www.runoob.com'}
>>> f'{w["name"]}: {w["url"]}'
'Runoob: www.runoob.com'
```

### 函数

Eg

```Python
print("A 对应的 ASCII 值为：", ord('A')) # 输出：A 对应的 ASCII 值为： 65

print("\x41 为 A 的 ASCII 代码") # 输出：A 为 A 的 ASCII 代码

decimal_number = 42
binary_number = **bin**(decimal_number) # 十进制转换为二进制
print('转换为二进制:', binary_number) # 转换为二进制: 0b101010

octal_number = **oct**(decimal_number) # 十进制转换为八进制
print('转换为八进制:', octal_number) # 转换为八进制: 0o52

hexadecimal_number = **hex**(decimal_number) # 十进制转换为十六进制
print('转换为十六进制:', hexadecimal_number) # 转换为十六进制: 0x2a

len(string)#返回字符串长度
```

## 列表

列表是最常用的 Python 数据类型，它可以作为一个方括号内的逗号分隔值出现。

列表的数据项**不需要具有相同的类型**

创建一个列表，只要把逗号分隔的不同的数据项使用方括号括起来即可。如下所示：

```Python
list1 = ['Google', 'Runoob', 1997, 2000]
```

### 列表的更新

列表的大小一旦确定，我们就可以通过append添加元素

```Python
list=[]
for i in range(101):
    #list[i]=i,错误示范
    list.append(i)#正确添加
```

错误示范会爆超过列表大小的错误，如果非要用第一种方法更改也行：

```Python
list=[0]*101
for i in range(101):
    list[i]=i
```

也就是要**提前确定好list的大小**



当然也可以通过del来删除元素

```Python
list1 = ['physics', 'chemistry', 1997, 2000]
 
print list1
del list1[2]
print "After deleting value at index 2 : "
print list1
```

输出

```Python
['physics', 'chemistry', 1997, 2000]
After deleting value at index 2 :
['physics', 'chemistry', 2000]
```

### 列表的截取

```Python
>>>L = ['Google', 'Runoob', 'Taobao']
>>> L[2]
'Taobao'
>>> L[-2]
'Runoob'
>>> L[1:]
['Runoob', 'Taobao']
>>>
```

### 列表函数及方法

python包含以下几个函数

包含以下几个方法

## 元组

Python 的元组与列表类似，不同之处在于元组的元素不能修改。

元组使用小括号 **\( \)**，列表使用方括号 **\[ \]**。

元组创建很简单，只需要在括号中添加元素，并使用逗号隔开即可。



**当元组中只包含一个元素时，需要在元素后面添加逗号 ****,**** ，否则括号会被当作运算符使用：**

```Python
>>> tup1 = (50)
>>> type(tup1)     # 不加逗号，类型为整型
<class 'int'>

>>> tup1 = (50,)
>>> type(tup1)     # 加上逗号，类型为元组
<class 'tuple'>
```

元组与字符串类似，下标索引从 0 开始，可以进行截取，组合等。

### 访问元组

元组可以使用下标索引来访问元组中的值，如下实例:

```Python
tup1 = ('Google', 'Runoob', 1997, 2000)
tup2 = (1, 2, 3, 4, 5, 6, 7 )
 
print ("tup1[0]: ", tup1[0])
print ("tup2[1:5]: ", tup2[1:5])
```

### 修改元组

```Python
tup1 = (12, 34.56)
tup2 = ('abc', 'xyz')
 
# 以下修改元组元素操作是非法的。
# tup1[0] = 100
 
# 创建一个新的元组
tup3 = tup1 + tup2
print (tup3)
```

输出结果

```Python
(12, 34.56, 'abc', 'xyz')
```



切片拼接法：

```Python
tup1 = (12, 34.56)

# 想要把索引0的12改成100
# 原理：取索引0之前的部分 + 新元素 + 取索引0之后的部分
new_tup = tup1[:0] + (100,) + tup1[1:] 

print(new_tup) # 输出 (100, 34.56)
```

或者转换成列表 修改好之后再换成元组

```Python
tup1 = (12, 34.56)

# 1. 先转成列表（列表是可以随意修改的）
temp_list = list(tup1)

# 2. 在列表上随便改
temp_list[0] = 100

# 3. 改完后，再转回元组，重新赋值给变量
tup1 = tuple(temp_list)

print(tup1) # 输出 (100, 34.56)
```



### 删除元组

元组中的元素值是不允许删除的，但我们可以使用del语句来删除整个元组，如下实例:

```Python
tup = ('Google', 'Runoob', 1997, 2000)
 
print (tup)
del tup
print ("删除后的元组 tup : ")
print (tup)
```

元组被删除之后 输出变量会有异常信息



**关于元组是不可变的**

所谓元组的不可变指的是元组所指向的内存中的内容不可变。

```Python
>>> tup = ('r', 'u', 'n', 'o', 'o', 'b')
>>> tup[0] = 'g'     # 不支持修改元素
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
TypeError: 'tuple' object does not support item assignment
>>> id(tup)     # 查看内存地址
4440687904
>>> tup = (1,2,3)
>>> id(tup)
4441088800    # 内存地址不一样了
```

## 字典

字典是另一种**可变容器**模型，且可存**储任意类型对象**。

字典的每个键值 `key=>value`** **对用冒号 `:` 分割，每个对之间用逗号`,`分割，整个字典包括在花括号 `{}` 中 ,格式如下所示：

```Python
d = {key1 : value1, key2 : value2, key3 : value3 }
```

键一定是唯一的 但是值不一定

### 创建字典

1. 创建空字典

```Python
# 使用大括号 {} 来创建空字典
emptyDict = {}
 
# 打印字典
print(emptyDict)
 
# 查看字典的数量
print("Length:", len(emptyDict))
 
# 查看类型
print(type(emptyDict))
```

输出

```Python
{}
Length: 0
<class 'dict'>
```

2. 使用内建函数`dict()`来创建字典

```Python
emptyDict = dict()
 
# 打印字典
print(emptyDict)
 
# 查看字典的数量
print("Length:",len(emptyDict))
 
# 查看类型
print(type(emptyDict))
```

输出结果：

```Python
{}
Length: 0
<class 'dict'>
```

或者

```Go
person = dict(name="小明", age=18, city="北京")
print(person) 
# 输出：{'name': '小明', 'age': 18, 'city': '北京'}
```

### 访问字典里的值

把相应的键放入方括号中

```Python
tinydict = {'Name': 'Runoob', 'Age': 7, 'Class': 'First'}
 
print ("tinydict['Name']: ", tinydict['Name'])
print ("tinydict['Age']: ", tinydict['Age'])
```



### 字典内置函数\&方法

## 推导式

### 列表推导式

```Python
[表达式 for 变量 in 列表] 
[out_exp_res for out_exp in input_list]

或者 

[表达式 for 变量 in 列表 if 条件]
[out_exp_res for out_exp in input_list if condition]
```

- out\_exp\_res：**列表生成元素表达式，可以是有返回值的函数。**

- for out\_exp in input\_list：迭代 input\_list 将 out\_exp 传入到 out\_exp\_res 表达式中。

- if condition：条件语句，可以过滤列表中不符合条件的值。

Eg\.

计算30以内能被3整除的整数

```Python
multiples = [i **for** i **in** range(30) **if** i % 3 == 0]
**print**(multiples)
```

### 字典推导式

基本格式：

```Python
{ key_expr: value_expr for value in collection }

或

{ key_expr: value_expr for value in collection if condition }
```

Eg\.

```Python
listdemo = ['Google','Runoob', 'Taobao']
**# 将列表中各字符串值为键，各字符串的长度为值，组成键值对**
>>> newdict = {key:len(key) for key in listdemo}
>>> newdict
{'Google': 6, 'Runoob': 6, 'Taobao': 6}
```

### 集合推导式

基本格式：

```Python
{ expression for item **in Sequence** }
或
{ expression for item in Sequence if conditional }
```

Eg\.

1. 计算数字1、2、3的平方数

```Python
>>> setnew = {i**2 for i in (1,2,3)}
>>> setnew
{1, 4, 9}
```

2. 判断不是abc的字母并输出对应字母

```Python
>>> a = {x for x in 'abracadabra' if x not in 'abc'}
>>> a
{'d', 'r'}
>>> type(a)
<class 'set'>
```

### 元组推导式

元组推导式可以**利用 range 区间、元组、列表、字典和集合等数据类型**，快速**生成一个满足指定需求的元组。**

基本格式：

```Python
(expression for item in Sequence )
或
(expression for item in Sequence if conditional )
```

元组推导式和列表推导式的用法也完全相同，只是元组推导式是用 `()` 圆括号将各部分括起来，而列表推导式用的是中括号 `[]`，另外元组推导式返回的结果是一个**生成器对象**。

Eg\.

生成一个包含数字 1\~9 的元组：

```Python
>>> a = (x for x in range(1,10))
>>> a
<generator object <genexpr> at 0x7faf6ee20a50>  # 返回的是生成器对象

>>> tuple(a)       # 使用 tuple() 函数，可以直接将生成器对象转换成元组
(1, 2, 3, 4, 5, 6, 7, 8, 9)
```



## 迭代器与生成器

### 迭代器

迭代是 Python 最强大的功能之一，是访问集合元素的一种方式。

迭代器是一个可以记住遍历的位置的对象。

**迭代器对象从集合的第一个元素开始访问，直到所有的元素被访问完结束。迭代器只能往前不会后退。**

迭代器有两个基本的方法：`iter()` 和 `next()`。

```Python
nums = [10, 20, 30]  # 这是一个列表（一本书）

# 1. 使用 iter() 拿到迭代器（请来翻书机器人，夹上书签）
it = iter(nums)  
print(type(it))  # <class 'list_iterator'>

# 2. 使用 next() 一页一页地翻（让机器人翻页）
print(next(it))  # 输出 10
print(next(it))  # 输出 20
print(next(it))  # 输出 30

# 3. 书翻完了，如果继续 next()，就会报错 StopIteration
# print(next(it))  # 报错：StopIteration
```

#### for循环

```Python
# for 循环的底层逻辑（伪代码）
nums = [10, 20, 30]
it = iter(nums)          # 第一步：偷偷调用 iter()
while True:
    try:
        x = next(it)     # 第二步：偷偷调用 next()
        print(x)         # 第三步：执行 for 循环里面的代码
    except StopIteration: # 遇到这个异常
        break            # 结束循环
```

for循环会自动帮我们调用了 `iter()`，然后又自动不停地调 `next()`，直到遇到 `StopIteration` 异常，就安静地结束循环，不报错。

### yield

> 生成器函数在调用的时候，本身就是一个迭代器。
> 
> 

在 Python 中，使用了 `yield` 的函数被称为**生成器（generator）**。

`yield` 是一个关键字，用于定义生成器函数，生成器函数是一种特殊的函数，可以在**迭代过程中逐步产生值，而不是一次性返回所有结果。**

跟普通函数不同的是，生成器是一个**返回迭代器的函数**，只能用于迭代操作，更简单点理解生成器就是一个迭代器。

当在生成器函数中使用 `yield` 语句时，**函数的执行将会暂停，并将 ****`yield`**** 后面的表达式作为当前迭代的值返回。**

然后，**每次调用生成器的 ****`next()`**** 方法或使用 ****`for`**** 循环进行迭代时，函数会从上次暂停的地方继续执行，直到再次遇到 ****`yield`**** 语句**。这样，**生成器函数可以逐步产生值，而不需要一次性计算并返回所有结果。**

> 简单来说，生成器是一个会**记住执行位置的特殊函数**，它把一次性返回变成了分批供应，专门用来处理海量数据或流式数据（比如读取超大文件）。
> 
> 

这样处理的好处是节省内存空间 因为跟普通函数处理不同 每次只占用一个空间 而不需要提前准备全部的空间 并且节省时间（在很大的文件中）

Eg\.

```Python
def countdown(n):
    print("--- 准备开始倒计时 ---")
    while n > 0:
        yield n        # 暂停点：交出 n，然后卡在这里
        n -= 1         # 下次唤醒时，从这里继续执行
    print("--- 点火，发射！ ---")

# 1. 创建生成器
c = countdown(3)  
print("生成了对象 c，但函数代码一行都没执行！\n")

# 2. 手动要值（模拟需要一点挤一点）
print("第一次要值：", next(c))
print("第二次要值：", next(c))
print("第三次要值：", next(c))

# 3. 如果还要第四次，会发生什么？
# print(next(c))  # 会打印“点火，发射！”，然后抛出 StopIteration 报错
```

（注意：如果没有第四次 `next(c)`，“点火，发射！”这一句永远不会打印。）

> **为什么“函数走到最后”会触发 StopIteration？**
> 
> 这就是 Python 迭代器协议（Iterator Protocol） 的硬性规定：
> 
> 当生成器函数执行到末尾，或者遇到 `return` 时，Python 会在底层自动抛出 `StopIteration` 异常。
> 
> 如果函数走到最后不抛这个异常，外面的 `for` 循环或 `next()` 就不知道已经结束了，会永远死循环等下去。
> 
> 

## 函数

### 参数

以下是调用函数时可使用的正式参数类型：

- 必需参数

- 关键字参数

- 默认参数

- 不定长参数

#### 必需参数

必需参数须以**正确的顺序**传入函数。调用时的**数量**必须和声明时的一样。

调用 printme\(\) 函数，你必须传入一个参数，不然会出现语法错误：

```Python
#可写函数说明
def printme( str ):
   "打印任何传入的字符串"
   print (str)
   return
 
# 调用 printme 函数，不加参数会报错
printme()
```

#### 关键字参数

关键字参数和函数调用关系紧密，函数调用使用关键字参数来确定传入的参数值。

使用关键字参数**允许函数调用时参数的顺序与声明时不一致**，因为 Python 解释器能够用参数名匹配参数值。

以下实例中演示了函数参数的使用不需要使用指定顺序：

```Python
#可写函数说明
def printinfo( name, age ):
   "打印任何传入的字符串"
   print ("名字: ", name)
   print ("年龄: ", age)
   return
 
#调用printinfo函数
printinfo( age=50, name="runoob" )
```

输出结果：

```Python
名字:  runoob
年龄:  50
```

#### 默认参数

调用函数时，如果没有传递参数，则会使用默认参数。以下实例中如果没有传入 age 参数，则使用默认值

```Python
#可写函数说明
def printinfo( name, age = 35 ):
   "打印任何传入的字符串"
   print ("名字: ", name)
   print ("年龄: ", age)
   return
 
#调用printinfo函数
printinfo( age=50, name="runoob" )
print ("------------------------")
printinfo( name="runoob" )
```

输出结果

```Python
名字:  runoob
年龄:  50
------------------------
名字:  runoob
年龄:  35
```

#### 不定长参数

我们需要一个函数能**处理比当初声明时更多的参数**。这些参数叫做不定长参数，和上述 2 种参数不同，声明时不会命名。基本语法如下：

```Python
def functionname([formal_args,] *var_args_tuple ):
   "函数_文档字符串"
   function_suite
   return [expression]
```

**加了星号 ****\***** 的参数会以元组\(tuple\)的形式导入，存放所有未命名的变量参数。**

Eg\.

```Python
# 可写函数说明
def printinfo( arg1, *vartuple ):
   "打印任何传入的参数"
   print (arg1)
   print (vartuple)
 
# 调用printinfo 函数
printinfo( 70, 60, 50 )
```

输出结果

```Python
70
(60, 50)
```



还有一种是参数带两个星号`**`，这种参数会以**字典**的形式导入

```Python
# 可写函数说明
def printinfo( arg1, **vardict ):
   "打印任何传入的参数"
   print ("输出: ")
   print (arg1)
   print (vardict)
 
# 调用printinfo 函数
printinfo(1, a=2,b=3)
```

输出

```Python
输出: 
1
{'a': 2, 'b': 3}
```



声明函数中，参数中型号`*`可以单独出现

Eg\.

```Python
def f(a,b,*,c):
    return a+b+c
```

如果单独出现星号 **\***，则星号 **\*** 后的参数**必须用关键字传入**：

```Python
>>> def f(a,b,*,c):
...     return a+b+c
... 
>>> f(1,2,3)   # 报错
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
TypeError: f() takes 2 positional arguments but 3 were given
>>> f(1,2,c=3) # 正常
6
>>>
```

### 匿名函数

Python 使用 **lambda** 来创建匿名函数。

所谓匿名，意即不再使用 **def** 语句这样标准的形式定义一个函数。

- **lambda** 只是一个表达式，函数体比 **def** 简单很多。

- **lambda 的主体是一个表达式，而不是一个代码**块。仅仅能在 lambda 表达式中封装有限的逻辑进去。

- **lambda 函数拥有自己的命名空间，且不能访问自己参数列表之外或全局命名空间里的参数。**

- 虽然 lambda 函数看起来只能写一行，却不等同于 C 或 C\+\+ 的内联函数，内联函数的目的是调用小函数时不占用栈内存从而减少函数调用的开销，提高代码的执行速度。

语法

```Python
lambda [arg1 [,arg2,.....argn]]:expression
```

Eg\.

```Python
x = lambda a : a + 10
print(x(5))
```

> `lambda a : a + 10` 里的 **`a`**** 就是参数，冒号 ****`:`**** 后面的 ****`a + 10`**** 就是函数体**。而且，lambda 会自动把冒号后面的计算结果当作返回值（相当于自带了 `return`），不需要你写 `return`。
> 
> 

输出结果

```Python
15
```

## 装饰器

装饰器（decorator）是 Python 中的一种高级功能，用于**在不修改原函数代码的前提下，动态扩展函数或类的功能**。

本质上，装饰器是一个函数：**它接收一个函数作为参数，并返回一个新的函数**（通常是对原函数的增强版本）。

### 基本语法

装饰器的核心思想是：用一个函数包装另一个函数

```Python
def decorator_function(original_function):
    def wrapper(*args, **kwargs):
        # 调用前
        print("执行前")

        result = original_function(*args, **kwargs)

        # 调用后
        print("执行后")

        return result
    return wrapper

@decorator_function
def target_function():
    print("原函数执行")
```



这个`@decorator_function` 完全等同于下面的代码：

```Python
def target_function():
    print("原函数执行")

target_function = decorator_function(target_function)
```

加上注释理解：

```Python
def decorator_function(original_function):  # 1. 接收原函数
    def wrapper(*args, **kwargs):           # 2. 定义包装函数
        print("执行前")                     # 3. 原函数执行前的“附加动作”
        result = original_function(*args, **kwargs) **# 4. 真正执行原函数**
        print("执行后")                     # 5. 原函数执行后的“附加动作”
        return result                       # 6. 把原函数的返回值原封不动送出去
    return wrapper                          # 7. 把包装函数交出去
```

按照我的理解就是：将一个函数的调用放入另一个函数中

## 模块

我们基本上是用 python 解释器来编程，如果我们从 Python 解释器退出再进入，那么我们定义的所有的方法和变量就都消失了。

为此 Python 提供了一个办法，把这些定义存放在文件中，为一些脚本或者交互式的解释器实例使用，这个文件被称为模块。

**Python 中的模块（Module）是一个包含 Python 定义和语句的文件，文件名就是模块名加上 ****\.py**** 后缀。**

模块可以包含函数、类、变量以及可执行的代码。通过模块，我们可以将代码组织成可重用的单元，便于管理和维护。



**模块的作用**

- 代码复用：将常用的功能封装到模块中，可以在多个程序中重复使用。

- 命名空间管理：模块可以避免命名冲突，不同模块中的同名函数或变量不会互相干扰。

Eg\.

```Python
# 文件名: using_sys.py
 
import sys
 
print('命令行参数如下:')
for i in sys.argv:
   print(i)
 
print('\n\nPython 路径为：', sys.path, '\n')
```

执行结果为

```Python
$ python using_sys.py 参数1 参数2
命令行参数如下:
using_sys.py
参数1
参数2


Python 路径为： ['/root', '/usr/lib/python3.4', '/usr/lib/python3.4/plat-x86_64-linux-gnu', '/usr/lib/python3.4/lib-dynload', '/usr/local/lib/python3.4/dist-packages', '/usr/lib/python3/dist-packages'] 

```



一个模块只会被导入一次，不管你执行了多少次 `import`。这样可以防止导入模块被一遍又一遍地执行。

### 搜索路径

当导入一个模块时，Python 会按照以下顺序查找模块：

1. 当前目录。

2. 环境变量 `PYTHONPATH` 指定的目录。

3. Python 标准库目录。

4. `.pth` 文件中指定的目录。

因此如果**在当前目录下存在与要引入模块同名的文件，就会把要引入的模块屏蔽掉。**

了解了搜索路径的概念，就可以在脚本中修改 `sys.path` 来引入一些不在搜索路径中的模块。

### `from...import`语句

Python 的 from 语句让我们**从模块中导入一个指定的部分到当前命名空间**中

```Python
from modname import name1[, name2[, ... nameN]]
```

Eg\.

导入模块 fibo 的 fib 函数

```Python
>>> from fibo import fib, fib2
>>> fib(500)
1 1 2 3 5 8 13 21 34 55 89 144 233 377
```

这个声明不会把整个fibo模块导入到当前的命名空间中，它只会将fibo里的fib函数引入进来。

### 给模块起别名

使用as关键字

```Python
import numpy as np  # 将 numpy 模块别名设置为 np
from math import sqrt as square_root  # 将 sqrt 函数别名设置为 square_root
```

### `from...import*`语句

把**一个模块的所有内容全都导入到当前的命名空间**也是可行的，只需使用如下声明：

```Python
from modname import *
```

## \_\_name\_\_与\_\_main\_\_

在python代码的末尾 我们经常能够看到

```Python
if __name__ == "__main__":
    main()
```

在 Python 中，`name` 是模块的一个特殊属性，`"main"` 是用于标识主执行模块的名称。

通过判断 **`name`**** 是否等于 ****`"main"`****，可以区分当前模块是作为程序入口运行，还是作为普通模块被导入。**

这种写法通常用于将程序的功能定义与运行入口分开，方便代码复用和测试。

### \_\_name\_\_变量

`name` 是 Python 自动设置的模块特殊属性，用于表示当前模块的名称。

它的值取决于模块的运行方式：

- **直接运行模块：**`name` 通常等于 `"main"`。

- **通过 import 导入模块：**`name` 通常等于模块的名称。

- **导入包中的子模块：**`name` 通常是完整模块名，例如 `"mypackage.utils"`。



下面创建一个名为 `module.py` 的文件：

```Python
# module.py

print("模块名称：", __name__)
```

运行之后的输出结果：

```Python
模块名称： __main__
```

但是如果在**另一个 Python 文件中通过 ****`import module`**** 导入该模块**，输出则为：

```Python
模块名称： module
```

**这是因为两种运行方式下，Python 为模块设置的 ****`name`**** 不同。**

### if name == "main": 的作用

在 Python 中，一个文件既可以直接运行，也可以被其他文件导入。

如果直接将测试代码、命令行交互或程序启动逻辑放在模块顶层，那么这些代码在模块首次被导入时也可能执行。

为了避免这种情况，可以使用以下判断：

```Python
if __name__ == "__main__":
    # 只有作为主程序运行时才执行
    main()
```

## file文件方法

### open\(\)方法

用于打开一个文件，并返回文件对象

在对文件进行处理过程都需要使用到这个函数，如果该文件无法被打开，会抛出 `OSError`。

注意：

使用`open()`方法的时候一定要保证关闭文件对象，即调用`close()`方法

open方法使用通常是接受两个参数，文件名和模式

```Python
open(file, mode='r')
```

完整语法格式为

```SQL
open(file, mode='r', buffering=-1, encoding=None, errors=None, newline=None, closefd=True, opener=None)
```

参数说明:

- file: 必需，文件路径（相对或者绝对路径）。

- mode: 可选，文件打开模式

- buffering: 设置缓冲

- encoding: 一般使用utf8

- errors: 报错级别

- newline: 区分换行符

- closefd: 传入的file参数类型

- opener: 设置自定义开启器，开启器的返回值必须是一个打开的文件描述符。

mode参数：



file对象常用的函数

## OS文件/目录方法

`os` 模块是 Python 标准库中的一个重要模块，它提供了**与操作系统交互**的功能。

通过 `os` 模块，你可以执行文件操作、目录操作、环境变量管理、进程管理等任务。

`os` 模块是跨平台的，这意味着你可以在不同的操作系统（如 Windows、Linux、macOS）上使用相同的代码。

在使用 `os` 模块之前，你需要先导入它。导入 `os` 模块的代码如下：

```Python
import os
```

### os板块常用功能

1. 获取当前工作目录

`os.getcwd()` 函数用于**获取当前工作目录的路径**。当前工作目录是 Python 脚本执行时所在的目录。

```Python
current_directory = os.getcwd()
**print**("当前工作目录:", current_directory)
```

2. 改变当前工作目录

`os.chdir(path)` 函数用于**改变当前工作目录**。`path` 是你想要切换到的目录路径。

Eg\.

```Python
os.chdir("/path/to/new/directory")
**print**("新的工作目录:", os.getcwd())
```

3. 列出目录内容

`os.listdir(path)` 函数用于**列出指定目录中的所有文件和子目录**。如果不提供 `path` 参数，则默认列出当前工作目录的内容。

Eg\.

```Python
files_and_dirs = os.listdir()
**print**("目录内容:", files_and_dirs)
```

4. 创建目录

**`os.mkdir(path)`** 函数用于创建一个新的目录。如果目录已经存在，会抛出 `FileExistsError` 异常。

Eg\.

```Python
os.mkdir("new_directory")
```

5. 删除目录

`os.`**`rmdir`**`(path)` 函数用于删除一个空目录。如果目录不为空，会抛出 `OSError` 异常。

Eg\.

```Python
os.rmdir("new_directory")
```

6. 删除文件

**`os.remove`**`(path)` 函数用于删除一个文件。如果文件不存在，会抛出 `FileNotFoundError` 异常。

Eg\.

```Python
os.remove("file_to_delete.txt")
```

7. 重命名文件或目录

**`os.rename`**`(src, dst)` 函数用于重命名文件或目录。`src` 是原始路径，`dst` 是新的路径。

Eg\.

```Python
os.rename("old_name.txt", "new_name.txt")
```

8. 获取环境变量

`os.getenv(key)` 函数用于获取指定环境变量的值。如果环境变量不存在，返回 `None`。

Eg\.

```Python
home_directory = os.getenv("HOME")
**print**("HOME 目录:", home_directory)
```

9. 执行系统命令

**`os.system`**`(command)` 函数用于在操作系统的 shell 中执行命令。命令执行后，返回命令的退出状态。

Eg\.

```Python
os.system("ls -l")
```

## 错误和异常

### 异常处理

#### try/except

![](/images/python/QQ_1791865541488.png)

Eg\.

让用户输入一个合法的整数，但是允许用户终端这个程序。

```Python
while True:
    try:
        x = int(input("请输入一个数字: "))
        break
    except ValueError:
        print("您输入的不是数字，请再次尝试输入！")
```

用户中断的信息会引发一个 KeyboardInterrupt 异常。

一个 try 语句可能包含多个except子句，分别来处理不同的特定的异常。最多只有一个分支会被执行。

处理程序将只针对对应的 try 子句中的异常进行处理，而不是其他的 try 的处理程序中的异常。



一个except子句可以同时处理多个异常，**这些异常将被放在一个括号里成为一个元组**，例如:

```Python
except (RuntimeError, TypeError, NameError):
    pass
```

最后一个except子句可以忽略异常的名称，它将被当作通配符使用。你可以使用这种方法打印一个错误信息，然后再次把异常抛出。

```Python
import sys

try:
    f = open('myfile.txt')
    s = f.readline()
    i = int(s.strip())
except OSError as err:
    print("OS error: {0}".format(err))
except ValueError:
    print("Could not convert data to an integer.")
except:
    print("Unexpected error:", sys.exc_info()[0])
    raise
```

#### try/except\.\.\.else

`try/except` 语句还有一个可选的 else 子句，如果使用这个子句，那么必须放在所有的 except 子句之后。

else 子句将在 try 子句没有发生任何异常的时候执行。

![](/images/python/QQ_1791865776560.png)

Eg\.

判断文件是否能被打开，如果打开文件时正常的没有发生异常则执行 else 部分的语句，读取文件内容：

```Python
for arg in sys.argv[1:]:
    try:
        f = open(arg, 'r')
    except IOError:
        print('cannot open', arg)
    else:
        print(arg, 'has', len(f.readlines()), 'lines')
        f.close()
```

#### try\-finally

try\-finally 语句无论是否发生异常都将执行最后的代码。

![](/images/python/QQ_1791865871471.png)

Eg\.

```Python
try:
    runoob()
except AssertionError as error:
    print(error)
else:
    try:
        with open('file.log') as file:
            read_data = file.read()
    except FileNotFoundError as fnf_error:
        print(fnf_error)
finally:
    print('这句话，无论异常是否发生都会执行。')
```





总的来说就是这些了 也算是系统地学习了一遍了 有很多小的知识点也复习到了 不过感觉一碰到那种大段的东西我就有点不想阅读了 像那种非常多的方法和模式之类的我复制粘贴之后浅浅看了一遍就跳过了 希望这次学习对我的手搓脚本有所帮助吧 明天应该找几个题目练习一下

虽然我也不知道现在手搓脚本到底是不是在学习精进ctf 主要现在AI太先进了 不过我觉得就算手搓不出来的话 也得能够识别分辨AI写的东西 找到他的错误 了解他的逻辑吧（这不是安慰自己么！
