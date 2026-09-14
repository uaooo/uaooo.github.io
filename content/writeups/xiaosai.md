+++
title = '校赛'
date = '2026-08-01T12:00:00+08:00'
draft = false
summary = ''
tags = []
showtoc = true
+++

## Magic

flag:

HnuCTF\{marvelously\_\!\*you\_can\_understand\_the\_magic\_and\_interest\_of\_reverse\_engine\_and\_join\_us\*\!\!\}

![b364bad4dd1d6876f6cffb1c9a6cd952\.png](/images/xiaosai/b364bad4dd1d6876f6cffb1c9a6cd952.png)

1. 打印提示 `"=== Magic Lesson ==="` 和 `"Speak the correct incantation: "`

2. 用 `fgets(s, 64, stdin)` 读取输入（最多 63 个字符），去掉换行符。

3. 调用 `sub_4011B6(s)` 进行验证：

    - 要求输入长度必须为 16。

    - 对每个字节 `i`（0\~15），验证 `i + (s[i] ^ 0x5A) == byte_402020[i]`。

4. 如果验证通过（返回 1），则调用 `sub_401237()` 输出正确信息；否则输出 `"That incantation has no power."`。

![f3d0d39a7fd812a84b0becbe7fe2d238\.png](/images/xiaosai/f3d0d39a7fd812a84b0becbe7fe2d238.png)



![5e9d1bd9556d3cc7881ac4dee8806209\.png](/images/xiaosai/5e9d1bd9556d3cc7881ac4dee8806209.png)



![93b2767e48e3f5e586e73299a624e37d\.png](/images/xiaosai/93b2767e48e3f5e586e73299a624e37d.png)

```C
i + (input[i] ^ 0x5A) = byte_402020[i]
```

反解

```C
input[i] = (byte_402020[i] - i) ^ 0x5A
```



```Python
# 给定的数据
byte_402020 = [
    62, 36, 54, 62, 59, 56, 63, 12, 63, 68,
    71, 62, 69, 18, 120, 122
]

byte_402040 = [
    18, 52, 47, 25, 14, 28, 33, 55, 59, 40,
    44, 63, 54, 53, 47, 41, 54, 35, 5, 123,
    112, 35, 53, 47, 5, 57, 59, 52, 5, 47,
    52, 62, 63, 40, 41, 46, 59, 52, 62, 5,
    46, 50, 63, 5, 55, 59, 61, 51, 57, 5,
    59, 52, 62, 5, 51, 52, 46, 63, 40, 63,
    41, 46, 5, 53, 60, 5, 40, 63, 44, 63,
    40, 41, 63, 5, 63, 52, 61, 51, 52, 63,
    5, 59, 52, 62, 5, 48, 53, 51, 52, 5,
    47, 41, 112, 123, 123, 39
]

def compute_input():
    s = []
    for i in range(16):
        s.append(chr((byte_402020[i] - i) ^ 0x5A))
    return ''.join(s)

def verify(s):
    if len(s) != 16:
        return False
    for i in range(16):
        if i + (ord(s[i]) ^ 0x5A) != byte_402020[i]:
            return False
    return True

def decrypt_output():
    return ''.join(chr(b ^ 0x5A) for b in byte_402040)

input_str = compute_input()
print("Calculated input:", input_str)
print("Verification result:", verify(input_str))

print("\nDecrypted output from sub_401237:")
print(decrypt_output())
```

## Welcome

flag：`HnuCTF{HunSec_is_welcome_2_U}`

这是混合使用 RC4 和修改版 XXTEA 的题

由文件名 challenge\_rc4\_xxtea\.exe 也可以猜测到

用ida打开 密钥好像是 `rc4_xxtea_2026`



RC4加密：用密钥 `"rc4_xxtea_2026"` 对输入的29字节进行RC4流加密，得到29字节密文。

内存填充：将这29字节密文拷贝到一个 8个int32\_t（共32字节）的数组 `v[0] ~ v[7]` 中。

因为只有29字节，数组前29字节被填充，最后3个字节（`v[7]`的高3字节）强制补0。

这意味着 `v[7]` 只有低1个字节是RC4密文的有效数据（取值范围0\~255），高3字节恒为0。

### xxtea

本题**xxtea被魔改了**

借助了ai的力量 坑真的想不出

![5901545c7768f179ad9f62f1a02ae6aa\.png](/images/xiaosai/5901545c7768f179ad9f62f1a02ae6aa.png)

![8791d9243a15ab87b6394d185fb8c7ef\.png](/images/xiaosai/8791d9243a15ab87b6394d185fb8c7ef.png)

![e85b2c0881a18d9885b7603bcc8067fd\.png](/images/xiaosai/e85b2c0881a18d9885b7603bcc8067fd.png)

