+++
title = 'Moectf 2025'
date = '2026-09-11T12:00:00+08:00'
draft = false
summary = ''
tags = []
showtoc = true
+++

除了那个土豆大爆炸是moectf2026 其他wp都是来自moectf2025的题目。

## upx\_revenge

本来moectf2026也有这道题做不出想跳过去 发现之前的比赛经常出现这一类题目

> 为什么 `upx -d` 脱不了？\-\-因为出题人故意把 UPX 的特征码（Magic Number）给篡改了（比如把 `UPX!` 改成了 `TUX!` 或者其他乱码），导致 UPX 官方工具不认这个文件，所以拒绝脱壳。
> 
> 

找到upx的身份证：

任何 UPX 加壳的程序，在文件开头的某个固定位置（通常是 偏移量 0x40 到 0x44 附近），都会有一串固定的标记：**`55 50 58 21`****（这就是 ASCII 码的 ****`U`**** ****`P`**** ****`X`**** ****`!`****）**。

![QQ\_1788406529259\.png](/images/moectf-2025/QQ_1788406529259.png)

第一次做只知道是改为UPX\! 但是不知道是在哪里改 所以就头脑简单地选择了和UPX长得最像的地方 但是改了之后发现脱壳还是不成功。

原因：

`0x200`（改的地址）：这里是 **PE 文件的节表**（Section Table）。里面写的 `UPX0` 是区段的名称（相当于给这块内存起了个名字叫“UPX0”）。把 `UPX0` 最后的 `0` 改成 `!` 变成 `UPX!`，这在 PE 结构里相当于把硬盘分区名从“C盘”改成了“C\!”——这根本不影响 UPX 工具的识别，反而把标准的区段名破坏了，导致 PE 结构畸形。

为了我们能找到正确的位置 我们先复习一下010editor：

1. 第 1 步：找到 PE 头（文件的“总指挥部”）
在 010 Editor 中，按 `Ctrl + G`，输入 **`0x3C`**（十进制 60）。
看光标处的 4 个字节（例如显示为 `E0 00 00 00`，即 `0xE0`）。这个值叫 **`e_lfanew`**，它告诉你了**真正的 PE 头（NT Headers）在文件的哪个位置**。

2. 第 2 步：找到节表数组的起始地址（“户口本”的位置）
按下 `Ctrl + G`，跳转到第 1 步读出的地址（比如 `0xE0`）。
在这个地址（PE 头）处，结构是这样的：

- `PE` 头标记占 4 字节（`50 45 00 00`）。

- 标准文件头（File Header）占 20 字节（0x14）。

- 扩展头（Optional Header）的大小不固定，但它的大小值就写在文件头的第 17\-18 个字节处（即 `e_lfanew + 0x14` 处）。

![QQ\_1788409528363\.png](/images/moectf-2025/QQ_1788409528363.png)

修改之后即能完成脱壳。

![b8a8699cb3f3ea82324380080eccb72b\.png](/images/moectf-2025/b8a8699cb3f3ea82324380080eccb72b.png)

再将脱壳之后的文件拖入ida

main函数中伪代码实在是太长了 我一开始提取不出有效信息

分析：

> 看到 `operator new`（申请内存）、`memmove`（拷贝）、`free`（释放）、`v31 > 0xF`（这是 `std::string` 的短字符串优化判断）——全部跳过，一眼都不要看。这些都是 C\+\+ 编译器自动生成的“搬砖代码”，跟解题逻辑毫无关系。
> 
> 

主要看三个：

1. 输入数据从哪里来？（`std::cin` 或 `argv`）

2. 核心处理函数是哪个？（调用了哪个奇怪的自定义函数）

3. 最终跟谁比较？（硬编码的字符串）

一开始一直在找我的输入在哪里 找fget之类的函数一直找不到

> 在 C\+\+ 标准库（STL） 里，输入可不是调用 `fgets` 或 `scanf`，而是 **`std::cin`**。但是 IDA 反编译 C\+\+ 的模板时，会把 `operator>>` 运算符重载展开成一个极其恶心的内部函数（比如 `sub_140002100`），所以你翻遍整个代码都找不到 `fgets`——因为根本就没有！
> 
> 

因此输入输出查找方法更新了

1. **看到 ****`std::cin`**** 或 ****`std::cout`**** 全局变量**：如果伪代码开头出现这两个名字（或者 IDA 解析成了 `std::cin`），那**下面紧跟着的那个函数调用 100% 是输入/输出**。

2. 看到 `std::ios::widen`：这通常是**为了确定“换行符”或“空格”分隔符**，跟在 `cin` 后面出现，必是用户输入。

3. 看到 `operator new` 紧跟 `memmove`：这是 `std::string` 在动态分配内存并拷贝数据。`Src` 就是你输入的字符串，`Size` 就是它的长度。

看出输入是Src而不是v5的原因：

C\+\+ 的 `getline`（或 `>>`）函数的参数顺序：

- 第一个参数 `std::cin`：输入流对象（键盘）。

- 第二个参数 `Src`：用来存放读取结果的容器（也就是装数据的桶）。

- 第三个参数 `v5`：**分隔符**（Delimiter），告诉程序读到哪个字符就停下来（通常是换行符 `\n`）。

结论：`v5` 只是一个“结束标志”，数据被存进了 `Src`。所以用户输入的内容绝对在 `Src` 里，不在 `v5` 里。

Src又通过媒介将值传给了v25

```Java
v6 = Src;          // 把 Src 的地址给了 v6
if ( si128... > 0xF )
    v6 = (void **)Src[0];  // 如果是长字符串，取实际指针

v7 = Src;          // 把 Src 的地址给了 v7
if ( si128... > 0xF )
    v7 = (void **)Src[0];  // 同理

v8 = (char *)v6 + ... - (char *)v7;  // 计算 Src 的长度

memmove(v11, v7, v8);  //  关键！把 v7（也就是 Src 里的数据）拷贝到 v11 里

v25[0] = v11;      //  关键！把拷贝好的数据（即输入内容）放进 v25 数组里！
```

`memmove(v11, v7, v8);`：

把 `v7` 这个地址开始，长度为 `v8` 个字节的数据，全部复制到 `v11` 这个地址去。

1300处的函数又臭又长。。ai居然一眼就看出来base64我不中了。

![QQ\_1788427927612\.png](/images/moectf-2025/QQ_1788427927612.png)

回忆一下 Base64 的核心算法：

> Base64 把每** 3 个字节（24 位） 拆成 4 组，每组 6 位。**
> 怎么取 6 位？**右移 18 位取第一组，右移 12 位取第二组，右移 6 位取第三组，最后左移 0 位（即 ****`& 0x3F`****）取第四组。**
> 
> 

a3是base64的那张表

```C
v11 = a3;               // ← 把 a3 赋值给 v11
if ( a3[3] > 0xF )      
    v11 = (_QWORD *)*a3; // 如果是长字符串，取实际指针
v12 = *((_BYTE *)v11 + ((v7 >> 18) & 0x3F)); // ← v11 就是 a3！
```

原因：

**索引范围只能是 0\~63（物理限制）**

看这句代码：`*((_BYTE *)v11 + ((v7 >> 18) & 0x3F))`。

- 无论 `v7` 是什么值，**`& 0x3F`**** 意味着结果永远被限制在 0 到 63 之间**。

- 结论：`a3` 指向的必须是一个长度为 64 的表格。如果不是 64 个元素，程序就会访问非法内存崩溃。

