+++
title = '磐石行动'
date = '2026-09-10T12:00:00+08:00'
draft = false
summary = ''
tags = []
showtoc = true
+++

## Baby\_randomized\_VM

打开ida的main函数 先读取输入 去掉换行符之后得等于42个字节

程序内部有一个463个字节的数组 通过一下变换生成字节码

```C
v4 = byte_402040[i] ^ (v5 + 11 * (i >> 1));
```

其中v5初始为\-49 每次递增37

通过各个指令集写出exp

1. BitVec\-\-位向量变量

创建一个符号化的未知变量，可以理解成“数学里的未知数x”

```C
s=[BitVec(f's{i}',8)for i in range(42)]
```

创建了42个未知数 分别代表输入的42个字符 没有具体值，只是为了让z3根据条件算出这些具体的值

2. BitVecVal\-\-位向量常量

创建一个具体的，固定的数值

作用是把寄存器v8初始化为确定的数字0

```C
v8=BitVecVal(0,8)
```

类似于c语言中的unsigned v8=0

j每次要自增2：

> 一个指令占用的字节数，决定了j跳多远
> 
> 

- 占2个字节的指令

格式：\[操作码\]\[操作数\] 比如E5占用两个格子

执行完这一条之后，程序计数器必须跳过这两个格子，才能指向下一条指令的开头，所以必须j\+=2

- 占1个字节的指令

格式是\[操作码\]，后面没有跟数字，所以执行完只需要跳一格，即j\+=1\.



限可见字符的固定写法

```C
for ch in s:
    solver.add(And(ch>=0x20,ch<=0x7E))
```

Exp:

```Python
from z3 import *
int_chars=[
  0x84, 0xE2, 0x02, 0x91, 0x67, 0x40, 0x81, 0xF1, 0x66, 0x26, 
  0x59, 0xD6, 0xCE, 0xD4, 0x86, 0x59, 0x52, 0xD3, 0xC8, 0xB4, 
  0xAF, 0x67, 0x3D, 0x92, 0xED, 0x1C, 0x3E, 0xD2, 0x3A, 0x99, 
  0x8F, 0xCE, 0x3E, 0x0F, 0x52, 0xBF, 0x6D, 0xF0, 0x04, 0x0C, 
  0x77, 0xDD, 0xC3, 0xCC, 0x56, 0x66, 0x54, 0x4F, 0xD9, 0xAC, 
  0x53, 0x43, 0x34, 0x7D, 0xE7, 0xA0, 0x3E, 0x66, 0x9C, 0x8B, 
  0x9E, 0xA5, 0x19, 0x7A, 0xC6, 0xB5, 0x8F, 0xC9, 0x3F, 0x6D, 
  0x70, 0x0C, 0x8C, 0xED, 0x5D, 0xBD, 0x4C, 0xD9, 0xE0, 0xC1, 
  0xC7, 0x22, 0x46, 0xDE, 0xC6, 0xA3, 0x11, 0x1A, 0x20, 0x8B, 
  0xE6, 0x35, 0x0B, 0xC3, 0x25, 0x88, 0xFA, 0x14, 0x35, 0x72, 
  0x7C, 0xA8, 0x9F, 0xFD, 0x33, 0x77, 0x69, 0xC8, 0xD9, 0xC3, 
  0x59, 0x1E, 0x41, 0x5C, 0xA2, 0xBA, 0x5E, 0x31, 0x23, 0x8F, 
  0x9A, 0xAB, 0x1B, 0x13, 0x36, 0x94, 0xB6, 0x90, 0x0A, 0x71, 
  0x8A, 0xA8, 0xF2, 0xD3, 0x28, 0xE3, 0x7D, 0x1F, 0xF7, 0xDA, 
  0x48, 0x78, 0x43, 0xCC, 0xAB, 0xFA, 0x2D, 0x2F, 0x30, 0xC9, 
  0xB7, 0x9E, 0xB1, 0x11, 0x2B, 0x97, 0x93, 0x89, 0x14, 0x12, 
  0x10, 0x81, 0xF1, 0xAE, 0x28, 0x65, 0x5C, 0xA5, 0x5F, 0xC6, 
  0x6E, 0x62, 0x5E, 0xC7, 0x2D, 0xF6, 0x4C, 0x2C, 0x7A, 0xA0, 
  0xAF, 0x5B, 0x49, 0x2A, 0x1E, 0x29, 0x91, 0x9E, 0x03, 0x0C, 
  0x8A, 0x61, 0xC9, 0x9B, 0x03, 0x6C, 0xFF, 0x5F, 0xE5, 0xD7, 
  0x25, 0x7B, 0x46, 0xA6, 0xE2, 0xD7, 0x47, 0x47, 0x76, 0x37, 
  0xAD, 0xF7, 0xD9, 0x38, 0x1D, 0x34, 0xA9, 0x95, 0xFF, 0x04, 
  0x1E, 0x74, 0x8C, 0xEE, 0xE1, 0xCB, 0x1B, 0x78, 0xEC, 0x31, 
  0xDF, 0x68, 0x7B, 0x5E, 0x52, 0xD3, 0x83, 0x6D, 0x54, 0x32, 
  0xE0, 0xED, 0xB7, 0x00, 0x77, 0x8C, 0xB8, 0x86, 0xB4, 0x26, 
  0x15, 0xB0, 0x84, 0x81, 0xF0, 0x39, 0xEB, 0x6A, 0xF2, 0x86, 
  0xFD, 0x5B, 0xE0, 0x52, 0xE8, 0xEB, 0xDE, 0x3C, 0x53, 0xF0, 
  0xED, 0xC6, 0xB2, 0x31, 0x6D, 0x3A, 0xA6, 0xE0, 0xD7, 0x05, 
  0xF5, 0x3F, 0xA1, 0x80, 0x5C, 0x3B, 0x01, 0x70, 0xB9, 0x60, 
  0xEA, 0xF0, 0x06, 0x6A, 0xDB, 0x29, 0xD2, 0x53, 0x44, 0x4B, 
  0x67, 0xDC, 0x48, 0x58, 0x41, 0x29, 0x3D, 0xE0, 0xBA, 0x1E, 
  0x60, 0xB3, 0x85, 0xBC, 0xBF, 0x17, 0x00, 0xCF, 0xBB, 0xF4, 
  0xFB, 0x32, 0x94, 0x77, 0x51, 0xF1, 0xE9, 0x56, 0x16, 0x49, 
  0xD3, 0xA7, 0xCB, 0xE8, 0x5C, 0x7B, 0xD8, 0xBA, 0xA9, 0x3F, 
  0x60, 0x2D, 0x99, 0x9D, 0x33, 0x0E, 0xED, 0x2A, 0x97, 0xFF, 
  0xD0, 0x2E, 0x74, 0x7C, 0xB2, 0x1D, 0xF7, 0xB6, 0x71, 0x67, 
  0xD6, 0x5F, 0xC9, 0x46, 0x2E, 0x44, 0x68, 0xA9, 0x0C, 0x43, 
  0x3A, 0x24, 0xFF, 0x97, 0xAD, 0x1B, 0x1D, 0x8C, 0x8E, 0x7D, 
  0xAA, 0x09, 0x7F, 0xE5, 0xAE, 0xFF, 0xC3, 0x2F, 0x6A, 0x40, 
  0x5E, 0xFC, 0xE6, 0x4D, 0xD8, 0x7C, 0xC6, 0xAF, 0xC4, 0xDF, 
  0x29, 0x53, 0xC3, 0xB3, 0xA4, 0xE1, 0x17, 0x10, 0x8E, 0x96, 
  0x1A, 0x1B, 0xBC, 0x15, 0x8C, 0xEA, 0x0D, 0x25, 0x7F, 0x47, 
  0xAF, 0x42, 0xC0, 0x29, 0x7C, 0x5B, 0xCD, 0x9D, 0xFC, 0x49, 
  0x2B, 0x71, 0xD4, 0xB2, 0xB2, 0x4E, 0x34, 0x13, 0x5F, 0x8A, 
  0x90, 0x11, 0x16, 0xF1, 0x9B, 0x2D, 0x95, 0xFB, 0x6A, 0xB5, 
  0xA5, 0xE2, 0xCE, 0xD8, 0xC2, 0x4D, 0x7A, 0xE7, 0xDB, 0xB8, 
  0xF8, 0x73, 0xEE
]
v13=[]
v5=-49
for i in range(463):
    byte=int_chars[i] ^ ((v5+11*(i>>1)) & 0xFF)
    v13.append(byte)
    v5+=37

s=[BitVec(f's{i}',8)for i in range(42)]

v8=BitVecVal(0,8)
V7=BoolVal(False)
j=0
solver=Solver()

for ch in s:
    solver.add(And(ch>=0x20,ch<=0x7E))

while True:
    if j >= len(v13):
        break
    op=v13[j]
    if op==0x45:
        if j+1>=len(v13):
            break
        operand=v13[j+1]
        v7=(v8==operand)
        j+=2
    elif op==0x21:
        solver.add(v7==True)
        j+=1
    elif op==0x26:
        if j+1>=len(v13):
            break
        operand=v13[j+1]
        v8=v8^operand
        j+=2
    elif op==0x1E:
        if j+1>=len(v13):
            break
        operand=v13[j+1]
        v8=v8+operand
        j+=2
    elif op==0x4F:
        if j+1>=len(v13):
            break
        rot=v13[j+1]%8
        v8=RotateLeft(v8,rot)
        j+=2
    elif op==0x4B:
        if j+1>=len(v13):
            break
        idx=v13[j+1]
        if idx>41:
            solver.add(False)
            break
        v8=s[idx]
        j+=2
    elif op==0x6C:
        break
    else:
        solver.add(False)
        break

if solver.check()==sat:
    model=solver.model()
    flag=''.join(chr(model[ch].as_long())for ch in s)
    print("found flag:",flag)
else:
    printf("no")
```

