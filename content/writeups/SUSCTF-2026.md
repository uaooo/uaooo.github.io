+++
title = 'SUSCTF-2026'
date = '2026-10-04T12:00:00+08:00'
draft = false
summary = ''
tags = []
showtoc = true
+++
## classical

附件：

[classical](图片和附件/classical)

找到main函数

![](/images/SUSCTF-2026/QQ_1789969359644.png)

看出'ctfreverse'是密钥 要找到这道题的secret

我们输入的为v4 做了加密之后得到v5 然后v5和v6最比较 如果相同则拿到flag

加密部分

![](/images/SUSCTF-2026/QQ_1789969578485.png)

- 密钥被循环使用

```C
v3 = strlen(a2);          // 密钥长度
...
a2[v5 % v3]               // 用 v5 对密钥长度取模，实现循环
```

- 移位量由密钥字母决定

```C
result_1[i] = (a1[i] - 97 + a2[v5 % v3] - 97) % 26 + 97;
```

- `a1[i] - 97`：把明文字母转成 0\~25 的数字（`a=0, b=1, …, z=25`）。

- `a2[v5 % v3] - 97`：把当前密钥字母也转成 0\~25 的数字。

- 两者相加，再 `% 26`，最后 `+ 97` 转回小写字母。

这是**维吉尼亚加密**：

```C
密文 = (明文索引 + 密钥索引) mod 26。
```

这个加密是一种古典加密 同时对应了这道题的题目

另外 这个非字母字符原样保留 且不消耗密钥

```Java
if ( a1[i] <= 96 || a1[i] > 122 )   // 不是小写字母
{
    if ( a1[i] <= 64 || a1[i] > 90 ) // 也不是大写字母
    {
        result_1[i] = a1[i];         // 原样复制
    }
    else
    {
        // 大写字母处理，++v5
    }
}
else
{
    // 小写字母处理，++v5
}
```

看完加密函数 接下来我们就要找到v6这个字符 他是trans函数写出来的

![](/images/SUSCTF-2026/QQ_1789970503562.png)

这里有一个小陷阱 那个字符串只是全部的一部分 是ida自己取的名字

真正的完整字符串是

![](/images/SUSCTF-2026/QQ_1789970692525.png)

```C
46783477204569726766653376752c20506a6367306869206b6720376c6720507
4697079207377204a6978336b787620496939317276777631707a21
```

然后我们知道这些之后就可以写解密脚本了

把那个加密函数反向进行解密 其实就是把加减互换一下就可以解密了

Exp

```Python
hex_str = ("46783477204569726766653376752c20"
           "506a6367306869206b6720376c672050"
           "74697079207377204a6978336b787620"
           "496939317276777631707a21")

expected = bytes.fromhex(hex_str).decode()
key = "ctfreverse"

def decrypt(cipher, key):
    out = []
    ki = 0
    for c in cipher:
        if 'a' <= c <= 'z':
            p = (ord(c) - ord('a') - (ord(key[ki % len(key)]) - ord('a'))) % 26
            out.append(chr(p + ord('a')))
            ki += 1
        elif 'A' <= c <= 'Z':
            p = (ord(c) - ord('A') - (ord(key[ki % len(key)]) - ord('a'))) % 26
            out.append(chr(p + ord('A')))
            ki += 1
        else:
            out.append(c)
    return ''.join(out)

plaintext = decrypt(expected, key)
print(plaintext)
print("susctf{" + plaintext + "}")
```

最后输出flag：susctf\{De4r Newcom3rs, Welc0me to 7he World of Rev3rse En91neer1ng\!\}

## **【中秋限定】玉兔的月饼工坊**

[【中秋限定】玉兔的月饼工坊\.zip](图片和附件/【中秋限定】玉兔的月饼工坊.zip)

### 分析

![](/images/SUSCTF-2026/QQ_1790325916189.png)

附件解压之后发现是一个jar文件

JAR 就是 Java Archive，本质是一个 ZIP 压缩包，只是里面通常装的是 Java 程序：

- `META-INF/MANIFEST.MF`：清单文件，里面常有 `Main-Class: xxx`，指定程序入口。

- `*.class`：Java 编译后的字节码，反编译后基本能还原成 Java 源码。

- `resources/`、图片、音频、FXML、HTML、JS 等：资源文件。

CTF RE 的核心不在页面资源，而在 `.class` 字节码里。

![](/images/SUSCTF-2026/QQ_1790326137134.png)

跳转到jar文件所在的桌面位置

```Bash
cd /mnt/c/Users/hp/Desktop 
```

![](/images/SUSCTF-2026/QQ_1790326539682.png)

我们为后续的逆向操作准备一个专属的 Linux 工作目录，避开 Windows 挂载盘。

```Bash
mkdir -p ~/ctf
cp yutu-mooncake-workshop.jar ~/ctf/
cd ~/ctf
```

> 1. `mkdir -p ~/ctf`
> `mkdir` 是 make directory，创建文件夹。
> `~` 在 Linux 里代表当前用户的主目录（你的 WSL 用户是 `uaooo`，所以 `~` 就是 `/home/uaooo`）。
> `-p` 的意思是：如果 `ctf` 文件夹已经存在，不要报错；如果上级目录不存在，也一并创建。
> 这条命令相当于在你的 WSL 家目录下建一个叫 `ctf` 的文件夹，专门放 CTF 题目。
> 
> 2. `cp challenge.jar ~/ctf/`
> `cp` 是 copy，复制文件。
> 把当前目录下的 `challenge.jar` 复制到刚才建的 `~/ctf/` 文件夹里。
> 
> 3. `cd ~/ctf`
> 切换当前工作目录到 `~/ctf`，之后的操作都在这里进行。
> 
> 



```Bash
file yutu-mooncake-workshop.jar
unzip -l yutu-mooncake-workshop.jar
unzip -p yutu-mooncake-workshop.jar META-INF/MANIFEST.MF
```

1. `file yutu-mooncake-workshop.jar`：识别这个文件的真实类型。

2. `unzip -l yutu-mooncake-workshop.jar`：**列出压缩包里的所有文件，但不解压。**

3. `unzip -p yutu-mooncake-workshop.jar META-INF/MANIFEST.MF`：把 JAR 包里的 `META-INF/MANIFEST.MF`** **这个**文件的内容直接输出到屏幕**，不保存到磁盘。

![](/images/SUSCTF-2026/QQ_1790326864235.png)

### 反编译

接下来我们反编译整个jar文件

#### CFR反编译器

CFR 是一个**把 Java 字节码（**`.class`**）翻译回 Java 源代码（**`.java`**）的工具**，专门用于反编译。

下载

```Bash
wget https://github.com/leibnitz27/cfr/releases/download/0.152/cfr-0.152.jar -O cfr.jar
ls -lh cfr.jar
```

太慢的话可以换成阿里云镜像下载

```Bash
rm -f cfr.jar
wget -c https://maven.aliyun.com/repository/public/org/benf/cfr/0.152/cfr-0.152.jar -O cfr.jar
```

下载完成后进行反编译：

```Bash
java -jar cfr.jar yutu-mooncake-workshop.jar --outputdir out
```

含义：用 CFR 这个反编译工具，把 `yutu-mooncake-workshop.jar` 里面的 `.class` 字节码，还原成 `.java` 源代码，并输出到 `out` 文件夹里。

![](/images/SUSCTF-2026/QQ_1790329425600.png)



```Bash
ls out/ctf/mooncake
```

- `ls`：列出目录里的文件。

- `out/ctf/mooncake`：刚才 CFR 输出的文件夹路径。

![](/images/SUSCTF-2026/QQ_1790329656702.png)

接下来 全局搜索可疑字符串

```Bash
grep -RIn -E "flag|ctf|secret|key|pass|win|success|Base64|Cipher|xor|decode" out
```

> - `grep`：在文本里搜关键词。
> 
> - `-R`：递归搜索（连子文件夹一起搜）。
> 
> - `-I`：忽略二进制文件（只搜文本文件）。
> 
> - `-n`：显示匹配的行号。
> 
> - `-E`：支持正则表达式。
> 
> - `"..."`：要搜的词，用 `|` 分隔，意思是“或者”。
> 
> - `out`：在 `out` 文件夹里搜。
> 
> 

```Bash
grep -RIn -E "flag\{|secret|Base64|Cipher|xor|win|success|pass|vault|char\[\]" out/ctf/mooncake
```

会发现这样没有任何输出

说明：**常量池里没有直接的字符串 flag，必须看字节码理解算法。**

换个思路\-\-

我们在刚刚反编译出的文件中找到最可疑的文件\-\-SecrrtVault（秘密金库）

```Bash
grep -RIn "SecretVault" out/ctf/mooncake
```

看哪些文件引用了 `SecretVault`

![](/images/SUSCTF-2026/QQ_1790331619057.png)

信息：

1. 在哪定义的：`SecretVault.java` 里写了 `revealFirst()` 和 `revealSecond()` 两个方法，这俩方法分别调用了 `d(1834636965)` 和 `d(1546352026)`。

