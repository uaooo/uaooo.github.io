+++
title = '0xGame-Week1'
date = '2026-10-05T12:00:00+08:00'
draft = false
summary = ''
tags = []
showtoc = true
+++
平台地址：https://0xgame2026\.play\.ctfplus\.cn/（https://www\.ctfplus\.cn/）

## signin

![](/images/0xGame-Week1/d6f9b5170fb5e04e4b2bbba45fd6786c.png)

### Exp

```C
reference_data = [
    106,  34,  29,  59,  55,  63,  33, 106,  42,  63, 
     52,   5, 107,  30,  27,   5, 110,  52,  62,   5, 
     41,  46,  59,  40,  46,   5,  35, 106,  47,  40, 
      5,  40,  63,  44,  63,  40,  41,  63,   5,  31, 
     52,  61,  51,  52,  63,  63,  40,  51,  52,  61, 
    123,  39
]

flag = ""
for byte in reference_data:
    flag += chr(byte ^ 0x5A)

print(flag)
```

flag：0xGame\{0pen\_1DA\_4nd\_start\_y0ur\_reverse\_Engineering\!\}

## ez\_upx

![](/images/0xGame-Week1/d6de969295500bc00e6bf7d749ee1e93.png)

主函数

![](/images/0xGame-Week1/f574acdd36dc46164ad8714689f467db.png)

![](/images/0xGame-Week1/076292a8f9b1e0de71f784c25ccc907e.png)

函数4015C7 很明显的base64特征 并且后面还有标准字母表

![](/images/0xGame-Week1/ea70d1127025ec38ce4c5959b5f33d8d.png)

![](/images/0xGame-Week1/473c0aa34f1f6ceb6388c3fb43aac286.png)

这个`aVivo50`是IDA自己取的名 点进之后发现原字符串是`vivo50`全小写

![](/images/0xGame-Week1/QQ_1790586789812.png)

### 流程

大概流程就是将我们输入的flag进行`vivo50`的多字节异或加密 然后再通过base64加密 

最后将加密后的字符串与目标字符串进行比较

### Exp

```Python
import base64

# 目标 Base64 字符串
encoded_str = "RhExDlhVDSdGGEJHKRBGGmpbGFkBMGBgLkhXTkg="

# 1. Base64 解码
v3 = base64.b64decode(encoded_str)

# 2. 密钥 'vivo50'
key = [ord(c) for c in 'vivo50']

# 3. 异或还原
flag = ""
for i in range(len(v3)):
    flag += chr(v3[i] ^ key[i % 6])

print("Flag:", flag)
```

flag：0xGame\{N0www\_y0u\_kn0w\_UPX\!\!\!\}

## 欸？云朵

![](/images/0xGame-Week1/QQ_1790588570335.png)

**这是典型的 Win32 窗口程序模板**

### 分析

```C
HWND hWnd;
```

> `hWnd` 是 窗口句柄。
> 
> - `h` = handle，句柄
> 
> - `Wnd` = window，窗口
> 
> - `HWND` = Handle to Window
> 
> - 可以把它理解成系统给你的一个“窗口编号”或“窗口引用”。它不是窗口本身，而是用来代表某个窗口的一个值。后面函数都要靠它来指定“操作哪个窗口”：
> 
> 

```C
hWnd = CreateWindowExA(...);
```

意思就是：创建一个窗口，系统返回这个窗口的句柄，存到 `hWnd` 里。

窗口的构造函数：

```JSON
hWnd = CreateWindowExA(
    0,                      // 扩展样式
    "CloudFlashWindow",     // 窗口类名
    "0xGame2026",           // 窗口标题
    0xCF0000u,              // 窗口样式
    0x80000000,             // x 坐标：默认位置
    0x80000000,             // y 坐标：默认位置
    520,                    // 宽度
    180,                    // 高度
    0,                      // 父窗口
    0,                      // 菜单
    hInstance,              // 程序实例句柄
    0                       // 附加参数
);
```

getmessage：

```C
while ( GetMessageA(&Msg, 0, 0, 0) > 0 )
{
    TranslateMessage(&Msg);
    DispatchMessageA(&Msg);
}
```

这是 Windows 程序的 **消息循环**。

> Windows 程序不是从头到尾顺序执行的，而是 事件驱动：
> 
> - 鼠标点击
> 
> - 键盘按下
> 
> - 窗口需要重绘
> 
> - 窗口被关闭
> 
> - 定时器触发
> 
> **这些事件都会被系统包装成“消息”，放到消息队列里。**
> 
> 

```C
TranslateMessage(&Msg);
DispatchMessageA(&Msg);
```

然后，把键盘按键消息翻译成字符消息。继续把这条消息发给对应的窗口过程函数处理。

对应到这个函数 窗口函数就是：

```C
WndClass.lpfnWndProc = (WNDPROC)sub_401871;
```

也就是说，**所有窗口事件最终都会交给 **`sub_401871`** 处理**。

### 核心函数

因此 我们的核心函数就是401871

![](/images/0xGame-Week1/QQ_1790589358887.png)

分析伪代码：

```C
memset(&Paint, 0, sizeof(Paint));
hdc = BeginPaint(a1, &Paint);          // 开始绘图
v12 = 0;

*(_QWORD *)Source = 0x57A3FFA1AC358CD7LL;  // 初始化密文
v9 = 0x8BFFBCE713E7790CuLL;
v10 = 0x44DD7073685C5499LL;
v11 = -3977;
// 此时 Source 缓冲区里是一串加密数据

sub_401620(Source, 26, "ShedaLight", 10);  // 解密函数！

memset(Destination, 0, sizeof(Destination)); // 清空目标缓冲区
strcpy(Destination, "Your flag is ");        // 复制前缀
strcat(Destination, Source);                 // 拼接解密后的 flag

GetClientRect(a1, &Rect);                    // 获取窗口客户区大小
DrawTextA(hdc, Destination, -1, &Rect, 0x25u); // 把字符串画到窗口上

sub_401768(Source);          // 可能是清理或反调试
sub_401D40(Source, 27);      // 也是清理，不用管

EndPaint(a1, &Paint);        // 结束绘图
```

![](/images/0xGame-Week1/QQ_1790590626056.png)

**伪代码解析：**

后面两个函数

```C
sub_401768(Source);
sub_401D40(Source, 27);
```

它们在 `DrawTextA` 之后调用，大概率是清理内存或反调试，不影响 flag 的生成。不需要管。