flag\{8775a086\-19c3\-423e\-b3f8\-20a6045b62de\}

## Matrix\_License

整体结构：

**1\.反调试检测**

**2\.时间检测（检测运行速度）**

如果\>0\.25s 则跳转到失败

**3\.输入验证**

如果直接输入“please\_give\_me\_flag”虽然能够直接校验通过，但是无法呈现出flag 只能输出一个correct

否则输入的长度==38 并且以''flag\{''开头 以''\}''结尾

5\+32\+1=38 因此flag内为32格字符 则进入加密校验

**4\.加密校验**

在flag内部的32格字符经过4轮变换之后与目标值相比较 若相等则校验通过

**主函数：**

```C
v9 = 0;
v10 = 0;
do
{
  v11 = 3 * v9 + 5; //算移位位数
  v12 = dword_4020C0[v9] ^ dword_4020A0[v9] ^ *((_DWORD *)&v13[0].tv_sec + v9); 
  //异或常量A0 C0
  ++v9;
  **v10 |= __ROL4__(20260716, v11) ^ v12; //累加 按位或**
 }
 while ( v9 != 8 );
 if ( !v10 )  //要求最终v10==0
 ...
```

按位或：

只要两个位中有一个是1，结果就是1；两个都是0时结果才是0。

即v10一开始全为0 每次循环算出一个数，就用按位或把这个数粘到v10上 如果其中有一个是1 则v10为1

最后是要求v10等于0

每一次都等于0即

```C
ROL ^ v12 ==0
```

两边同时异或ROL 得到

```C
v12 = ROL
```

又因为v12满足：

```C
v12=C0[i] ^ A0[i] ^ Encrypted[v9]
```

所以得到

```C
Encrypted[v9]=ROL^C0[i]^A0[i]
```

**核心：加密校验 401520**

![a6c24814e406473538871237c5b17c13\.png](/images/panshi-action/a6c24814e406473538871237c5b17c13.png)

发现c语言401880的伪代码中有\_\_ROL4\_\_  \-\>是**4字节**循环左移的编译器内置函数

同样的ROL1 \-\>8位循环左移

ROL2 \-\>16位循环左移       ROL8 \-\>64位循环左移     

python中我们用z3的内置函数** RotateLeft**\-\-循环左移 是将一个二进制的所有位向左移动，并且左边溢出的位不丢弃，而是补到右边空出来的位置。



依靠伪代码中的加密循环逻辑写出相应的解密脚本

接下来 告诉z3约束条件：