2. 在哪被调用：`GamePanel.java`（游戏主界面）在特定条件下（比如玩家通关），会调用这两个方法弹窗。

所以，**核心逻辑全在 **`SecretVault.java`** 里的那个 **`d()`** 方法里。**

> - `revealFirst` 和 `revealSecond`：是作者认真起名的。名字直译过来就是“揭晓第一个”、“揭晓第二个”。这是给游戏界面用的。
> 
> - `.d`：是作者故意乱起名的（混淆）。作者不想让你知道这个按钮是干嘛的，所以就起了一个毫无意义的单字母名字 `d`。
> 
> 

可以看看这两个函数的完整流程：（打印第22行到第30行）

```Bash
sed -n '22,30p' out/ctf/mooncake/SecretVault.java
```

![](/images/SUSCTF-2026/QQ_1790336755322.png)

#### d方法

接下来 我们就进入最关键最核心的方法：

（打印第30行到150行）

```Bash
sed -n '30,150p' out/ctf/mooncake/SecretVault.java
```

![](/images/SUSCTF-2026/QQ_1790337011095.png)

信息：

1. `while (true)`：外层套了一个无限循环，意味着它不会轻易结束，而是不停地转圈。

2. `switch (n2)`：这是分发器。`n2` 就是指示牌，告诉你下一站去哪个数字的房间。

3. `n2 = 数字; continue block21;`：每执行完一个小房间，就给指示牌赋一个新的数字，然后 `continue`（回到循环开头），去下一个数字的房间。

看出这是一个控制流平坦化

##### 控制流平坦化

正常控制流：

```Bash
if (x > 0) {
    y = 1;
} else {
    y = 2;
}
z = y + 3;
```

编译成汇编之后，是这样：

```Bash
entry
  |
  v
判断 x > 0
  |        \
  v         v
y = 1     y = 2
  |        /
  v       v
z = y + 3
  |
  v
exit
```

这叫**控制流图，CFG。节点是基本块，边是跳转。**

基本块就是一段顺序执行、只有一个入口一个出口的指令。

**平坦化之后：**

上面C代码被改写为：

```Java
state = 0;

while (1) {
    switch (state) {
        case 0:
            if (x > 0)
                state = 1;
            else
                state = 2;
            break;

        case 1:
            y = 1;
            state = 3;
            break;

        case 2:
            y = 2;
            state = 3;
            break;

        case 3:
            z = y + 3;
            state = 4;
            break;

        case 4:
            return;
    }
}
```

原来的每个基本块，现在变成了一个 `case`。

执行顺序变成：

```Shell
state = 0
  -> case 0 判断
  -> 如果 x > 0，state = 1
  -> 回到 while 顶部
  -> switch(state) 进入 case 1
  -> y = 1，state = 3
  -> 回到 while 顶部
  -> case 3
  -> z = y + 3，state = 4
  -> case 4
  -> 结束
```

程序之间真实的跳转关系还在，但是被隐藏成了：

```Bash
state = 下一个块的编号
```

这个 `state` 就像软件模拟的程序计数器。CPU 本来用 PC 决定下一条指令，现在程序自己用一个变量决定下一个 case。

###### 为什么叫平坦化？

正常 CFG 有层次、有分支、有循环，像一棵树或者一张有结构的图。

平坦化之后，所有基本块都变成 `case`，它们都从同一个 `dispatcher` 分发出去，执行完又回到 `dispatcher`：

```Bash
+------------+
        | dispatcher |
        | switch(state) |
        +------------+
         /  |  |  |  \
     case0 case1 case2 case3 ...
         \  |  |  |  /
        +------------+
        | dispatcher |
        +------------+
```

从 CFG 上看，它变得很“扁”：

- 深度很浅；

- 宽度很大；

- 所有块都围着分发器转；

- 原本的嵌套、分支、循环结构消失了。

所以叫控制流平坦化。

###### 平坦化之后隐藏了什么？

正常代码中，跳转关系是显式的：

```Assembly language
cmp eax, 0
jg  loc_1
jmp loc_2
```

平坦化之后，跳转变成：

```C
state = 3;
break;
```

Or

```C
state = 0x8A2F;
continue;
```

反编译器看到的是巨大的 `while + switch`，但很难直接看出：

- 哪个 case 先执行；

- 哪个 case 是条件分支；

- 哪个 case 是循环；

- 哪个 case 是异常路径；

- 真实逻辑顺序是什么。

它把“控制流”藏进了“状态变量的赋值”。

总结：**逻辑明明是一样的，但是执行顺序被完全打乱了**，根本无法顺着读下来。

###### 逆向时识别

典型特征：

- 函数里有一个巨大的 `while(1)` 或 `for(;;)`；

- 里面一个巨大的 `switch(state)`；

- 有一个变量频繁被赋值，然后回到循环顶部；

- 很多 `case` 只做一点点事，然后设置 `state`；

- 反编译器给出的伪代码像状态机；

- 函数 CFG 呈星形，所有块都指向 dispatcher。

##### 代码分析

```Java
private static String d(int n) {
        Object[] objectArray = new Object[7];
        int[] nArray = new int[5];
        nArray[0] = n;
        int n2 = 83;
        block21: while (true) {
            try {
                while (true) {
                    switch (n2) {
                        case 83: {
                            nArray[1] = SecretVault.h(nArray[0]);
                            n2 = 25;
                            continue block21;
                        }
                        case 25: {
                            n2 = nArray[1] == -525158178 ? 107 : 65;
                            continue block21;
                        }
                        case 65: {
                            n2 = nArray[1] == -698505751 ? 47 : 122;
                            continue block21;
                        }
                        case 107: {
                            nArray[2] = 0;
                            objectArray[0] = A0;
                            objectArray[1] = A1;
                            n2 = 53;
                            continue block21;
                        }
                        case 47: {
                            nArray[2] = 1;
                            objectArray[0] = B0;
                            objectArray[1] = B1;
                            n2 = 53;
                            continue block21;
                        }
                        case 53: {
                            objectArray[2] = SecretVault.j((byte[])objectArray[0], (byte[])objectArray[1]);
                            n2 = 103;
                            continue block21;
                        }
                        case 103: {
                            objectArray[3] = SecretVault.k(nArray[1]);
                            n2 = 13;
                            continue block21;
                        }
                        case 13: {
                            objectArray[4] = SecretVault.u(115);
                            n2 = 92;
                            continue block21;
                        }
                        case 92: {
                            objectArray[5] = SecretVault.u(45);
                            n2 = 114;
                            continue block21;
                        }
                        case 114: {
                            objectArray[6] = Cipher.getInstance((String)objectArray[4]);
                            n2 = 38;
                            continue block21;
                        }
                        case 38: {
                            ((Cipher)objectArray[6]).init(2, new SecretKeySpec((byte[])objectArray[3], (String)objectArray[5]));
                            n2 = 74;
                            continue block21;
                        }
                        case 74: {
                            objectArray[0] = ((Cipher)objectArray[6]).doFinal((byte[])objectArray[2]);
                            n2 = 17;
                            continue block21;
                        }
                        case 17: {
                            Arrays.fill((byte[])objectArray[3], (byte)0);
                            n2 = 99;
                            continue block21;
                        }
                        case 99: {
                            return new String((byte[])objectArray[0], StandardCharsets.UTF_8);
                        }
                        case 122: {
                            objectArray[0] = SecretVault.q(nArray[0]);
                            n2 = 68;
                            continue block21;
                        }
                        case 68: {
                            if (((byte[])objectArray[0]).length == Short.MAX_VALUE) {
                                n2 = 53;
                                continue block21;
                            }
                            n2 = 126;
                            continue block21;
                        }
                        case 126: {
                            return SecretVault.e();
                        }
                    }
                    n2 = 126;
                }
            }
            catch (Exception exception) {
                n2 = 126;
                continue;
            }
            break;
        }
    }

    private static int h(int n) {
        int n2 = Integer.rotateLeft(n ^ 0x51ED270B, 11);
        n2 = Integer.rotateRight(n2 + 1831565813, 3);
        return n2 ^ 0xA5A5A5A5;
    }

    private static byte[] k(int n) {
        Object[] objectArray = new Object[2];
        int[] nArray = new int[5];
        nArray[0] = n;
        nArray[1] = 0;
        int n2 = 97;
```

这个迷宫真的非常长非常乱啊 但是莫名很有意思！

利用AI帮助我们进行梳理一下。