![a3e8b04acbf383ef10a0d653709f51f4\.png](/images/xiaosai/a3e8b04acbf383ef10a0d653709f51f4.png)

![0e71aa534471c782677a5fe93e97ee28\.png](/images/xiaosai/0e71aa534471c782677a5fe93e97ee28.png)

标准版用`sum += delta`且取数用`v[(i+1)%n]`，而本题汇编里把`sum`换成了`edi`，并且取数逻辑变了

![fb139aeacfc96967281c0cc5ed76f9e6\.png](/images/xiaosai/fb139aeacfc96967281c0cc5ed76f9e6.png)

```Python
for guess in range(256):
    # 假设 v_init[7] = guess (高3字节为0)
    # 用魔改XXTEA解密函数解出整个 v 数组（32字节）
    v_recovered = xxtea_decrypt_mod(硬编码密文, XXTEA_KEY, guess)
    
    # 校验：解密出来的 v[7] 是否等于我们假设的 guess
    # 如果相等，说明本次爆破正确
    if v_recovered[7] == guess:
        # 打包成32字节，取前29字节
        rc4_cipher = pack_32bit(v_recovered)[:29]
        
        # 用RC4密钥解出原始输入
        flag = rc4_decrypt("rc4_xxtea_2026", rc4_cipher)
        
        # 若全是可打印字符，即为最终flag
        if flag.isprintable():
            print(flag)  # HnuCTF{HunSec_is_welcome_2_U}
```

## 我们爱奶龙

flag：`HnuCTF{W0M3nA1N@1L0ng!!}`

首先脱壳

```C
wsl upx -d /mnt/c/Users/hp/Downloads/095418_N@iLOn9 -o /mnt/c/Users/hp/Downloads/095418_unpacked
```

根据提示 奶龙爱上了花 本题应该有花指令

main函数

![c8bbf12d1c09a768d1f10c59d3e4a4ea\.png](/images/xiaosai/c8bbf12d1c09a768d1f10c59d3e4a4ea.png)

看函数，以为是“哈希验证”

哈希验证的特征：

![5447453ac9cd82c09c231c094647c4be\.png](/images/xiaosai/5447453ac9cd82c09c231c094647c4be.png)

1. 程序要求输入 24 个字符。

2. 它对输入做了一次编码（循环左移 \+ 加偏移）。

3. 把编码后的结果 \+ 一串固定后缀（`d913...`），一起丢进 SHA\-256 算哈希。

4. 对比算出来的哈希值和内存里写死的哈希值（`1dac...`）是否相等。

出题人在这里埋下了**陷阱**：24 位密码的空间是天文数字，根本爆不开。SHA\-256 是单向的，也逆推不了。这条路是死路！

在地址 `0x40195c` 有一个函数，**主程序从头到尾都没调用它（Dead Code）**。这叫 **“花指令”的变种**。通常花指令是乱序跳转，这里的花指令是“伪装成废弃代码的藏宝图”。

> "花指令"的真正含义:这里的花指令不是传统意义上的 jump 混淆,而是另一个完全不同的 encode 算法——让你以为只有 7 模数\+加号一条路,实际上 5 模数\+减号才通向答案。
> 
> 

![57ff67f891f5c87a8362258a4db0866b\.png](/images/xiaosai/57ff67f891f5c87a8362258a4db0866b.png)

标红或是loc开头的函数 一般为不被调用的函数

![116daaca58cc8b07aacec7ad89b5dfae\.png](/images/xiaosai/116daaca58cc8b07aacec7ad89b5dfae.png)

刚好24个函数对应上了

> 它用了一组完全不同的参数：
> 
> - `i % 5`（不是 7）
> 
> - `13*i + 0x31`（不是 11\*i \+ 0x3d）
> 
> - `c = data[i] - (13*i + 0x31)`（减号不是加号）
> 
> - 还是 `rol8`，但 shift 模 5
> 
> 并且——
> 
> - 它不被 main 调用（所以 IDA 不会自动建函数）
> 
> - 它前面被花指令包裹（`call` 到负地址 \+ `jmp` 跳过 loop start）
> 
> 经典"看起来无用 \+ 看着像垃圾"的双重伪装。
> 
> 

反向解密

```Python
def rol8(c, t):
    return ((c << t) | (c >> (8 - t))) & 0xff

def unbanner(data):
    out = b''
    for i in range(24):
        shift = (i % 5) + 1
        # 编码时是 c = rol8(data[i] - (13*i + 0x31), shift)
        # 所以 data[i] = ror8(c, shift) + (13*i + 0x31)
        c = ((data[i] >> shift) | (data[i] << (8 - shift))) & 0xff
        c = (c + 13*i + 0x31) & 0xff
        out += bytes([c])
    return out
```