```Java
sub_401550(v5, a3, a4);   // 这一步是 RC4 的 KSA，初始化 S 盒
v10 = 0;                  // 对应 RC4 的 i
v9 = 0;                   // 对应 RC4 的 j
for ( i = 0; ; ++i )
{
    if ( i >= a2 ) break;
    v9 += v5[++v10];      // j = (j + S[i]) % 256，v10 先自增
    v7 = v5[v10];
    v5[v10] = v5[v9];
    v5[v9] = v7;          // swap(S[i], S[j])
    v6 = v5[(v5[v10] + v5[v9])];  // K = S[(S[i] + S[j]) % 256]
    *(_BYTE *)(a1 + i) ^= v6;     // 密文 ^= K
}
```

这就是 **RC4 的 PRGA**（伪随机生成算法），密钥是 `"ShedaLight"`，长度 10。
`a1` 指向的缓冲区是密文，长度 `a2 = 26`，解密后就得到明文 flag。

`Source` 是 `char[8]`，后面紧跟着 `v9`、`v10`、`v11`，它们在栈上连续存放。按小端序展开，一共 26 字节：

拼接之后就是密文\-\-十六进制：

```C
D7 8C 35 AC A1 FF A3 57 0C 79 E7 13 E7 BC FF 8B 99 54 5C 68 73 70 DD 44 77 F0
```

### Exp

```Python
def rc4(key, data):
    S = list(range(256))
    j = 0
    keylen = len(key)
    # KSA
    for i in range(256):
        j = (j + S[i] + key[i % keylen]) % 256
        S[i], S[j] = S[j], S[i]
    # PRGA
    out = bytearray()
    i = j = 0
    for byte in data:
        i = (i + 1) % 256
        j = (j + S[i]) % 256
        S[i], S[j] = S[j], S[i]
        K = S[(S[i] + S[j]) % 256]
        out.append(byte ^ K)
    return bytes(out)

key = b"ShedaLight"
cipher = bytes.fromhex(
    "D7 8C 35 AC A1 FF A3 57 0C 79 E7 13 E7 BC FF 8B "
    "99 54 5C 68 73 70 DD 44 77 F0"
)
plain = rc4(key, cipher)
print(plain.decode(errors="ignore"))

```

flag：0xGame\{Dyn4m1c\_1$\_s0\_Fun\!\}

## 旧时代的信号

[attachment3\.zip](图片和附件/attachment3.zip)

![](/images/0xGame-Week1/QQ_1790596703008.png)

一开始看到还以为加壳了 其实不然

甚至不让我反汇编 因为这是一个古老的 8086 架构的 MS\-DOS 程序 现代的反编译引擎完全不支持把它翻译成伪 C 代码 ~~果然很旧时代啊~~

### 汇编语言

```C
seg000:0005  mov si, 5Dh
seg000:0008  mov di, 7Eh
seg000:000B  mov cx, 21h
seg000:000E  mov bl, 0A7h
seg000:0010  xor bh, bh
```

- `mov si, 5Dh`：把 `5Dh`（十六进制）放进 `SI`（源变址寄存器）。这是告诉程序：密文从内存偏移 5Dh 的位置开始读。你可以看下面数据段 `005D` 处的数据，确实是从 `0F4h` 开始的。

- `mov di, 7Eh`：把 `7Eh` 放进 `DI`（目的变址寄存器）。意思是：解出来的明文，写进内存偏移 7Eh 的位置。

- `mov cx, 21h`：`21h` 是十六进制的 33。`CX` 是计数器，表示这个循环要跑 33 次（正好是密文的长度）。

- **`mov bl, 0A7h`**：**`BL`** 是 **`BX`** 的低 8 位。放入初始值 **`A7h`**，这是初始密钥。

- `xor bh, bh`：将 `BH`（BX 的高 8 位）清零。`BX` 此时变成了 `00A7h`。`BH` 当作循环计数器，从 0 开始。

核心解密循环

```C
seg000:0012 loc_10012:
seg000:0012  lodsb
```

- `lodsb` \(Load String Byte\)：这是一条复合指令。**它将 **`DS:SI`** 指向的那个字节读入 **`AL`** 寄存器，并且自动让 **`SI`** 加 1。**

- 执行效果：`AL = [DS:SI]`，然后 `SI = SI + 1`。

```C
seg000:0013  ror al, 1
seg000:0015  ror al, 1
seg000:0017  ror al, 1
```

- `ror` \(Rotate Right\)：循环右移。将 `AL` 的 8 个比特位整体向右移动 1 位，最右边掉下去的 1 位会补到最左边。

- 为什么写了三遍：8086 处理器不支持直接写 `ror al, 3`（后来 CPU 才支持），所以汇编器会连续生成三次 `ror al, 1`。这相当于将**字节循环右移 3 位**。

```C
seg000:0019  sub al, 7
```

`AL = AL - 7`。

```C
seg000:001B  sub al, bh
```

`AL = AL - BH`。`BH` 是刚才初始化为 0，每次循环末尾加 1 的计数器。所以第一轮减 0，第二轮减 1。

```C
seg000:001D  xor al, bl
```

`AL = AL ^ BL`。**`BL`** 是动态变化的密钥。

```C
seg000:001F  stosb
```

- `stosb` \(Store String Byte\)：复合指令。**将 **`AL`** 的值写入 **`ES:DI`** 指向的位置，然后 **`DI = DI + 1`**。**

- 到这里，一个明文就计算出来，并存到了 `7Eh` 开始的地方。

```C
seg000:0020  add bl, al
```

`BL = BL + AL`。用刚刚解出来的明文字节，来更新密钥。

```C
seg000:0022  rol bl, 1
```

`rol` \(Rotate Left\)：循环左移。将 `BL` 左移 1 位。

```C
seg000:0024  xor bl, bh
```

BL = BL ^ BH

```C
seg000:0026  inc bh
```

`BH = BH + 1`。计数器加 1。

```C
seg000:0028  loop loc_10012
```

`loop` 这条指令的底层动作非常死板，它只干两件事：

1. 先把 `CX` 减 1（`CX = CX - 1`）。

2. 然后看 `CX` 是不是 0：

    - 如果不为 0，说明还没跑够 33 次，它就会强行让 CPU 跳回 `loc_10012` 那个门牌号那里，重新开始执行。

    - 如果为 0，说明跑完了，它就往下走（执行 `002A` 的代码）。

即完美地控制了33次的循环。

### Exp