> 1. 去 `case 83` 房间：
> 
>     - 代码：`nArray[1] = SecretVault.h(nArray[0]);`
> 
>     - 翻译：调用 `h` 方法，算出个结果存起来。
> 
>     - 下一步：`n2 = 25`（去25号房间）。
> 
> 2. 去 `case 25` 房间：
> 
>     - 代码：`n2 = nArray[1] == -525158178 ? 107 : 65;`
> 
>     - 翻译：如果刚才算出来的值是 `-525158178`，指示牌变成 107；否则变成 65。
> 
>     - 因为第一个密码（revealFirst）传进来的数字是 `1834636965`，我们算出来它的哈希值确实是 `-525158178`，所以下一步去 107 房间。
> 
> 3. 去 `case 107` 房间：
> 
>     - 代码：`nArray[2] = 0; objectArray[0] = A0; objectArray[1] = A1;`
> 
>     - 翻译：给变量赋值，把准备好的数据 `A0` 和 `A1` 放进储物柜。
> 
>     - 下一步：`n2 = 53`。
> 
> 4. 去 `case 53` 房间：
> 
>     - 代码：`objectArray[2] = SecretVault.j(...)`
> 
>     - 翻译：调用 `j` 方法，把刚才的 `A0` 和 `A1` 拼起来（得到密文）。
> 
>     - 下一步：`n2 = 103`。
> 
> 5. 去 `case 103` 房间：
> 
>     - 代码：`objectArray[3] = SecretVault.k(nArray[1]);`
> 
>     - 翻译：调用 `k` 方法，利用哈希值生成一个密钥（key）。
> 
>     - 下一步：`n2 = 13`。
> 
> 6. 去 `case 13` 房间：
> 
>     - 代码：`objectArray[4] = SecretVault.u(115);`
> 
>     - 翻译：调用 `u` 方法，参数是 115。`u` 方法在混淆前就是拼字符串的，它其实是生成 `"AES"` 这个单词。
> 
>     - 下一步：`n2 = 92`。
> 
> 7. 去 `case 92` 房间：
> 
>     - 代码：`objectArray[5] = SecretVault.u(45);`
> 
>     - 翻译：调用 `u` 方法，参数是 45。生成的是 `"AES/ECB/PKCS5Padding"`。
> 
>     - 下一步：`n2 = 114`。
> 
> 8. 去 `case 114` 房间：
> 
>     - 代码：`objectArray[6] = Cipher.getInstance(...)`
> 
>     - 翻译：获取 AES 解密器。
> 
>     - 下一步：`n2 = 38`。
> 
> 9. 去 `case 38` 房间：
> 
>     - 代码：`((Cipher)objectArray[6]).init(2, new SecretKeySpec(...))`
> 
>     - 翻译：用刚才生成的密钥初始化解密器。
> 
>     - 下一步：`n2 = 74`。
> 
> 10. 去 `case 74` 房间：
> 
>     - 代码：`objectArray[0] = ((Cipher)objectArray[6]).doFinal(...)`
> 
>     - 翻译：执行 AES 解密，把密文变成明文 flag！
> 
>     - 下一步：`n2 = 17`。
> 
> 11. 去 `case 17` 房间：
> 
>     - 代码：`Arrays.fill(...)`
> 
>     - 翻译：把密钥清空（安全习惯）。
> 
>     - 下一步：`n2 = 99`。
> 
> 12. 去 `case 99` 房间：
> 
>     - 代码：`return new String(...)`
> 
>     - 翻译：把解密出来的字节转换成字符串，返回给调用者，故事结束。
> 
> 

###### 方法解读

1. **`j`** 方法 —— 拼接密文

- 现场：`case 53`

- 代码：`objectArray[2] = SecretVault.j(objectArray[0], objectArray[1]);`

- 推理：

    - `objectArray[0]` 是 `A0`（32字节），`objectArray[1]` 是 `A1`（32字节）。

    - 把两个东西传给 `j` 方法，返回值放进 `objectArray[2]`。

    - **后面的 **`case 74`** 里，**`objectArray[2]`** 被直接传给 **`doFinal`** 去解密了。而 AES 解密通常需要一个完整的密文块（64字节刚好是4个AES块）**

    - 结论：`j` 方法就是把两个数组拼起来（拼接），组合成完整的密文。

2. **`k`** 方法 —— 生成密钥

- 现场：`case 103`

- 代码：`objectArray[3] = SecretVault.k(nArray[1]);`

- 推理：

    - 它接收 `nArray[1]`（那个哈希值）。

    - 返回值放进 `objectArray[3]`。

    - 接着在 `case 38` 里，`objectArray[3]` 被传给了一个叫 `SecretKeySpec` \-\-“秘密密钥规范”。

    - 结论：**`k`** 方法就是根据哈希值，生成一个 AES 密钥（生成密钥）

3. **`u`** 方法 —— 生成算法字符串

- 现场：`case 13` 和 `case 92`

- 代码：

    - `objectArray[4] = SecretVault.u(115);`

    - `objectArray[5] = SecretVault.u(45);`

    - 然后在 `case 114` 里：`Cipher.getInstance((String)objectArray[4]);`

    - 在 `case 38` 里：`new SecretKeySpec(..., (String)objectArray[5]);`

- 推理：

    - `Cipher.getInstance` 是 Java 标准库里的方法，它专门用来获取加密算法，必须传一个字符串给它（比如 "AES"）。

    - 它接收的是 `objectArray[4]`，而 `objectArray[4]` 是 `u(115)` 算出来的。

    - 同样，`SecretKeySpec` 第二个参数也需要一个字符串（比如 "AES"）。

    - 结论：**`u`** 方法就是根据输入的数字，查表算出对应的字符串（生成字符串）。

4. **`h`** 方法 —— 哈希值

```Java
private static int h(int n) {
    int n2 = Integer.rotateLeft(n ^ 0x51ED270B, 11);
    n2 = Integer.rotateRight(n2 + 1831565813, 3);
    return n2 ^ 0xA5A5A5A5;
}
```

- 特征：有一堆固定的十六进制数字（`0x51ED270B`、`1831565813`、`0xA5A5A5A5`），有循环移位操作（`rotateLeft`、`rotateRight`），有异或操作（`^`）。

- 结论：这看起来就像一个哈希函数或随机数生成器。虽然我们不知道具体是什么哈希，但知道它是“一锅乱炖”，把输入打碎。

### 脚本

按照前面的分析我们先安装一个`pycryptodome`库

```Bash
sudo apt install python3-pycryptodome
```

> 这个包是 Python 用来**做 AES 加密解密**的。
> 
> 

![](/images/SUSCTF-2026/QQ_1790340078463.png)

（因为第一次尝试的时候密码库下载了但是却提示no module 因此我们换为虚拟环境操作）

创建一个虚拟环境

```Bash
cd ~/ctf
python3 -m venv myenv
```

然后激活这个环境

```Bash
source myenv/bin/activate
```

在这个专属环境中装一个密码库

```Bash
pip install pycryptodome
```

![](/images/SUSCTF-2026/QQ_1790341144960.png)



新建一个文件

```Bash
nano solve.py
```

#### Exp

