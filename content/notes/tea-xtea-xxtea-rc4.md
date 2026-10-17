+++
title = '魔改算法实战手册（TEA / XTEA / XXTEA / RC4）'
date = '2026-08-28T12:00:00+08:00'
draft = false
summary = ''
tags = []
showtoc = true
+++

> 这是moectf新生赛分值最重的板块，校赛"Welcome"题就是这个套路。

***

## 第1章：基础回顾

### 1.1 TEA是什么

TEA（Tiny Encryption Algorithm）是一种**对称分组密码**，特点：

- 处理8字节数据（两个32位整数）
- 密钥16字节（4个32位整数）
- 32轮Feistel结构
- 特征常量：`delta = 0x9E3779B9`（黄金比例导数）

### 1.2 标准TEA加密伪代码

```c
void tea_encrypt(uint32_t v[2], uint32_t k[4]) {
    uint32_t v0 = v[0], v1 = v[1];
    uint32_t sum = 0;
    uint32_t delta = 0x9E3779B9;
    for (int i = 0; i < 32; i++) {
        sum += delta;
        v0 += ((v1 << 4) + k[0]) ^ (v1 + sum) ^ ((v1 >> 5) + k[1]);
        v1 += ((v0 << 4) + k[2]) ^ (v0 + sum) ^ ((v0 >> 5) + k[3]);
    }
    v[0] = v0; v[1] = v1;
}
```

### 1.3 标准TEA解密伪代码

```c
void tea_decrypt(uint32_t v[2], uint32_t k[4]) {
    uint32_t v0 = v[0], v1 = v[1];
    uint32_t delta = 0x9E3779B9;
    uint32_t sum = delta * 32;  // 注意：从总和开始倒推
    for (int i = 0; i < 32; i++) {
        v1 -= ((v0 << 4) + k[2]) ^ (v0 + sum) ^ ((v0 >> 5) + k[3]);
        v0 -= ((v1 << 4) + k[0]) ^ (v1 + sum) ^ ((v1 >> 5) + k[1]);
        sum -= delta;
    }
    v[0] = v0; v[1] = v1;
}
```

### 1.4 XTEA区别

XTEA把TEA里的"`+k[i]`"改成了"`+(sum+k[...])`"，密钥选取跟轮数相关：

```c
// XTEA加密
v0 += (((v1 << 4) ^ (v1 >> 5)) + v1) ^ (sum + k[sum & 3]);
sum += delta;
v1 += (((v0 << 4) ^ (v0 >> 5)) + v0) ^ (sum + k[(sum >> 11) & 3]);
```

### 1.5 XXTEA区别

XXTEA处理**任意长度**（不一定是2个uint32），用变长数组：

```c
// XXTEA核心循环（简化版）
while (rounds-- > 0) {
    sum += delta;
    v[0] += ((v[1] << 4) + k[0]) ^ (v[1] + sum) ^ ((v[1] >> 5) + k[1]);
    for (int i = 1; i < n-1; i++) {
        // 取数魔改重点
        v[i] += ((v[i+1] ^ v[i-1]) + sum) ^ ...;
    }
    v[n-1] += ...
}
```

### 1.6 RC4基础

RC4是**流密码**（不是分组），特点：

- 256字节S盒
- KSA（密钥调度）+ PRGA（生成密钥流）
- 加密 = 异或

```python
def rc4(data, key):
    s = list(range(256))
    j = 0
    for i in range(256):
        j = (j + s[i] + key[i % len(key)]) & 0xFF
        s[i], s[j] = s[j], s[i]
    i = j = 0
    out = bytearray()
    for b in data:
        i = (i + 1) & 0xFF
        j = (j + s[i]) & 0xFF
        s[i], s[j] = s[j], s[i]
        out.append(b ^ s[(s[i] + s[j]) & 0xFF])
    return bytes(out)
```

***

## 第2章：魔改大全（核心）

出题人最爱改的几个点：

### 2.1 TEA/XTEA/XXTEA 魔改点

