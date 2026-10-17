+++
title = 'Moectf 2026 -1'
date = '2026-09-12T12:00:00+08:00'
draft = false
summary = ''
tags = []
showtoc = true
+++

## Moectf wp

![97bce42f957d2d5abd46891ce45e9198\.png](/images/moectf-2026-1/97bce42f957d2d5abd46891ce45e9198.png)

### 入门指北

这个指北好帅！

![QQ\_1786975910499\.png](/images/moectf-2026-1/QQ_1786975910499.png)

给新手玩的 有一点鸡肋 但是这个教学挺不错

![75de6a71f2c2c18cf43724dca78d521e\.png](/images/moectf-2026-1/75de6a71f2c2c18cf43724dca78d521e.png)

![59b6caece1e9d1509544504ed42e201e\.png](/images/moectf-2026-1/59b6caece1e9d1509544504ed42e201e.png)

### **Assembly**

flag:moectf\{Assemb1y\_L4nguage\_1S\_co0o0Oool\!\!\}

```Assembly language
; x86-64, Intel syntax
; rdi points to output buffer

start:
    lea     rdi, [buf]

    lea     rsi, [byte_404000]
    mov     ecx, 25

loc_401000:
    mov     al, byte ptr [rsi]
    mov     byte ptr [rdi], al
    inc     rsi
    inc     rdi
    loop    loc_401000

    mov     eax, 0x2a
    add     eax, 0x16
    cmp     eax, 0x40
    jne     loc_401080

    mov     ebx, 0x10
    shl     ebx, 2
    cmp     eax, ebx
    jne     loc_401080

    mov     ecx, 0x39
    sub     ecx, 0x20
    cmp     ecx, 0x18
    jg      loc_401050

    jmp     loc_401080

loc_401050:
    lea     rsi, [byte_404020]
    mov     ecx, 15

loc_401060:
    mov     al, byte ptr [rsi]
    xor     al, 0x42
    mov     byte ptr [rdi], al
    inc     rsi
    inc     rdi
    loop    loc_401060

    jmp     loc_4010b0

loc_401080:
    lea     rsi, [byte_404030]
    mov     ecx, 9

loc_401090:
    mov     al, byte ptr [rsi]
    mov     byte ptr [rdi], al
    inc     rsi
    inc     rdi
    loop    loc_401090

loc_4010b0:
    mov     byte ptr [rdi], 0
    ret


byte_404000:
    db 0x6d, 0x6f, 0x65, 0x63, 0x74, 0x66, 0x7b
    db 0x41, 0x73, 0x73, 0x65, 0x6d, 0x62, 0x31, 0x79
    db 0x5f, 0x4c, 0x34, 0x6e, 0x67, 0x75, 0x61, 0x67, 0x65, 0x5f

byte_404020:
    db 0x73, 0x11, 0x1d, 0x21, 0x2d
    db 0x72, 0x2d, 0x72, 0x0d, 0x2d
    db 0x2d, 0x2e, 0x63, 0x63, 0x3f

byte_404030:
    db 0x63, 0x6f, 0x72, 0x72, 0x65, 0x63, 0x74, 0x21, 0x7d

buf:
    db 64 dup(0)
```

手动读这段汇编语言 找出flag

完了 这下不能用ida反汇编了看得很吃力



第一段数据

```Assembly language
byte_404000:
    db 0x6d, 0x6f, 0x65, 0x63, 0x74, 0x66, 0x7b
    db 0x41, 0x73, 0x73, 0x65, 0x6d, 0x62, 0x31, 0x79, 0x5f
    db 0x4c, 0x34, 0x6e, 0x67, 0x75, 0x61, 0x67, 0x65, 0x5f
```

转成ASCII

```Assembly language
moectf{Assemb1y_L4nguage_
```



第二段数据

与0x42异或之后写入

```Assembly language
byte_404030:
    db 0x63, 0x6f, 0x72, 0x72, 0x65, 0x63, 0x74, 0x21, 0x7d
```



第三段数据 ASCII

```Assembly language
correct!}
```



独立看汇编语言的能力不太行 后面在学习中会补足

判断走哪一条分支

![3081ae17df0464cd612b23dbc218ee69\.png](/images/moectf-2026-1/3081ae17df0464cd612b23dbc218ee69.png)

第二段数据异或之后

```Assembly language
1S_co0o0Oool!!}
```

拼接得到最终flag

#### sub

减法

```Assembly language
sub     ecx, 0x20
```

- `ecx = ecx - 0x20`

- 前面 `mov ecx, 0x39` 让 `ecx = 57`，减 `32` 得 `25`（`0x19`）

#### shl

左移

```Assembly language
shl     ebx, 2
```

- `ebx = ebx << 2`，也就是乘以 4

- 前面 `mov ebx, 0x10` 让 `ebx = 16`，左移 2 位变成 `64`（`0x40`）



- 左移（SHL） = 乘以 2 的 n 次方（`× 2ⁿ`）

- 右移（SHR） = 除以 2 的 n 次方（`÷ 2ⁿ`，整数除法，向下取整）

#### loop

循环

```Assembly language
loop    loc_401000
```

- 执行 `loop` 时，先执行 `ecx = ecx - 1`

- 如果 `ecx != 0`，就跳转到 `loc_401000` 继续循环

- 如果 `ecx == 0`，就不跳转，继续往下执行

- 所以它相当于 C 语言的：

```C
for (int ecx = 25; ecx != 0; ecx--) {
    // 循环体
}
```

#### inc

自增1

```Assembly language
inc     rsi
inc     rdi
```

- `inc rsi` → `rsi = rsi + 1`

- 作用就是让指针向后移动一个字节，指向下一个数据。

### bbxor

入门xor

flag:moectf\{B4sic\_x0r\_cha1lenge\_solved\!\!\}