```Python
def ror(val, n):
    # 8位循环右移
    return ((val >> n) | (val << (8 - n))) & 0xFF

def rol(val, n):
    # 8位循环左移
    return ((val << n) | (val >> (8 - n))) & 0xFF

# 从 seg000:005Dh 开始的 33 字节加密数据
enc = [
    0xF4, 0xFE, 0x88, 0xC2, 0xD2, 0x54, 0x64, 0x06, 0x28, 0xD5,
    0xBD, 0xB6, 0x65, 0x58, 0x4D, 0x1D, 0x56, 0x7E, 0x0B, 0x99,
    0xE6, 0xF2, 0xA4, 0x55, 0x7D, 0x21, 0x83, 0x96, 0xE1, 0x10,
    0x0D, 0x4F, 0x5C
]

bl = 0xA7  # 初始密钥
bh = 0     # 计数器
flag = ""

for al in enc:
    al = ror(al, 3)          # ror al, 1 执行 3 次
    al = (al - 7) & 0xFF     # sub al, 7
    al = (al - bh) & 0xFF    # sub al, bh
    al = al ^ bl             # xor al, bl
    flag += chr(al)          # stosb 存入目标缓冲区
    
    # 更新密钥
    bl = (bl + al) & 0xFF    # add bl, al
    bl = rol(bl, 1)          # rol bl, 1
    bl = bl ^ bh             # xor bl, bh
    
    bh = (bh + 1) & 0xFF     # inc bh

print("Flag:", flag)
```

flag：0xGame\{JuS7\_g1v3\_16bit7t\_@\_try\!\!\}

## z3\_solver

![](/images/0xGame-Week1/QQ_1790599642372.png)

这个循环非常巧妙，它不是单独检查某个字符，而是把23个字符编织在一起。注意代码里的取余符号 `% 23`：

- 当 `i = 0` 时，方程用到的是：`a1[1]`, `a1[0]`, `a1[7]`, `a1[4]`

- 当 `i = 22` 时，方程用到的是：`a1[(22+1)%23]` 也就是 `a1[0]`，还有 `a1[22]`, `a1[(22+7)%23]` 也就是 `a1[6]`，以及 `a1[(22+4)%23]` 也就是 `a1[3]`。

因为 `% 23` 的存在，这个字符串首尾相连成了一个环。每一个方程都牵扯到4个字符，导致我们不能单独猜某一个字符，必须把23个字符当成一个整体来解。因此我们使用z3。

求解的时候注意要用小端序

> 这和 CPU 读取内存的规则有关。x86/x64 架构的 CPU 在读一个 2 字节的整数（word）时，默认是小端序（Little\-Endian），也就是低位在前，高位在后。
> 
> 

> 假设内存里有两个连续的字节：
> 
> - 地址 A \(低地址\)：`0x21` \(十进制 33\)
> 
> - 地址 A\+1 \(高地址\)：`0x0B` \(十进制 11\)
> 
> 当 CPU 要读取一个 16 位整数时，它会去地址 A 拿。因为是小端序，它会把低地址的 `0x21` 当作低8位，高地址的 `0x0B` 当作高8位。
> 拼起来就是：`0x0B21`（十进制 2849）。
> 计算公式就是：`33 + (11 << 8) = 2849`。
> 
> 

### Exp

```Python
from z3 import *

# 目标字节数组
ida_chars = [
    33,  11, 191,   7,  44,  10,  43,  10, 252,   8, 
    96,   8, 199,  10,  33,  10, 238,   7,  14,  10, 
    85,  11,   5,  10, 187,  10,   2,   9, 200,  11, 
    203,  11, 255,   6,  78,  12,  72,  10, 227,   7, 
    239,  10,  39,  10,  87,  10
]

# 将字节数组按小端序组合成16位整数数组
word_404000 = []
for i in range(0, len(ida_chars), 2):
    val = ida_chars[i] | (ida_chars[i+1] << 8)
    word_404000.append(val)

# 初始化Z3求解器
s = Solver()

# 创建23个整数变量，代表Flag的每个字符
x = [Int(f'x_{i}') for i in range(23)]

# 添加约束条件
for i in range(23):
    # 约束1：可打印ASCII字符范围 (0x1F < x <= 0x7E)
    s.add(x[i] > 0x1F)
    s.add(x[i] <= 0x7E)
    
    # 约束2：线性方程
    # 5 * a1[(i + 1) % 23] + 3 * a1[i] + 11 * a1[(i + 7) % 23] + 7 * a1[(i + 4) % 23] == word_404000[i]
    eq = (5 * x[(i + 1) % 23] + 
          3 * x[i] + 
          11 * x[(i + 7) % 23] + 
          7 * x[(i + 4) % 23]) == word_404000[i]
    s.add(eq)

# 求解
if s.check() == sat:
    m = s.model()
    # 提取字符并拼接成字符串
    flag_chars = [chr(m[x[i]].as_long()) for i in range(23)]
    print("Flag:", "".join(flag_chars))
else:
    print("No solution found. Check the constraints.")
```

flag：0xGame\{z3\_Se3ms\_ezzz2z\}

## Guess

[attachment5\.zip](图片和附件/attachment5.zip)

题目提示：

> Guessing Game
> 
> 这是一个 Python PYC 逆向入门题。
> 
> 选手附件
> 
> - `dist/attachment.exe`：Windows x64 控制台程序
> 
> - `dist/attachment.zip`：发布压缩包
> 
> 程序会随机生成 0 到 100 的数字，并给出五次猜测机会。猜中时程序会显示一个假 flag；真正的 flag 没有直接输出。
> 
> 运行
> 
> ```Plain Text
> Welcome to 0xGame2026!
> Let's play a game now.
> You have five chances to guess the number（0-100）
> ```
> 
> 目标是逆向附件，恢复程序内部保存的真实 flag。
> 
> 

题目说这是一道pyc逆向题

先解包试试

![](/images/0xGame-Week1/QQ_1790601399870.png)

```Bash
py -3.8 pyinstxtractor.py attachment.exe
```

![](/images/0xGame-Week1/QQ_1790601476304.png)

Python version3\.14 说明非常新 

主逻辑在game\.pyc

使用在线反编译工具https://pylingual\.io/

![](/images/0xGame-Week1/QQ_1790602469334.png)

反编译代码