```Python
from Crypto.Cipher import AES
A0 = bytes([0x3F,0x1E,0x70,0x56,0xD3,0x49,0xE0,0x64,0x4A,0x23,0x33,0xDB,
            0xEF,0x50,0xFB,0x80,0xA1,0x37,0xFD,0x1A,0x11,0x06,0x65,0x24,
            0x77,0x12,0xEB,0x95,0x38,0x34,0xB3,0xFC])
A1 = bytes([0x6B,0xC1,0xD5,0xFE,0x28,0x03,0x03,0x0B,0xA8,0x29,0xF9,0x4E,
            0x99,0xF7,0xE8,0x7D,0x4B,0x4A,0x89,0x4A,0xDC,0x14,0xAE,0x4D,
            0xAC,0xB1,0xBE,0x77,0x92,0xD1,0xB7,0xF2])
B0 = bytes([0x17,0x5F,0xA2,0xAB,0xFD,0x98,0xC5,0xC3,0x2B,0xC8,0xBC,0x78,
            0xE0,0x71,0xEF,0xCF,0x27,0xFB,0xBC,0xE7,0x39,0x9D,0xC7,0xD3,
            0xCB,0x17,0xF4,0x7A,0x01,0x3D,0x75,0x6E])
B1 = bytes([0xB0,0x6C,0xCC,0xD0,0x21,0xDF,0xE6,0x6E,0xBA,0x60,0x1A,0x27,
            0x36,0xB4,0xED,0x48,0xD2,0xE6,0xCD,0xF4,0x26,0xA0,0x76,0xD7,
            0x78,0xE4,0x8A,0xA6,0xEA,0xBB,0xA5,0x7A])
X0 = [145,36,215,106,62,184,85,12,225,114,73,165,31,195,136,55]
X1 = [75,241,38,157,112,19,200,94,164,57,223,98,8,183,81,236]
C0 = [50,214,234,202,82,12,207,254,75,32,130,78,74,183,52,173,39,170,39,178]
C1 = [108,8,32]
def sb(x): x&=0xFF; return x-256 if x>=128 else x
def rl(v,n): n&=31; v&=0xFFFFFFFF; return ((v<<n)|(v>>(32-n)))&0xFFFFFFFF
def rr(v,n): n&=31; v&=0xFFFFFFFF; return ((v>>n)|(v<<(32-n)))&0xFFFFFFFF
def h(a):
    v=rl((a^1374496523)&0xFFFFFFFF,11)
    v=rr((v+1831565813)&0xFFFFFFFF,3)
    return (v^0xA5A5A5A5)&0xFFFFFFFF
HF=h(1834636965); HS=h(1546352026)
def p(a,b):
    v=(a^1327217884)&0xFFFFFFFF; i=0
    while i<len(b):
        by=b[i] if b[i]>=0 else b[i]+256
        v=(rl((v^by^i)&0xFFFFFFFF,5)+0x9E3779B9)&0xFFFFFFFF; i+=3
    return (a==HF or a==HS) and len(b)==16
def q(a):
    arr=[0]*16; v=(a^1243072995)&0xFFFFFFFF; i=0; s=42
    while True:
        if s==42: s=23 if i<len(arr) else 88
        elif s==23: v=rl((v+73244475+i)&0xFFFFFFFF,3); s=109
        elif s==88: return bytes((x+256)%256 for x in arr)
        elif s==109:
            arr[i]=sb((v^(i*57))&0xFF); i+=1; s=42
def j(a,b):
    out=[0]*(len(a)+len(b)); idx=[0,0]; s=51
    while True:
        if s==51: s=9 if idx[0]<len(a) else 70
        elif s==9: out[idx[0]]=a[idx[0]]; idx[0]+=1; s=51
        elif s==70: s=18 if idx[1]<len(b) else 113
        elif s==18: out[idx[0]+idx[1]]=b[idx[1]]; idx[1]+=1; s=70
        elif s==113: return bytes((x+256)%256 for x in out)
def k(a):
    ia=[a,0,0,0,0]; A=[None,None]; s=97
    while True:
        if s==97: s=43 if ia[0]==(-525158178&0xFFFFFFFF) else 73
        elif s==43: A[0]=X0; ia[2]=90; ia[3]=25; s=20
        elif s==73: A[0]=X1; ia[2]=195; ia[3]=45; s=20
        elif s==20: A[1]=[0]*16; s=55
        elif s==55: s=94 if ia[1]<16 else 118
        elif s==94:
            v=((ia[2]+ia[1]*23)^(ia[1]<<2))&0xFF; ia[4]=v; s=11
        elif s==11:
            v=(A[0][ia[1]]^ia[4])-ia[3]-ia[1]*3
            A[1][ia[1]]=sb(v&0xFF); s=82
        elif s==82: ia[1]+=1; s=55
        elif s==118: return bytes((x+256)%256 for x in A[1])
        elif s==36: return q(ia[0])
def u(a):
    s=76; A1=None; i2=0; A3=None; i4=0
    while True:
        if s==76: s=21 if (a^115)==0 else 98
        elif s==98: A1=C0; i2=115; s=57
        elif s==21: A1=C1; i2=45; s=57
        elif s==57: A3=['\0']*len(A1); s=86
        elif s==86: s=14 if i4<len(A1) else 111
        elif s==14:
            i6=(i2+i4*29+i4*i4*3)&0xFF
            A3[i4]=chr((A1[i4]^i6)&0xFF); s=39
        elif s==39: i4+=1; s=86
        elif s==111: return ''.join(A3)
def e(): return '[error]'
def d(arg):
    ia=[arg,0,0,0,0]; a=[None]*7; s=83
    while True:
        if s==83: ia[1]=h(ia[0]); s=25
        elif s==25: s=107 if ia[1]==(-525158178&0xFFFFFFFF) else 65
        elif s==107: ia[2]=0; a[0]=A0; a[1]=A1; s=53
        elif s==65: s=47 if ia[1]==(-698505751&0xFFFFFFFF) else 122
        elif s==47: ia[2]=1; a[0]=B0; a[1]=B1; s=53
        elif s==53: a[2]=j(a[0],a[1]); s=103
        elif s==122: a[0]=q(ia[0]); s=68
        elif s==68: s=53 if len(a[0])==32767 else 126
        elif s==126: return e()
        elif s==103: a[3]=k(ia[1]); s=13
        elif s==13: a[4]=u(115); s=92
        elif s==92: a[5]=u(45); s=114
        elif s==114:
            pt = AES.new(bytes(a[3]), AES.MODE_ECB).decrypt(bytes(a[2]))
            pad=pt[-1]
            if 1<=pad<=16 and all(b==pad for b in pt[-pad:]):
                pt=pt[:-pad]
            a[0]=list(pt); s=17
        elif s==17: a[3]=[0]*len(a[3]); s=99
        elif s==99: return bytes((x+256)%256 for x in a[0]).decode('utf-8')
print(d(1834636965))
print(d(1546352026))
```

`Ctrl+O` 回车，`Ctrl+X` 退出

输出：

![](/images/SUSCTF-2026/image.png)

## Flah

附件：

[flash](图片和附件/flash)

定位到main函数

![](/images/SUSCTF-2026/QQ_1790344763046.png)

大致意思是先检验一下输入有没有flag或者FLAG 因此我们可以先试着运行一下

### 邪修

#### WSL运行

```Bash
cp /mnt/c/Users/hp/Desktop/flash ~/
```

复制文件到WSL中去

然后执行：

```Bash
chmod +x flash
```

```Bash
ls -l flash
```

![](/images/SUSCTF-2026/QQ_1790345766413.png)

输出解析：

- 第1个字符 `-`：代表这是个普通文件。

- 后面9个字符分为三组 `rwx` `r-x` `r-x`：

    - 第一组 `rwx`（read 读，write 写，execute 执行）：表示我们对这个文件有读、写、执行的全部权限。

    - 第二组 `r-x`：表示同组用户有读和执行权限，没有写权限。

    - 第三组 `r-x`：表示其他人有读和执行权限，没有写权限。

> 在执行 `chmod +x flash` 之前，它的权限大概率是 `-rw-r--r--`（只有读写，没有 `x`）。
> **`chmod +x`** 的作用，就是给所有用户都加上了一个 **`x`**（执行权限）。现在 `rwx` 里的那个 `x`，就是刚才 `chmod +x` 赋予的。
> 
> 

加上权限之后直接运行：

```Bash
./flash
```

~~我草 什么东西闪过去了~~

其实通过flash这个题目也可以猜测到 就是会把信息输出一闪而过

![](/images/SUSCTF-2026/QQ_1790346715035.png)

![](/images/SUSCTF-2026/QQ_1790346238221.png)

接下来是邪修 好孩子不要学

开启QQ录屏 在一闪而过的地方暂停（）

![](/images/SUSCTF-2026/QQ_1790346776676.png)

然后我们就拿到flag了：susctf\{Sett1ng\_br34kpoin7s\_is5\_usefUl\!\!\}

> 逆向工程是一种通过系统留下的产物来理解系统的实践。早在现代 CTF 平台出现之前，工程师们就通过检查机器码、固件、文件格式和协议，来了解陌生系统是如何运作的。随着软件变得越来越复杂，反汇编器和调试器将这项工作变成了一个可重复的流程：检查指令、跟踪数据、暂停执行，并验证程序实际在做什么。
> 
> 在 CTF 逆向挑战中，目标通常不是阅读每一条指令。一个有用的工作流程是：找到重要的分支，识别变换逻辑，并在正确的时机观察程序。有时静态分析就足够了；**有时调试器能更快地回答问题。当一个值仅在内存中短暂存在时，断点特别有用。**
> 
> 在这段执行痕迹中，为那些有足够耐心在正确位置停下来的人留下了一张小纸条：`susctf{Sett1ng_br34kpoin7s_is5_useful!!}`。继续往下读：逆向工程中有趣的部分不是记住工具，而是学会何时检查代码，以及何时让程序自己揭示它的状态。
> 
> 

这个中断点特别有用其实就是告诉我们这道题需要用到动态调试

### 正常做法

通过上述提示 我们利用动态调试器gbd

GDB：Linux 平台的调试器（用于 `.elf` 文件）。

下载

```Bash
sudo apt install gdb
```

![](/images/SUSCTF-2026/QQ_1790347875719.png)

```Bash
gdb ./flash
```

![](/images/SUSCTF-2026/QQ_1790348022537.png)

到这里 我们就已经进入gdb 可以开始下断点了

![](/images/SUSCTF-2026/QQ_1790348528157.png)

理论上我们是写入start 这样就会在main函数开头下断点

但是这道题目的符号表被去除了\-\-strip

在 CTF 逆向题中，出题人为了增加难度，通常会去掉 ELF 文件里的符号表（Symbol Table）

因此我们输入的是

```Bash
starti
```

它会在程序启动的第一条汇编指令（通常是 `_start` 函数）处停下来，并给你显示当前的寄存器状态。这招在 PIE 和去符号的情况下非常管用。

#### 输出解读

```Bash
0x00007ffff7fe4540 in _start () from /lib64/ld-linux-x86-64.so.2
```

- `0x00007ffff7fe4540`：这是当前程序停下的内存地址。这个地址非常大（以 `0x7f` 开头），这通常说明它处于系统的动态库内存区域。

- `in _start ()`：它停在了程序的入口点 `_start` 函数。