### 反方向的rc4

flag:moectf\{OH\~Dyn4mic\!\}

入门rc4

![545548fceebd493228894d11b2a25926\.png](/images/moectf-2026-1/545548fceebd493228894d11b2a25926.png)

![QQ\_1787048364697\.png](/images/moectf-2026-1/QQ_1787048364697.png)

g\_cipher

```C
unsigned char g_cipher[] =
{
  178, 36, 36, 3, 227, 180, 65, 98, 17, 243, 
  138, 40, 160, 113, 155, 190, 39, 70, 25, 169
};
```

### **Ultra Potato Xplosion**

flag:moectf\{EaSy\_UPX\_anD\_Base58\}

加壳 脱壳  这是一个 ELF64 文件，目标操作系统是 Linux（ABI 3\.2\.0）

![QQ\_1787126747564\.png](/images/moectf-2026-1/QQ_1787126747564.png)

![00a2127913534d3a85a4179c3cfaf5cd\.png](/images/moectf-2026-1/00a2127913534d3a85a4179c3cfaf5cd.png)

```C
n = 0;
  strcpy(v5, "Fnrr68qUFDSTA5tupNAp8pgrFPJNesF3R6KNk");
  printf("Input flag: ");
  if ( fgets(s, 128, stdin) )
  {
    s[strcspn(s, "\n")] = 0;
    if ( (unsigned int)sub_401216(v5, **s2**, 128, &n) )
    {
      puts("Internal error!");
      return 0;
    }
    else
    {
      v4 = strlen(s);
      if ( v4 == n && !memcmp(s, **s2**, n) )
        puts("Correct!");
      else
        puts("Wrong!");
      return 0;
    }
  }
  else
  {
    puts("Wrong!");
    return 0;
  }
```

> `memcmp` 是 C 语言标准库里的内存比较函数  比较 `s`（你输入的字符串）和 `s2`（sub\_401216 生成的结果）的前 `n` 个字节是否相同。
> 
> 

#### 静态

主要逻辑在sub\_401216里 发现是base58

放到cyberchef里面一把梭

### 奇怪的APP

flag:moectf\{Apk\_REv3rse\_1s\_fuN\_r1ghT?\!\!\!\}

apk文件 考察安卓类题目

**把 APK 当成 ZIP 解包**

APK 本质就是 ZIP，可以直接解压看原始内容：

```Bash
mkdir unpacked && unzip app.apk -d unpacked
```

得到 7 个文件：

text

```Plain Text
META-INF/MANIFEST.MF      ← APK 签名相关
META-INF/CTFKEY.SF
META-INF/CTFKEY.RSA
AndroidManifest.xml       ← 注意:这是二进制格式,直接看不了
classes.dex               ← 700 字节,极小
res/values/strings.xml    ← 字符串资源
assets/config.json        ← 应用配置
```

> 关键观察： 一个 4KB 的 APK，只有一个 `classes.dex`、一个 XML 资源、一个 JSON 配置。没有任何 native so、没有任何图片资源。出题人没地方藏东西，flag 必然就散落在这几个文件里。
> 
> 



![QQ\_1787135382217\.png](/images/moectf-2026-1/QQ_1787135382217.png)

4 段 base64，散布在 APK 4 个不同位置，识别后顺序拼接：

### **请你喝茶**

![56f100f3a75177a037b64535dc4770e6\.png](/images/moectf-2026-1/56f100f3a75177a037b64535dc4770e6.png)

![86a75a54de89dad2b83ea68f6cfe6d10\.png](/images/moectf-2026-1/86a75a54de89dad2b83ea68f6cfe6d10.png)

这个比赛特别适合初学者啊 甚至准备了一个解密脚本

```C
unsigned char tea_key[] =
{
  0x78, 0x56, 0x34, 0x12, 0x21, 0x43, 0x65, 0x87, 0x68, 0x24, 
  0x57, 0x13, 0x57, 0x13, 0x68, 0x24
};

unsigned char xtea_key[] =
{
  0xEF, 0xBE, 0xAD, 0xDE, 0xBE, 0xBA, 0xFE, 0xCA, 0x44, 0x33, 
  0x22, 0x11, 0x88, 0x77, 0x66, 0x55
};
```

![deb2e7b750f5dfa071a2c0945f267164\.png](/images/moectf-2026-1/deb2e7b750f5dfa071a2c0945f267164.png)

![658fb027107f3ecd94b6638b0b568c9d\.png](/images/moectf-2026-1/658fb027107f3ecd94b6638b0b568c9d.png)

tea和xtea的算法结合 组成flag

之前tea之类的算法都是直接套脚本的 也是第一次半手搓了 感觉手搓能了解的更深刻一些