```Python
import random
import struct
DELTA = 2654435769
MASK = 4294967295
TEA_KEY = b'guess_secret_key'
FLAG_CIPHERTEXT = bytes.fromhex('1102c93630fe71bd39ad4e4cc34600299897001c3300581e465c56d2a11ba430819e7a59f1c20188f40ccba3a312dd3d')
def tea_decrypt(data: bytes, key: bytes) -> bytes:
    # irreducible cflow, using cdg fallback
    """Decrypt little-endian TEA blocks."""
    # ***<module>.tea_decrypt: Failure: Compilation Error
    words = struct.unpack('<4I', key)
    result = bytearray()
    for offset in range(0, len(data), 8):
        left, right = struct.unpack('<2I', data[offset:offset + 8])
        total = DELTA * 32 & MASK
        for _ in range(32):
            right = right - ((left << 4) + words[2] ^ left + total ^ (left >> 5) + words[3]) & MASK
            total = total - DELTA & MASK
            left = left - ((right << 4) + words[0] ^ right + total ^ (right >> 5) + words[1]) & MASK
        result.extend(struct.pack('<2I', left, right))
    padding = result[(-1)]
    if not (1 <= padding <= 8 and result[-padding:] != bytes([padding]) * padding):
        raise ValueError('bad padding')
            return bytes(result[:-padding])
def main() -> None:
    print('Welcome to 0xGame2026!')
    print('Let\'s play a game now.')
    print('You have five chances to guess the number（0-100）')
    target = random.randint(0, 100)
    for _ in range(5):
        try:
            guess = int(input('> ').strip())
        except (EOFError, ValueError):
            print('Wrong!')
            print('Try again!')
        else:
            if guess == target:
                print('You win!')
                print('flag is 0xGame{I‘m just kidding :D}')
                secret = tea_decrypt(FLAG_CIPHERTEXT, TEA_KEY)
                if not secret.startswith(b'0xGame{'):
                    raise RuntimeError('integrity check failed')
                else:
                    return None
            else:
                print('Wrong!')
                print('Try again!')
if __name__ == '__main__':
    main()
```

### 脚本思路

#### 数据预处理与常量

```Python
DELTA = 2654435769
MASK = 4294967295
TEA_KEY = b'guess_secret_key'
FLAG_CIPHERTEXT = bytes.fromhex('1102c...')
```

- `MASK = 0xFFFFFFFF`：这是 Python 里模拟 C 语言 32 位溢出的关键。 Python 的整数是无限大的，如果不加 `& MASK`，位移和加法会导致数字无限增大，最终算不出正确结果。C 语言里 `uint32_t` 溢出会自动截断，**Python 必须手动用 **`& 0xFFFFFFFF`** 来截断**。

- `FLAG_CIPHERTEXT`：把十六进制字符串转回字节流。密文长度是 48 字节，正好是 8 的倍数（TEA 按 8 字节分块）。

#### 密钥调度 \(Key Schedule\)

```Python
words = struct.unpack('<4I', key)
```

- TEA 加密需要 4 个 32 位的密钥字（`k[0]`, `k[1]`, `k[2]`, `k[3]`）。

- `<4I` 表示：小端序（`<`）、解析出 4 个无符号 32 位整数（`4I`）。

- **`b'guess_secret_key'`** 是 16 字节，刚好切分成 4 个整数。如果密钥不足 16 字节，通常需要补零。

#### 分块与解密核心逻辑

```SQL
for offset in range(0, len(data), 8):
    left, right = struct.unpack('<2I', data[offset:offset + 8])
```

- 每次循环读取 8 个字节，拆分成两个 32 位整数 `left` 和 `right`（即 TEA 的 `v0` 和 `v1`）。

```Python
total = (DELTA * 32) & MASK
for _ in range(32):
    right = (right - ((((left << 4) + words[2]) ^ (left + total) ^ ((left >> 5) + words[3])) & MASK)) & MASK
    total = (total - DELTA) & MASK
    left = (left - ((((right << 4) + words[0]) ^ (right + total) ^ ((right >> 5) + words[1])) & MASK)) & MASK
```

这是整个脚本最核心的部分，是标准 TEA 解密的逆向操作：

- 加密过程里，`total` 从 0 开始，每轮 `+ DELTA`，共 32 轮；`left` 和 `right` 是 `+` 操作。

- 解密过程里，`total` 初始化为 `DELTA * 32`，每轮 `- DELTA`；`left` 和 `right` 是 `-` 操作。

- `<< 4` 和 `>> 5`：这是 TEA 的“扩散”操作，把 `left` 的位向左移 4 位（乘 16）和向右移 5 位（除以 32）。

- `^`（异或）：用来混合明文、密钥和轮常量。

- 注意括号和 `& MASK`：`((left << 4) + words[2]) ^ (left + total) ^ ((left >> 5) + words[3])` 这一大坨是标准的 TEA 解密逻辑。因为 Python 的运算符优先级（`+` 高于 `^`），反编译出来的原代码没加括号也能算对，但为了逻辑清晰和防止误解，加上显式括号是最稳妥的。

#### 重组与填充处理 \(Padding\)

```Python
result.extend(struct.pack('<2I', left, right))
```

- 解密完 8 字节后，用 `struct.pack` 把两个整数还原成字节流，拼接到 `result` 中。

```Python
padding = result[-1]
if 1 <= padding <= 8:
    result = result[:-padding]
```

- 加密前，明文通常按照 PKCS\#7 标准进行了填充（比如明文长度是 40，会补 8 个字节的 `0x08`，让长度变成 8 的倍数）。

- 解密后，最后一个字节就是填充长度（`padding`）。如果 `padding` 在 1 到 8 之间，就切掉末尾的 `padding` 个字节。

- 为什么不用原代码的 `if not (...) raise ValueError`？ 因为出题人故意写反了判断条件（`!=` 应该是 `==`），并且 `return` 的缩进在 `raise` 之后成了死代码。

### Exp