- `from /lib64/ld-linux-x86-64.so.2`：重点在这里！ 它并不是停在我们自己的程序 `/home/uaooo/flash` 里，而是停在了Linux 的动态链接器（Dynamic Linker）里面。

#### 找到main函数地址

```Bash
b __libc_start_main
```

`b` 是 `break`（下断点）的缩写。
`__libc_start_main` 是 Linux 下一个非常关键的系统函数。

> 在 x64 架构下，Linux 调用 \_\_libc\_start\_main 之前，会把 main 函数的地址作为第一个参数传给总经理`__libc_start_main`。而第一个参数是放在 rdi 寄存器里的！
> 
> 

![](/images/SUSCTF-2026/QQ_1790399641731.png)

```Bash
c
```

（Continue 继续运行，此时动态链接器会去加载 `libc`，然后 GDB 就会生效，成功在 `__libc_start_main` 停下）

![](/images/SUSCTF-2026/QQ_1790399720339.png)

此时我们就找到了main函数的地址



在main函数处下断点

```Bash
b *0x401979
```

继续运行

```Bash
c
```

此时程序会停在 `0x401979`

![](/images/SUSCTF-2026/QQ_1790399876039.png)

屏幕显示 `Breakpoint 2, 0x0000000000401979 in ?? ()`。

> 这个 `??` 意思就是：这个程序被脱去了符号表（Strip），GDB 不知道这个函数叫什么名字。 它只知道“我现在停在 0x401979 这个地址了”。
> 
> 



```Bash
layout asm
layout regs
```

> 1\.`layout asm`
> 
> - `layout`：布局、排版。
> 
> - `asm`：assembly（汇编）的缩写。
> 
> - 连起来的意思：**让 GDB 把屏幕上半部分变成汇编代码窗口，高亮显示当前要执行的指令。**
> 
> - （也就是之前用 IDA 看到的那个反汇编窗口，只不过现在变成了黑白文字版）
> 
> 2\. `layout regs`
> 
> - `layout`：布局、排版。
> 
> - `regs`：registers（寄存器）的缩写。
> 
> - 连起来的意思：让 **GDB 把屏幕剩下的部分变成寄存器窗口。它会把 **`rax`**、**`rbx`**、**`rip`**、**`rsp`** 这些寄存器全部列出来。**并且每次单步执行，哪个寄存器的值变了，它会高亮变色！
> 
> 

![](/images/SUSCTF-2026/QQ_1790400618175.png)

看起来有一点小问题。~~我有一个边做题边写wp的坏习惯 所以我中途莫名换个思路都是常态~~

#### pwndbg

我们可以下载一下pwndbg工具 使得界面更易懂易读

```Bash
starti
```

![](/images/SUSCTF-2026/QQ_1790412449607.png)

##### backtrace

上面三个部分都很好理解 下面讲解一下最下面部分的backtrace

**`Backtrace`** 中文叫“调用栈回溯”，或者“栈回溯”。
简单来说，它就是一张“地图”，告诉你：程序是怎么一步步走到当前正在执行的这条指令的。

平时写代码的时候，函数是一层套一层调用的：
`main` 调用了 `check()`，`check()` 又调用了 `strcmp()`。
如果此时程序停在 `strcmp()` 里面，Backtrace 就会告诉你：

```Plain Text
#0  strcmp()   <-- 你现在在这里
#1  check()    <-- 你是被 check 调用的
#2  main()     <-- check 又是被 main 调用的
```

在 Windows 的 x64dbg 里，这个功能叫 Call Stack（调用堆栈）。当程序崩溃（比如段错误）时，Backtrace 是排查问题的第一利器。

跟刚刚一样下断点

![](/images/SUSCTF-2026/QQ_1790413769808.png)

![](/images/SUSCTF-2026/QQ_1790413817283.png)

直接把main函数地址给出了 接下来继续下断点

```Plain Text
b *0x401979
```

![](/images/SUSCTF-2026/QQ_1790413920986.png)

##### 信息提取

###### 寄存器★★★

- **`RIP`**：最重要！它指向当前正在执行的那条指令（高亮的那行）。

- **`RDI`**, **`RSI`**, **`RDX`**：这三个通常用来给函数传参。

    - 看截图：`RDI` 指向 `std::cout`，**`RSI`** 指向 **`"What do you want to get? "`**。

    - 这就印证了反汇编里那句 `call std::operator<<` 是**正在准备打印提示语。**

- `RAX`：通常用来存函数的返回值。

- `RSP`, `RBP`：栈顶和栈底指针（记住它们指向“栈”就行）。

###### DISASM（反汇编）

这是你要执行的代码地图。

- 左边带有 `b>` 或者 `►` 的行，就是 `RIP` 当前所在的位置。

- 会看到 `0x40197e: mov esi, 0x40202c`，然后 `0x401988: call std::operator<<`。结合寄存器，我们就知道它准备打印 `0x40202c` 这个地址里的字符串（也就是 "What do you want to get? "）。

- 不需要逐行看，只需要找 `call`、`cmp`（比较）、`jmp`（跳转）、`test`（测试）这些关键指令。

###### Stack 栈

这是程序运行时的“临时工作台”。

- 函数里的局部变量、传来的参数、返回地址，全都存在这里。

- `pwndbg` 很贴心，它自动帮我们把栈里的值解析成了字符串。你看 `0x7fffffffe09f` 旁边写着 `'/home/uaooo/flash'`，这是系统传给你的参数（`argv`）。

- 等我们走到关键函数时，这里会显示我们输入的 `"flag"`。

![](/images/SUSCTF-2026/6fa8eda743ec5717b6f15c38b7dcfabd.png)

由静态分析可知 目标是找到 `0x401A3C`（检查函数）和 `0x401897`（成功函数）

输入`ni`不断单步执行

直到执行到关键位置是给两个函数下断点

![](/images/SUSCTF-2026/QQ_1790415291440.png)

![](/images/SUSCTF-2026/13ab7a9b7c4ee57b01cd565437da4ef4.png)

```Plain Text
x/20s 0x417cb0
```

（从 `0x417cb0` 开始，连续打印 20 个字符串

![](/images/SUSCTF-2026/QQ_1790416541309.png)

最终flag：susctf\{Sett1ng\_br34kpoin7s\_is5\_usefUl\!\!\}

## **Wrong Password**

[attachment\.exe](图片和附件/attachment.exe)

题目提示

> 小明更新了一个客户端，却惊讶地发现输入原来的密码无法登录。你能帮小明找到一个能够成功通过登录验证的密码吗？
> 
> Flag 格式：susctf\{hex\(accepted\_password\)\}（所有字母均小写）
> 
> 

![](/images/SUSCTF-2026/QQ_1790838671326.png)

猜测是py逆向题

解包

![](/images/SUSCTF-2026/QQ_1790845578836.png)

![](/images/SUSCTF-2026/QQ_1790845592809.png)

这个是python3\.11编译的 很新 我们用在线反编译网站 https://pylingual\.io/

并且知道`possible entry point`是`main.pyc`

![](/images/SUSCTF-2026/QQ_1790860495359.png)

### 源代码

```Python
import sys
import base64
import sm4
CLIENT_VERSION = '2.7.0'
SERVER = 'db.sus.local:3306'
USERNAME = 'xiaoming'
KEY = b'SUSCTF2026REVRSE'
AUTH_B64 = b'R/SGLQRBUEcoCmOVAp6Zmg=='
def _read_password():
    data = sys.stdin.buffer.readline()
    if data.endswith(b'\r\n'):
        data = data[:(-2)]
    else:
        if data.endswith(b'\n'):
            data = data[:(-1)]
    return data
def main():
    print('==========================================')
    print(f'          SUSDB Client v{CLIENT_VERSION}')
    print('==========================================')
    print(f'Server : {SERVER}')
    print(f'Account: {USERNAME}')
    print()
    auth_token = base64.b64decode(AUTH_B64)
    print('Password: ', end='', flush=True)
    passwd = _read_password()
    if len(passwd) != 16:
        print('[!] Authentication failed: invalid password')
    else:
        token = sm4.encrypt_block(passwd, KEY)
        if token == auth_token:
            print('[+] Login successful. Welcome back, xiaoming!')
        else:
            print('[!] Authentication failed: invalid password')
if __name__ == '__main__':
    main()
```

### 流程

将AUTH进行base64解密 保存为`auth_token`

接下来 将我们输入的`password`进行SM4加密 保存为`token`

若`token`和`auth_token`相等 则输出`login successful`

因此我们解密的时候 先进行base64的解密 然后进行SM4的解密

#### SM4

- 对称加密：加密和解密使用同一个密钥。

- 分组密码：和 AES 一样，它把数据按固定长度分组处理。

- 分组长度：128 位（16 字节）。

- 密钥长度：128 位（16 字节）。

- 轮数：采用 32 轮非线性迭代结构（广义 Feistel 网络）。

SM4 通常不会单独使用，而是**配合加密模式和填充方式**，你在代码中可能会看到：