```C
#include <stdio.h>
/**
 * @brief 这是一个简短的 TEA 解密指南，依据 IDA 反编译的结果，
 *        正确填充代码中的空缺处，运行后就可以获得 flag！
 * 
 * @attention 请先移步 main 函数，阅读此题拆解！
 */

#define uint unsigned int

/**
 * @brief TEA 解密一个 64 位数据块
 *
 * @param cipher 待解密数据（2×32 bit）
 * @param key    128 位密钥（4×32 bit）
 * @param delta  常量值
 */
void tea_decrypt(uint cipher[2], uint key[4])
{
    /**
     * @brief 解密是加密的逆过程。如果我们已知最终的密文，
     *        并可以通过某种方式恢复上一轮的状态，
     *        那么一直恢复到最初状态，就可以得到明文。
     *        在此例中，加密的逻辑是这样的：
     *     -> 先将 delta 减去 1640531527（或为加上 0x9E3779B9）
     *     -> 更新 cipher[0]
     *     -> 更新 cipher[1]
     *     -> 重复以上操作，循环 32 次
     *        由于更新某一个数据时，另外两个数据和密钥的值都是固定的，
     *        于是在解密时，我们只需要：
     *     -> 反向更新 cipher[1]
     *     -> 反向更新 cipher[0]
     *     -> 将 delta 加上 1640531527（或为减去 0x9E3779B9）
     *     -> 重复以上操作，循环 32 次
     * 
     * @attention 根据 IDA 反编译展示的逻辑，修改下面代码中填 0x0 的部分。 
     */
    uint delta = -1640531527 * 32;

    for(int i = 1; i <= 32; i++)
    {
        cipher[1] -= (cipher[0] + delta) ^ (16 * cipher[0] + key[2]) ^ ((cipher[0]>>5) + key[3]);
        cipher[0] -= (cipher[1] + delta) ^ (16 * cipher[1] + key[0]) ^ ((cipher[1]>>5) + key[1]);
        delta += 1640531527;
    }
}

/**
 * @brief XTEA 解密一个 64 位数据块
 *
 * @param cipher 待解密数据（2×32 bit）
 * @param key    128 位密钥（4×32 bit）
 * @param delta  常量值
 */
void xtea_decrypt(uint cipher[2], uint key[4])
{
    /**
     * @brief 这里的反编译可能会出现 *(_DWORD *)。
     *        不用害怕，以 (4LL * (v4 & 3) + xtea_key_address) 为例，
     *        由于 uint 的存储空间为 4 字节，乘上几个 4 就代表偏移量是几。
     * 
     * @attention 根据 IDA 反编译的结果，修改下面代码中填 0x0 的部分。
     */
    uint delta = -1640531527 * 32;

    for(int i = 1; i <= 32; i++)
    {
        cipher[1] -= (((cipher[0] >> 5) ^ (16 * cipher[0])) + cipher[0]) ^ (key[(delta >> 11) & 3] + delta);
        delta += 1640531527;
        cipher[0] -= (((cipher[1] >> 5) ^ (16 * cipher[1])) + cipher[1]) ^ (key[delta & 3] + delta);
    }
}

int main()
{
    /**
     * @brief 你看懂 main 函数的逻辑了吗？
     *        本题分为两个加密部分：
     *        第一，tea_encrypt 函数对 flag 前 16 字节进行加密。
     *        第二，xtea_encrypt 函数对 flag 后 16 字节进行加密。
     *        密文分别存储在 tea_cipher 和 xtea_cipher 中。
     * 
     * @attention 让我们先来解密 tea_encrypt 部分！
     *            请双击 check_tea_part 函数，找到这部分的密文以及密钥。
     */

     /**
      * @brief 密文数组由 4 个 32 位无符号整数构成。
      * 
      * @attention 双击 tea_cipher，填充以下数据！我已经帮你填好一个了。
      */
    uint cipher1[4] = {
        0xB3E7E33E,
        0xB4114672,
        0x8E088C0C,
        0x14B2C329
    };
    /**
     * @brief 密钥数组同样由 4 个 32 位无符号整数构成。
     *        双击 get_tea_key_address，再双击 tea_key，填充...
     *        等一下，我的 32 位整数呢？！实际上，呈现在你面前的 16 字节，
     *        是密钥数组在内存中原始的存储形式。按每四个字节划分，
     *        就可以得到 4 个密钥。那么，第一个密钥是 0x78563412 吗？
     *        并不是！x86-64 机器一般采用小端序存储。记住一点：
     *        低位字节存储在低地址，高位字节存储在高地址。因此，
     *        第一个密钥应该是 0x12345678。
     * 
     * @attention 完成剩下的填充！
     */
    uint key1[4] = {
        0x12345678,
        0x87654321,
        0x13572468,
        0x24681357
    };
    /**
     * @brief 加密算法 TEA 要求加密密钥为 128 比特，密文块分组长度为 64 比特。
     *        这里密文长度为 128 比特，因此要分为两个块分别加密。
     * 
     * @attention 请移步 tea_decrypt 函数，完成解密逻辑编写！
     */
    tea_decrypt(cipher1, key1);
    tea_decrypt(cipher1 + 2, key1);

    /**
     * @brief 祝贺你成功完成第一部分的解密！第二部分是 xtea 解密，
     *        整体思路和 tea 差不多，不过在加密流程中有些许出入。
     * 
     * @attention 填充对应密文。
     */
    uint cipher2[4] = {
        0x60EC68AB,
        0x940251CE,
        0xB427534C,
        0xDF435416
    };
    /**
     * @attention 填充对应密钥。注意：别忘记小端序！
     */
    uint key2[4] = {
        0xDEADBEEF,
        0xCAFEBABE,
        0x11223344,
        0x55667788
    };
    /**
     * @attention 移步 xtea_decrypt，继续完成解密逻辑编写。
     */
    xtea_decrypt(cipher2, key2);
    xtea_decrypt(cipher2 + 2, key2);
    /**
     * @attention 补全所有部分后，运行程序。如果解密正确，就能看到输出的 flag 啦！
     */
    printf("%.16s%.16s\n", (char *)cipher1, (char *)cipher2);

    return 0;
}
```

### 让我们说中文

flag:moectf\{Spe4K\_e@$y\_W07ds\}

![47020bc3814b43c924b996caeb2a7c80\.png](/images/moectf-2026-1/47020bc3814b43c924b996caeb2a7c80.png)

一开始以为是两次base64解密（然后解出一坨乱码）

> 以为是「两次 base64 解码」,**实际是「一次字符替换 \+ 一次 base64 解码」。两者的查表形式上像,但语义不同 —— 字符替换是位置映射,base64 解码是 6\-bit 还原字节。**
> 
> 

#### 区分解码和字符替换