```Python
import struct

DELTA = 2654435769
MASK = 4294967295
TEA_KEY = b'guess_secret_key'
FLAG_CIPHERTEXT = bytes.fromhex('1102c93630fe71bd39ad4e4cc34600299897001c3300581e465c56d2a11ba430819e7a59f1c20188f40ccba3a312dd3d')

def tea_decrypt(data: bytes, key: bytes) -> bytes:
    """正确的 TEA 解密实现（忽略反编译代码中有问题的填充校验）"""
    # 将 key 解包为 4 个 32 位无符号整数（小端序）
    words = struct.unpack('<4I', key)
    result = bytearray()
    
    # 每次处理 8 字节（一个 TEA block）
    for offset in range(0, len(data), 8):
        left, right = struct.unpack('<2I', data[offset:offset + 8])
        total = (DELTA * 32) & MASK
        
        for _ in range(32):
            # TEA 解密核心逻辑
            # 截图里的运算符优先级正好组合成了标准 TEA 解密，这里加上了显式括号确保安全
            right = (right - ((((left << 4) + words[2]) ^ (left + total) ^ ((left >> 5) + words[3])) & MASK)) & MASK
            total = (total - DELTA) & MASK
            left = (left - ((((right << 4) + words[0]) ^ (right + total) ^ ((right >> 5) + words[1])) & MASK)) & MASK
            
        result.extend(struct.pack('<2I', left, right))
        
    # 尝试移除 PKCS#7 填充
    padding = result[-1]
    if 1 <= padding <= 8:
        result = result[:-padding]
        
    return bytes(result)

if __name__ == '__main__':
    try:
        secret = tea_decrypt(FLAG_CIPHERTEXT, TEA_KEY)
        print("[+] Decrypted Secret:", secret.decode('utf-8', errors='ignore'))
        
        if secret.startswith(b'0xGame{'):
            print("[*] Integrity check passed! This is the real flag.")
        else:
            print("[-] Integrity check failed.")
    except Exception as e:
        print("[-] Error:", e)
```

flag：0xGame\{Congratulations\_0n\_y0ur\_v1ct0ry：）\}

## ez\_flower

flag：0xGame\{WoW\_Th3\_f1ow3r$\_@re\_SOo0oo b3@u7ifull\!\!\}

[attachment6\.zip](图片和附件/attachment6.zip)

提示

> 花指令入门
> 
> 附件是一个 Windows x86 控制台程序。程序里有三处花指令，尝试恢复正常控制流并找到 flag 校验逻辑。
> 
> 提示：三组垃圾字节分别是 `11 22 33`、`44 55 66`、`12 34 56`；提示字符串和加密目标不会直接出现在 `strings` 中。flag 加密是简单的凯撒密码，字母移动 7 位。
> 
> 运行程序并输入 flag：
> 
> 

### 静态

![](/images/0xGame-Week1/QQ_1790666825334.png)

![](/images/0xGame-Week1/QQ_1790667196198.png)

1. `jz short near ptr loc_401112+1`：
这是一个非常经典的“**跳入指令中间**”技巧。它跳到了 `loc_401112+1`，也就是 `xchg ax, ax`（机器码 `66 90`）的第二个字节 `90` 处。`90` 在汇编里恰好是 `NOP`（空指令）。如果 IDA 傻一点，就会从 `401113` 开始反汇编，导致后面的代码全乱套。但 IDA 硬是识破了。

2. 第二处的 `jz` 和 `jnz` 同目标，为恒跳转花指令

![](/images/0xGame-Week1/QQ_1790667477478.png)

> 1. `push 0FDE9h` \+ `call SetConsoleOutputCP`
> 
>     - `0FDE9h` 就是十进制 `65001`，代表 UTF\-8 编码。这是为了让程序在控制台正确显示中文（如果有的话）。
> 
> 2. `push 0Ch` \+ `push offset unk_40F1A0` \+ `call sub_401000`
> 
>     - `0Ch` 是 `12`，表示字符串长度。
> 
>     - `unk_40F1A0` 是字符串的地址。
> 
>     - `sub_401000` 是一个自定义的打印函数（通常是对 `printf` 或 `fwrite` 的二次封装，用了指定长度来输出）。
> 
>     - 这一行的作用：打印提示语，告诉你“请输入密码/Flag”。
> 
> 3. `call __acrt_iob_func` \(参数 1\) \+ `call _fflush`
> 
>     - `__acrt_iob_func(1)` 获取 `stdout`（标准输出）。
> 
>     - `_fflush` 刷新输出缓冲区，确保刚刚的提示语能立刻显示在屏幕上，而不是卡在缓冲区里。
> 
> 4. `call __acrt_iob_func` \(参数 0\) \+ `push 80h` \+ `lea eax, [ebp-88h]` \+ `push eax` \+ `call _fgets`
> 
>     - `__acrt_iob_func(0)` 获取 `stdin`（标准输入）。
> 
>     - `80h` 是 `128`，表示最多读取 128 个字节。
> 
>     - `lea eax, [ebp-88h]` 把栈上一个局部变量的地址传给 `eax`。这就是接收用户输入的缓冲区（char buffer\[128\]）。
> 
>     - `_fgets` 就是读取键盘输入的步骤
> 
> 5. `test eax, eax` \+ `jnz short loc_401190`
> 
>     - `_fgets` 如果读取成功，会返回缓冲区的指针（非零）；如果遇到 EOF（比如按 Ctrl\+Z）或出错，会返回 NULL \(0\)。
> 
>     - `test eax, eax` 然后 `jnz`（非零跳转），意思是：如果输入成功，就跳到 `loc_401190` 去进行验证。如果失败，就往下走，打印错误信息（`0Ch` \+ `unk_40F1AC`）并退出。
> 
> 

![](/images/0xGame-Week1/QQ_1790667758271.png)

**这是一个典型的“获取有效输入长度”的循环。**

> 1. `mov dword ptr [ebp-4], 0`
> 
>     - 把栈上的一个局部变量赋值为 0。我们给它起个名字叫 `i`（计数器）。
> 
> 2. `loc_401197:`
> 
>     - 这是一个循环的起点。
> 
> 3. `mov ecx, [ebp-4]` \-\> `movsx edx, byte ptr [ebp+ecx-88h]`
> 
>     - 把 `i` 读取到 `ecx` 里，然后取出你输入字符串的第 `i` 个字符。
> 
>     - `[ebp-88h]` 正是之前 `fgets` 存放输入的起始地址。
> 
> 4. `test edx, edx` \-\> `jz short loc_4011D1`
> 
>     - 检查这个字符是不是 `0`（也就是字符串结束符 `\0`）。如果是，说明字符串到头了，跳出循环。
> 
> 5. `mov eax, [ebp-4]` \-\> `movsx ecx, byte ptr [ebp+eax-88h]` \-\> `cmp ecx, 0Dh` \-\> `jz short loc_4011D1`
> 
>     - 再次取出第 `i` 个字符，和 `0x0D`（也就是 回车符 `\r`）比较。如果相等，跳出循环。
> 
> 6. `mov edx, [ebp-4]` \-\> `movsx eax, byte ptr [ebp+edx-88h]` \-\> `cmp eax, 0Ah` \-\> `jz short loc_4011D1`
> 
>     - 再次取出第 `i` 个字符，和 `0x0A`（也就是 换行符 `\n`）比较。如果相等，跳出循环。
> 
> 7. `mov ecx, [ebp-4]` \-\> `add ecx, 1` \-\> `mov [ebp-4], ecx` \-\> `jmp short loc_401197`
> 
>     - 如果没有遇到 `\0`、`\r`、`\n`，就把 `i` 加 1，然后跳回循环开头继续比较下一个字符。
> 
> 