1. 加密后的结果必须等于目标值

2. 输入的32格字节必须都是可见字符

将每个dword拆成4个独立的字节（0\~255） 每个字节都必须在ASCII的打印范围内

最后提取一下要用的数据

![afdad2bd22f521ecef570e4223063e9b\.png](/images/panshi-action/afdad2bd22f521ecef570e4223063e9b.png)

写出最终的脚本

```Python
from z3 import *
A0_bytes=[
  0x51, 0x8D, 0xA5, 0xD2, 0x9F, 0xAF, 0x0F, 0x93, 0xA4, 0x16, 
  0xC8, 0x1F, 0xE3, 0xF6, 0xA3, 0xAF, 0x72, 0x4B, 0x9C, 0x71, 
  0xBA, 0x4A, 0x73, 0xE7, 0x66, 0x87, 0x8A, 0x13, 0xFC, 0xD1, 
  0x47, 0xB6
]
C0_bytes=[
  0xF8, 0x63, 0x71, 0x01, 0x64, 0xC2, 0x88, 0x9A, 0xBD, 0xD8, 
  0xBB, 0xBC, 0xC5, 0x0A, 0x26, 0xEB, 0x9B, 0xC4, 0x02, 0x13, 
  0xBD, 0xC3, 0x87, 0x0E, 0x2F, 0x7F, 0xCD, 0x29, 0xD8, 0xFC, 
  0xD3, 0x0B
]
E0_bytes=[
    1,   6,   0,   4,   3,   5,   7,   2,   2,   0, 
    4,   5,   3,   7,   6,   1,   3,   4,   0,   6, 
    2,   1,   7,   5,   7,   1,   6,   0,   5,   4, 
    2,   3
]
I100_bytes=[
   17,  15,  16,  23,   6,  12,  14,  13,  14,   3, 
   26,   5,  13,  26,   4,  21,  23,  22,  26,  26, 
   24,   6,   5,  16,  12,  26,  23,  11,  15,   5, 
   19,  15
]
I120_bytes=[
  99, 193,  45, 117, 228, 128,  89, 199, 190, 140, 
   7,  25, 232,  54, 136,   1, 232, 125, 155, 121, 
  187, 142, 111,  65,  32, 234, 129,  42, 103,  53, 
   64, 221, 193, 116,  30,  30, 253, 234,  83, 247, 
  164, 135, 121, 222, 121,   0, 245,  26, 170, 225, 
  155, 120,  38,  38, 238,  91, 240, 104, 168, 239, 
  142, 183, 131, 201,  36, 104, 253, 252, 239, 174, 
  231, 142,  52, 154,  86,  86,  51, 222, 113, 236, 
  174, 121,  70,  27, 161,  23, 216,  58, 119,  19, 
  171, 230,  91, 250,  34, 197, 113,  91, 162,  42, 
  240, 186,  88,  69, 164, 196, 201,  83, 116,   3, 
  178, 221, 229, 226,  18, 204, 161, 250,  49, 237, 
   93,  54, 233,  61, 219,  32,  38,  65
]
I1A0_bytes=[
   68,   0,  36,  74, 206, 226,  41,  29,  23,  39, 
  228,  68,  79,  62, 182, 107, 208, 231, 254, 207, 
  138, 249, 104,  69, 221, 133, 137, 255,   4,  34, 
  202, 193,  66, 149,  91, 163, 141,  60,  78,  97, 
  251, 106,  58,  70, 138, 103, 134, 127, 199, 107, 
   95,  58, 170,  36, 209, 117, 231,  62, 106,  51, 
  182, 252, 168,  16, 209,  60, 146, 170, 135, 253, 
   56, 128, 238, 229, 130, 141,  43, 148, 227, 247, 
  247,  37, 134, 237, 128,  84,  37, 142,  23, 243, 
   73, 234,  60, 202, 254, 142, 175, 188, 245, 229, 
  102, 185, 254, 231, 190, 188, 133,   5,  54, 248, 
   48, 118,  35, 190, 104, 130,  44, 179, 223, 145, 
  194,  52,  52, 123,  84, 249, 158,  31
]


def bytes_to_dwords(data):
    return [int.from_bytes(data[i:i+4],'little') for i in range(0,len(data),4)]

A0=bytes_to_dwords(A0_bytes)
C0=bytes_to_dwords(C0_bytes)
E0=E0_bytes
I100=I100_bytes
I120=bytes_to_dwords(I120_bytes)
I1A0=bytes_to_dwords(I1A0_bytes)

CONST=0x135276C
target=[]
for i in range(8):
    shift=3*i+5
    rol=((CONST<<shift)|(CONST>>(32-shift)))&0xFFFFFFFF
    target.append(rol^A0[i]^C0[i])

X=[BitVec(f'x{i}',32) for i in range(8)]

a1=X[:]

for i in range(4):
    for j in range(8):
        idx=8*i+j
        v6=j
        v5=(j+1)&7

        v2=RotateLeft(
            I120[idx]^(a1[v6]+I1A0[idx]),
            I100[idx]
            )
        a1[v5]=a1[v5]+v2

        rot2=RotateLeft(
            I120[8*i+((j+3)&7)]^a1[v5],
            I100[idx] % 0x11 + 1
            )
        a1[v6]=a1[v6]^rot2

    v1=[0]*8
    for k in range(8):
        v1[k]=a1[E0[8*i+k]]
    for m in range(8):
        a1[m]=v1[m]

solver=Solver()

for i in range(8):
    solver.add(a1[i]==target[i])

for i in range(8):
    b0=(X[i]>>0)&0xFF
    b1=(X[i]>>8)&0xFF
    b2=(X[i]>>16)&0xFF
    b3=(X[i]>>24)&0xFF
    for b in [b0,b1,b2,b3]:
        solver.add(And(b>=0x20,b<=0x7E))

if solver.check()==sat:
    model=solver.model()
    flag_bytes=[]
    for i in range(8):
        val=model[X[i]].as_long()
        flag_bytes.append((val>>0)&0xFF)
        flag_bytes.append((val>>8)&0xFF)
        flag_bytes.append((val>>16)&0xFF)
        flag_bytes.append((val>>24)&0xFF)

    inner=''.join(chr(b) for b in flag_bytes)
    flag=f"flag{{{inner}}}"
    print("found flag",flag)
else:
    print("no")
```