| 魔改类型 | 怎么改 | 怎么识别 |
| --- | --- | --- |
| **delta魔改** | `0x9E3779B9` → `0x12345678` 或 `0x61C88647`（负数形式） | 看伪代码里的"魔法常量" |
| **轮数魔改** | 32 → 16/64/任意 | 看 `for` 循环 |
| **移位魔改** | `<< 4` → `<< 2/5/8` | 看到非4/5的移位 |
| **密钥顺序** | k[0]k[1]k[2]k[3] → k[2]k[3]k[0]k[1] | 看下标 |
| **加减号** | `+` 改 `-` | 加密=加、解密=减，永远成对 |
| **取数逻辑** | `k[i&3]` → `k[(i>>1)&3]` | 异或移位组合 |
| **右移位数** | `>> 5` → `>> 3/4/6` | 看右移数 |
| **整体结构** | FEISTEL结构打乱 | 看运算顺序 |
| **密文长度** | 不是8字节 | 看输入参数 |

### 2.2 RC4 魔改点

| 魔改类型 | 怎么改 |
| --- | --- |
| S盒大小 | 256 → 128 |
| KSA交换逻辑 | `j = (j + s[i] + key[i%len])` 加项调整 |
| 交换的目标数 | s[i]、s[j] 顺序 |
| 输出位置 | `(s[i]+s[j])` 加/减/异或 |
| 初始状态 | 不从0开始 |

### 2.3 怎么快速看出"魔改了什么"

**关键三看**：

1. **看 delta** —— 找到那个魔法常量，记下它的值
2. **看轮数** —— for循环的次数
3. **看运算结构** —— 加/减/异或/移位与标准版对一下

**方法**：把你的笔记里"标准TEA伪代码"截图存手机里，IDA里看到的伪代码跟它**逐行对比**。

***

## 第3章：通用模板（背下这个能解80%的题）

### 3.1 通用TEA解密模板

```python
import struct

def tea_decrypt(v0, v1, k, delta=0x9E3779B9, rounds=32, shift1=4, shift2=5, op='+'):
    sum_val = (delta * rounds) & 0xFFFFFFFF
    for _ in range(rounds):
        if op == '+':
            v1 = (v1 - (((v0 << shift1) + k[2]) ^ (v0 + sum_val) ^ ((v0 >> shift2) + k[3]))) & 0xFFFFFFFF
            v0 = (v0 - (((v1 << shift1) + k[0]) ^ (v1 + sum_val) ^ ((v1 >> shift2) + k[1]))) & 0xFFFFFFFF
        else:  # op == '-'
            v1 = (v1 - (((v0 << shift1) - k[2]) ^ (v0 - sum_val) ^ ((v0 >> shift2) - k[3]))) & 0xFFFFFFFF
            v0 = (v0 - (((v1 << shift1) - k[0]) ^ (v1 - sum_val) ^ ((v1 >> shift2) - k[1]))) & 0xFFFFFFFF
        sum_val = (sum_val - delta) & 0xFFFFFFFF
    return v0, v1

# 使用示例（针对具体题改参数）
key = [0x12345678, 0x9abcdef0, 0xfedcba98, 0x76543210]
cipher = bytes.fromhex("你的密文")
v0, v1 = struct.unpack('<2I', cipher)
v0, v1 = tea_decrypt(v0, v1, key, delta=0x9E3779B9, rounds=32, shift1=4, shift2=5)
flag = struct.pack('<2I', v0, v1)
print(flag)
```

### 3.2 通用XXTEA解密模板

```python
import struct

def xxtea_decrypt(v, k, delta=0x9E3779B9, rounds=32):
    n = len(v)
    sum_val = (delta * rounds) & 0xFFFFFFFF
    while rounds > 0:
        v[n-1] = (v[n-1] - (((v[0] << 4) + k[2]) ^ (v[0] + sum_val) ^ ((v[0] >> 5) + k[3]))) & 0xFFFFFFFF
        for i in range(n-1, 0, -1):
            # 关键：取数逻辑是魔改重点
            e = (v[i-1] ^ sum_val)  # 标准版本
            # e = (v[i-1] ^ (sum_val >> 2))  # 魔改示例
            v[i] = (v[i] - ((((v[i-1] << 4) + k[0]) ^ (v[i-1] + sum_val) ^ ((v[i-1] >> 5) + k[1])) + e)) & 0xFFFFFFFF
        v[0] = (v[0] - ((((v[n-1] << 4) + k[2]) ^ (v[n-1] + sum_val) ^ ((v[n-1] >> 5) + k[3])) + e)) & 0xFFFFFFFF
        sum_val = (sum_val - delta) & 0xFFFFFFFF
        rounds -= 1
    return v
```