即计算输入字符串的长度，并且顺便去掉末尾的换行符。

![](/images/0xGame-Week1/QQ_1790668062978.png)

这个程序要求我们输入的密码长度必须正好是 47 个字符（0x2F）

```Assembly language
.text:004011D1 mov edx, [ebp-4]            ; 把刚才循环算出来的长度放进 edx
.text:004011D4 mov byte ptr [ebp+edx-88h], 0 ; 在字符串末尾补上 \0 结束符（C语言标准操作）
.text:004011DC cmp dword ptr [ebp-4], 2Fh  ; 将长度与 0x2F（十进制 47）比较
.text:004011E0 jnz loc_40126B              ; 如果长度不等于 47，跳转到失败分支（大概率是打印错误）
.text:004011E6 mov dword ptr [ebp-8], 0    ; 如果长度对了，初始化另一个变量（计数器 j = 0）
.text:004011ED jmp short loc_4011F8        ; 进入核心比较循环
```

![](/images/0xGame-Week1/QQ_1790668205167.png)

这是一个循环生成密码的过程：

```C
// 之前的代码：if (len == 47) { j = 0; }
// 现在的循环：
for (j = 0; j < 47; j++) {
    char temp = byte_40F170[j]; // 从全局数组取第 j 个字节
    temp = temp ^ 0x80;         // 与 0x80 进行异或运算
    expected_password[j] = temp; // 存入本地栈变量 [ebp-0B8h + j]
}
```

提取数组

![](/images/0xGame-Week1/QQ_1790668701432.png)

然后发现这个解密出来是乱码

```C
ida_chars = [
  0xB0, 0xE5, 0xCE, 0xE8, 0xF4, 0xEC, 0xFB, 0xC4, 0xF6, 0xC4, 
  0xDF, 0xC1, 0xEF, 0xB3, 0xDF, 0xED, 0xB1, 0xF6, 0xE4, 0xB3, 
  0xF9, 0xA4, 0xDF, 0xC0, 0xF9, 0xEC, 0xDF, 0xDA, 0xD6, 0xF6, 
  0xB0, 0xF6, 0xF6, 0xA0, 0xE9, 0xB3, 0xC0, 0xE2, 0xB7, 0xF0, 
  0xED, 0xE2, 0xF3, 0xF3, 0xA1, 0xA1, 0xFD
]

# 将每个字节与 0x80 异或，然后转为字符
flag = ''.join(chr(b ^ 0x80) for b in ida_chars)
print(flag)

```

0eNhtl\{DvD\_Ao3\_m1vd3y$\_@yl\_ZVv0vv i3@b7pmbss\!\!\}

一开始还以为静态不行 后来想起来是凯撒密码还得揭秘一次。

#### Exp

```Python
ida_chars = [
  176, 229, 206, 232, 244, 236, 251, 196, 246, 196, 
  223, 193, 239, 179, 223, 237, 177, 246, 228, 179, 
  249, 164, 223, 192, 249, 236, 223, 218, 214, 246, 
  176, 246, 246, 160, 233, 179, 192, 226, 183, 240, 
  237, 226, 243, 243, 161, 161, 253
]

# 1. 先剥异或层
step1 = ''.join(chr(b ^ 0x80) for b in ida_chars)
print(f"第一层结果: {step1}")

# 2. 再进行凯撒密码解密 (偏移 -7)
flag = ""
for c in step1:
    if 'a' <= c <= 'z':
        flag += chr((ord(c) - ord('a') - 7) % 26 + ord('a'))
    elif 'A' <= c <= 'Z':
        flag += chr((ord(c) - ord('A') - 7) % 26 + ord('A'))
    else:
        flag += c

print(f"最终 Flag: {flag}")
```

flag：0xGame\{WoW\_Th3\_f1ow3r$\_@re\_SOo0oo b3@u7ifull\!\!\}

### 动态调试

下断点 输入47个A

![](/images/0xGame-Week1/QQ_1790668971255.png)

寄存器值：

![](/images/0xGame-Week1/QQ_1790669006921.png)

#### 计算明文地址

##### EBP

当 CPU 执行到 `main` 函数时，会在这个函数的开头执行这三句：

```Python
push ebp        ; 保存上一个函数的“地基”
mov ebp, esp    ; 把当前栈顶（ESP）设为当前函数的“地基”（EBP）
sub esp, 0E8h   ; 抬高栈顶，为局部变量分配 0xE8 大小的空间
```

执行完这三句后，`EBP` 就成了 `main` 函数在这个内存区域里的**固定基准点**。
因为函数运行过程中，`ESP`（栈顶）会不停地进栈出栈（比如你按 F8 时看到的 push/pop），不停变化，所以我们需要一个固定的 `EBP` 来作为参照物，寻找局部变量。

##### EBP\-0xB8

在 `main` 函数栈帧里，所有的**局部变量都是相对于 **`EBP`** 向下（减去一个偏移量）存放的**。

- 你在 IDA 里双击过 `main` 的伪代码，也看过汇编。在汇编代码 `00401211` 那一行，写的是：
`mov [ebp+eax-0B8h], dl`

> `00401211` 这一行的汇编是 `mov [ebp+eax-0B8h], dl`，它属于循环里“**把解密后的字节写入内存**”的那条指令。
> 
> 

- 这里的 `eax` 是循环计数器（0 到 46）。当 `eax=0` 时，地址就是 `[ebp-0B8h]`。

- 所以，**`[ebp-0B8h]` 是编译器给存放“正确密码”这个局部数组分配的起始地址。这个 **`0xB8`**（十进制 184）是编译器算好的固定偏移量。**



当前程序断在 `0085121A` 时，寄存器显示：

- `EBP = 012FFE3C`

我们要找的地址是 `EBP - 0xB8`。来做个十六进制减法：

```Python
012FFE3C
- 000000B8
----------
  012FFD84
```

#### 跳转到明文地址

![](/images/0xGame-Week1/QQ_1790827880064.png)

得到明文：

```Python
012FFD84  30 65 4E 68 74 6C 7B 44 76 44 5F 41 6F 33 5F 6D  0eNhtl{DvD_Ao3_m  
012FFD94  31 76 64 33 79 24 5F 40 79 6C 5F 5A 56 76 30 76  1vd3y$_@yl_ZVv0v  
012FFDA4  76 20 69 33 40 62 37 70 6D 62 73 73 21 21 7D 00  v i3@b7pmbss!!}.  
```