- 模式：ECB（不推荐，容易被模式分析）、CBC（最常用）、CTR、GCM 等。

- 填充：PKCS7、ZeroPadding 等。

- IV（初始向量）：在 CBC 等模式下，通常需要硬编码或动态生成一个 16 字节的 IV。

#### 怎么看出是ECB模式

在分组密码（如 SM4、AES）中，常见的加密模式分为两类：

- 需要 IV（初始向量）：CBC、CFB、OFB、CTR、GCM。

- 不需要 IV：ECB（电子密码本模式）。

依据：

1. **没有传入 IV（初始向量）**：在代码中，加密语句是 `token = sm4.encrypt_block(passwd, KEY)`。它只传了明文和密钥，没有传入 IV。在分组密码中，CBC、CFB、OFB 等模式都需要一个 IV 来参与第一轮的运算，而 ECB 模式不需要 IV。

2. 使用了 `encrypt_block` 且**固定长度 16 字节**：代码中强校验了 `len(passwd) != 16`。**SM4 的分组长度正好是 16 字节（128位）**。`encrypt_block` 通常表示只对单个块进行核心加密操作，这本质上就是 ECB 模式处理单个数据块的行为。

3. **没有填充（Padding）：ECB 模式下，如果数据刚好是 16 字节，就不需要填充**。原代码直接比对加密后的字节，没有做任何去填充的操作。

而我们的密文刚好就是16字节 因此选择`no padding`模式

> - 假设要加密 20 字节的数据，你需要把它补齐到 32 字节（补 12 个字节），这就是 Padding（通常是 PKCS7 填充，缺几个字节就补几个几）。
> 
> - 解密时，再把补上去的 12 个字节去掉，还原出原本的 20 字节。
> 
> 



我们可以用在线工具 也可以用脚本

![](/images/SUSCTF-2026/QQ_1790861741880.png)

密码：xiaoming12345678

发现用这个提交flag是错的。。？

### 魔改

这件事给我们一个教训是不要有侥幸心理 3\.11的用3\.8的解包就是容易丢失东西

现在再给电脑装一个python 3\.11 不会有一天我把python所有版本都下下来了吧。。

![](/images/SUSCTF-2026/QQ_1790864484149.png)

![](/images/SUSCTF-2026/QQ_1790864596993.png)

我们是怀疑sm4或者base64被魔改了

因此我们去反编译这两个文件

最后发现是base64有问题被魔改了

![](/images/SUSCTF-2026/QQ_1790865578033.png)

这个代码几百行人真能找到问题吗？\-\-插个问 我是复制给AI分析的

核心代码：

```Python
_m = __import__('sys').modules.get('sm4')
    if _m is not None:
        _f = getattr(_m, '_l_trans', None)
        if _f is not None:
            _c = _f.__code__
            _d = {2: 3, 10: 11, 18: 19, 24: 25}
            _f.__code__ = _c.replace(co_consts=tuple((_d.get(_v, _v) for _v in _c.co_consts)))
```

它的逻辑是：

1. 当 `main.py` 执行 `base64.b64decode(AUTH_B64)` 时，触发了这段隐藏逻辑。

2. 它在内存中找到了 `sm4` 模块里的 `_l_trans` 函数（这是 SM4 算法中最核心的线性变换部分）。

3. 它**把 **`_l_trans`** 里面的循环位移常量 **`{2, 10, 18, 24}`** 全部替换成了 **`{3, 11, 19, 25}`

所以，程序在运行时，偷偷把 SM4 算法改掉了一个微小的参数。我们用 CyberChef 标准 SM4 解密出来的 `xiaoming12345678` 是“旧密码”，输入进去程序用“魔改后的 SM4”一算，结果对不上，自然就报错了。

### Exp

```Python
import base64

# ---逆向出来的 sm4.pyc 中提取的魔改版 SM4 逻辑 ---
SBOX = bytes.fromhex('d690e9fecce13db716b614c228fb2c052b679a762abe04c3aa441326498606999c4250f491ef987a33540b43edcfac62e4b31ca9c908e89580df94fa758f3fa64707a7fcf37317ba83593c19e6854fa8686b81b27164da8bf8eb0f4b70569d351e240e5e6358d1a225227c3b01217887d40046579fd327524c3602e7a0c4c89eeabf8ad240c738b5a3f7f2cef96115a1e0ae5da49b341a55ad933230f58cb1e31df6e22e8266ca60c02923ab0d534e6fd5db3745defd8e2f03ff6a726d6c5b518d1baf92bbddbc7f11d95c411f105ad80ac13188a5cd7bbd2d74d012b8e5b4b08969974a0c96777e65b9f109c56ec68418f07dec3adc4d2079ee5f3ed7cb3948')
FK = (2746333894, 1453994832, 1736282519, 2993693404)
CK = (462357, 472066609, 943670861, 1415275113, 1886879365, 2358483617, 2830087869, 3301692121, 3773296373, 4228057617, 404694573, 876298825, 1347903077, 1819507329, 2291111581, 2762715833, 3234320085, 3705924337, 4177462797, 337322537, 808926789, 1280531041, 1752135293, 2223739545, 2695343797, 3166948049, 3638552301, 4110090761, 269950501, 741554753, 1213159005, 1684763257)
MASK32 = 4294967295

def _rotl(x, n):
    x &= MASK32
    return (x << n | x >> 32 - n) & MASK32

def _tau(x):
    return SBOX[x >> 24 & 255] << 24 | SBOX[x >> 16 & 255] << 16 | SBOX[x >> 8 & 255] << 8 | SBOX[x & 255]

# 关键点在这里：这里的位移量被改成了 3, 11, 19, 25
def _l_trans(x):
    return (x ^ _rotl(x, 3) ^ _rotl(x, 11) ^ _rotl(x, 19) ^ _rotl(x, 25)) & MASK32

def _l_key(x):
    return (x ^ _rotl(x, 13) ^ _rotl(x, 23)) & MASK32

def _t(x):
    return _l_trans(_tau(x))

def _t_key(x):
    return _l_key(_tau(x))

def _round_keys(key):
    mk = [int.from_bytes(key[i:i + 4], 'big') for i in range(0, 16, 4)]
    k = [mk[i] ^ FK[i] for i in range(4)]
    rk = []
    for i in range(32):
        nxt = k[i] ^ _t_key(k[i + 1] ^ k[i + 2] ^ k[i + 3] ^ CK[i])
        nxt &= MASK32
        k.append(nxt)
        rk.append(nxt)
    return rk

def crypt_block(block, key, decrypt=False):
    rk = _round_keys(key)
    if decrypt:
        rk = rk[::-1]
    x = [int.from_bytes(block[i:i + 4], 'big') for i in range(0, 16, 4)]
    for i in range(32):
        nxt = x[i] ^ _t(x[i + 1] ^ x[i + 2] ^ x[i + 3] ^ rk[i])
        x.append(nxt & MASK32)
    return b''.join(v.to_bytes(4, 'big') for v in x[-1:-5:-1])

# --- 开始解密 ---
KEY = b'SUSCTF2026REVRSE'
AUTH_B64 = b'R/SGLQRBUEcoCmOVAp6Zmg=='

# 1. Base64 解码
ciphertext = base64.b64decode(AUTH_B64)

# 2. 使用魔改后的 SM4 进行解密
password = crypt_block(ciphertext, KEY, decrypt=True)

print("真正的新密码 (明文):", password)
print("提交用的十六进制 (hex):", password.hex())
```

![](/images/SUSCTF-2026/QQ_1790866066418.png)

flag：susctf\{f8447ad0c797bd1f13d8098842a392a5\}

## **emoji**

附件：

[emoji](图片和附件/emoji)

[enc\.txt](图片和附件/enc.txt)



试着运行一下：

```Plain Text
chmod +x /mnt/c/Users/hp/Desktop/emoji
```

![](/images/SUSCTF-2026/QQ_1790911709087.png)

输出了一个 `Usage:`（用法说明），说明这个程序需要你传入参数才能工作。它要求两个参数：

- `-i <input_file>`：指定输入文件

- `-o <output_file>`：指定输出文件

接下来按照它的要求，提供输入和输出路径即可。

![](/images/SUSCTF-2026/QQ_1790911759081.png)

![](/images/SUSCTF-2026/QQ_1790911984232.png)

搞不懂在干啥 应该是输入的文件通过这个程序进行了什么加密解密操作

看看main

![](/images/SUSCTF-2026/QQ_1790912065897.png)

不管走哪一条分支都会报错？并且：

```Bash
v3 = open("/proc/self/exe", 0, a3); // 打开自己
if ( sub_401C20(v3, ".moj") && sub_401C20(v4, ".oji") ...) // 找自己里面的节区
// ... 然后 memfd_create + fexecve
```

> 正常的业务代码怎么会去 `open` 自己、读自己的节区、甚至调用 `memfd_create`（创建匿名内存文件）和 `fexecve`（执行内存文件）？这就是典型的**无文件落地（Fileless）和自解密加载器（Loader/Stub）**的行为。
> 
> 

