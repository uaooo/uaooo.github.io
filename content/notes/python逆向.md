+++
title = 'python逆向'
date = '2026-09-21T18:12:27+08:00'
draft = false    # 内容改完后改成 false，否则线上博客看不到这篇
summary = ''
tags = []
showtoc = true
+++
参考文章：

https://xz\.aliyun\.com/news/12245

https://hello\-ctf\.com/hc\-skill/reverse/python\-reverse/

发现这个 hello CTF 的技能树蛮厉害的 可以看看

> Python 是一种解释型语言，意味着其代码在运行时是由 **Python 解释器 逐行执行**的。这种特性使得 Python 在开发过程中非常灵活，但也为代码保护带来了挑战。在某些情况下，开发者可能需要对 Python 字节码（\.pyc 文件）进行反编译，以恢复原始源代码。
> 
> 

在python中，源代码首先会被转换为字节码，然后字节码由python解释器执行。通常情况下，python源代码文件 \(\.py\) 会被编译为`.pyc`文件，存储在`__pycache__`文件夹中。

过程即：

1. 编译：python源代码 \(`.py`\) 会被转换为字节码 \(`.pyc`\)

2. 存储：\.pyc文件通常存储在`__pycache__`文件夹，并在程序执行时加载。

3. 执行：字节码由python解释器执行

反编译的目标就是**将这些字节码重新转化为源代码**。

## 原理

在这之前 我们可以先来搞清楚 pyinstaller打包成exe文件到底是怎么做的？

为什么电脑里即使没有下载python 也能执行我们写的`exe`文件呢？

这是因为`pyinstaller`把 代码 和 解释器 一起打包了。

```C
test.py (源码)
   ↓  (PyInstaller 打包)
test.exe (一个压缩包/旅行箱)
   ↓  (双击运行)
【内部动作】：
1. 解压自己到临时目录 (Temp)
2. 释放出 python38.**dll (Python解释器)**
3. 释放出 test.pyc (字节码)
   ↓
用释放出的 python38.dll 去执行 test.pyc
```

当我们双击这个 exe 时，它其实是在后台偷偷把箱子打开，把里面的 Python 环境和字节码释放到临时文件夹，然后再用里面的 Python 去跑我们的字节码。

现在我们明白它是怎么打包的，逆向就顺理成章了——把旅行箱拆开，还原回源码。

```C
test.exe (目标文件)
   ↓  (用 pyinstxtractor 提取)
拿到 test.pyc (缺文件头的字节码) + python38.dll 等
   ↓  (手动给 test.pyc 补上 16 字节的文件头)
完整的 test.pyc
   ↓  (用 pycdc 或 uncompyle6 反编译)
test.py (成功还原源码！)
```

详细解释：

1. pyinstxtractor：负责暴力拆开 exe 这个旅行箱，把里面的 `test.pyc` 和 Python 环境抠出来。

2. 补文件头：因为 PyInstaller 打包时会把 `.pyc` 的前 16 个字节（文件头）抹掉，所以你抠出来的 `.pyc` 是残缺的，需要手动补上（一般是 `magic + 时间戳`）。

3. 反编译器：拿着完整的 `.pyc`，用 `uncompyle6` 或 `pycdc` 把字节码翻译回 Python 源码。

> 分析脚本文件，递归找到所有依赖的模块。如果依赖模块有\.pyd文件，即将其复制到disk目录。如果没有\.pyd文件，则生成\.pyc文件拷贝到disk目录，并压缩为\.zip保存。制作一个exe，导入PythonXX\.dll\(解析器库\)，并添加exe运行需要的相关运行时库。这就构成了一个不用安装Python的运行包。
> 
> 

## 工具

### python

由于出题人通常用的是 Python 3\.8 到 3\.10 左右的环境。如果电脑上只有 3\.14，会无法还原这些题目的环境。

因此我们需要重新安装一个3\.8版本的python

安装的时候不勾选底部的add to path 这样就不会搞崩我们电脑的环境

![](/images/python逆向/QQ_1789831710074.png)

### PyInstaller（打包工具）

![](/images/python逆向/image.png)

### pyinstxtractor（拆包工具）

https://github\.com/extremecoders\-re/pyinstxtractor

### uncompyle6（反编译器）

```C
py -3.8 -m pip install uncompyle6
```

![](/images/python逆向/QQ_1789873664131.png)

把刚才拆出来的 `.pyc`（字节码）翻译回最初写的 `.py`（源码）。

### PyLingual（在线反编译）

- 用途：当本地所有工具都失败，或者版本太新（比如 Python 3\.11/3\.12），直接进行在线反编译。