![2557b31d36269dbd8a9e2700545c364a\.png](/images/moectf-2026-1/2557b31d36269dbd8a9e2700545c364a.png)

![c318f5b1c4b2a0ccee9748d4b902b461\.png](/images/moectf-2026-1/c318f5b1c4b2a0ccee9748d4b902b461.png)

![86a6af561c6e0e86926260895a5f6699\.png](/images/moectf-2026-1/86a6af561c6e0e86926260895a5f6699.png)

![3746fd8262cd81934251a3b0ae54c82f\.png](/images/moectf-2026-1/3746fd8262cd81934251a3b0ae54c82f.png)

程序做的事\(正向\):

1. 把你输入的字符串 → 标准 base64 编码 → 一串 base64 字符\(用 ABCDEFG\.\.\. 这套\)

2. 把这串 base64 字符 → 逐字查"乱序表" → 同位置的"标准表"字符替换

3. 跟它存的 target 比

解题步骤

**第 ① 步:字符替换\(乱序表 → 标准表\)**

target 是用乱序表字符写的,我们把它"翻译"回标准 base64 字符:

```Python
# 对 target 里每个字符 c:
#   1. 在乱序表里找到 c 的位置 i
#   2. 用标准表位置 i 的字符替换
rev = "".join(标准表[乱序表.index(c)] for c in target)
```

比如 target 第一个字符 `K`,它在乱序表里第 31 个 → 标准表第 31 个是 `R` → 替换成 `R`。

**第 ② 步:标准 base64 解码**

```Python
import base64raw = base64.b64decode(rev)
```

这一步把"标准 base64 字符串"解回原始字节。

**第 ③ 步:hex 解码出中文**

raw 拿出来一看是 390 个字符,全是 `[0-9a-f]` → 是个 hex 字符串 → 还原成中文:

```Python
cn = bytes.fromhex(raw.decode("ascii")).decode("utf-8")
```



```Plain Text
爱慕欧裔吸踢爱抚 左括号 大写 艾斯 小写 辟 小写 役 数字 四 大写 克诶 下划线 小写 役 艾特 美元 小写 外 下划线 大写 达不溜 数字 零 数字 七 小写 地 小写 艾斯 右括号
 m  o e c t f    {        S        p      e       4      K       _       e    @    $     y     _          W      0      7        d      s       }
```

#### base64的原理

Base64 就是把“二进制数据”转成“文本”，只使用 64 个安全字符（`A-Z a-z 0-9 + /`）。

想象成：

> 把原始数据（字节流）重新“打包”成 6 位一组（因为 2^6=64），然后去查表换成字符。
> 
> 

- 输入：3 个字节（24 位）

- 输出：4 个 Base64 字符（4 × 6 = 24 位）

- 如果字节数不是 3 的倍数，末尾用 `=` 补齐。

### 请fanchai喝茶  \-\-？



```Python
delta = 1597463007   # 0x5F3759DF
target = 1492265175  # 0x58F70097
mod = 1 << 32

v = 0
for r in range(1, 1000000):  # 通常不会太大
    v = (v + delta) % mod
    if v == target:
        print(f"循环次数: {r}")
        break
else:
    print("未找到，可能目标值不对或轮数过大")
```

循环次数：9











### Memtype★★★（\.py）

flag:moectf\{l@mbd4\_c@lcu1us\_4r3\_h4rd\_but\_z3\_s0lv3r\_1s\_3asy\}

**py题目**

附件就一个 Python 文件 `challenge.py`，整个文件只有一行，5604 个字符长，内容清一色是 `lambda`：

```Python
exit(1 - (lambda myk43: (lambda myk7: lambda vol8: lambda myk9: myk7(vol8)(myk9))((lambda myk17: (lambda myk3: lambda vol4: myk3) if myk17 else lambda myk5: lambda vol6: vol6)(len(myk43) == 54))(lambda: (lambda myk13: ...
```

看到这种特征 = **典型的 Lambda Calculus 混淆**，CTF 入门常见套路。看到 `lambda myk43:` `lambda vol8:` 这种乱码变量名、层层嵌套就基本能确认。

#### 准备工作

Python

##### Venv\-\-Python虚拟环境

作用：把每个项目的依赖分离，不污染系统python

```Bash
# 创建虚拟环境
python3 -m venv venv

# 激活（不同平台命令不同）
# Linux/macOS:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# 激活后命令行会多一个 (venv) 前缀
# 这时候 pip install 才不会报警告
```

##### Black\-\-代码格式化工具

将一整行字符的lamba展开为多行代码

```Bash
**# 先激活 venv（重要！）**
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple black  #安装black
```

```Bash
black challenge.py
```

![dfa646462066e627df4028bc0cf784aa\.png](/images/moectf-2026-1/dfa646462066e627df4028bc0cf784aa.png)

##### Z3\-solver  SMT约束求解器

```Bash
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple z3-solver  #安装
```

用法：

```Python
from z3 import BitVec, Solver, sat

x = BitVec('x', 32)  # 32 位无符号整数
s = Solver()
s.add(x >= 0, x <= 100)
s.add(x * x == 64)    # x² = 64

if s.check() == sat:
    print(s.model())  # 解
```



文本编辑器\-\-IDE

比如VScode pycharm

#### 解题步骤

**step1：将challenge\.py复制到工作区**

```Bash
mkdir -p ~/ctf_lambda
cp challenge.py ~/ctf_lambda/
cd ~/ctf_lambda
```

作用：将原文件备份好

**step2：格式化代码**

```Bash
source venv/bin/activate
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple black
black challenge.py
```

**step3：识别Church Encoding**