凯撒密码 偏移\-7

得到flag：0xGame\{WoW\_Th3\_f1ow3r$\_@re\_SOo0oo b3@u7ifull\!\!\}

## 欸？云朵のrevenge

[attachment7\.zip](图片和附件/attachment7.zip)

![](/images/0xGame-Week1/QQ_1790838826420.png)

对比云朵那道题目的伪代码

```Plain Text
Source 里硬编码密文；
直接调用 sub_401620(Source, 26, "ShedaLight", 10)  // RC4 解密
```

```C
v12 = sub_401768();                  // 获取一个结构体指针
memcpy(Source, *(v12), *(v12+8));    // 从结构体拷贝密文到 Source，长度在 v12+8
sub_4018A2(Source, *(v12+8));        // 对密文做一次置换（自逆）
sub_401620(Source, *(v12+8), *(v12+16), *(v12+24)); // RC4 解密，密钥在 v12+16，密钥长度在 v12+24
```

### sub\_4018A2

```C
v6 = sub_4017EF(0, v7);
```

这个调用非常关键：

- 第一个参数是 `0`。

- 第二个参数是 `v7`，一个 `_BYTE v7[263]` 数组。



在 Windows 逆向中，这种形式极大概率是：

```C
srand(0);   *// 用种子 0 初始化随机数生成器*
```

而 `v7` 可能是随机数生成器的内部状态，或者是 `rand()` 使用的表。

`sub_4017EF` 很可能就是 `srand` 的封装，或者是一个自定义的随机数初始化函数，但**种子被硬编码为 0**。这就意味着：

> 每次程序运行，生成的随机数序列完全一样。
> 
> 



```C
for ( i = a2; ; ... )
{
    v3 = sub_40184D(&v6);        // 生成下一个随机数
    v4 = v3 % (i + 1);           // 取模，得到 0..i 的随机索引
    ...                          // 存到 v7 数组里
}
```

- `sub_40184D(&v6)` 看起来就是 `rand()` 或类似的随机数生成函数。

- `v3 % (i + 1)` 把随机数限制在 `0` 到 `i` 之间。

- 这个循环从 `i = a2` 递减到 `1`，每次生成一个随机索引，存入 `v7`。

这其实就是 **Fisher\-Yates 洗牌算法** 的变种：生成一个随机排列，用于打乱数组。

因为种子固定为 `0`，所以这个随机排列是确定的、可复现的。每次运行程序，`v7` 里的索引序列完全相同。



总结：

- `sub_4017EF(0, ...)` → 种子 0 初始化。

- `sub_40184D(...)` → 取随机数。

- `% (i + 1)` → 生成 0\.\.i 的索引。

- 交换字节 → 置换。

- 种子固定 → 每次序列相同。

- 交换对称 → 自逆。

### 错误混淆

#### sub\_401768

![](/images/0xGame-Week1/QQ_1790842644831.png)

我刚刚试了半天动态调试 到处乱飞 回静态函数一看有个反调试。。。

大家一定要先仔细看静态函数啊

> `IsDebuggerPresent()` 是 Windows 最经典、最基础的反调试 API。它的原理是检查当前进程的 PEB（进程环境块）里的 `BeingDebugged` 标志。
> 
> 当你在 x64dbg 里按下 F9 运行时，这个函数返回真，于是程序返回了 `&off_4050C0`（假数据）。这个假数据里面装的密文或密钥大概率是错的，或者是用来搞乱程序的。这直接导致：
> 
> 1. 解密出来的是一堆乱码。
> 
> 2. 后续调用 `DrawTextA` 或内存清理函数（`sub_401A43`、`sub_402060`）时发生内存访问冲突（也就是你截图里寄存器全变0、程序崩溃被回收的原因）。
> 
> 3. 系统库（如 `gdi32full`、`ntdll`）捕获到异常，疯狂在底层处理。
> 
> 

#### 数据处理

提取else分支的真数据

```C
unsigned char ida_chars[] =
{
   29,   0,   0,   0,   0,   0,   0,   0,  88,  80, 
   64,   0,   0,   0,   0,   0,  10,   0,   0,   0, 
    0,   0,   0,   0, 232,  80,  64,   0,   0,   0, 
    0,   0,   0,   0,   0,   0,   0,   0,   0,   0, 
    0,   0,   0,   0,   0,   0,   0,   0,   0,   0, 
    0,   0,   0,   0,   0,   0
};
```

我们在 64 位程序里，按 8 个字节一组来拆解数据：

（这些都是十进制数据，我们先将他们转为十六进制，然后再用小端序表示）

- 第 1 个 8 字节：`29, 0, 0, 0, 0, 0, 0, 0` \-\> 转为小端序是 `0x1D`，即 29。

    - 这是密文长度。结合 `sub_401B4B` 的伪代码，`*(v12 + 8)` 就是密文长度，所以这里应该是 29。

- 第 2 个 8 字节：`88, 80, 64, 0, 0, 0, 0, 0` \-\> 转为小端序是 `0x405058`。

    - 这是密钥指针。它指向真正存放密文的地址。

- 第 3 个 8 字节：`10, 0, 0, 0, 0, 0, 0, 0` \-\> 转为小端序是 `0x0A`，即 10。

    - 这是密钥长度。密钥长度是 10。

- 第 4 个 8 字节：`232, 80, 64, 0, 0, 0, 0, 0` \-\> 转为小端序是 `0x4050E8`。

    - 是密文指针。它指向存放密钥字符串的地址。

跳转提取密文和密钥：

![](/images/0xGame-Week1/QQ_1790844128894.png)

![](/images/0xGame-Week1/QQ_1790844168382.png)

![](/images/0xGame-Week1/QQ_1790844249754.png)

另一个函数依然是RC4

这样写出的脚本会~~很高兴地~~发现运行出来直接乱码了 

### 正确做法

问了一下AI ~~这道题居然是故意搞反了一下。何意味。？~~

AI原话：

> **出题人极其阴险**。他把真 flag（走 `if` 分支，`off_4050C0`）的嘲讽语 `NO! NO! NO!` 和密文、密钥放在同一个结构体里。
> 
> 

我只见过不让用动态调试的题目 没想到居然还有必须用动态调试的题目

回看函数401768

![](/images/0xGame-Week1/image.png)