- 网址：[https://pylingual\.io/](https://pylingual.io/)

- 用法：把 `.pyc` 文件拖进去，它自动反编译。

## Eg

新建一个文件夹 里面放入test\.py

```C
print("Hello CTF Reverse!")
```

### 打包

```C
py -3.8 -m PyInstaller -F test.py
```

![](/images/python逆向/QQ_1789870843246.png)

![](/images/python逆向/QQ_1789870863488.png)

dist文件夹之下就有了一个exe文件

![](/images/python逆向/QQ_1789871054102.png)

这个就是pyinstaller将解释器和代码带包到一起的结果

在没有python的电脑上运行这个exe文件也可以打印出hello ctf reverse！

- `build` 文件夹：这是打包时的“临时厨房”。里面全是中间文件、日志和缓存。这个文件夹对我们一点用都没有，可以直接删掉。它唯一的作用是：下次你重新打包时，PyInstaller 能利用里面的缓存，打包得快一点。

- `test.spec` 文件：这是打包的“配方单”。PyInstaller 实际上是先根据我的命令生成了一个 `.spec` 文件，然后再照着这个文件去干活。如果以后要打包很复杂的项目（比如加图片、加数据文件），我们就可以直接去改这个 `.spec` 文件，然后运行 `pyi-makespec` 或 `pyinstaller test.spec`。目前可以把它当成一个自动生成的配置文件，不用管它。

### 解包

绝大部分考察此类知识的题目给我们的就是这个打包好的exe文件

接下来 我们就开始还原这个文件

先将这个解包文件pyinstxtractor复制到test文件夹之下 

```C
py -3.8 pyinstxtractor dist\test.exe
```

![](/images/python逆向/QQ_1789872950855.png)

![](/images/python逆向/QQ_1789873085031.png)

### 反编译

双击进入 `test.exe_extracted` 文件夹。里面会有一堆 `.pyc` 和 `.pyd` 文件。
而我们要找的是刚才工具提示的 `test.pyc`

![](/images/python逆向/QQ_1789873196521.png)

```C
E:\reverse\Scripts\uncompyle6.exe test.exe_extracted\test.pyc
```

![](/images/python逆向/QQ_1789874013732.png)

这样我们就通过反编译拿到了源码。

## \.pyc

\.pyc：python**编译后的二进制文件**，是\.py文件经过编译产生的**字节码**，pyc文件是可以由python虚拟机直接执行的程序（PyCodeObject对象在硬盘上的保存形式）。

pyc文件会加快程序的加载速度，而不会加快程序的实际执行速度。

### 文件格式

pyc文件一般由3个部分组成:

1. Magic num：标识此pyc的**版本信息**, 不同的版本的 Magic 都在 `Python/import.c` 内定义

2. 文件**创建时间**：UNIX时间戳（从1970\.1\.1开始计数秒数）

为什么要有时间戳？

![](/images/python逆向/QQ_1789886007713.png)

3. 序列化了的 PyCodeObject：此结构在 `Include/code.h` 内定义，序列化方法在 `Python/marshal.c` 内定义

### 序列化

把内存里的“活对象”（相当于 Python 正在运行这段代码），变成硬盘上的“死数据”（字节流），就叫序列化。

反之，把硬盘上的“死数据”读回内存变成“活对象”，就叫反序列化（Unmarshal）。

#### 辅助理解

一个小比喻：

（所以ai真的是一个很好的工具 但是现在实在是发展的太快了 我感觉我毕业就没饭碗了。

![](/images/python逆向/QQ_1789876376648.png)

![](/images/python逆向/QQ_1789876438197.png)

`PyCodeObject` 并不是“正在运行的代码”，而是“代码的蓝图/菜谱”。它本身不运行，它只是躺在内存里的一个数据结构。真正执行它的是 Python 虚拟机（PVM）。

所以，**`PyCodeObject`**** 在内存里的状态**，我们称之为“活对象”。因为它随时可以被大厨拿起来执行。当我们要把它存进硬盘（离开厨房）时，就把它序列化（压缩/加密）成了 `.pyc` 文件。

**到达****`pyc`****文件的时候就是已经经历过一次序列化了**

**marshal**是序列化的工具，负责把内存里的 `PyCodeObject` 塞进硬盘变成 `.pyc`，或者把 `.pyc` 读回内存。

可能会听到另一个词叫 `pickle`（泡菜），它也是 Python 的序列化工具。但它俩用途不同：

- `pickle` 是给普通开发者用的（用来保存游戏存档、爬虫数据）。

- `marshal` 是 Python 官方内部专用的（用来保存代码对象）。官方说了，`marshal` 的格式可能会变，普通开发者别瞎用，出了问题不负责。所以，你才会遇到不同 Python 版本编译出来的 pyc 互不兼容的情况。

**co\_consts**\-\-constant的缩写 常量池

就是代码里那些固定不变的、写死的值

比如：数字 字符串 布尔值 none等等

如果只是一个简单的 `print("Hello")`，`co_consts` 里装的只有 `"Hello"` 和 `None`。
但如果**代码里定义了函数或者类，那个函数本身（也就是另一个 ****`PyCodeObject`****）也会被当成一个“常量”，塞进父级的 ****`co_consts`**** 里**！

这里**如果函数和类没有放在const常量里的话 ****`.py`****编译成****`.pyc`****的时候就会丢失。**

`.pyc` 文件本质上是一个压缩包（旅行箱）。当 Python 把代码编译并保存成 `.pyc` 时，它需要把内存里的东西打包。

> 在内存里，函数体 `hello` 仅仅是一个 `PyCodeObject` 对象（也就是一段冰冷的代码指令）。它必须依附在某个父级对象上，才能被一起打包带走。
> 
> 

总结来说就是：**`co_consts`**** 是 Python 专门留给“嵌套作用域”的唯一合法存放点。**

#### 区分编译、打包和序列化

> 打包包含了序列化，而序列化只是打包的一小部分。
> 
> 

编译（Compilation）—— 从“源码”变成“内存蓝图”

- 动作：把写的 `test.py`（人类能看懂的字符），变成 Python 虚拟机才能看懂的指令。

- 产物：内存里的 `PyCodeObject`。

- 结论：这一步只发生在内存里，它是把“英语”翻译成“机器语”的过程。翻译完，内存里就多了一堆代码对象。

序列化（Serialization）—— 从“内存蓝图”变成“硬盘文件”

- 动作：把内存里的 `PyCodeObject` 保存到硬盘上，变成一个二进制文件。

- 工具：`marshal` 模块。

- 产物：`.pyc` 文件。

- 结论：这一步是为了省时间。下次运行代码**，Python 一看有 ****`pyc`**** 文件，直接跳过“编译”阶段，把 ****`pyc`**** 读进内存（反序列化）就能跑**。这一步，是整个 py 变成 pyc 的过程，也是我们逆向的起点。

打包（Packaging）—— 从“散装文件”变成“旅行箱”

- 动作：把所有需要的零碎东西全塞进一个独立的 exe 里。

- 工具：PyInstaller。

- 产物：`.exe` 文件。

- 结论：PyInstaller 在后台，第一步先做“编译”，第二步做“序列化”，得到了 `test.pyc`。然后它觉得不够，它把 `test.pyc`、`python38.dll`（解释器）、`VCRUNTIME140.dll` 等所有东西，一股脑儿塞进了一个叫 `test.exe` 的箱子里。

## 文件头魔改

出题人知道我们要用 `uncompyle6` 或者 `pycdc`，于是他故意把 `.pyc` 文件的前 16 个字节（文件头）给删掉，或者把 magic number（版本号）改成了别的数字。

后果：你反编译时，工具直接报错 `Unknown magic number` 或 `bad marshal data`。

应对：

- 查表：用 `xdis` 工具，或者用 Python 代码

```Python
import importlib.util
print(importlib.util.MAGIC_NUMBER.hex())
```

查出当前python版本的magic number

- 补头：打开十六进制编辑器（HxD），手动在最前面补上 `03 F3 0D 0A` 加上 12 个 `00`。

- 脚本：写个 Python 脚本，自动读取文件并补上正确的头。这就是为什么你要学会看 `marshal` 和 `dis` 的原因，实在不行手动反汇编。

前置知识：python在不同的版本下 pyc的头部内容和长度是不同的 

因此他才能通过修改魔数来混淆我们

![](/images/python逆向/QQ_1789879871601.png)

### xdis工具

`uncompyle6` 依赖于 `xdis`

- `xdis` 是底层的“引擎”：它是个独立的工具库，专门负责解析各种版本的 Python 字节码。它自己就能独立运行，跟 `uncompyle6` 一点关系都没有。你完全可以只用 `xdis` 去分析 pyc，不用 `uncompyle6`。

- `uncompyle6` 是上层的“翻译官”：它自己不会读二进制文件，它必须调用 `xdis` 帮它把数据读出来，然后再把这些数据翻译成人类能看懂的源码。

因此其实我们刚刚下载uncompyle的时候就已经顺带下载了xdis

![](/images/python逆向/QQ_1789888292912.png)

作用：

- 跨版本兼容：Python 版本众多（3\.6\~3\.12\+），每个版本的字节码格式、文件头长度都不一样。`xdis` 能识别并解析几乎所有版本的 `.pyc`。

- 文件体检（诊断）：当你不知道一个残缺的 `.pyc` 文件到底是什么版本，或者 magic number 被魔改时，用它来检验。

- 强行反汇编：当高级反编译工具（如 `uncompyle6`）彻底罢工时，`xdis` 可以强行把底层字节码指令一条条扒出来，让你手工分析。

使用场景：

- 不知道拿到的 `.pyc` 是哪个 Python 版本编译的。

- 反编译时报错 `Unknown magic number` 或 `bad marshal data`。

- 反编译工具跑出来的代码全是乱码，需要看底层字节码排查原因。

命令：

```Python
xdis -c target.pyc
```

*作用*：检查 magic number、时间戳、版本号，判断文件头是否被魔改。

强行反汇编：

```Python
pydisasm target.pyc
```

*作用*：无视反编译错误，直接打印最底层的字节码指令序列（类似汇编），用于手工硬推逻辑。

## 字节码混淆与加密

找到了一篇从原理到实战的文章 还是很厉害的 不过我现在还没有办法看懂 回头再补

https://blog\.csdn\.net/weixin\_33423874/article/details/164926792



参考文章：https://cloud\.tencent\.com\.cn/developer/article/2320366

由于 pyc 文件有现成的工具 uncompyle6，可以还原成 Python 代码，所以说我们不了解 pyc 格式也没有关系。这样我们混淆 pyc 的思路就可以是欺骗像 uncompyle6 这类反编译的工具，让它误以为指令的序列不合法，但是又不影响真正的 Python [虚拟机](https://cloud.tencent.com.cn/developer/techpedia/1523?from_column=20065&from=20065)执行。

Python 的虚拟机是根据 PyCodeObject 中的 `co_code` 这个字段中存储的 `opcode` 序列来决定程序的执行流程的。所以说**一个混淆的手段就是修改 ****`co_code`**** 字段中的 ****`opcode`**** 序列**，**可以添加一些加载超出范围的变量的指令，再用一些指令去跳过这些会出错的指令**，这样执行的时候就不会出错了，但是反编译工具就不能正常工作了。

（感觉其实有点类似于花指令 通过恒真恒假恒跳转来混淆 虽然能执行但是ida反编译会变得一团糟）

### opcode

Python 编译后，把`.py`变成了机器（PVM）能看懂的字节码。

而字节码，其实就是一个个 Opcode 的序列。

比如我们写了一行：

```Python
x = 1 + 2
```

Python 编译器不会直接算，而是把它翻译成 PVM 能懂的“指令清单”（Opcode）：

```Python
LOAD_CONST 1   (把常量 1 压入栈)
LOAD_CONST 2   (把常量 2 压入栈)
BINARY_ADD     (把栈顶两个数拿出来相加)
STORE_NAME x   (把结果存进变量 x)
```

这里的 `LOAD_CONST`、`BINARY_ADD`、`STORE_NAME` 就是 Opcode（操作码）。
它们每个都对应一个数字（比如 `LOAD_CONST` 是 100，`BINARY_ADD` 是 23），这些数字就躺在 `.pyc` 文件的 `co_code` 字段里。

- 加载/存储：

    - `LOAD_CONST`：加载常量（去 `co_consts` 里拿东西）。

    - `LOAD_FAST` / `STORE_FAST`：加载/存储局部变量（函数里的 `x`）。

    - `LOAD_NAME` / `STORE_NAME`：加载/存储全局变量（模块里的 `x`）。

    - `LOAD_GLOBAL`：加载全局变量（比如 `print` 函数本身）。

- 运算：

    - `BINARY_ADD`：加法。

    - `BINARY_SUBTRACT`：减法。

    - `BINARY_XOR`：异或（CTF 加密最爱）。

    - `COMPARE_OP`：比较（==、\>、\<）。

- 控制流：

    - `JUMP_ABSOLUTE`：无条件跳转（去某一行）。

    - `POP_JUMP_IF_TRUE` / `POP_JUMP_IF_FALSE`：条件跳转（if 判断）。

- 函数调用：

    - `CALL_FUNCTION`：调用函数。

    - `RETURN_VALUE`：返回结果。

### Eg\.

本来的普通代码语言

```Python
0 LOAD_NAME                0 (print)
2 LOAD_CONST               0 ('Hello World! --idiot.')
4 CALL_FUNCTION            1
6 POP_TOP
```

这是python生成的pyc的一段opcode序列

这是我们可以在代码的中间插入一些东西来混淆

```Python
0 JUMP_ABSOLUTE            4
2 LOAD_CONST               255
4 LOAD_NAME                0 (print)
6 LOAD_CONST               0 ('Hello, world')
8 CALL_FUNCTION            1
10 POP_TOP
```

其中 `JUMP_ABSOLUTE 4` 表示直接跳转到 `offset` 为4的位置去执行指令，也就是插入的第二条指令 `LOAD_CONST 255` 并不会被执行，所以也并不会报错。但是对于反编译工具来说，这就是一个错误了，直接导致了反编译的失败。  

**实现：**

根据上面的那个思路，我们可以插入许多这样类似的指令，任意的不合法指令（其实随机数据都可以），然后用一些 JUMP 指令去跳过这样的不合法指令，上面的 `JUMP_ABSOLUTE` 只是一个简单的例子。甚至我们可以跳转到一些自行添加的虚假分支再跳转到到真实的分支。

Python的opcode与jump相关的有：

```Python
'JUMP_FORWARD',
'JUMP_IF_FALSE_OR_POP',
'JUMP_IF_TRUE_OR_POP',
'JUMP_ABSOLUTE',
'POP_JUMP_IF_FALSE',
'POP_JUMP_IF_TRUE',
```

### 常见魔改方式

1. 删掉或替换关键指令：比如把验证 flag 的关键跳转 `POP_JUMP_IF_FALSE` 改成 `NOP`（空指令，什么都不做），代码就永远跳过错误提示了。

2. 插入垃圾指令：在中间插入一堆 `JUMP_ABSOLUTE`，让你的反编译工具绕晕，报 `bad marshal data`。

3. Python 3\.6\+ 的变长指令：新版 Python 的指令变成 2 个字节（1个字节 Opcode，1个字节参数），如果你手动改字节，很容易把参数和 Opcode 搞混。

## 题目

### easy\_pyc

题目链接：https://www\.nssctf\.cn/problem/3690

拿到附件pyc文件

#### 文件头

首先先到010editor里面看一眼 确认文件开头是否有被篡改

![](/images/python逆向/QQ_1789913537995.png)

1. 前 4 个字节（偏移 0x00 到 0x03）：`42 0D 0D 0A`

    - **这是 Python 3\.7 的 Magic Number**。（Python 3\.8 是 `03 F3 0D 0A`，3\.7 是 `42 0D 0D 0A`）。说明出题人没有改 magic。

2. 接下来 4 个字节（0x04 到 0x07）：`00 00 00 00`

    - 这是文件头的标志位，全 0 表示用的是时间戳。

3. 再接下来 8 个字节（0x08 到 0x0F）：`0A EA 0D 63 0F 03 00 00`

    - 这是时间戳和文件大小。完全正常。

4. 第 16 个字节开始（偏移 0x10）：`E3 00 00 00`

    - `E3` 是 Python 3\.7\+ 中代码对象（PyCodeObject）的起始标记。从这里开始，后面就是序列化（marshal）的数据了。

结论：这只是一个平平无奇的 Python 3\.7 编译出来的 pyc 文件，没有任何“魔改”陷阱。



接下来我们用uncompyle拿到源码

```Python
E:\reverse\Scripts\uncompyle6.exe ezpy.pyc
```

![](/images/python逆向/QQ_1789914572858.png)

一开始没有看懂 然后问了一下AI 我去**RSA算法** 也是直接和数论梦幻联动了

- `m = bytes_to_long(flag)`：把 flag 字符串变成一个大整数。

- `e = 3066...`：RSA 的公钥指数。

- `q = 7021...`，`p = 8228...`：RSA 的两个大质数。

- `c = 2181...`：RSA 加密后的密文。

因为源码里用了crypto这个库 因此我们现在我们python3\.8的环境下装一个crypto库

```Python
py -3.8 -m pip install pycryptodome
```

接着我们直接写一个解密脚本解出flag

```Python
from Crypto.Util.number import *

# 去掉了Python 2时代的L后缀
e = 306645347334662727966285107364291531289
q = 7021910101974335245794950722131367118195509913680915814438898999848788125908122655583911434165700354149914056221915541094395668546921268189522005629523759
p = 8228801334907462855397256098699556584084854642543205682719705217859576250443629616812386484797164506834582095674143447181804355696220642775619711451990971
c = 21812306272967730147845738706030680242331165675981994115949615844012361551700506020612445969402056602389411244248745130826969002161047213415607978602535719418999319494842608994479027676787499235277662156571617957720793923983451286566879014875330118016740706736991981355194846993958405444652507211603807160958

# 1. 计算 n = p * q
n = p * q

# 2. 计算欧拉函数 phi(n)
phi = (p - 1) * (q - 1)

# 3. 计算私钥 d (e 在模 phi 下的逆元)
d = pow(e, -1, phi)

# 4. 解密 m = c^d mod n
m = pow(c, d, n)

# 5. 把大整数变回字符串
m_bytes = long_to_bytes(m)
print("解密出的原始字节：", m_bytes)

# 尝试打印出 flag
print("Flag:", m_bytes.decode('utf-8'))
```

![](/images/python逆向/QQ_1789914862843.png)

![](/images/python逆向/QQ_1789915322339.png)

Flag: flag\{IfYouWantItThenYouHaveToTakeIt\} 

### pyc

题目链接：https://www\.nssctf\.cn/problem/1227

先用 010 editor 看文件头

![](/images/python逆向/QQ_1789915866766.png)

对照版本表

- Python 3\.7：`42 0D 0D 0A`

- Python 3\.8：`03 F3 0D 0A`

- Python 3\.10：`6F 0D 0D 0A`

发现该`pyc`文件时python 3\.10

这就表示我们的uncompyle罢工了 因为他只能反编译3\.8版本以下的python文件

#### 反编译

那么到了3\.10这个版本我们就需要用到在线反编译网站https://pylingual\.io/

![](/images/python逆向/QQ_1789917282154.png)

源代码为：

```Python
import hashlib
s = input()
if len(s) != 72:
    print('wrong')
a1 = set()
a2 = set()
a3 = set()
a4 = [2654435769, 2654435769]
for d in '012345678':
    a3.add(s.count(d))
for i in range(0, len(s), 9):
    for l in range(0, 15, 2):
        a2.add(sum((int(s[i + j:i + j + 1]) for j in [int(v) for v in str(a4[1] ^ 64201746666225664 ^ 3446703994)[l:l + 3]])))
    if int(s[i:i + 9]) >= a4[0]:
        break
    else:
        a4[0] = int(s[i:i + 9])
        a1.add(s[i:i + 9])
if print((len(a1) == 8 and len(a2) == 1 and (len(a3) == 1)) and s.count('9') == 0):
    flag{(f"flag{{hashlib.md5(s.encode('ascii')).hexdigest()}}")
```

#### 代码逻辑分析

1. `a1 = set()` / `a2 = set()` / `a3 = set()`

    - 这就像三个自动去重的数组。往里面塞重复的值，它只保留一个。最后看 `len(a1)` 其实就是看“里面有几个不重复的元素”。

2. `for d in '012345678': a3.add(s.count(d))`

    - C语言逻辑：

```C
for (int d = 0; d <= 8; d++) {
    int count = 0; // 统计 s 里数字 d 出现了几次
    // 遍历 s 统计次数...
    a3.add(count); // 把次数塞进去
}
```

即：统计字符串 `s` 中，数字 `0` 到 `8` 分别出现了多少次。如果这些数字出现次数都一样（比如每个数字都出现 8 次），那 `a3` 里最终只会有一个数字（去重了）。

3. `for l in range(0, 15, 2):`

    - C语言：`for (int l = 0; l < 15; l += 2)`（步长为2）

4. `[int(v) for v in str(...)[l:l + 3]]`

    - C语言：先算出一个常量数字（异或运算），转成字符串。然后从第 `l` 个位置开始，切 3 个字符出来（比如字符串是 `"642017466"`，`l=0` 切出 `"642"`，`l=2` 切出 `"201"`），然后把每个字符转成 int，存进数组。比如 `"642"` 就变成数组 `[6, 4, 2]`。

5. `for j in [6, 4, 2]: sum += int(s[i+j])`

    - C语言：用刚才切出来的数字作为索引。比如 `j=6`，就去取字符串 `s` 的第 `i+6` 个字符，转成数字，累加。最后求出一个总和。

6. `if len(a2) == 1:`

    - C语言：所有 8 个 9 位数块，算出来的“总和”必须全部相同。如果 `a2` 里只有 1 个元素，说明大家的和都是相等的。

在 `for i in range(0, len(s), 9):` 这个循环里：

- 第一次循环 `i=0`，它截取的是 `s[0:9]`（第 1 到第 9 个字符）—— 这是第 1 块。

- 第二次循环 `i=9`，它截取的是 `s[9:18]`（第 10 到第 18 个字符）—— 这是第 2 块。

- \.\.\.

- 第八次循环 `i=63`，它截取的是 `s[63:72]` —— 这是第 8 块。

72 / 9 = 8。所以整个字符串被完美地切成了 8 个 9 位数块。



现在可以写脚本了 用z3求解器

我们py3\.8版本还没有z3脚本器 可以下载一下

但是实际上这个不管源代码的版本是多少 这个z3都可以在任意的环境跑 因为这二者之间毫无关系

但是考虑到环境的一致性 我依然选择在3\.8版本之下安装一个z3 

```C
py -3.8 -m pip install z3-solver
```

![](/images/python逆向/QQ_1789919574866.png)

Exp

```Python
from z3 import *

# 1. 算出那个复杂的常量 C
C = 2654435769 ^ 64201746666225664 ^ 3446703994
C_str = str(C) # 转成字符串，方便后面切片

# 2. 创建 72 个整数变量 x_0 到 x_71，代表 s 的每一位
s = [Int(f'x_{i}') for i in range(72)]
solver = Solver()

# 3. 条件：只能由 0-8 组成，绝对不允许出现 9
for x in s:
    solver.add(x >= 0, x <= 8)

# 4. 条件：0-8 每个数字必须正好出现 8 次
for d in range(9):
    # 如果 x 等于 d，就计 1，最后总数必须等于 8
    solver.add(Sum([If(x == d, 1, 0) for x in s]) == 8)

# 5. 条件：切成 8 块，每块 9 位数，且必须严格递增，小于 2654435769
blocks = []
for i in range(8):
    # 把 9 个数字拼成一个真正的 9 位数（比如 [1,2,3] -> 123）
    block_val = Sum([s[i*9 + j] * (10 ** (8 - j)) for j in range(9)])
    blocks.append(block_val)

for i in range(7):
    solver.add(blocks[i] < blocks[i+1])  # 严格递增
    solver.add(blocks[i] < 2654435769)   # 必须小于这个数
solver.add(blocks[7] < 2654435769)       # 最后一块也要小于

# 6. 条件：那个诡异的数学求和（最核心的约束）
# 对于每个块，计算出来的“和”必须全部完全相同
all_sums = []
for i in range(8): # 8个块
    for l in range(0, 15, 2): # l 步长为 2
        # 取出 3 个字符，比如 "642" -> [6, 4, 2]
        j_values = [int(v) for v in C_str[l:l+3]]
        # 按照这些索引，去块里取数字求和
        current_sum = Sum([s[i*9 + j] for j in j_values])
        all_sums.append(current_sum)

# 让所有的和全部等于第一个和
for sm in all_sums[1:]:
    solver.add(sm == all_sums[0])

# 7. 让 Z3 开始计算！
if solver.check() == sat:
    model = solver.model()
    # 把求解出的 72 个数字拼成字符串
    result_s = "".join([str(model[x].as_long()) for x in s])
    print("🎉 成功找到满足条件的字符串 s:", result_s)
    
    # 8. 计算最终的 flag
    import hashlib
    md5_hash = hashlib.md5(result_s.encode('ascii')).hexdigest()
    print(f"🚩 最终 Flag: flag{{{md5_hash}}}")
else:
    print("无解，可能条件抄错了")
```

运行脚本为：

![](/images/python逆向/QQ_1789919705244.png)

因此得到Flag：flag\{485f364e86a37859b4b9a7ed7c887983\} 

### 贪吃蛇

这道题目是8\.1号社团的招新题目 我要学习这个知识点的时候第一个就想到这个了

那个新生赛的平台已经进不去了 不过我保存了附件嘻嘻 ~~我是全世界最有先见之明的人~~

[bc1594f2\_\_0b2c6420\-e5dd\-4355\-87b6\-296d8abac4ec\.exe](图片和附件/bc1594f2__0b2c6420-e5dd-4355-87b6-296d8abac4ec.exe)

> 题目提示：
> 
> 曼波曼波
> 
> 俄罗斯方块里面充满了神秘的py力量
> 
> 你能找到方法破解吗
> 
> 

这个题目虽然附件是exe结尾 但是题目提示又描述了说是充满了py的力量

直接猜测这是一道pyinstaller的打包解包题目

用 010 editor 打开，直接印证了我们的猜想

![](/images/python逆向/QQ_1789920573457.png)

#### 解包

接下来 我们就可以进行解包操作了

切回到存放 `pyinstxtractor.py` 的那个文件夹 （原来那个名字太长我把文件名改成challenge了）

```C
py -3.8 pyinstxtractor.py challenge.exe
```

![](/images/python逆向/QQ_1789921076048.png)

日志解读：

1. Python version: 3\.11：这是最重要的一条！出题人打包这个 exe 用的是 Python 3\.11，而不是我们之前习惯的 3\.8。

2. Warning 提示：因为我用 3\.8 的脚本去解包 3\.11 的程序，所以工具警告“版本不对，可能会在反序列化时出错，并且跳过了 PYZ 压缩包的提取”。这也是正常的，因为跨版本解析底层代码对象确实有风险，但好在主文件提取出来了。

3. Possible entry point: `main.pyc`：入口文件叫 `main.pyc`。

![](/images/python逆向/QQ_1789921138565.png)

在文件夹中找到main\.py

然后由于版本的问题无法使用uncompyle 因此我们依然借助在线反编译的工具

[https://pylingual\.io/](https://pylingual.io/)

![](/images/python逆向/QQ_1789921364928.png)

#### 源码

```Python
# Decompiled with PyLingual (https://pylingual.io)
# Internal filename: 'main.py'
# Bytecode version: 3.11a7e (3495)
# Source timestamp: 1970-01-01 00:00:00 UTC (0)

import pygame
import sys
import set
import class_set
from pygame.locals import *
from config_set import CONFIG
class Game:
    def __init__(self):
        self.screen, self.background = set.game_init()
        self.case()
        self.play_music()
    def case(self):
        self.load_data()
        self.run = True
        self.case = 'main_menu'
        self.case_temp = None
        self.game_case = None
        self.timer = 0
        self.sprite_init()
        self.scord_list = [0] * 5
    def sprite_init(self):
        self.all_sprites = pygame.sprite.Group()
        self.main_menu = self.create_main_menu()
        self.chars_menu = self.create_charts()
        self.game_over_menu = self.create_game_over()
    def load_data(self):
        self.backgrounds = {'main_menu': set.load_background('main_menu'), 'game': set.load_background('game'), 'charts': set.load_background('charts'), 'game_over': set.load_background('game_over')}
        self.sounds = {'main_menu': set.load_sound(CONFIG['main_menu_sound']), 'game': set.load_sound(CONFIG['game_sound']), 'game_over': set.load_sound(CONFIG['game_over_sound']), 'charts': set.load_sound(CONFIG['chartas_sound'])}
    def create_main_menu(self):
        meau = class_set.Menu(self.screen)
        start_btn = class_set.Button(CONFIG['start'], CONFIG['confirm'], (400, 100), self.begin_game, True, (150, 100))
        charts_btn = class_set.Button(CONFIG['charts'], CONFIG['confirm'], (400, 300), self.show_charts, True, (150, 100))
        exit_btn = class_set.Button(CONFIG['exit'], CONFIG['confirm'], (400, 500), self.exit_game, True, (150, 100))
        meau.add_button(start_btn)
        meau.add_button(charts_btn)
        meau.add_button(exit_btn)
        return meau
    def create_charts(self):
        menu = class_set.Menu(self.screen)
        back_btn = class_set.Button(CONFIG['back'], CONFIG['confirm'], (400, 500), self.back, True, (100, 100))
        menu.add_button(back_btn)
        return menu
    def create_game_over(self):
        menu = class_set.Menu(self.screen)
        regame_btn = class_set.Button(CONFIG['restart'], CONFIG['confirm'], (200, 450), self.begin_game, True, (150, 100))
        go_back_main_btn = class_set.Button(CONFIG['back_main_menu'], CONFIG['confirm'], (500, 450), self.go_back_main, True, (150, 100))
        menu.add_button(go_back_main_btn)
        menu.add_button(regame_btn)
        return menu
    def begin_game(self):
        self.sounds[self.case].stop()
        self.case_temp = self.case
        self.game_case = 'playing'
        self.case = 'game'
        self.board = class_set.Board()
        self.play_music()
    def show_charts(self):
        self.sounds[self.case].stop()
        self.case_temp = self.case
        self.case = 'charts'
        self.game_case = 'not_game'
        self.play_music()
    def exit_game(self):
        self.run = False
    def back(self):
        self.sounds[self.case].stop()
        self.case = self.case_temp
        self.play_music()
    def go_back_main(self):
        self.sounds[self.case].stop()
        self.case = 'main_menu'
        self.play_music()
    def handle_event(self, events, dt):
        # irreducible cflow, using cdg fallback
        # ***<module>.Game.handle_event: Failure: Different control flow
        self.run = set.handle_exit(self.run, events)
        if self.case == 'main_menu':
            self.main_menu.handle_event(events)
        else:
            if self.case == 'charts':
                self.chars_menu.handle_event(events)
            else:
                if self.case == 'game':
                    if self.board.game_over and self.game_case == 'playing':
                        self.scord_list.append(self.board.score)
                        self.scord_list.sort(reverse=True)
                        self.sounds[self.case].stop()
                        self.case = 'game_over'
                        self.game_case = 'game_over'
                        self.play_music()
                    else:
                        if self.board.score > 1000000:
                            self.board.game_over = True
                            self.scord_list.append(self.board.score)
                            self.scord_list.sort(reverse=True)
                            self.sounds[self.case].stop()
                            self.case = 'charts'
                            self.game_case = 'game_over'
                            self.play_music()
                            return
                        else:
                            self.board.update(dt)
                            for event in events:
                                pass
                else:
                    if self.board.game_over:
                        self.game_over_menu.handle_event(events)
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    if self.board.pause == False:
                        self.board.pause = True
                    else:
                        self.board.pause = False
                    if event.key == K_LEFT:
                        self.board.move((-1), 0)
                        if event.key == K_RIGHT:
                            self.board.move(1, 0)
                            if event.key == K_DOWN:
                                self.board.move(0, 1)
                                if event.key == K_UP:
                                    self.board.rotate()
                                    if event.key == K_r:
                                        self.board.game_over = True
    def update_screen(self):
        self.screen.blit(self.backgrounds[self.case], (0, 0))
        if self.case == 'main_menu':
            self.main_menu.draw()
        else:
            if self.case == 'game':
                self.board.draw(self.screen)
            else:
                if self.case == 'charts':
                    self.chars_menu.draw()
                    self.printscord()
                else:
                    if self.board.game_over:
                        self.game_over_menu.draw()
                        set.draw_text('GAME OVER', CONFIG['font1'], 50, (255, 255, 255), self.screen, 250, 50)
                        set.draw_text('你的分数:', CONFIG['font1'], 50, (255, 255, 255), self.screen, 280, 150)
                        set.draw_text(f'{self.board.score}', CONFIG['font1'], 50, (255, 255, 255), self.screen, 350, 250)
        pygame.display.flip()
    def printscord(self):
        if max(self.scord_list) > 1000000:
            set.draw_text(f'你的flag:{self.success()}', CONFIG['font1'], 30, (255, 255, 255), self.screen, 0, 100)
        else:
            set.draw_text('积分前五高', CONFIG['font1'], 50, (255, 255, 255), self.screen, CONFIG['screen_width'] // 2 - 100, 50)
            for i in range(5):
                set.draw_text(f'第{i + 1}高：     {self.scord_list[i]}', CONFIG['font1'], 20, (255, 255, 255), self.screen, CONFIG['screen_width'] // 2 - 100, 150 + 50 * i)
    def play_music(self):
        self.sounds[self.case].play((-1))
    def run_game(self):
        clock = pygame.time.Clock()
        while self.run:
            clock.tick(60)
            dt = clock.tick(60) / 1000.0
            events = pygame.event.get()
            self.handle_event(events, dt)
            self.update_screen()
        pygame.quit()
        sys.exit()
    def success(self):
        return set.get_flag()
if __name__ == '__main__':
    game = Game()
    game.run_game()
```

函数主要逻辑：

```Python
def printscord(self):
        if max(self.scord_list) > 1000000:
            set.draw_text(f'你的flag:{self.success()}', CONFIG['font1'], 30, (255, 255, 255), self.screen, 0, 100)
        else:
            set.draw_text('积分前五高', CONFIG['font1'], 50, (255, 255, 255), self.screen, CONFIG['screen_width'] // 2 - 100, 50)
            for i in range(5):
                set.draw_text(f'第{i + 1}高：     {self.scord_list[i]}', CONFIG['font1'], 20, (255, 255, 255), self.screen, CONFIG['screen_width'] // 2 - 100, 150 + 50 * i)
    def play_music(self):
        self.sounds[self.case].play((-1))
    def run_game(self):
        clock = pygame.time.Clock()
        while self.run:
            clock.tick(60)
            dt = clock.tick(60) / 1000.0
            events = pygame.event.get()
            self.handle_event(events, dt)
            self.update_screen()
        pygame.quit()
        sys.exit()
    def success(self):
        return set.get_flag()
```

逻辑：玩游戏 → 拿积分 → 如果分数超过 `1000000`（一百万），游戏就会调用 `self.success()`。

我们注意到 python源码的开头有`import set`什么的 因此意味着：作者自己写了一个叫 `set.py` 的文件，里面装着一些自定义的函数。

因此我们去文件夹里面找set的文件 但是发现找不到

原因是这个是一个3\.11版本的文件 而我们刚刚解包是用了3\.8的工具解包 因此它跳过了提取压缩包

回顾刚刚的日志警告

```C
[!] Warning: This script is running in a different Python version than the one used to build the executable.
[!] Skipping pyz extraction
```

这句话的意思是：“你用的是 Python 3\.8 的脚本，但目标程序是 3\.11 打包的，版本不匹配。为了安全起见，我跳过提取 PYZ 压缩包了。”

#### 交互式查看器

因此我们换一种方式

首先打开交互式查看器

```C
py -3.8 -m PyInstaller.utils.cliutils.archive_viewer challenge.exe
```

![](/images/python逆向/QQ_1789972804455.png)

最下面这个PYZ\.pyz就是之前那个没被提取出来的压缩包

**`z`**** 代表它是一个特殊的 Zlib 压缩文件**。我们要找的 `set`、`class_set`、`config_set` 这三个纯 Python 模块，全部藏在这个 `PYZ.pyz` 里面。

对这个交互页面的操作：

> 1. 输入 `O`（大写字母 O，意思是 Open 打开）
> 
>     - 它会提示你输入要打开的文件名，输入：`PYZ.pyz`
> 
>     - 按回车。这时你会发现，黑框里列出的文件瞬间变了！里面全是 `set`、`class_set`、`config_set` 这种你需要的模块！
> 
> 2. 输入 `X`（大写字母 X，意思是 Extract 提取）
> 
>     - 它会问你要提取哪个文件？输入：`set`
> 
>     - 它会问你提取到哪里？直接按回车（默认提取到当前目录）。
> 
>     - 成功！此时你应该能在黑框所在的文件夹里看到 `set.pyc` 了。
> 
>     - 重复这步：再输入 `X`，提取 `class_set` 和 `config_set`（这两个也可能藏有 flag 逻辑，先提出来备用）。
> 
> 3. 输入 `Q`（大写字母 Q，意思是 Quit 退出）
> 
>     - 退出这个交互界面。
> 
> 

![](/images/python逆向/QQ_1789973627557.png)

找到了set

![](/images/python逆向/eec1b046098addd29f2237815b54cd31.png)

提取出来

![](/images/python逆向/QQ_1789974073813.png)

![](/images/python逆向/QQ_1789974098437.png)

在线反编译网站拒绝反编译 原因是pylingual看到开头不是标准的 `A7 0D 0D 0A`（3\.11 的 Magic）

因此我们直接用010在开头插入16个数字 再修改最开头的magic number

![](/images/python逆向/QQ_1789974983784.png)

有时候反编译网站会发癫 我们换一个工具pyinstxtractor\_ng 来解包

https://github\.com/pyinstxtractor/pyinstxtractor\-ng

![](/images/python逆向/QQ_1789977226191.png)

![](/images/python逆向/QQ_1789978038269.png)

找到set\.pyc

![](/images/python逆向/QQ_1789978111362.png)

反汇编

![](/images/python逆向/QQ_1789978224595.png)

#### 源码

拿到了源码！

看到有一个get\_flag函数 是逻辑重点

```C
def get_flag():
    iv = b'0123456789abcdef'
    key = b'ORZ!!66666666666'
    test = 'n/l8uB+jX64J7GK9M3kXgmmGuadUbODl/T2ahcgk7nY='
    MODE = AES.MODE_CBC
    cipher = AES.new(key, MODE, iv)
    decrypted = cipher.decrypt(base64.b64decode(test))
    return unpad(decrypted, AES.block_size).decode()
```

- 加密算法：AES\-CBC（对称加密）

- 密钥 \(key\)：`b'ORZ!!66666666666'` \(16 字节\)

- 偏移量 \(iv\)：`b'0123456789abcdef'` \(16 字节\)

- 密文 \(test\)：一串 Base64 编码的字符串 `'n/l8uB+jX64J7GK9M3kXgmmGuadUbODl/T2ahcgk7nY='`

- **逻辑：Base64 解码 \-\> AES 解密 \-\> 去除填充 \-\> 输出明文**

> AES\-CBC 和 AES\-ECB 是最常见的两种。判断标志就是看有没有 IV（偏移量）。
> 
> - 没有 IV 的，基本是 ECB。
> 
> - 有 IV 的，大概率是 CBC。
> 
> 

> IV 的全称是 Initialization Vector（初始化向量）。在 CBC 模式里，它的作用极其关键，主要有两个：
> 
> 1\.保证每次加密出的密文都不一样（防模式泄露）
> 
> 如果我们在 CBC 模式里去掉 IV，或者 IV 固定不变，会发生什么？
> 假设你加密两个明文块：`AAAA` 和 `AAAA`。
> 如果没有 IV，加密后的密文块会一模一样！黑客只要看到密文里有两个一样的块，就能推测出明文里也有重复的内容，这叫**模式泄露**。
> 
> 加入 IV 后：
> 
> CBC 模式在加密第一个块时，会先让第一个明文块和 IV 做一次异或（XOR），然后再丢给 AES 引擎加密。这样，即使明文一样，只要 IV 不同，密文就完全不同。
> 
> 2\.充当“链条”的起点
> 
> CBC 叫“密码块链接”（Cipher Block Chaining），意思是后面的块会依赖前面的块。
> 
> - 第一个块：`密文块1 = AES加密(明文块1 ^ IV)`
> 
> - 第二个块：`密文块2 = AES加密(明文块2 ^ 密文块1)`
> 
> - 第三个块：`密文块3 = AES加密(明文块3 ^ 密文块2)`
> ……以此类推。IV 就是这条锁链的第一环。
> 
> 3\.在解密时的作用？
> 
> 解密是一个逆过程。你拿到第一段密文，用 AES 解密后，得到的结果是一堆乱码。你必须再异或（XOR）上正确的 IV，才能还原出真正的第一个明文块。
> 
> 

#### Exp

获得加密逻辑之后就可以写脚本了

```Python
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import base64

#  set.py 里的参数
iv = b'0123456789abcdef'
key = b'ORZ!!66666666666'
test = 'n/l8uB+jX64J7GK9M3kXgmmGuadUbODl/T2ahcgk7nY='
MODE = AES.MODE_CBC

# 解密流程
cipher = AES.new(key, MODE, iv)
decrypted = cipher.decrypt(base64.b64decode(test))
flag = unpad(decrypted, AES.block_size).decode()

print("最终 Flag:", flag)

```

HnuCTF\{mabo\_y0u\_kn0w\_pyc\_m4bO\!\}