> Church Encoding 是把逻辑值，if\-else，数字，pair等都用纯lambda表示。这是函数式编程的技巧，但放在re里就是纯粹的混淆。
> 
> 比如：
> 
> 数字  正常：5是一个整数。
> 
> church：数字n是一个函数，作用是把某个函数重复执行n次。
> 
> 因此当我们看到代码里某个函数被嵌套调用了5次，就代表数字5。
> 
> 

但是在汇编（x86/ARM）层面，根本就没有函数作为参数这种概念。编译器或混淆器为了实现这种逻辑，会把上面的东西编译成乱七八糟的形态：

1. 到处都是“间接跳转”（call rax / call rbx）

正常的 if\-else 编译出来是 cmp \+ je（条件跳转），一眼能看清分支。

Church 编码的 if 编译出来是 通过寄存器去调用函数指针。

在 IDA 里，会看到大量 call rax，但 rax 的值在静态分析时根本算不出来，控制流图全是断开的虚线，F5 伪代码直接炸掉。

2. 数字常量消失了

你在汇编里找 mov eax, 0x66 这种异或密钥？找不到！

因为 5 被编译成了一段循环 5 次的代码块。你必须动态跑起来，数一数循环执行了几次，才能知道这个“数字”是多少。

3. 数据变成了代码，代码变成了数据

你会发现堆栈上全是函数地址，而不是具体的数值。如果在 IDA 里看数据段，以为看到的是“密文”，实际上那可能是“函数指针表”，解密逻辑被藏在了这些指针的调用顺序里，极其难以跟踪。



格式化后看到这些模式就是church encoding（丘奇编码）

```Python
# Church True  = lambda a: lambda b: a
# Church False = lambda a: lambda b: b
(lambda myk3: lambda vol4: myk3)   # True
(lambda myk5: lambda vol6: vol6)   # False

# Church If = lambda c: lambda t: lambda e: c(t)(e)
(lambda myk7: lambda vol8: lambda myk9: myk7(vol8)(myk9))
```

**step4：识别 ****`Y Combinator`****（递归）**

```Python
(lambda myk13: lambda vol14: myk13(vol14)(myk13))(
    (lambda vol0: (lambda myk1: myk1(myk1))(lambda vol2: vol0(lambda *a: vol2(vol2)(*a))))(
        lambda myk39: ...
    )
)
```

这是 Z Combinator（严格求值的Y Combinator）

作用是把一个会调用直接的lambda变成可递归的函数

**step5：识别5类约束**

通读代码，找到这5类约束：

约束1：长度

```Python
len(myk43) == 54
```

约束2：字符ASCII累加

```Python
ord(vol28[myk29]) + myk27(vol28)(myk29 + 1)  #递归求和
== 5138
```

即sum\(ord\(s\[i\]\) for i\) ==5138

约束3：所有字符 ASCII 异或

```Python
ord(vol31[vol32]) ^ vol30(vol31)(vol32 + 1)  # 递归异或
== 26
```

约束 4：字符 ASCII 平方和

```Python
ord(vol34[vol35]) * ord(vol34[vol35]) + myk33(vol34)(vol35 + 1)== 520600
```

约束 5：相邻字符乘积和

```Python
ord(vol37[vol38]) * ord(vol37[vol38 + 1]) + vol36(vol37)(vol38 + 1)== 467644
```

即 `sum(ord(s[i]) * ord(s[i+1]) for i=0..52) == 467644`

约束 6：53 个多项式（核心！）

递归函数每次 `idx` 加 1，按 `idx % 3` 三种模式：

```Python
# 模式 0 (idx=0, 3, 6, ..., 51):
# c1 + c2 + c3² = targets[idx] ^ 90
# c1=ord(s[idx]), c2=ord(s[idx+1]), c3=ord(s[(idx+17) % 54])

# 模式 1 (idx=1, 4, 7, ..., 52):
# c1 * c2 + c3 = targets[idx] ^ 90

# 模式 2 (idx=2, 5, 8, ..., 50):
# c1² + c2² + c3³ = targets[idx] ^ 90
```

> 提取 target 的小技巧：用 `grep -E '[0-9]{5,7}' challenge.py` 找出所有 5\+ 位数字，或者直接用 ast 找大整数元组。
> 
> 

**Step 6：用 z3 BitVec 求解**

把上面的约束用 z3 写出来（注意用 BitVec 不要用 Int——非线性约束下 BitVec 快几百倍）：



最终脚本

```Python
TARGETS = (10111, 11290, 137705, 13834, 12017, 882822, 2861, 6952, 148686,
           9290, 9962, 153274, 13069, 9595, 871218, 9834, 10851, 1584472,
           9149, 5765, 159511, 9289, 5093, 126222, 11887, 4921, 152566,
           13114, 6109, 140607, 13366, 9447, 156018, 9712, 11045, 1795540,
           15852, 4864, 1389923, 10278, 5369, 1586542, 10519, 5995, 1281695,
           4298, 5674, 963368, 10232, 5085, 880083, 10095, 15119)
N = 54
W = 16  # 每个字符 8 位，乘积需要 16 位
solver = Solver()
# 用 32 位整数存乘积
chars32 = [BitVec(f"c{i}", 32) for i in range(N)]
# 字符范围
for c in chars32:
    solver.add(c >= 32)
    solver.add(c <= 126)
# 约束
total = BitVecVal(0, 32)
for c in chars32:
    total = total + c
solver.add(total == 5138)
total_sq = BitVecVal(0, 32)
for c in chars32:
    total_sq = total_sq + c * c
solver.add(total_sq == 520600)
total_pair = BitVecVal(0, 32)
for i in range(N-1):
    total_pair = total_pair + chars32[i] * chars32[i+1]
solver.add(total_pair == 467644)
# 53 个多项式约束
for idx in range(53):
    c1 = chars32[idx]
    c2 = chars32[idx + 1]
    c3 = chars32[(idx + 17) % N]
    target = TARGETS[idx] ^ 90
    mode = idx % 3
    if mode == 0:
        solver.add(c1 + c2 + c3 * c3 == target)
    elif mode == 1:
        solver.add(c1 * c2 + c3 == target)
    else:
        solver.add(c1 * c1 + c2 * c2 + c3 * c3 * c3 == target)
print("BitVec 求解中...")
result = solver.check()
print(f"结果: {result}")
if result == sat:
    m = solver.model()
    flag = "".join(chr(m[c].as_long()) for c in chars32)
    print(f"\nflag = {flag}")
    import subprocess
    p = subprocess.run(
        ["python3", "/workspace/ctf_lambda/challenge.py"],
        input=flag + "\n",
        capture_output=True, text=True, timeout=5
    )
    print(f"原程序退出码: {p.returncode}")
    if p.returncode == 0:
        print("✅ 验证通过！")
else:
    print("无解")
```