### 3.3 通用RC4模板

```python
def rc4(data, key):
    s = list(range(256))
    j = 0
    for i in range(256):
        j = (j + s[i] + key[i % len(key)]) & 0xFF
        s[i], s[j] = s[j], s[i]
    i = j = 0
    out = bytearray()
    for b in data:
        i = (i + 1) & 0xFF
        j = (j + s[i]) & 0xFF
        s[i], s[j] = s[j], s[i]
        out.append(b ^ s[(s[i] + s[j]) & 0xFF])
    return bytes(out)
```

***

## 第4章：实战案例（手把手教你解）

### 案例1：标准TEA（送分题）

**题目**：BUUCTF "TEA"

**伪代码**（简化）：

```c
for (i = 0; i < 32; i++) {
    sum += 0x9E3779B9;
    v0 += ((v1 << 4) + k[0]) ^ (v1 + sum) ^ ((v1 >> 5) + k[1]);
    v1 += ((v0 << 4) + k[2]) ^ (v0 + sum) ^ ((v0 >> 5) + k[3]);
}
```

**解法**：

1. 看到 `0x9E3779B9` → 标准TEA
2. 看到 `<< 4` 和 `>> 5` → 标准移位
3. 看到32轮 → 标准轮数
4. 直接用标准模板

**脚本**：

```python
import struct
key = struct.unpack('<4I', bytes.fromhex("你的密钥"))  # 16字节
cipher = bytes.fromhex("密文")  # 8字节
v0, v1 = struct.unpack('<2I', cipher)
# 套用标准解密（省略，见3.1）
```

### 案例2：delta魔改

**伪代码**：

```c
for (i = 0; i < 32; i++) {
    sum += 0x12345678;  // 改了的delta
    v0 += ((v1 << 4) + k[0]) ^ (v1 + sum) ^ ((v1 >> 5) + k[1]);
    v1 += ((v0 << 4) + k[2]) ^ (v0 + sum) ^ ((v0 >> 5) + k[3]);
}
```

**解法**：把模板里的 `delta=0x9E3779B9` 改成 `delta=0x12345678`，其他不变。

### 案例3：轮数魔改

**伪代码**：

```c
for (i = 0; i < 16; i++) {  // 改成16轮
    sum += 0x9E3779B9;
    ...
}
```

**解法**：把 `rounds=32` 改成 `rounds=16`。

### 案例4：移位魔改

**伪代码**：

```c
v0 += ((v1 << 2) + k[0]) ^ (v1 + sum) ^ ((v1 >> 3) + k[1]);
                                       // ^5 改成 ^3 了
```

**解法**：`shift1=4` 改 `shift1=2`，`shift2=5` 改 `shift2=3`。

### 案例5：取数逻辑魔改（最难）

**伪代码**：

```c
v0 += (((v1 << 4) ^ (v1 >> 5)) + v1) ^ (sum + key[sum & 3]);
```

**注意**：这是XTEA的样式，但是密钥取数逻辑可能被改。比如 `sum & 3` 改成 `(sum >> 1) & 3`。

**解法**：仔细看取数表达式，照抄下来。

### 案例6：XXTEA魔改综合（校赛Welcome原题）

**伪代码特征**：

```c
for (i = 0; i < 32; i++) {
    sum -= 1640531527;  // delta = 0x9E3779B9，但用减号
    v4 += (v5 + sum) ^ (16 * v5 + 1702060386) ^ ((v5 >> 5) + 1870148662);
    v5 += (v4 + sum) ^ (16 * v4 + 1634038898) ^ ((v4 >> 5) + 1634038904);
}
```

**魔改点分析**：

- 用了减号（标准是加号）
- delta = 1640531527（标准值，但用减法）
- 移位 << 4 写成 16 \* v5（等价）
- 加的"密钥"是固定常量（不是数组）

**解法**：写一个反向脚本，从循环末值反推32轮。这题是爆破v7高3字节的已知值（看doc6的笔记）。

### 案例7：RC4 + 魔改密钥

**伪代码**：

```c
RC4(input, key);  // 标准的RC4
```

**解法**：直接套标准RC4模板。

**魔改RC4的伪代码识别**：

- 看到 `s[i], s[j] = s[j], s[i]` 但前面公式不一样
- 看到循环里 `s[(s[i] + s[j]) & 0xFF]` 但加减号变了
- 看到 `if s[i] + s[j] > 256: s[i] + s[j] - 256` 而不是 `& 0xFF`