flag\{b6f5c8102ce74931967eb974a9760284\}

## 总结

这次比赛不能使用ai真的看到了自己的很多不足  并且第一题解题太慢解出来的时候组长已经解完了

总结分为两点吧 我觉得最重要的 一个是看和分析伪代码的能力 一个是写脚本的能力

### 分析伪代码和汇编语言 

简单的伪代码可以看懂 但是一旦复杂起来比如加了C\+\+的什么库 main函数伪代码变得很复杂之后我就感觉完全看不进去了

并且感觉对于各个加密虽然有所了解但是并不能立马反应 比如之前做题都是看到名字是base 或者tea 或者RC4 很自然地直接使用各个加密解密方法了

但是碰到的更多的情况却是 函数名被ida反汇编吞掉 然后必须得依靠自己读伪代码的能力以及对各个机密方法的特征的判断读取能力 来进行一系列的解密操作

所以我感觉这是re手最应该加强的第一个方面 不仅要能识别加了各种库的又长又复杂的伪代码 并且要训练自己的汇编语言 以防被ida伪代码骗



### 写脚本

妈呀 这个比赛手搓脚本更是痛苦 

本来是要手搓的 完全手搓不出来 之前在网上做题都是ds一键生成脚本。。no。。

然后看了一遍代码试图手搓 结果报了一堆错 结果好不容易修改完错误了 一看发现题目已经被做了哈哈

我感觉写这个python脚本还是可以好好学一下 因为之前都是学的c语言 对这个python不够熟悉



另外 我觉得打这种比赛很好的一点就是能静下心不用ai 好好发现一下自己的不足。

比如平常用ai一键翻译看不懂的伪代码或者反汇编

比如平常看到ai分析出常见的base、rc4、tea之类的加密类型就认为自己已经会了然后一件解密

再比如平常知道逻辑之后就直接让ai一键生成脚本了 也没有自己重新学习着再写一遍 

以上种种的问题在禁用ai的比赛中全部都暴露了出来 我也进行了反思和重新学习。