结果

```C
>>> unbanner(bytes.fromhex("55d9f98c07955d769c104c5bf5ed59144d971e9be88a7333"))
b'HnuCTF{W0M3nA1N@1L0ng!!}'
```

## 界园志异

flag: flag\{jieyuan\_archive\_weave\_solved\}

程序是一个状态机验证器，读取二进制文件 `route.bin`，逐字节解析并更新内部状态，最终若满足所有校验条件，则输出固定 flag（与输入无关）



题目提示为：

程序接受一个由你自行构造的**二进制路线文件**；

恢复能稳定终局记录的路线，并获得 flag。

### 理解学习

之前未涉足二进制的领地 因此借助ai学习

![0c7e09c97d635ab3735b6ae95b3c03db\.png](/images/xiaosai/0c7e09c97d635ab3735b6ae95b3c03db.png)

![11868d9d9d7e306d3cdd1c92c73d61de\.png](/images/xiaosai/11868d9d9d7e306d3cdd1c92c73d61de.png)

![381503d0d86ce9ef5d27091ab7f510aa\.png](/images/xiaosai/381503d0d86ce9ef5d27091ab7f510aa.png)

![8d5a3e1084026bfb341c477a96261ae3\.png](/images/xiaosai/8d5a3e1084026bfb341c477a96261ae3.png)

![6b4553d0fdfa5cfb1aba672a8259600c\.png](/images/xiaosai/6b4553d0fdfa5cfb1aba672a8259600c.png)

![263b5729ff0c2feb10f61ae7abecd2c3\.png](/images/xiaosai/263b5729ff0c2feb10f61ae7abecd2c3.png)

![5e4e42b98342888ea61f1476e905b7da\.png](/images/xiaosai/5e4e42b98342888ea61f1476e905b7da.png)

![03cc2d4bc74f41583fde07f2257eadb2\.png](/images/xiaosai/03cc2d4bc74f41583fde07f2257eadb2.png)

### 符号

![79c987b209f61b8b78a3787c03177084\.png](/images/xiaosai/79c987b209f61b8b78a3787c03177084.png)

![e0ea242ccab1488c7e1613992422c2c8\.png](/images/xiaosai/e0ea242ccab1488c7e1613992422c2c8.png)

![a2b16e78976e10b14fd279e51c132b1f\.png](/images/xiaosai/a2b16e78976e10b14fd279e51c132b1f.png)

### 梳理

![QQ\_1785572485493\.png](/images/xiaosai/QQ_1785572485493.png)

![165a553dc3dec9bbb1c2c05d0c902226\.png](/images/xiaosai/165a553dc3dec9bbb1c2c05d0c902226.png)

```Python
# 直接从 IDA 中提取的 34 字节密文
cipher = bytes([
    0xe1, 0xf8, 0xc0, 0xf6, 0xe5, 0xe4, 0xf2, 0xee,
    0xe1, 0xfd, 0xf4, 0xcc, 0xcd, 0xfe, 0xfd, 0xff,
    0xe4, 0xf0, 0xff, 0xf3, 0xfc, 0xe4, 0xc5, 0xf1,
    0xeb, 0xe8, 0xc5, 0xf9, 0xf8, 0xeb, 0xe2, 0xc4,
    0xf5, 0xe3
])

flag_chars = []
v34 = 0  # 对应伪代码中的计数器
for i in range(34):
    # 计算密钥字节：v34 % 0x1D - 121，并转为无符号字节（& 0xFF）
    key = (v34 % 0x1D - 121) & 0xFF
    flag_chars.append(cipher[i] ^ key)
    v34 += 13  # 每次循环加 13

flag = bytes(flag_chars).decode('utf-8')
print(flag)
```

## 赛马娘的俄罗斯方块

exe文件可以直接玩 ~~0分怎么不给我flag 看不起0分~~

猜测是要玩到一定的分数才会给flag

### 学习

第一次做 **PyInstaller RE 题**

> 它不是用C/C\+\+写的原生程序，而是把Python源码（\.py）和Python解释器（python\.exe）像“压缩包”一样捆在一起，做成了一个独立的\.exe文件。
> 
> 

> 技术原理：它使用 PyInstaller、Nuitka 或 cx\_Freeze 等工具，把你的 `.py` 文件编译成字节码 `.pyc`，再和 Python 运行库打包在一起。运行时，它会在内存或临时文件夹里把 `.pyc` 解出来，然后让内置的 Python 解释器去执行它。
> 
> 

与其他的题目的区别：

做 C\+\+ 题，你是在跟“机器的语言”打交道；做 Python 打包题，你是在跟“程序员写的源代码”打交道。只要能**把源码还原出来**，比赛就赢了一半。