### Tell Me No Lies

![7c93b6d14503afe588cea5fc0864d5f9\.png](/images/moectf-2026-1/7c93b6d14503afe588cea5fc0864d5f9.png)

看起来考察的应该是反调试

**整体的流程是：**

```Python
1. 检查调试器（IsDebuggerPresent）    → 如果有就退出
2. build_required_token(s)          // 生成一个参考 token 存到 s
3. v8 = acquire_operator_token()    // 获取实际 token（可能从系统读取）
4. compare_operator_token(v8, s)    // 比较两个 token，不等则退出
5. self_driven_decrypt(0, 0, v4)    // 解密得到 flag，输出 v4
```

因为我的反调试还没有学清楚 因此我们先试试能不能绕过不调试

先查看这个函数

```Python
__int64 __fastcall **build_required_token**(__int64 a1)
{
  unsigned __int64 i; // [rsp+10h] [rbp-8h]

  for ( i = 0; i <= 0x13; ++i )
    *(_BYTE *)(a1 + i) = *(_BYTE *)(i + 4203008) ^ 0x5A;
  *(_BYTE *)(a1 + 20) = 0;
  return a1 + 20;
}
```

![ec517b19f32cac9afb7d96a3481ebc95\.png](/images/moectf-2026-1/ec517b19f32cac9afb7d96a3481ebc95.png)

![dd0ae21b1f020bb2d7ba41aae5dce746\.png](/images/moectf-2026-1/dd0ae21b1f020bb2d7ba41aae5dce746.png)

> 所以结论是：
> 程序在数据段里预先存了 20 个“密文字节”（地址从 `0x402200` 开始），`build_required_token` 把它们逐一读出来，异或 `0x5A`，写入缓冲区 `s`。
> 
> 

我们静态算出了 `build_required_token` 生成的预期 token：

```Plain Text
MOE-LEVEL-7-OPERATOR
```

```C++
const char *acquire_operator_token()
{
  if ( (getpid() & 1) != 0 )
    return "MOE-LEVEL-1-GUEST";
  else
    return "MOE-LEVEL-3-TECH";
}
```

1. `build_required_token` 返回：`"MOE-LEVEL-7-OPERATOR"`

2. `acquire_operator_token` 的逻辑：

    - 调用 `getpid()` 获取当前进程的 PID（进程 ID）。

    - 如果 PID 是奇数（`& 1 != 0`），返回 `"MOE-LEVEL-1-GUEST"`。

    - 如果 PID 是偶数（`& 1 == 0`），返回 `"MOE-LEVEL-3-TECH"`。

3. 比较：
`"MOE-LEVEL-1-GUEST"` 或 `"MOE-LEVEL-3-TECH"` 与 `"MOE-LEVEL-7-OPERATOR"` 比较。

    - 不管你的 PID 是奇数还是偶数，两者永远不相等（因为 `1`、`3` 跟 `7` 不同，字符串整体不同）。

> 结论：
> `compare_operator_token` 永远返回非 0（表示不相等），程序必然进入：
> 
> ```C
> puts("[!] Operator token mismatch.");puts("[-] Recovery console terminated.");return 1;
> ```
> 
> 也就是说，如果不修改程序，任何人正常跑都拿不到 flag。
> 
> 

#### 静态patch

首先我们刚刚已经知道那个compare是无法完成的了

因此我们patch

将compare后汇编代码的jz改为jmp

然后apply

![QQ\_1787488300328\.png](/images/moectf-2026-1/QQ_1787488300328.png)

![c0c6cffea385833e206e8a52d6940310\.png](/images/moectf-2026-1/c0c6cffea385833e206e8a52d6940310.png)

![QQ\_1787488152481\.png](/images/moectf-2026-1/QQ_1787488152481.png)

```C
cd /mnt/c/Users/hp/Downloads/
```



```C
cd /mnt/c/Users/hp/Downloads/ && chmod +x chall10 && ./chall10
```

输出为：

![QQ\_1787488789406\.png](/images/moectf-2026-1/QQ_1787488789406.png)

艾玛 忘了还有解密函数了

![77210aa4c3c15bd138176b47648ce2e7\.png](/images/moectf-2026-1/77210aa4c3c15bd138176b47648ce2e7.png)