接着我们由block这个参数锁定到函数1230

![fd336a5c94c94ca61d40fb42bbbd3888\.png](/images/moectf-2025/fd336a5c94c94ca61d40fb42bbbd3888.png)

核心循环：

```C
for ( ... )
{
    v5 = *(_BYTE *)v3 ^ 0xE;   // 从某个地方取一个字节，异或 0x0E
    // 然后把 v5 追加到 Src (即 Block) 里
}
```

因此我们就知道这个题目是把标准的表的每一个数都异或了0xE

Exp

```Python
# 标准 Base64 表（字节形式）
std = b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"

# 自定义表 = 标准表逐字节异或 0x0E
custom = bytes([c ^ 0x0E for c in std])

# 以字符串形式打印，方便复制到解码脚本中
print(custom.decode('latin-1'))

```

得到：

```C
OLMJKHIFGDEBC@A^_\]Z[XYVWTolmjkhifgdebc`a~|}z{xyvwt>?<=:;8967%!
```

![1f45935e2952f61467b7651d31100494\.png](/images/moectf-2025/1f45935e2952f61467b7651d31100494.png)

但是如果直接用cyberchef的话要注意input的双斜杠 要删掉两个中的一个 否则会出现乱码

解释：我们在伪代码中看到的长这样：

```C
strcpy(v13, "lY7bW=\\ck?eyjX7]TZ\\}CVbh\\tOyTH6>jH7XmFifG]H7");
```

IDA 为了符合 C/C\+\+ 语法，把内存里真实存储的 1 个反斜杠字符 `\`，显示成了 `\\`（两个字符）

> 总结：IDA 里带反斜杠的（`\\`、`\t`、`\n`）都是“转义表示”，实际内存里只有一个字节。动手操作时，必须按照“真实字节”去还原，而不是照抄 IDA 的显示文本。
> 
> 

或者直接 一步到位。

```Python
import base64

# 1. 标准 Base64 表
std = b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"

# 2. 自定义表 = 标准表逐字节异或 0x0E
custom = bytes([c ^ 0x0E for c in std])

# 3. 密文（注意：在 IDA 里复制时是 "lY7bW=\\ck?eyjX7]TZ\\}CVbh\\tOyTH6>jH7XmFifG]H7"）
#    直接用原始字符串，反斜杠不会被转义，正好对应 `\` 字符。
cipher = r"lY7bW=\ck?eyjX7]TZ\}CVbh\tOyTH6>jH7XmFifG]H7"

# 4. 映射：将密文中的每个字符，按照自定义表找到其在标准表中的索引，
#    再用标准表中的对应字符替换，得到标准 Base64 编码字符串。
def decode_custom(cipher, custom_table, std_table):
    # 构建映射字典 {自定义字符: 标准字符}
    trans = {custom_table[i]: std_table[i] for i in range(64)}
    std_cipher = ''.join(trans.get(c, '') for c in cipher)
    # 补齐等号（Base64 要求长度是 4 的倍数）
    pad = 4 - (len(std_cipher) % 4)
    if pad != 4:
        std_cipher += '=' * pad
    return base64.b64decode(std_cipher)

flag = decode_custom(cipher, custom.decode('latin-1'), std.decode('latin-1'))
print(flag.decode('utf-8', errors='ignore'))
```

得到flag：moectf\{Y0u\_Re4l1y\_G00d\_4t\_Upx\!\!\!\}

## **Ultato Polosion Xptra \-\-？**

之前尝试过 同样是无法正常脱壳 对`UPX!`做了魔改

这个文件是ELF 和上面upx的报复的PE文件还不太一样。

### 怎么定位魔改点

UPX 文件里 **`"UPX!"`****（hex ****`55 50 58 21`****）**这个 4 字节串应该精确出现 3 次：

1. `l_info.l_magic`（loader 解压入口）

2. end marker `b_info` 的 `sz_cpr`（值 `0x21585055`，标志压缩流结束）

3. `PackHeader` 的 magic（前 4 字节）



我们先下载一个ELF的模板 然后加载

![f2ef1601a85068df96ed5cad23c5d133\.png](/images/moectf-2025/f2ef1601a85068df96ed5cad23c5d133.png)

`e_phoff`（程序头偏移）

`e_phnum`（程序头数量）

```C
UPX! 的偏移 = e_phoff + (e_phentsize × e_phnum)
```

代入数据：

- `e_phoff = 0x40`

- `e_phentsize = 0x38`（56 字节）

- `e_phnum = 5`

计算：
`0x40 + (0x38 × 5) = 0x40 + 0x118 = 0x158`

但是！！这个位置并不是真正的魔改点！

> 为什么算到 0x158？ 因为你的公式 `e_phoff + e_phentsize × e_phnum = 0x158` 算的是 phdr 数组结束位置 —— 这只对了一半！**问题是这题 phdr 后面还塞了一段 PT\_NOTE 段（build\-id 那些），所以 0x158 是 NOTE 开始，不是 l\_info。**真正的 l\_info 偏移 = `0x158 + p_filesz_of_PT_NOTE = 0x158 + 0x74 = 0x1CC`，l\_magic 在 `0x1CC + 4 = 0x1D0`。
> 
> 

但是在修改完正确的魔改位置之后还是不能用upx工具脱壳

ai说这是一道 `伪 UPX + 非标准 ELF`



























## **Flower \-\-？**

![QQ\_1788514435270\.png](/images/moectf-2025/QQ_1788514435270.png)

> 虽然 IDA 没有“飘红”（**红色通常指函数名未识别或指令解析失败**），但伪代码里的函数调用参数和逻辑已经完全错乱了。这种“看起来能编译，但逻辑狗屁不通”恰恰是花指令最成功的效果。
> 
> 

IDA 的“飘红”主要针对指令解码失败（无法识别字节码）或栈帧完全损坏。

- 这道题的混淆（Flower）手法比较高级，它没有破坏指令，而是破坏了反编译器的“变量生存期分析”和“参数定位”。

- 反编译器虽然没崩溃，但它“尽力”把一团乱麻的汇编强行翻译成了 C\+\+ 代码。由于翻译出的代码在语法层面（C\+\+ 语法）是合法的（比如 `operator<<` 确实存在，只是参数多了），IDA 就不会标红，但它的分析结果已经不可信了。

### `std::operator>>` 参数丢失

代码中有这一行：

```C
std::operator>><char>((std::istream *)&std::cin);
```

问题：C\+\+ 标准库的 `operator>>` 输入流重载，必须有 2 个参数（流对象 \+ 接收变量的引用）。这里只传了 `std::cin` 一个参数，第二个参数（应该是 `v7`）被反编译器彻底吃掉了。

- 为什么会这样？因为花指令插入了大量无意义的跳转或垃圾字节，导致反编译器的数据流跟踪（Data\-flow）断裂。它知道 `v7` 存在，但无法推断出 `v7` 被传进了这个函数，于是伪代码生成器强行拼凑出了这个“缺斤短两”的调用。

### `std::ostream::operator<<` 有 3 个参数

```C
std::ostream::operator<<(&std::cout, (unsigned int)(10 / main::zero), (unsigned int)(10 % main::zero));
```

问题：**`std::ostream::operator<<`**** 作为成员函数，标准重载最多接收 2 个参数**（隐式 this 指针 \+ 要打印的值）。这里硬塞了 3 个参数（`cout` \+ 商 \+ 余数）。

### `main::zero` 和除零异常！

代码先检查 `if ( !main::zero )` 并抛出“Division by zero”异常，接着又去计算 `10 / main::zero`。
这在正常源码中是极度矛盾的行为。

这极大概率是**虚假控制流**（Obfuscation）——`main::zero` 这个全局变量可能在 `check()` 函数中（或者通过内联汇编）被动态修改，或者这里的 `10 / main::zero` 根本就不是真正的除法，只**是反编译器把某条无关的算术指令（比如异或、加法）错误地识别成了除法。**

### 学习

#### C\+\+标准库函数

C\+\+ 的标准库函数（STL）就像现实中的快递员，送几个包裹是固定的。

- **`operator>>`****（输入）**：天生就是 2个参数（`cin` 和 变量）。伪代码里只出现了 1 个（只有 `cin`）——缺少包裹，快递员姿势不对，必是伪代码崩了。

- **`operator<<`****（输出）**：作为成员函数，天生只有 1个显式参数（要打印的值）。伪代码里出现了 2 个（商和余数）——快递员突然长出第三只手，必是反编译器把两句话合成了一句。

步骤：

1. 找到 `solve(v8)` 这个函数（这是核心加密逻辑）。

2. 动态调试（F9 跑起来），在输入后观察 `solve` 函数的参数和返回值。

3. 绕过那些恶心的 `check()` 花指令（直接 NOP 掉或者跳过）。

#### check\(\)

`check()` 是一个“专门负责捣乱的垃圾代码生成器”。

- 它不干正事（不是真正的系统检查，也不是真正的加密）。

- 它唯一的目的就是把反编译器（IDA 的 Hex\-Rays）给“绕晕”。

举个例子 check\(\)函数可能在程序里面做：

- 虚假的算术运算：它可能在里面疯狂地计算 `a = 1 + 2; b = a * 3; a = b - 6;`（最终结果永远是 0）。这些计算对程序运行结果毫无影响，但反编译器为了分析 `main` 函数，必须先进 `check()` 里“绕一圈”，结果出来时，反编译器脑子里的“寄存器状态记录表”就被这些垃圾运算弄脏了。

- 扰乱栈帧（Stack Frame）：更高级的花指令会在 `check()` 里故意 `push` 大量寄存器，然后不按常规顺序 `pop` 回来。这导致反编译器回到 `main` 函数时，算错了栈上变量（比如 `v7`、`v8`）的偏移地址。所以它才会把 `v7` 传给 `operator>>` 时传丢了——因为反编译器根本不知道 `v7` 此时被放在栈的哪个位置了。













## Base

flag:moectf\{Y0u\_C4n\_G00d\_At\_B45e64\!\!\}

由题目名字看出base解码 结果一把梭就试出来了

![d283423c36ff3b4a8a8caed10829b893\.png](/images/moectf-2025/d283423c36ff3b4a8a8caed10829b893.png)

但是还是看一眼伪代码是怎么实现的

![QQ\_1788512529039\.png](/images/moectf-2025/QQ_1788512529039.png)

核心算法：3 字节转 4 字符
代码中提取了三个输入字节（`v16`、`v14`、`v15`），并严格按照 Base64 的位操作规则生成四个索引：

- `v16 >> 2`：取第1个字节的高6位。

- `(16 * v16) | (v14 >> 4)`：取第1个字节的低4位 \+ 第2个字节的高4位，合并成6位（左移4位即 `*16`）。

- `(v15 >> 6) | (4 * v14)`：取第2个字节的低2位 \+ 第3个字节的高6位，合并成6位（左移2位即 `*4`）。

- `v15 & 0x3F`：取第3个字节的低6位。

![QQ\_1788512664584\.png](/images/moectf-2025/QQ_1788512664584.png)

这里的 `*`（乘号）本质上就是“左移”（`<<`），是反编译器（IDA）没有识别出位移优化而生成的等效数学表达。

- `16 * v16` = `v16 << 4`（左移 4 位，相当于乘以 2^4）

- `4 * v14` = `v14 << 2`（左移 2 位，相当于乘以 2^2）



- `v16 >> 2`：把第1个字节（8位）右移2位，丢弃低2位，原来的高6位就变成了新的低6位（Base64的第一组6位）。

- `v14 >> 4`：把第2个字节右移4位，丢弃低4位，原来的高4位（B7\~B4）被挪到了最低4位。

- `v15 >> 6`：把第3个字节右移6位，丢弃低6位，原来的高2位（C7\~C6）被挪到了最低2位。

```C
原始: [1] [0] [1] [1] [0] [1] [0] [1]
      \   \   \   \   \   \   \   \
       >   >   >   >   >   >   >   >   (整体向右挪)
           结果: [0] [0] [1] [0] [1] [1] [0] [1]
                 ↑补进来的    ↑原来高位的“1011”搬过来了
                 
原来最右边的“01”呢？—— 掉出去了，丢弃了！
```

- `v16 >> 2`：丢弃 `v16` 的低2位，取出了它的高6位（Base64第一组）。

- `v14 >> 4`：丢弃 `v14` 的低4位，取出了它的高4位（用来拼接第二组）。

- `v15 >> 6`：丢弃 `v15` 的低6位，取出了它的高2位（用来拼接第三组）。

## **ezandroid**

锁定函数的主入口：`com.example.ezandroid.MainActivity`

![d7c361257b0ee2865d32dc34f5e5e95d\.png](/images/moectf-2025/d7c361257b0ee2865d32dc34f5e5e95d.png)

```C
if (MainActivity.this.base64Encode(
        MainActivity.this.inputEditText.getText().toString().trim()
    ).equals("bW9LY3Rme2FuZHJvaWRfUmV2ZXJzZVV9JNV9LYXN5FQ==")) {
    // correct
} else {
    // incorrect
}
```

即把输入的内容先做 Base64 编码，然后和那一长串 Base64 字符串比较。

![18eec6cc050db701b007a24cd842376c\.png](/images/moectf-2025/18eec6cc050db701b007a24cd842376c.png)

flag:moectf\{android\_Reverse\_I5\_easy\}

## **ez3**

flag:moectf\{Y0u\_Kn0w\_z3\_S0Iv3r\_N0w\_a1f2bdce4a9\}

### 伪代码分析

主函数：

- 开头初始化和输入：

- 长度校验

- 格式检查

- 提取中间内容

- 调用核心校验





真正的逻辑处在check函数中

![a120c2dfdb0b233757838ea503bd80e4\.png](/images/moectf-2025/a120c2dfdb0b233757838ea503bd80e4.png)

设输入的第 `i` 个字符的 ASCII 值为 `x[i]`（0 ≤ i ≤ 33），变换过程如下：

- 第 0 位（i=0）：
`b[0] = (47806 * (x[0] + 0)) % 51966`
然后判断 `b[0]` 是否等于全局数组的 `a[0]`。

- 第 i 位（i \> 0）：
`temp = 47806 * (x[i] + i)`
`b[i] = (temp ^ b[i-1] ^ 0x114514) % 51966`
然后判断 `b[i]` 是否等于全局数组的 `a[i]`。

因为循环过程是：

最后，如果每一位算出来的 `b[i]` 都和全局数组 `a[i]` 完全相等，就返回 1（正确），否则返回 0。

![QQ\_1788613612929\.png](/images/moectf-2025/QQ_1788613612929.png)

```C
unsigned char a[] =
{
  176, 177,   0,   0, 120,  86,   0,   0, 242, 127, 
    0,   0,  50, 163,   0,   0, 232, 160,   0,   0, 
   76,  54,   0,   0, 212,  43,   0,   0, 254, 200, 
    0,   0, 124,  74,   0,   0,  24,   0,   0,   0, 
  228,  43,   0,   0,  68,  65,   0,   0, 166,  59, 
    0,   0, 140, 190,   0,   0, 126, 143,   0,   0, 
  248,  53,   0,   0, 170,  97,   0,   0,  74,  43, 
    0,   0,  40, 104,   0,   0, 158, 179,   0,   0, 
   66, 181,   0,   0, 236,  51,   0,   0, 216, 199, 
    0,   0, 140,  68,   0,   0,  16, 147,   0,   0, 
    8, 136,   0,   0, 212, 173,   0,   0, 194,  60, 
    0,   0, 150,   7,   0,   0,  64, 201,   0,   0, 
   50,  78,   0,   0,  46,  78,   0,   0,  74, 146, 
    0,   0,  92,  91,   0,   0
};
```

`check(std::string)::b[i]` 里的 `std::string` 啥意思？

这是 IDA 在给“静态局部变量”起名字时加的作用域标识。

- 在 C\+\+ 里，如果你在函数内部定义了一个静态数组（比如 `static int b[34];`），编译器会给它起一个只在函数内部可见的符号名。

- IDA 为了让你知道这个 `b` 是属于哪个函数的，就在前面加了函数签名作为前缀。`check(std::string)` 表示“**这个函数的参数是 std::string 类型**”。



```C
cur = ( 47806 * (c + i) ^ prev ^ 0x114514 ) % 51966
```

这里面出现了 `%`（取模） 和 `^`（异或） 的组合。
**给定目标 ****`target[i]`**** 和上一步的 ****`prev`****，反推 ****`c`**** 是一个非常麻烦的数学问题（涉及到离散对数或模逆元，且因为异或打乱了二进制位，很难直接列方程）。**
与其解复杂的数学方程，不如直接暴力枚举 `c`（只有 32\~126 共 95 种可能），把 `c` 代进去算一遍，看结果对不对。这就是正向爆破。

**多解：**

- 层面一（局部多解）：在某个位置 `i`，可能有 2 个或 3 个不同的字符 `c`，都能让算出来的 `cur` 恰好等于 `target[i]`。比如空格（32）和大写字母（65）在当前公式下可能算出同样的结果。

- 层面二（全局连锁反应）：即使每个位置只找到一个候选字符，如果第 `i` 位选错了字符，虽然它满足了第 `i` 位的等式，但计算出来的 `prev`（也就是 `b[i]`）会变，导致后续第 `i+1` 位无论怎么试都匹配不上。

DFS函数的参数：

```C
def dfs(i, prev, path):
```

- `i`：表示当前正在处理第几位（从 0 开始，到 33 结束）。它对应 C\+\+ 代码里的 `for ( i = 0; i <= 33; ++i )`。

- `prev`：**表示上一步计算出来的 ****`b[i-1]`**** 的值。**
对应 C\+\+ 里的 `check(std::string)::b[i - 1]`。因为第 `i` 位要异或上一位，所以必须把上一位的结果带进递归。

- `path`：一个列表，用来存放已经确定的字符。比如确定第 0 位是 `'Y'`，`path` 里就存 `['Y']`。等走到 `i == 34` 时，就把所有字符拼成字符串。

模块四：核心计算 \& 匹配逻辑

```C
for c in range(32, 127):
    cur = 47806 * (c + i)
    
    if i != 0:
        cur = cur ^ prev ^ 0x114514
    
    cur = cur % 51966
    
    if cur == target[i]:
        dfs(i + 1, cur, path + [chr(c)])
```

前四步依靠伪代码的逻辑完成

第四步（匹配与递归）：
`if cur == target[i]: dfs(i + 1, cur, path + [chr(c)])`

- 如果算出来的 `cur` 和硬编码的目标值相等，说明这个字符 `c` 有可能是正确的。

- **带着这个 ****`cur`**** 作为新的 ****`prev`****，去搜索下一位（****`i+1`****）。**

- `path + [chr(c)]`：把当前字符转成普通字符（比如 89 变成 `'Y'`）追加到路径里，传给下一层。

exp

```Python
target = [
    45488, 22136, 32754, 41778, 41192, 13900, 11220, 51454,
    19068, 24, 11236, 16708, 15270, 48780, 36734, 13816,
    25002, 11082, 26664, 45982, 46402, 13292, 51160, 17548,
    37648, 34824, 44500, 15554, 1942, 51520, 20018, 20014,
    37450, 23388
]   #从 IDA 里提取出来的 unsigned char a[] 经过小端序拼合后的 34 个整数

# 存储所有找到的解
solutions = []

# DFS 回溯：i 表示当前处理到第几位，prev 表示上一步的 b[i-1] 值，path 存储已拼好的字符
def dfs(i, prev, path):
    **# 如果 34 位全部匹配成功，记录这个解**
    if i == 34:
        solutions.append(''.join(path))
        return

    # 尝试所有可见 ASCII 字符（32~126）
    for c in range(32, 127):
        # 1. 计算初始值
        cur = 47806 * (c + i)
        
        # 2. 如果不是第一位，异或上一位的结果和固定值
        if i != 0:
            cur = cur ^ prev ^ 0x114514
        
        # 3. 对 51966 取模
        cur = cur % 51966
        
        # 4. 如果匹配上了目标值，递归进入下一位
        if cur == target[i]:
            dfs(i + 1, cur, path + [chr(c)])

# 从第 0 位开始搜索，prev 初始为 0（因为第 0 位不涉及异或）
dfs(0, 0, [])

# 打印所有找到的解
print("找到的所有解（内层内容）：")
for idx, s in enumerate(solutions):
    print(f"{idx}: {s}")
```

![QQ\_1788614505973\.png](/images/moectf-2025/QQ_1788614505973.png)

能看出第三个解比较合理一些 因此flag为:moectf\{Y0u\_Kn0w\_z3\_S0Iv3r\_N0w\_a1f2bdce4a9\}

## **ezandroid\.pro**

flag:moectf\{SM4\_Android\_I5\_Funing\!\!\!\}

找到主函数入口

![f01d9e840b1904f1822a7a889a96dba3\.png](/images/moectf-2025/f01d9e840b1904f1822a7a889a96dba3.png)

题目提示说 涉及到native层的相关知识：

在Android系统中，**Native层**（本地服务层）是指使用C和C\+\+语言实现的一部分系统组件和服务。它位于Java框架层和Linux内核空间之间，主要负责处理一些复杂的计算任务和与底层硬件的交互。

> 题目提示“涉及 native 层面”的意思是：**核心代码不在 Java（DEX）里，而在 SO（ELF）动态库中**。
> 
> - **Java 层只是负责接收输入，然后把输入传给 ****`check`**** 函数。**
> 
> - **真正的加密、解密、比较运算，全都在 ****`libxx.so`**** 的汇编/C\+\+ 代码里执行。**
> 
> - 所以你在 JADX 里只能看到一个 `public native boolean check(String str);`，没有任何算法细节。
> 
> 

### SM4

SM4 是中国国家密码管理局发布的**对称加密算法**（类似于 AES）。

- 密钥长度：128 位（16 个字节）

- 分组长度：128 位（16 个字节）

- 常见模式：ECB（电子密码本）或 CBC（密码块链接）

如何分辨：

如果函数名被混淆了（比如叫 `sub_1234`），就进去看有没有一个**固定的 256 字节的 S 盒**（替换盒）。**SM4 的 S 盒开头是 ****`0xD6, 0x90, 0xE9, 0xFE, 0xCC, 0xE1, ...`**只要看到这串常数，铁定是 SM4。

SM4 有三大“指纹”：

- 指纹 1：S 盒（S\-Box）
SM4 算法内部有一个固定的 256 字节替换表，开头是：
`D6 90 E9 FE CC E1 3D B7 16 B6 14 C2 28 FB 2C 05 ...`
如果你在 IDA 的数据段（`.rodata`）里看到这串字节，100% 是 SM4。

- 指纹 2：系统参数 FK（4 个常数）
SM4 密钥扩展时用到 4 个固定常数：
`0xA3B1BAC6`, `0x56AA3350`, `0x677D9197`, `0xB27022DC`
只要看到这 4 个值，立刻锁定 SM4。

- 指纹 3：轮常数 CK（32 个常数）
密钥扩展还会用到 32 个轮常数，开头是：
`0x00070E15`, `0x1C232A31`, `0x383F464D`\.\.\.
如果看到这种有规律的递增常数，也是 SM4 的特征。

**解题步骤：**

1. 找密钥（Key）

2. 找密文（CipherText）

3. 找模式（ECB / CBC）
然后直接用 Python 的 `gmssl` 库一把梭解密。

安装gmssl库：

```C
pip install gmssl
```

![765504a9d95e4d2a0b379aa21c78f00e\.png](/images/moectf-2025/765504a9d95e4d2a0b379aa21c78f00e.png)

### 伪代码分析

#### 1

既然题目说了主要的加密逻辑是在so文件中 我们就用ida查看so文件

![33b518785064e5bb514e6400eff0737c\.png](/images/moectf-2025/33b518785064e5bb514e6400eff0737c.png)

很容易看出是sm4

**到中间的一系列if\-else逻辑都是没用的**

特征：

**特征一：判断长度是否 ****`>= 0x17`****（23）**

```C
if ( v10 >= 0xFFFFFFFFFFFFFFF0LL )   // 溢出检查，无视
...
if ( v10 >= 0x17 )  // 就是这个！23字节是分界线
```

这是 C\+\+ 标准库的短字符串优化（SSO）。长度 ≤ 22 的字符串存在栈上（不申请堆内存），长度 ≥ 23 的字符串去堆上申请空间。

**特征二：****`operator new`**** 和 ****`memcpy`**** 成对出现**

```C
v12 = (char *)operator new(v14);   // 堆上申请内存
memcpy(v12, v7, v11);              // 把原始数据拷贝进去
```

这就是“字符串太长，栈上放不下，去堆里找个位置放”。

**特征三：标志位赋值（****`LOBYTE`**** / ****`| 1`****）**

```C
v25[0] = v14 | 1;    // 表示这是**堆分配**的字符串
LOBYTE(v25[0]) = 2 * v10;  // 表示这是**栈分配**的短字符串
```

这整串做的事情就是

> “把 C 字符串 `v7` 复制到一个 C\+\+ string 对象 `v25` 里。”
> 
> 

**至于它是走 ****`if`**** 分支还是 ****`else`**** 分支，完全不改变算法逻辑，只是内存分配策略不同。**

#### 2

主函数调用 `sm4Encrypt` 后面的代码是什么意思？？

```C++
// 第1步：执行加密（输入v24，密钥v23，输出v21）
sm4Encrypt(v21, v24, v23);

// 第2步：从 std::string 对象 v21 中，**提取出真正的 C 字符串指针（s1）**
// 下面这堆 **v13、v14、LOBYTE、&1 都是 std::string 的内部结构解析**
// 目的只有一个：**让 v19（或 s1）指向加密后的十六进制文本数据**
v13 = (__int64 *)v21[1];
v14 = (unsigned __int64)LOBYTE(v21[0]) >> 1;
if ( ((__int64)v21[0] & 1) == 0 )
    v13 = (__int64 *)((unsigned __int64)LOBYTE(v21[0]) >> 1);
// ... 省略中间的一些冗余判断 ...

// 第3步：最终比较（这是唯一的判决点！）
// **v19（加密结果） 和 v12（硬编码密文） 比较，长度 0x60 = 96 字节**
**v10 = memcmp(s1, v12, 0x60u) == 0;**
```

> 把加密结果从 C\+\+ 字符串里抠出来，跟硬编码在程序里的那串 `4EEB...` 逐个字节对比（memcmp），一样就返回真（正确），不一样就返回假（错误）。
> 
> 

那些 `v13`、`v14`、`LOBYTE` 的操作，**是 C\+\+ 标准库在处理 ****`std::string`**** 时为了区分“短字符串（栈上）”和“长字符串（堆上）”做的底层内存管理，跟算法本身毫无关系。**以后看到 **`LOBYTE(v21[0]) >> 1`**** 和 ****`& 1`**** 这种位运算，直接脑补成 ****`string 对象取地址`**** 就行。**

exp:

```Python
from gmssl import sm4

key = b"moectf2025!!!!!!"
ct = bytes.fromhex("4EEB1EEF2914D79BFA8C5006332097ED2EF06C4A59CAE31C827A08D45CC649C0B971BF2EFBCB160E531A646DF7A6AC0B")

c = sm4.CryptSM4()
c.set_key(key, sm4.SM4_DECRYPT)
pt_padded = c.crypt_ecb(ct)
print(pt_padded)
# b'moectf{SM4_Android_I5_Funing!!!}\x06\x06\x06\x06\x06\x06'
```

### exp解释

**`c = sm4.CryptSM4()`**

- `sm4`：这是第 1 行 `from gmssl import sm4` 带进来的库名字。你不能改，改了 Python 就找不到这个库。

- `CryptSM4`：这是 `gmssl` 库里写好的一个“类”（可以理解为蓝图/模具）。这也是库规定的，你不能改。

- `CryptSM4()`：这行代码的意思是“照着这个模具，**在内存里造出一个新的 SM4 工具对象**”。

汇编级理解： 相当于 `malloc` 了一块内存，里面放着 SM4 解密需要的状态数据，然后把这块内存的地址存到变量 `c` 里。

**`c.set_key(key, sm4.SM4_DECRYPT)`**

- `c`：这是你刚才贴了标签的那个工具对象。

- `.`（点）：这是一个连接符，意思是要操作 `c` 这个工具。

- `set_key`：这是库自带的内部函数（方法）。你不能改，它的作用是把密钥喂给工具。

- `(key, sm4.SM4_DECRYPT)`：括号里是传给这个内部函数的两个参数。

    - `key`：你在第 3 行定义的密钥变量（你自己起的名字）。

    - **`sm4.SM4_DECRYPT`****：这是库内部定义的常量**，告诉工具“要解密，不是加密”。

**`pt_padded = c.crypt_ecb(ct)`**

- `c`：还是那个工具对象。

- `.`：连接符。

- `crypt_ecb`：这是库自带的核心解密函数。你不能改。它的作用是用 ECB 模式去解密数据。

- `(ct)`：括号里只有一个参数，就是你在第 4 行准备的密文变量（你自己起的名字，代表二进制密文）。

- `pt_padded =`：这里用了等号！因为 `crypt_ecb` 这个函数会产出新的数据（解密后的明文）。你要用 `pt_padded`（你自己起的名字）这个变量把产出的明文接住、保存下来。

## **A simple program**

flag:moectf\{Y0u\_P4ssEd\!\!\}

![QQ\_1788704269129\.png](/images/moectf-2025/QQ_1788704269129.png)

很自然地去查看Str2

？欺骗啊欺骗 浪费我的感情 这是假的flag！

![b1661bf2413f4702436724c04f3b8857\.png](/images/moectf-2025/b1661bf2413f4702436724c04f3b8857.png)

### 为什么 `Str2` 里的内容是假的

其中有三行看似没用的代码

```C
Thread = CreateThread(0, 0, StartAddress, 0, 0, 0);  // 1. 创建一个新线程
v4 = Thread;
if ( Thread )
{
    WaitForSingleObject(Thread, 0xFFFFFFFF);        // 2. 主线程在这里等着！
    CloseHandle(v4);
}
```

执行顺序：

1. 程序一启动，`main` 函数立刻创建了一个新线程，这个线程的入口函数是 `StartAddress`。

2. 紧接着，主线程（`main`）调用了 `WaitForSingleObject`，把自己挂起（暂停）了。

3. 在 `main` 被暂停的这段时间里，新线程 `StartAddress` 正在后台疯狂运行！

4. `StartAddress` 线程唯一的目的就是把全局变量 `Str2` 里的假内容，解密/覆盖成真正的 Flag。

5. 等 `StartAddress` 线程执行完毕退出，`WaitForSingleObject` 才返回，主线程继续执行。

6. 这时才执行 `printf("plz input...")` 和 `strncmp(Str1, Str2, ...)`。

解决这种题目的标准答案：动态调试

1. 用 OD（OllyDbg）或 x64dbg 加载这个 exe。

2. 在 `strncmp` 函数调用处下断点（或者直接找到 `if ( !strncmp(Str1, Str2, ...)` 这一行）。

3. 运行程序，输入任意字符串（比如 `123456`），点击确定。

4. 程序会断在 `strncmp` 处。

5. 这时，查看 `Str2` 指向的内存地址（在 x64dbg 的数据窗口转到 `Str2` 的地址）。

6. 你会发现，内存里躺着的已经不是 IDA 里的那串假字符了，而是解密后的真实 Flag！

这叫做 “**内存补丁**” 或 “**运行时代码/数据解密**”。

### 静态做法

![a29626bc81ebdaf3f360a570be271c2d\.png](/images/moectf-2025/a29626bc81ebdaf3f360a570be271c2d.png)

> 原来这个 `0x401510` 假函数，被当作“替补队员”的地址，打包成参数，准备交给 `sub_401570` 去替换系统真正的 `strncmp`。
> 
> 

作者写了一个函数 里面有完整的密文和加密逻辑

![29503f5ccc74151080df7b8489d9b1d3\.png](/images/moectf-2025/29503f5ccc74151080df7b8489d9b1d3.png)

![QQ\_1788783577359\.png](/images/moectf-2025/QQ_1788783577359.png)

密文

```C
unsigned char ida_chars[] =
{
   78,  76,  70,  64,  87,  69,  88, 122,  19,  86, 
  124, 115,  23,  80,  80, 102,  71,   2,   2,  94, 
    0,   0,   0,   0
};
```

Exp

```Python
import sys

# 1. 
enc_hex = "4E4C46405745587A13567C73175050664702025E"

# 2. 转成字节
enc_bytes = bytes.fromhex(enc_hex)

# 3. 逐字节异或 0x23（这是解密，因为加密也是异或同一个值）
flag_bytes = bytes([b ^ 0x23 for b in enc_bytes])

# 4. 输出结果
try:
    flag = flag_bytes.decode('utf-8')
    print(f"解出的 flag 是：{flag}")
except:
    print(f"解出的字节（如有乱码请忽略）：{flag_bytes.hex()}")
```

flag：moectf\{Y0u\_P4ssEd\!\!\}

### 动态调试\-\-x64dbg ？

在命令栏敲 `bp strncmp` 下断点：

![QQ\_1788705817893\.png](/images/moectf-2025/QQ_1788705817893.png)

> 输入 `bp strncmp` 后，x64dbg 确实设置了断点。当你按 `F9` 运行并输入字符串后，程序调用了 `strncmp`，所以断点被触发，你被带到了 `strncmp` 的“肚子里”（系统代码里）。
> 
> 

接着**同时按下 ****`Alt + K`**，打开调用堆栈窗口（Call Stack）

![2346f423a2193b8f146adceca09919a3\.png](/images/moectf-2025/2346f423a2193b8f146adceca09919a3.png)







## guess

flag：moectf\{RrRRccCc44$$\_w1th\_fl0w3r\!\!\_3c6a11b5\}

进入ida之后反编译功能失败 可能是有花指令

先看看字符串

![QQ\_1788838899564\.png](/images/moectf-2025/QQ_1788838899564.png)

说是玩一个猜数字的游戏 从0到99 如果猜对了就给我flag

不过我敏锐地发现了有玄机

![QQ\_1788839917449\.png](/images/moectf-2025/QQ_1788839917449.png)

有一个密钥 还有一串看起来像密文的数字

猜测也许是循环异或？

```Python
import binascii

# 1. 密钥
key = b"moectf2025"

# 2. 密文（
cipher_hex = "464DCF81DE6F2E16BE203F10565CCDBFF18CCD6A45967D20DC558FB76C0CC3AE07D154"
cipher_bytes = bytes.fromhex(cipher_hex)

# 3. 尝试用密钥循环异或解密
decrypted = bytes([cipher_bytes[i] ^ key[i % len(key)] for i in range(len(cipher_bytes))])

# 4. 打印结果
try:
    flag = decrypted.decode('utf-8')
    print(f"解出的 flag 是：{flag}")
except:
    # 如果解出来不是纯文本，打印十六进制看看
    print(f"解出的十六进制：{decrypted.hex()}")
    print(f"尝试转为 ASCII：{decrypted}")

```

![QQ\_1788840224494\.png](/images/moectf-2025/QQ_1788840224494.png)

非也。

问了ai

发现ai是用代码查找可疑字符串和可疑字符串的 学习一下

在使用这些命令的时候记得要修改文件路径

```C
cd **/mnt**/c/Users/hp/Desktop
```

### Strings抓明文线索

```C
$ **strings -n 6 guess.exe | grep -iE "guessed|flag|moectf|right|input"**
Welcome to MoeCTF 2025!
If you successly guessed it, I will give you the flag!
Please input your number:
Invalid input
You are right!
The flag is moectf{
That's not right...
moectf2025
```

### Strings抓可疑密文

```C
**$ strings -n 6 guess.exe | grep -E "^[0-9A-F]{16,}$"**
464DCF81DE6F2E16BE203F10565CCDBFF18CCD6A45967D20DC558FB76C0CC3AE07D154
```

### 看导入表筛掉"标准算法"

> **用 ****`pefile`**** 或者****`objdump`****把所有 ****`import`**** 列出来。**看到 `KERNEL32.dll` 有 `IsDebuggerPresent`、`OutputDebugStringA`——这是反调试签名，先记着。**没有 ****`CryptEncrypt`****、****`BCryptEncrypt`**** 这种 Win32 加密 API。**
> 
> 

**→ 说明加密是程序自己写的，不是调系统库。这意味着我们得读反汇编自己认算法。**

#### objdump

```C
objdump -p guess.exe | grep -A 30 "DLL Name"
```

命令解释：

把 `|`（竖线）想象成 “传送带”：
左边命令的输出结果，被传送带（`|`）交给右边的命令去处理。

##### 1

- `objdump`：这是 Ubuntu 自带的一个“文件解剖师”，**专门用来查看二进制文件（\.exe、\.elf等）的内部结构。**

- `-p`：是 **`--private-headers`** 的缩写，意思是 “把文件头里的私密细节都抖出来”。对于 Windows 的 `.exe` 文件，这就会把**导入表**（Import Table）全部列出来（也就是程序调用了哪些外部 DLL 和函数）。

- `guess.exe`：要分析的目标文件。

单独运行 `objdump -p guess.exe` 会输出几百行杂乱的信息（包括文件头、节区、重定位表等），根本看不过来。

##### 2

- `grep`：相当于 Windows 里的 `Ctrl+F`（搜索关键词），专门从大段文字中抓取包含特定关键词的那一行。

- `"DLL Name"`：这是你要搜索的关键词。在 `objdump` 输出的导入表格式中，**每引入一个 DLL**（如 `KERNEL32.dll`），前面都会有一行标记为 `DLL Name`。

- `-A 30`：**是 ****`--after-context=30`**** 的缩写，意思是 “找到‘DLL Name’这一行后，把它下面的 30 行也一起打印出来”。**

##### DLL

DLL（Dynamic Link Library，动态链接库） 就是 Windows 系统里预先写好的 “公共函数超市”。里面存放着各种现成的代码功能（函数），比如：

- 创建文件（`CreateFile`）

- 弹出对话框（`MessageBoxA`）

- **检测是否在调试**（`IsDebuggerPresent`）

**为什么叫“动态链接”（Dynamic Link）？**

因为你的 `guess.exe` 在编译的时候，并没有把超市里的盐（函数代码）塞进自己的文件里。

- 它只是记了个小纸条：“我需要 `KERNEL32.dll` 里的 `IsDebuggerPresent` 函数”。

- 等到 `guess.exe` 真正运行的时候，操作系统才会去把 `KERNEL32.dll` 这个文件从硬盘加载到内存，然后把 `guess.exe` 和它“链接”起来，让 `guess.exe` 能调用里面的函数。

这就是 “动态” 的含义：运行时才去加载，而不是编译时打包进去。

#### 抓重点

全部的dll太多了 我们要抓一些重点来看

![QQ\_1788941211728\.png](/images/moectf-2025/QQ_1788941211728.png)

最先关注第一类：

> 这个程序确实有反调试机制。你之后写 Frida 脚本，第一件事就是把 `IsDebuggerPresent` 干掉。
> 
> 

第二类：

这些函数告诉你“数据是怎么被处理的”，是逆算法的重要路标。

#### 标准库

##### 用了系统真正的标准加密

\(MS Crypto API）

这是唯一你在导入表里能直接看到“加密”字样的标准算法。

- 你会看到 `CRYPT32.dll` 或 `BCRYPT.dll` 这两个系统库。

- 里面会有函数名：`CryptEncrypt`（加密）、`CryptDecrypt`（解密）、`CryptAcquireContext`（获取上下文）等。

> 判定标准：如果导入表里出现上面这几个函数，说明它用了 Windows 自带的加密（如 AES、RSA 等），属于“官方标准算法”。
> 
> 

##### 用了第三方加密

\(OpenSSL / LibTomCrypt 等）

如果作者用了著名的开源加密库，导入表里会出现 DLL 文件名，而不是算法名。

- 你会看到 libcrypto\-3\-x64\.dll 或 libssl\.dll 等。

- 函数名会是 AES\_encrypt、RSA\_public\_encrypt 之类的（直接带算法缩写）。

判定标准：看见 libcrypto 或具体的 AES\_ 前缀，也是标准算法（只不过不是微软写的）。

##### 用了base64

这个不是加密，是编码！

Base64 在 Windows 里没有专用的系统 API，只有间接工具：

- 如果你看到 `CRYPT32.dll` 里有 `CryptBinaryToStringA`，说明它用了系统自带的 Base64 转换。

- 但如果作者是自己手写的 Base64 表（几乎所有 CTFer 都这么干），导入表里绝对没有 Base64 字样，只有 `memcpy`、`malloc` 和大量的位运算（`>>`、`&` 0x3F）

### 花指令

按f5不能反汇编很自然联想到是花指令

我去 发现汇编语言又要复习（）

> `lea`（Load Effective Address，加载有效地址） = “取地址符 `&`”
> 它的作用就是计算一个内存地址，把这个地址值（指针）存到寄存器里，但绝对不去碰那个地址里存的数据。
> 
> 

即`mov` 取值，`lea` 取地址（指针）。

不过`lea` 虽然名义上是“取地址”，但因为 CPU 计算地址的硬件单元很强，编译器经常滥用 `lea` 来做快速算术运算

```C
lea eax, [rcx + rcx*4]   ; 相当于 eax = rcx * 5
```

这时候它根本不是取地址，纯粹是在用地址计算器做乘法。如果你以后看到 `lea` 后面的方括号里是乱七八糟的寄存器和系数相加

![bd443217a1571f6f0e5e2ee32358b51e\.png](/images/moectf-2025/bd443217a1571f6f0e5e2ee32358b51e.png)

发现了！不管是否相等 都会跳转到同一个地址去！！

那么在两条跳转指令的：

```C
.text:0000000140001A5A                 call    near ptr loc_140001A5F+3
```

就完全不可能被执行！

#### 精读汇编代码

由于我看汇编语言实在是非常抵触 所以这次逼着自己看

```Assembly language
push    rbp
push    rbx
mov     eax, 1428h      ; eax = 0x1428 (5160字节)
call    ___chkstk_ms    ; 检查栈空间是否够用
sub     rsp, rax        ; rsp 减去 5160，腾出局部变量空间
lea     rbp, [rsp+80h]  ; 设置新的栈基址指针
call    __main          ; 调用 C++ 初始化（构造全局对象）
```



```Assembly language
mov     ecx, 0          ; 参数: false
call    _ZNSt8ios_base15sync_with_stdioEb ; sync_with_stdio(false)
```

> 对应 C\+\+ 代码 `std::ios::sync_with_stdio(false);`
> 目的：关掉 C 和 C\+\+ 的输入输出同步，让 `cout` 跑得更快（CTF 题里为了防超时经常会加这句）。
> 
> 



```Assembly language
mov     edx, 0          ; 参数: nullptr (空指针)
mov     rax, cs:_refptr__ZSt3cin
add     rax, 10h        ; rax 指向 cin 对象内部
mov     rcx, rax
call    _ZNSt9basic_iosIcSt11char_traitsIcEE3tieEPSo ; cin.tie(nullptr)
```

> 对应 C\+\+ 代码 `std::cin.tie(nullptr);`。
> 意思是：“输入的时候不要强制刷新输出缓冲区”，也是常规优化操作。
> 
> 



```Assembly language
lea     rax, aWelcomeToMoect ; 取字符串 "Welcome..." 的首地址
mov     rdx, rax        ; 第二个参数（字符串指针）放进 rdx
mov     rax, cs:_refptr__ZSt4cout
mov     rcx, rax        ; 第一个参数（cout对象）放进 rcx
call    _ZStlsISt11char_traitsIcEERSt13basic_ostreamIcT_ES5_PKc ; operator<<
```

连续四次打印

> 对应 C\+\+ 代码 `std::cout << "Welcome to MoeCTF 2025!\n";`
> 调用约定（x64）：第一个参数放 `rcx`，第二个参数放 `rdx`，然后调用 `operator<<`。
> 
> 



以上的大多数代码对“破解算法”确实几乎毫无用处，这叫“**样板代码**”。

- `std::ios::sync_with_stdio(false)`：只是让输入输出变快。

- `std::cin.tie(nullptr)`：只是解除输入输出的绑定。

- 大段的 `lea... call operator<<`：只是打印提示文字。



精读完了 感觉脑中没有多了什么知识（

### 分析跳转

接下来我们跳转到那个函数中

![QQ\_1788945073421\.png](/images/moectf-2025/QQ_1788945073421.png)

还是无法进行反编译

看到是取了一个随机数 因此每次要猜的数字是不一样的 因此几乎不可能猜对

除此之外 我们还能看到一串左移右移之类的代码 这是我们纯手工操作的取模运算

```Assembly language
imul    rax, 51EB851Fh  ; rax = random_num * 0x51EB851F
shr     rax, 20h        ; 右移 32 位
shr     eax, 5          ; 再右移 5 位 (总共右移 37 位)
imul    ecx, eax, 64h   ; ecx = (结果) * 100
mov     eax, edx        ; eax = 原始随机数
sub     eax, ecx        ; eax = 原始随机数 - 上一步结果
**mov     [rbp+var_18], eax  ; 保存到局部变量**
```

> 结论：`[rbp+var_18]` 这个变量里，存的就是 随机数对 100 取模的结果，也就是一个 0 到 99 之间的整数！
> 
> 

#### 常识判断——为什么不用 `div`（除法）？

如果自己写 C 语言代码：`int result = random_num % 100;`
最笨的编译器会直接调用 `div` 指令（除法）。**但 ****`div`**** 指令在 CPU 里非常慢**（消耗几十个时钟周期）。

聪明的编译器（GCC/MinGW 开了 O2 优化）会干一件事：**用“乘法 \+ 移位”来替代“除法”。**
因为乘法（`imul`）和移位（`shr`）在 CPU 里极快，所以编译器会预先计算好一个魔数（Magic Number）。

![QQ\_1788946378645\.png](/images/moectf-2025/QQ_1788946378645.png)

```Assembly language
imul    ecx, eax, 64h   ; ecx = 商 * 100
mov     eax, edx        ; eax = 原始随机数
sub     eax, ecx        ; eax = 原始随机数 - 商*100
```

这在数学上就是：

> 余数 = 被除数 \- \(除数 × 商\)
> 也就是 `random_num % 100`
> 
> 

而取模运算的本质定义就是 `a % b = a - (a/b)*b`。这里用 `64h`（即 100）去乘商，再用原数去减，就是标准的“取余”操作。



接下来 我们继续向下跳转

```Assembly language
.text:0000000140001CAE                 cmp     [rbp+var_14], 9
.text:0000000140001CB5                 jle     loc_140001AD4
```

- `[rbp+var_14]`：还记得之前被初始化为 `0` 的那个计数器吗？就是它。

- `cmp ... , 9`：比较计数器的值是否 ≤ 9。

- `jle`（Jump if Less or Equal）：如果计数器 小于或等于 9，就跳转到 `loc_140001AD4`。

继续向下跳转：

![QQ\_1788946732510\.png](/images/moectf-2025/QQ_1788946732510.png)

继续跳转：

![f3ad8f5533d3316a43ad4eb783f4c1dd\.png](/images/moectf-2025/f3ad8f5533d3316a43ad4eb783f4c1dd.png)

发现这个最关键的代码就只显示了一行 这应该是之前花指令留下的残骸

动态调试

先跳转到我们最关键的函数位置：

```Assembly language
guess.exe+1B41
```

下断点

![QQ\_1788947615214\.png](/images/moectf-2025/QQ_1788947615214.png)

哈哈 这个程序有反调试我忘了我服了 ~~我是傻子~~



Ai这双眼睛到底看来多远。。。。

不是这个到底除了ai能通读我咋能发现呀 瞪眼法纯蹬吗 到时候函数名换一个不是炸了吗

![468f875f50ab13030b0c4f434f7c25e6\.png](/images/moectf-2025/468f875f50ab13030b0c4f434f7c25e6.png)

看出是rc4

但是rc4标准解密解出来是一个乱码

### 反编译分析

重新阅读关于rc4的代码

发现rc4被魔改了：

![296e6111e0f302b572f5c74b831e922b\.png](/images/moectf-2025/296e6111e0f302b572f5c74b831e922b.png)

```C
for ( i = 0; i <= 255; ++i )
{
    result = (int *)std::vector<int>::operator[](a1, a2, i, v32, v5, v6, v18, v22);
    *result = i;
}
```

> `for (int i = 0; i < 256; i++) S[i] = i;`
> 这是初始化 S 盒（0\~255 的置换表）。
> *（说明：**`std::vector<int>::operator[]`** 就是取数组第 **`i`** 个元素，**`*result = i`** 就是把当前下标的值设为 **`i`**。）*
> 
> 

相当于：

```C++
// 初始化累计变量 v29（也叫“真正的 RC4 j”）
v29 = 0;

// 循环计数器 i（在 F5 里写作 j）从 0 到 255
for ( j = 0; j < 256; j++ )
{
    // 用当前累计值 v29 加上 S[j]
    temp1 = S[j] + v29;

    // 用循环计数器 j 取密钥的第 j % len 个字符
    key_byte = key[j % key_len];

    // 加上 42（魔改点）
    temp2 = temp1 + key_byte + 42;

    // 更新累计变量（v29），只取低 8 位（相当于 % 256）
    v29 = temp2 & 0xFF;

    // 交换 S 盒里第 j 个和第 v29 个元素
    swap(S[j], S[v29]);
}
```

第二个循环里最关键的几行（我帮你把那些 `operator[]` 翻译成伪变量）：

1. `v7 = S[j] + v29;` （这里的 `v29` 就是累加的 `j`）

2. `v8 = key[j % keylen];`

3. `v9 = v7 + *v8 + 42;` （注意这里！）

4. `v29 = (v9) & 0xFF;` （汇编里的 `movzx edx, dl` 就是取低 8 位）

5. 接下来是 `swap(S[j], S[v29])`;



- 编译器把 `% 256` 拆成了“位运算”和“移位\+加减”来优化（因为 `% 256` 等价于 `& 0xFF`，但编译器为了效率用了更复杂的整数除法优化指令）。

对比标准版KSA

Exp

```Python
def rc4_ksa(key):
    S = list(range(256))
    j = 0
    for i in range(256):
        j = (j + S[i] + key[i % len(key)] + 0x2a) & 0xFF  # 唯一改动
        S[i], S[j] = S[j], S[i]
    return S

def rc4_prga(S, data):
    S = S[:]
    i = j = 0
    out = bytearray()
    for byte in data:
        i = (i + 1) & 0xFF
        j = (j + S[i]) & 0xFF
        S[i], S[j] = S[j], S[i]
        K = S[(S[i] + S[j]) & 0xFF]
        out.append(byte ^ K)
    return bytes(out)

key = b"moectf2025"
enc = bytes.fromhex("464DCF81DE6F2E16BE203F10565CCDBFF18CCD6A45967D20DC558FB76C0CC3AE07D154")
plain = rc4_prga(rc4_ksa(key), enc)
print(plain)

#b'RrRRccCc44$$_w1th_fl0w3r!!_3c6a11b5'
```

所以 flag：moectf\{RrRRccCc44$$\_w1th\_fl0w3r\!\!\_3c6a11b5\}