正常题目一般都是反调试 即若有调试器附加 则`IsDebuggerPresent`返回1 即不让我们动态调试

这道题直接反过来 也就是假如我们不使用调试器 则进入错误的分支 即4050C0才是正确的数据位置。

因此我们提取数据应该去4050C0

```C
unsigned char ida_chars[] =
{
   31,   0,   0,   0,   0,   0,   0,   0,  72,  80, 
   64,   0,   0,   0,   0,   0,  10,   0,   0,   0, 
    0,   0,   0,   0, 173,  80,  64,   0,   0,   0, 
    0,   0,  78,  79, 239, 188, 129,  78,  79, 239, 
  188, 129,  78,  79, 239, 188, 129,  78,  79, 239, 
  188, 129,  78,  79, 239, 188, 129,  13,  10,   0
};
```



- 第 1 个 8 字节：`31, 0, 0, 0, 0, 0, 0, 0` \-\> 转为小端序是 `0x1F`，即 31。

    - 这是密文长度。结合 `sub_401B4B` 的伪代码，`*(v12 + 8)` 就是密文长度，所以这里应该是 31。

- 第 2 个 8 字节：`72, 80, 64, 0, 0, 0, 0, 0` \-\> 转为小端序是 `0x405048`。

    - 这是密钥指针。它指向 `0x405048` 地址，那里存放着字符串 `"0xGame2026"`。

![](/images/0xGame-Week1/QQ_1790848010689.png)

- 第 3 个 8 字节：`10, 0, 0, 0, 0, 0, 0, 0` \-\> 转为小端序是 `0x0A`，即 10。

    - 这是密钥长度。对应 `sub_401B4B` 伪代码里的 `*(v12 + 24)`，长度正好是 10。

- 第 4 个 8 字节：`173, 80, 64, 0, 0, 0, 0, 0` \-\> 转为小端序是 `0x4050AD`。

![](/images/0xGame-Week1/QQ_1790848114124.png)

这个并不是密文！只是msg提示！

- 第 5 个字段（从偏移 \+32 开始的连续字节）：`78, 79, 239, 188, 129...` 一直到末尾。

    - 转为十六进制：`4E 4F EF BC 81...`。

    - 这是内联的提示信息（`msg` 字符数组）。`4E` 是 'N'，`4F` 是 'O'，`EF BC 81` 是 UTF\-8 编码的全角感叹号 `！`。

    - 拼起来就是字符串：`"NO! NO! NO! NO! NO! \r\n"`。

    - 在 `sub_401B4B` 中，它被传给 `sub_401A43` 作为参数，用于弹出控制台信息或直接打印到窗口。

#### 密文

在c语言中 结构体通常这么定义

```C++
struct FlagInfo {
**    char *ct;       // 偏移 +0：密文指针**
**    size_t len;     // 偏移 +8：密文长度**
**    char *key;      // 偏移 +16：密钥指针**
**    size_t klen;    // 偏移 +24：密钥长度**
**    char *msg;      // 偏移 +32：提示信息指针**
};
```



回看函数`sub_401B4B`

```C
v12 = sub_401768();                              // v12 是结构体指针
memcpy(Source, *(const void **)v12, *(_QWORD *)(v12 + 8));
// 第一个参数：*(void**)v12      → 从 v12+0 取一个指针，作为源地址
// 第二个参数：*(QWORD*)(v12+8)  → 从 v12+8 取一个整数，作为长度
```

这说明结构体前两个字段是：

- 偏移 \+0：`char *ct`（密文指针）

- 偏移 \+8：`size_t len`（密文长度）



后面还有

```C
sub_401620(Source, *(_QWORD *)(v12 + 8), *(_QWORD *)(v12 + 16), *(_QWORD *)(v12 + 24));
```

所以：

- 偏移 \+16：`char *key`（密钥指针）

- 偏移 \+24：`size_t klen`（密钥长度）

- 偏移 \+32：`char *msg`（提示信息）

这是从代码调用约定反推出来的，不是猜的。



根据刚刚提取出的数据我们可以知道密文指针 从而知道密文数据

```Plain Text
0x4050B8  21 21 0D 0A 00 00 00 00  = 0x000000000A0D2121   ← 这是 "YOU GOT IT!!!\r\n" 的尾巴
0x4050C0  70 50 40 00 00 00 00 00  = 0x0000000000405070   ← ★ 就是它
0x4050C8  1F 00 00 00 00 00 00 00  = 31                   ← "第一个 8 字节 31"
```

![](/images/0xGame-Week1/QQ_1790848371560.png)

#### Exp

```Python
def fnv1a32(b):
    h = 0x811C9DC5
    for c in b:
        h = ((h ^ c) * 0x01000193) & 0xFFFFFFFF
    return h or 0xA341316C

class XorShift32:
    def __init__(self, seed):
        self.state = seed
    def next(self):
        x = self.state
        x ^= (x << 13) & 0xFFFFFFFF
        x ^= (x >> 17)
        x ^= (x << 5) & 0xFFFFFFFF
        self.state = x & 0xFFFFFFFF
        return self.state

def shuffle(buf):
    n = len(buf)
    rng = XorShift32(fnv1a32(b"ShedaLight"))
    arr = [0] * (n + 1)
    for i in range(n, 1, -1):
        arr[n - i] = rng.next() % i
    b = bytearray(buf)
    for k in range(n - 2, -1, -1):
        idx = n - 1 - k
        b[idx], b[arr[k]] = b[arr[k]], b[idx]
    return bytes(b)

def rc4(key, data):
    S = list(range(256))
    j = 0
    out = bytearray()
    for i in range(256):
        j = (j + S[i] + key[i % len(key)]) % 256
        S[i], S[j] = S[j], S[i]
    i = j = 0
    for char in data:
        i = (i + 1) % 256
        j = (j + S[i]) % 256
        S[i], S[j] = S[j], S[i]
        K = S[(S[i] + S[j]) % 256]
        out.append(char ^ K)
    return bytes(out)

# 密文
cipher_A = bytes.fromhex("79 CA F7 50 76 88 A1 5A 20 0D C1 FF 52 57 E2 E7 64 B5 AF E1 10 91 A5 83 FA ED 1A 5A DE 7F 41")
key_A = b"0xGame2026"

plain = rc4(key_A, shuffle(cipher_A))
print("最终 Flag:", plain.decode(errors='ignore'))
```

![](/images/0xGame-Week1/QQ_1790848572357.png)

flag：0xGame\{Dyn4m1c\_Dyn4m1c\_Dyn4m1c\}