```C++
__int64 __fastcall self_driven_decrypt(unsigned int a1, unsigned int a2, __int64 *a3)
{
  // 局部变量：s 是一个结构体，包含 4 个 __int64，共 32 字节
  s = g_packed_flag;           // 全局硬编码的 32 字节密文（初始值）
  v8 = 0xC02861113754813LL;    // 第 2 个 8 字节
  v9 = 0xD70E8B5109ABB03DLL;   // 第 3 个
  v10 = 0x8858A04425BF416ALL;  // 第 4 个

  v11 = derive_root_seed(a1, a2);   // 根据 a1、a2 生成一个种子
  undo_permutation(&s, v11);
  rc4_transform(&s, 32, v11);
  xtea_cbc_decrypt(&s, v11);
  rolling_arx_decrypt(&s, v11);

  // 校验：检查解密后是否满足条件
  if ( HIBYTE(v10) || (unsigned int)fnv1a32(&s, 31) != 1932116973 )
  {
    memset(&s, 0, 0x20u);
    return 0;   // 失败
  }
  else
  {
    // 成功：把解密后的 32 字节存到 a3 指向的缓冲区
    *a3 = s;
    a3[1] = v8;
    a3[2] = v9;
    a3[3] = v10;
    memset(&s, 0, 0x20u);
    return 1;
  }
}
```

> ARX 是 Add\-Rotate\-Xor 的缩写，是一种常用的轻量级密码结构（比如 ChaCha20、Speck 都用它）。
> 
> 

![a5ae7f3d1a6fc134e41c3b0be4619425\.png](/images/moectf-2026-1/a5ae7f3d1a6fc134e41c3b0be4619425.png)

**`a2`**** 是主函数传进来的 ****`v6`****（即 ****`compare_operator_token`**** 的返回值）。**

> 返回值决定命运：0 是假，非 0 是真。
> 对 `main` 来说，`self_driven_decrypt` 返回 `0` → 它认为失败了；返回 `1` → 它认为成功了。
> 而 `compare_operator_token` 返回 `0` → 意味着“相等”；返回 `1` → 意味着“不等”。
> 我们让 `compare_operator_token` 永远返回 `0`，既骗过了 `main` 的 `if`，也给了 `derive_root_seed` 正确的钥匙。
> 
> 

a2试了很多种方法 一直报错

最后选择将调用函数的一行改掉

![83aba641b91c0a1ed7251ed08fb2c8b4\.png](/images/moectf-2026-1/83aba641b91c0a1ed7251ed08fb2c8b4.png)

![63cfef2016eb125f4e9c583a7f11173b\.png](/images/moectf-2026-1/63cfef2016eb125f4e9c583a7f11173b.png)

![6ca68160dee03b3450f69fe33f607f51\.png](/images/moectf-2026-1/6ca68160dee03b3450f69fe33f607f51.png)

![20c549adc00a8b22b189b1022bf84942\.png](/images/moectf-2026-1/20c549adc00a8b22b189b1022bf84942.png)

在WSL中运行 输出了flag

![QQ\_1787491048253\.png](/images/moectf-2026-1/QQ_1787491048253.png)

flag:moectf\{Wow\~h0w\_do\_Y0u\_f1nd\_IT?\}

### 广晨风语录

这道题的提示非常莫名其妙。？

> 我是广晨风，挑战 58\.3 元在 和平饭店 的购买力到底有多强
> 
> 还是推个车吧，怕拿不住
> 
> 今天我们主要买可乐和 Android Native 层
> 
> 58\.3 元买了一杯可乐 50 元，附加费 8\.3 元，可乐产生的热量全部用来打 moectf 花费 0 元
> 
> 购买力很强，爆赞！
> 
> 



问了ai

![QQ\_1787498601170\.png](/images/moectf-2026-1/QQ_1787498601170.png)

![QQ\_1787498633655\.png](/images/moectf-2026-1/QQ_1787498633655.png)

![QQ\_1787498640341\.png](/images/moectf-2026-1/QQ_1787498640341.png)



![4b7311cee46f24ff59ba6b6dbd662b6d\.png](/images/moectf-2026-1/4b7311cee46f24ff59ba6b6dbd662b6d.png)




## 学习笔记

### base58

```C++
memset(s, 0, 128u);
  v13 = strlen(a1);
  for ( i = 0; a1[i] == 49; ++i )
    ;
  for ( j = 0; j < v13; ++j )
  {
    v11 = strchr("123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz", a1[j]);
    if ( !v11 )
      return 0xFFFFFFFFLL;
    v19 = v11 - "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz";
    for ( k = 127; k >= 0; --k )
    {
      v10 = 58 * (unsigned __int8)s[k] + v19;
      s[k] = v10;
      v19 = v10 >> 8;
    }
    if ( v19 )
      return 0xFFFFFFFFLL;
  }
  for ( m = 0; m <= 0x7F && !s[m]; ++m )
    ;
  v12 = i - m + 128;
  if ( a3 < v12 )
    return 0xFFFFFFFFLL;
  v16 = 0;
  for ( n = 0; n < i; ++n )
  {
    v5 = v16++;
    *(_BYTE *)(a2 + v5) = 0;
  }
  for ( ii = m; ii <= 0x7F; ++ii )
  {
    v6 = v16++;
    *(_BYTE *)(v6 + a2) = s[ii];
  }
  *a4 = v12;
  return 0;
}
```

![image\.png](/images/moectf-2026-1/image.png)

### 安卓类题目

#### APK是什么

一句话：APK 就是一个 ZIP 包，里面按 Android 规范放了一堆文件。

```Plain Text
app.apk (本质是 ZIP)
├── **AndroidManifest.xml**    **二进制 XML。声明包名、组件（Activity/Service）、权限**
├── **classes.dex            Dalvik 字节码（Java 编译后的产物），可被 dex2jar/jadx 反编译**
├── classes2.dex           多 dex 项目会有（multidex）
├── resources.arsc         资源索引（字符串/图片/布局的元信息）
├── res/                   资源文件
│   ├── layout/            XML 布局
│   ├── **values/strings.xml 字符串常量**（**flag 高发区**）
│   ├── drawable/          图片
│   └── ...
├── **assets/ **               原始资源（不编译，直接打包）
│   ├── *.json             配置（**flag 高发区**）
│   ├── *.db               数据库
│   └── ...
├── lib/                   native 库（ARM/x86 的 .so 文件）
│   ├── arm64-v8a/
│   ├── armeabi-v7a/
│   └── x86/
└── META-INF/
    ├── MANIFEST.MF        签名清单
    ├── *.SF
    └── *.RSA / *.DSA      签名证书
```