***

## 第5章：做题流程（拿到题就按这个走）

### Step 1：识别算法（30秒）

看伪代码里有没有：

- `0x9E3779B9` → TEA系列
- `0x256` + 256字节S盒 → RC4
- 字符表 + 64字节 + `=` 填充 → Base64
- 重复 `xor` 单字节 → 单字节异或
- `S盒替换` + `行移位` + `列混淆` → AES

### Step 2：找魔改点（1-2分钟）

对照标准模板，**逐行**找：

- delta的值
- 轮数
- 移位数
- 加减号
- 取数表达式

### Step 3：找密文和密钥（1-2分钟）

- 密文：通常在 main 函数里有 `byte_xxxx[]` 数组
- 密钥：通常是 `key[]` 数组或者 `k0/k1/k2/k3` 这种4个uint32

**注意字节序**：x86小端，密钥在内存里是 `78 56 34 12`，但解释为 `0x12345678`，模板已经处理。

### Step 4：写脚本（3-5分钟）

- 复制通用模板
- 改参数（delta/rounds/shift/key）
- 跑

### Step 5：处理结果（1分钟）

- 如果输出是乱码：检查字节序、key顺序
- 如果长度不对：检查轮数
- 如果没有 flag{} 前缀：自己加

***

## 第6章：踩坑大全

### 坑1：字节序搞反

**症状**：解出来是反着的字符串
**原因**：小端序 vs 大端序
**解决**：用 `struct.unpack('<2I', data)` 还是 `'>2I'`

### 坑2：密钥顺序搞反

**症状**：解出来是乱码
**原因**：k0/k1/k2/k3 在内存里的顺序
**解决**：打印每个key看是不是和伪代码里对应

### 坑3：加解密方向搞反

**症状**：解出来还是密文
**原因**：用了加密的脚本解
**解决**：注意 sum 是 `delta * rounds` 起始还是 `0` 起始

### 坑4：delta魔改没看出来

**症状**：解出来全是乱码
**原因**：出题人改了 delta 但你以为是标准的
**解决**：把 `0x9E3779B9` 替换成伪代码里的实际值

### 坑5：没注意加密还是解密

**症状**：flag 倒过来才是正确的
**原因**：有时候程序内部先解密你的输入再比较
**解决**：看 main 函数最后是 `==` 比较还是 `!=` 比较

### 坑6：密文是负数

**症状**：从伪代码复制出来的密文是 `-60, 96, -81, -71`
**原因**：IDA把unsigned char显示成signed
**解决**：`[b & 0xFF for b in raw]`

***

## 第7章：z3在算法题里的用法

### 什么时候用z3

当算法里有\*\*"未知常数"**、**"输入的一部分未知"**、**"需要反推多步"\*\*时，用z3比手写循环简单。

### 模板

```python
from z3 import *

# 定义变量
v0 = BitVec('v0', 32)
v1 = BitVec('v1', 32)
sum_val = BitVecVal(0, 32)
delta = BitVecVal(0x9E3779B9, 32)
k = [BitVecVal(0x12345678, 32), BitVecVal(0x9abcdef0, 32), ...]

# 模拟加密
for i in range(32):
    sum_val = sum_val + delta
    v0 = v0 + ((v1 << 4) + k[0]) ^ (v1 + sum_val) ^ ((v1 >> 5) + k[1])
    v1 = v1 + ((v0 << 4) + k[2]) ^ (v0 + sum_val) ^ ((v0 >> 5) + k[3])

# 加约束（已知密文）
s = Solver()
s.add(v0 == 0xDEADBEEF)
s.add(v1 == 0xCAFEBABE)

if s.check() == sat:
    m = s.model()
    print(hex(m[v0].as_long()), hex(m[v1].as_long()))
```

### 实战

**校赛Welcome题的z3版**（替代爆破）：

```python
# 不用爆破v7，直接用z3
v = [BitVec(f'v{i}', 32) for i in range(8)]
# 把密文作为约束
for i, c in enumerate(cipher_as_4_ints):
    s.add(v[i] == c)
# 模拟魔改XXTEA加密（v是输入，约束是密文）
# ...（具体看你题的魔改方式）
# 解出v[0..6]就是flag的前28字节
```