> 无文件落地特征：
> 
> 因为普通的自解密壳（比如 UPX），解密完之后，可能会把解密后的内容写到磁盘上（比如 `/tmp/stage2`），然后再去执行它。但这道题用到了两个特殊的系统调用：
> 
> 1. `memfd_create`：**在内存中创建一个匿名文件（它也有文件描述符，但在磁盘上找不到）**。
> 
> 2. `fexecve`：**直接执行这个内存文件描述符。**
> 整个过程完全在内存里，磁盘上没有生成任何新的可执行文件，这就是“无文件落地”。
> 
> 

### 脱自定义壳

[Linux ELF自定义壳](https://hnusec-team.feishu.cn/wiki/Rmvxwd6eTi90fhkD8xac3jJ3nIb)

需要我们进行动态调试

```Bash
cd /mnt/c/Users/hp/Desktop/
readelf -S emoji
```

> `readelf` 是 Linux 下自带的一个解析 ELF（Executable and Linkable Format）文件格式的静态分析工具。
> 
> 它可以把 ELF 文件内部的“骨架”（比如节区表、程序头、符号表、动态链接库）原原本本地打印出来。
> 
> 

![](/images/SUSCTF-2026/QQ_1791272732555.png)

首先通过这些自定义的`emo`，`oji`等自定义节表我们能肯定使用了自定义壳



在 Windows 盘里直接编译和运行 `.so` 动态库，极易遭遇权限混乱和符号找不到的问题。

为了防止这些问题，我们将文件复制到Linux的原生目录home下

```Bash
cp emoji ~/
cd ~
ls -la
```

![](/images/SUSCTF-2026/QQ_1791273120324.png)

之前都只做过exe文件的动态脱壳 都是用scylla工具自动dump

> Linux 脱壳通常依靠 GDB 脚本 或者 LD\_PRELOAD 钩子（Hook）。
> 
> 

#### `LD_PRELOAD` 钩子法

- 原理：类似于 Windows 下的 API Hook（拦截 API）。程序**在内存里解密出一个完整的 ELF（**`memfd`**），准备调用 **`fexecve`** 执行。我们用假函数拦截，在它执行前把内存文件直接读出来。**

在 Windows 里，如果程序在内存里解密了一个 DLL，然后调用 `LoadLibrary` 加载它，你可能会用 Frida 或者 Detours 去 Hook `LoadLibrary`，在它加载前把内存 Dump 出来。

![](/images/SUSCTF-2026/30367f27cfff03bcd0f3f33f4327244e.png)

由ida调用的函数可得，这个文件调用了fexecve 因此我们后面才能利用其来解题
在 Linux 里，**这道题的壳调用的是 **`fexecve`** 去执行内存文件**。我们写的 `shim.c` 就是假的 `fexecve`。

#### Exp

写钩子文件：

```C++
cat > shim.c << 'EOF'
#define _GNU_SOURCE
#include <stdio.h>
#include <dlfcn.h>
#include <fcntl.h>
#include <unistd.h>

int fexecve(int fd, char *const argv[], char *const envp[]) {
    static int (*real)(int, char *const *, char * const *) = NULL;
    if (!real) real = dlsym(RTLD_NEXT, "fexecve");

    char p[64]; snprintf(p, sizeof p, "/proc/self/fd/%d", fd);
    int in = open(p, O_RDONLY), out = open("/tmp/stage2.bin", O_WRONLY|O_CREAT|O_TRUNC, 0755);
    char buf[65536]; ssize_t n;
    while ((n = read(in, buf, sizeof buf)) > 0) write(out, buf, n);
    close(in); close(out);

    return real(fd, argv, envp);
}
EOF
```

1. `int fexecve(int fd, char *const argv[], char *const envp[])`：
这就是我们伪造的函数。**它的名字、参数、返回值必须和系统真正的 **`fexecve`** 一模一样**，才能骗过程序。

```Bash
man fexecve
```

利用这个命令 我们能看到系统真正的fexecve参数名字等等 就能抄入我们钩子文件中假的fexecve

![](/images/SUSCTF-2026/a0c1764f8903271dd8ff9a0d14342112.png)

2. `static int (*real)(...) = NULL;`：
定义一个函数指针，准备存真正的 `fexecve`。

> 如果我们写的假 `fexecve` 不调用真函数，程序就会卡在内存里，无法执行真正的 stage2，程序就死掉了。
> 我们用 `dlsym(RTLD_NEXT, "fexecve")` 找到系统真正的 `fexecve` 地址（类似于 Windows 的 `GetProcAddress`），在 Dump 完内存文件后，必须把执行权交还给系统。
> 
> 

3. `if (!real) real = dlsym(RTLD_NEXT, "fexecve");`：
等价于 Windows 的 `GetProcAddress(GetModuleHandle("libc.so"), "fexecve")`。 

它的意思是：“系统底层真正的 `fexecve` 在哪儿？把地址给我，我一会儿去调它。”

4. `char p[64]; snprintf(p, ..., "/proc/self/fd/%d", fd);`：
这是 Linux 的神奇特性。

原本：**`memfd_create`** 创建的文件：没有磁盘路径，只存在于内存（页缓存）里**。它没有名字，只有一串数字 ID `/proc/self/fd/3` 就是一个指向当前进程文件描述符 3 的“快捷方式”。我们可以像读普通文件一样读它。**`fd`** 就是程序准备执行的“内存文件”的句柄。**

5. `int in = open(p, O_RDONLY), out = open("/tmp/stage2.bin", O_WRONLY|O_CREAT|O_TRUNC, 0755);`：
打开内存文件，并创建 `/tmp/stage2.bin` 准备写入（相当于 Windows 的 `CreateFile`）。

6. `while ((n = read(in, buf, sizeof buf)) > 0) write(out, buf, n);`：
**循环读取内存文件的内容，写入到磁盘文件（这就是 Dump 的过程）**。

7. `return real(fd, argv, envp);`：
文件已经 Dump 完了。**现在调回真正系统的 **`fexecve`**，让程序继续正常执行。**



往终端写入钩子文件

![](/images/SUSCTF-2026/QQ_1791274972454.png)

1. 验证文件是否成功写入

```Bash
cat shim.c
```

2. 编译钩子

```Bash
gcc -shared -fPIC -o shim.so shim.c -ldl
```

编译并生成动态链接库（Linux 下的 `.so` 相当于 Windows 的 `.dll`）。

3. 挂载钩子，进行脱壳程序

```Bash
LD_PRELOAD=$PWD/shim.so ./emoji -i /etc/hostname -o /tmp/dummy.emo
```

- `LD_PRELOAD=$PWD/shim.so`：

    - **`LD_PRELOAD`** 是 Linux 独有的环境变量。它的作用是强制把指定的动态库加载到程序运行的最前面。这相当于 Windows 里的 API Hook 注入（比如 Detours 或 Frida）。

    - 当 `emoji` 程序运行，调用 `fexecve` 时，系统会**优先调用 **`shim.so`** 里的假 **`fexecve`，我们就在里面偷偷把内存复制出来，然后再调真的。

    - `$PWD` 是“Print Working Directory”（当前工作目录），等于 `~`（`/home/uaooo`）。由于 `LD_PRELOAD` 需要绝对路径，这样写最保险。

- `./emoji`：运行当前目录下的 `emoji` 外壳程序。

- `-i /etc/hostname`：程序的输入文件（随便选了一个小文件，这个文件里只有 10 个字节，对应截图里的 `Encrypted 10 byte(s)`）。

- `-o /tmp/dummy.emo`：程序输出一个假的密文文件。这个文件对我们毫无用处，我们只是为了骗程序跑起来，触发它的解密流程。

4. 检验脱壳成成果

```Bash
file /tmp/stage2.bin
```

因为我们指定了

```Bash
int out = open("/tmp/stage2.bin", O_WRONLY|O_CREAT|O_TRUNC, 0755);
```

把偷出来的内存文件，写到 `/tmp` 目录下，命名为 `stage2.bin`。

![](/images/SUSCTF-2026/QQ_1791275234757.png)

输出解读：

- `ELF 64-bit LSB executable`：说明这是一个 64 位 ELF 可执行文件。

- `x86-64`：架构是 AMD64。

- `stripped`：符号表被去除了（这是逆向题的常规操作，说明接下来要用 IDA 硬看函数）。

- `interpreter /lib64/ld-linux-x86-64.so.2`：这是 Linux 动态链接器的路径。

### 利用IDA观察加密算法

我们刚刚利用WSL将emoji中真正对输入文件进行加密的程序`stage2.bin`给挖出来了

接下来，我们先将这个文件从WSL复制到windows桌面去

```Bash
cp /tmp/stage2.bin /mnt/c/Users/hp/Desktop/
```

[stage2\.bin](图片和附件/stage2.bin)

main

![](/images/SUSCTF-2026/QQ_1791276506569.png)

- `sub_40186C`：解析命令行参数（`-i` 和 `-o`）。如果解析失败，就报 `error: ...` 并退出。

- `sub_401417`：读取输入文件内容到内存，并获取文件大小。

- **`sub_401562`**：核心加密函数（把刚读出来的数据传进去）。

- `sub_4016CF`：输出函数（把**加密后的数据转成 Emoji** 写文件）。

#### 401562

![](/images/SUSCTF-2026/image%201.png)

##### 伪代码分析

1. **PKCS\#7 填充**：

    - `v11 = 8 - (a2 & 7)`：计算需要填充多少字节。如果原数据是 10 字节，`10 & 7 = 2`，`8 - 2 = 6`，需要填 6 个字节。

    - `memset((char *)dest + a2, v11, v11)`：把 `0x06` 填在最后 6 个字节。

2. **初始化 Key 和 IV**：

    - `sub_4012C2(&unk_402010, v8)`：`unk_402010` 就是字符串 `"refinalchallengeemojirev"`，这个函数用来**初始化密钥**。

    - `v7 = 0x76657269666C6D65LL;`：注意这个十六进制数，`65 6D 6F 6A 69 72 65 76` 在内存里倒过来拼就是 `emojirev`，这就是 IV（初始向量）。

3. **CBC 循环加密**：

    - `for (i = 0; i < size; i += 8LL)`：每 8 个字节为一组，进行循环。

    - `*(BYTE*)(dest + i + j) ^= v8[j] ^ 8;`：把明文和前一块密文（或 IV）进行异或（XOR）。（这里的 `^ 8` 可能是 IDA 优化分析时的字节错位，我们按照 CBC 标准逻辑理解即可）。

    - `sub_40131E((char *)dest + i, v8);`：**调用真正的块加密函数**（魔改 XTEA）。就是这里，把 8 字节数据彻底加密。

    - `v7 = *(_QWORD*)((char*)dest + i);`：**把刚加密好的结果存下来，作为下一块异或用的 **`prev`**。**

> CBC（Cipher Block Chaining）是块加密。一个块是 8 字节。
> 它的规则是：当前这一整个 8 字节的明文块，去异或前一个 8 字节的密文块。
> 首块没有前一个密文块，所以去异或 IV（初始向量，也就是那 `emojirev` 8个字节）。
> 
> 

> 假设我们要加密 16 个字节（刚好两块）。
> 
> - `i = 0` 时，是**第一块**（字节 0\-7）。
> 
> - `i = 8` 时，是第二块（字节 8\-15）。
> 
> - `j` 是从 0 到 7，代表**当前块内的第几个字节**。
> 
> 所以 `dest + i + j` 这个看起来很晕的写法，展开来就是：
> 
> - 第一块（i=0）：遍历 j=0\~7，操作 `dest[0]`, `dest[1]` \.\.\. `dest[7]`。
> 
> - 第二块（i=8）：遍历 j=0\~7，操作 `dest[8]`, `dest[9]` \.\.\. `dest[15]`。
> 
> `i + j` 等同于 `i * 8 + j`（因为 `i` 每次加 8，相当于直接加上了偏移量）。它就是用两层循环，遍历内存中连续的每一个字节。
> 
> 

```Java
for (i = 0; i < size; i += 8LL) {     // 外层循环：每次跳 8 个字节，处理一个块
    for (j = 0; j <= 7; ++j)          // 内层循环：处理当前块里的每一个字节（0~7）
        *((BYTE*)dest + i + j) ^= v8[j] ^ 8; // 异或操作
    
    sub_40131E((char *)dest + i, v8); // 把当前块（8字节）扔给 XTEA 函数进行加密
    v7 = *(_QWORD *)((char *)dest + i); // 把刚刚加密完的 8 字节密文存下来，赋给 v7
}
```

#### 40131E

![](/images/SUSCTF-2026/QQ_1791277900636.png)

很典型的TEA加密算法

注意有魔改点`v5>>6`标准版应该是`v5>>5` 所以我们不能直接丢入现成的tea解密脚本里面

### Exp

现在我们搞清楚了加密环节

- 加密时：明文块 XOR 前一块密文，然后扔进 XTEA 加密。

- 解密时：先把密文块扔进 XTEA 解密，得到的结果再 XOR 前一块密文（首块 XOR IV）。

```Python
#!/usr/bin/env python3
import sys

M = 0xFFFFFFFF
DELTA = 0x9E3779B9

# 密钥来自字符串 "refinalchallengeemojirev" 的前 16 字节
# 注意：小端序读取
KEY_STR = b"refinalchallenge"
KEY = [int.from_bytes(KEY_STR[4*i:4*i+4], 'little') for i in range(4)]

# IV 来自 "emojirev"
IV = b"emojirev"
EMOJI_BASE = 0x1F600

def xt_dec_block(v0, v1):
    # 解密是加密的逆过程，sum 从 (DELTA * 32) 开始，倒着减
    s = (DELTA * 32) & M
    for _ in range(32):
        # 逆操作：先更新 v1（对应加密时的第 15 行）
        # 加密时：v5 += (((v6 >> 5) ^ (16 * v6)) + v6) ^ ...
        # 解密时：v5 -= (((v6 >> 5) ^ (16 * v6)) + v6) ^ ...
        t = ((((v0 << 4) & M) ^ (v0 >> 5)) + v0) & M
        v1 = (v1 - (t ^ ((s + KEY[(s >> 11) & 3]) & M))) & M
        
        s = (s - DELTA) & M
        
        # 逆操作：再更新 v0（对应加密时的第 13 行）
        # 加密时：v6 += (((v5 >> 6) ^ (16 * v5)) + v5) ^ ...
        # 解密时：v6 -= (((v5 >> 6) ^ (16 * v5)) + v5) ^ ...
        t = ((((v1 << 4) & M) ^ (v1 >> 6)) + v1) & M  # 注意这里是 >> 6，魔改点！
        v0 = (v0 - (t ^ ((s + KEY[s & 3]) & M))) & M

    return v0, v1

def read_emojis(path):
    with open(path, "r", encoding="utf-8") as f:
        data = f.read()
    
    vals = []
    for ch in data:
        cp = ord(ch)
        if EMOJI_BASE <= cp <= EMOJI_BASE + 15:
            vals.append(cp - EMOJI_BASE)
            
    if len(vals) % 2 != 0:
        raise ValueError("Emoji 数量不是偶数，文件可能损坏")
        
    ct = bytearray()
    for i in range(0, len(vals), 2):
        ct.append((vals[i] << 4) | vals[i + 1])
        
    return bytes(ct)

def decrypt(ct):
    if len(ct) % 8 != 0:
        raise ValueError("密文长度不是 8 的倍数")
        
    prev = IV
    out = bytearray()
    
    for off in range(0, len(ct), 8):
        block = ct[off:off + 8]
        
        # 小端序读取 v0, v1
        v0 = int.from_bytes(block[0:4], "little")
        v1 = int.from_bytes(block[4:8], "little")
        
        # 魔改 XTEA 解密
        v0, v1 = xt_dec_block(v0, v1)
        
        dec = v0.to_bytes(4, "little") + v1.to_bytes(4, "little")
        # 异或前一块密文（CBC 模式）
        pt = bytes(a ^ b for a, b in zip(dec, prev))
        out.extend(pt)
        
        prev = block # 更新前一块密文
        
    # 去除 PKCS#7 填充
    pad = out[-1]
    if not (1 <= pad <= 8):
        raise ValueError(f"填充错误: {pad}")
    if out[-pad:] != bytes([pad]) * pad:
        raise ValueError("填充校验失败")
        
    return bytes(out[:-pad])

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 solve.py enc.txt")
        return
        
    ct = read_emojis(sys.argv[1])
    print(f"[+] 读入密文: {len(ct)} 字节")
    
    pt = decrypt(ct)
    print(f"[+] 解密完成: {len(pt)} 字节\n")
    
    print(pt.decode('utf-8', errors='replace'))
    
    # 自动提取 flag
    import re
    m = re.search(rb"susctf\{.*?\}", pt, re.S)
    if m:
        print("\n[+] 成功拿到 Flag:")
        print(m.group(0).decode('utf-8', 'replace'))

if __name__ == "__main__":
    main()
```

### WSL

先将题目给我们的密文文件enc\.txt从桌面上复制到WSL目录里面

```Bash
cp /mnt/c/Users/hp/Desktop/enc.txt ~/
```

将刚刚的脚本粘贴进WSL中 

（记得在开头加上

```Bash
cat > solve.py << 'EOF'
```



运行脚本

```Bash
python3 solve.py enc.txt
```

![](/images/SUSCTF-2026/QQ_1791279040744.png)

flag：susctf\{Woww\_You\_know\_unp4cking\!\!\!\_I\_am\_gl@d\_to\_see\_you\_solving\_these\_ch4llenges\_\&\_This\_is\_th3\_first\_journey\_7o\_learn\_reverse\_eng1neering\_and\_I\_wi5h\_y0u\_to\_keep\_your\_enthus1asm\_Best\_Wishes\_for\_you\_\&\_Later\_see\_you\_in\_master\_competitions\!\!\!\}