做 CTF 题时，按这个顺序摸一遍：

1. `AndroidManifest.xml`（看权限、组件、入口）

2. `assets/`（配置、密钥、URL）

3. `res/values/strings.xml`（flag 高发区）

4. `classes.dex`（主要逻辑，jadx 看）

5. `lib/**/*.so`（native 层，中高难度才看）

#### Java基础。。。。

之前学web的时候有基础的了解











#### 做题流程

Step 1: 摸底

```Bash
ls -la app.apk                        # 尺寸 (KB 级 = 入门 / MB 级 = 复杂)
file app.apk
unzip -l app.apk                      # 看文件列表
```

Step 2: 解包

```Bash
mkdir unpacked && unzip app.apk -d unpacked
```

Step 3: 翻文本类文件

```Bash
# 直接看
cat unpacked/assets/*                 # 配置、key
cat unpacked/res/values/strings.xml

# 解 AndroidManifest（用 apktool 把它转成文本 XML）
apktool d app.apk -o apktool_out
cat apktool_out/AndroidManifest.xml
```

Step 4: 全局搜可疑字符串

```Bash
# 搜 base64 特征
grep -rE "[A-Za-z0-9+/]{8,}={0,2}" unpacked/

# 搜 flag 关键词
grep -rE "flag|FLAG|ctf|CTF|magic" unpacked/

# 搜密钥、URL 等
grep -rE "key|secret|api|http|https" unpacked/
```

Step 5: 反编译 dex

```Bash
# 用 jadx 看 Java 源码
jadx -d jadx_out app.apk
# GUI 更直观
jadx-gui app.apk
```

打开 jadx 后：

- 左边的类树 找到 MainActivity（主入口）

- 顶部搜索框 搜 `flag`、`check`、`verify`、`password`、`key` 等关键词

- 右键方法名 → Find Usages（找谁调用了它）

Step 6: 找关键逻辑

在 jadx 里重点看：

- `onCreate`、`onClick`、`checkPassword` 等方法

- 字符串比较（`String.equals`、`compareTo`）

- 网络请求 URL（里面可能带 token）

- 加密函数（`Cipher` / `MessageDigest`）

#### 下载工具

##### JDK



##### apktool



##### adb\-\-Android Debug Bridge



##### 7zip



##### Frida











### python题

一些初学者细碎的小问题。

#### lambda是什么？

`lambda` 就是一种临时写的小函数，相当于 C 语言的 `int (*f)(int)` 那种东西，但写起来很短。

- 普通函数：`def add(x, y): return x + y`

- Lambda 版本：`lambda x, y: x + y`

在 C 语言里，你如果要把一个“计算规则”传来传去，你会写函数指针。
在 Python 里，你就用 `lambda` 来写这种“**一次性小函数**”。

为什么题目里到处都是 `lambda`？
因为出题人把所有的 `if`、`else`、`while`、`for`、`+`、`-` 都改成了用 lambda 调用的形式。
这就像有人把 C 语言的所有 `if` 全换成 `? :` 三目运算符，然后嵌套 100 层——你看得懂每个 `? :` 的意思，但连在一起就看不懂了。

没关系，它最终计算出来的数字和逻辑跟普通 Python 完全一样。

#### 识别 Y combinator 有什么用？

**Y combinator 就是用来代替 ****`while`**** 或 ****`for`**** 循环的。**

在普通 Python 里，你要循环 54 次，你会写：

```Python
for i in range(54):    sum += ord(s[i])
```

但在“纯 lambda 世界”里，没有 `for` 关键字，所以只能用 Y combinator 实现递归来模拟循环。

你识别它的作用只有 1 个：

> “哦，原来这里是在循环遍历输入的 54 个字符。”
> 
> 

你不需要理解它怎么实现的，只需要知道它循环了，然后看循环体里干了什么。
就像你调试 C 语言时，看到 `while (i < 54)`，你不会去深究 CPU 怎么执行跳转指令，你只看大括号里面的内容。

所以：**识别出 Y combinator = 找到循环的入口**。之后你就忽略它，**只盯住循环体里的计算。**

#### 怎么来写 z3 脚本？

**z3 就是一个自动解方程的计算器。**

1. 告诉 z3 有 54 个未知数（每个未知数代表 flag 的一个字符）：

```Python
chars = [BitVec(f'c{i}', 32) for i in range(54)]
```

2. 告诉 z3 每个未知数的范围（可打印字符）：

```Python
for c in chars:    s.add(c >= 32, c <= 126)
```

3. **把上面抄下来的 5 个数学等式，原封不动翻译给 z3：**

```Python
s.add(sum(chars) == 5138)                     # 特征 2
s.add(XorAll(chars) == 26)                    # 特征 3
s.add(sum(c*c for c in chars) == 520600)      # 特征 4
s.add(sum(chars[i]*chars[i+1]) == 467644)     # 特征 5        
```

4. 把 53 个多项式的约束也翻译给 z3：

```Python
for i in range(53):
    if i % 3 == 0: s.add(c1 + c2 + c3*c3 == targets[i] ^ 90)
    elif i % 3 == 1: s.add(c1*c2 + c3 == targets[i] ^ 90)
    else: s.add(c1*c1 + c2*c2 + c3*c3*c3 == targets[i] ^ 90)
```

5. 让 z3 算：`s.check()`，如果算出结果，打印出来。

#### Z3的语法

学习链接：https://ericpony\.github\.io/z3py\-tutorial/guide\-examples\.htm 
