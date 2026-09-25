+++
title = 'Moectf 2026 -2'
date = '2026-09-13T12:00:00+08:00'
draft = true    # 比赛未结束，暂时下架；赛后改回 false 即可重新发布
summary = ''
tags = []
showtoc = true
+++

接上周没有做完的

二编：后面出的题目做得好困难！虽然看起来做得不多但是其实一直在尝试\.\.\.



## 成都好舍友

flag:moectf\{PYC\_p1us\_QRc0dE\_M1ssing\_c0rN3r\}

> 一道 Python 3\.10 **`.pyc`**** 反编译** \+** 隐藏 QR 码的 CTF 题**。**flag 就藏在 QR 码里，但 QR 码被改造过** —— 三个 finder pattern 全是 7×7 实心黑块（不是标准 1:1:3:1:1 图案），format info 全部丢失。找到它需要先反编译 pyc，再从一堆混淆代码里挖出 base64 图像，接着手动把改造过的 QR 还原成能被标准解码器识别的样子。
> 
> 

我的pydc不成功 直接用在线反编译

[https://pylingual\.io/](https://pylingual.io/) 

![ae61b58bc49ffa3a778a14c08a07d8f6\.png](/images/moectf-2026-2/ae61b58bc49ffa3a778a14c08a07d8f6.png)

```Java
IMAGE_BASE64 = '\niVBORw0KGgoAAAANSUhEUgAAAlsAAAJbCAYAAADTxVFxAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAAHYcAAB2HAY/l8WUAAAGHaVRYdFhNTDpjb20uYWRvYmUueG1wAAAAAAA8P3hwYWNrZXQgYmVnaW49J++7vycgaWQ9J1c1TTBNcENlaGlIenJlU3pOVGN6a2M5ZCc/Pg0KPHg6eG1wbWV0YSB4bWxuczp4PSJhZG9iZTpuczptZXRhLyI…Qd5h7uQ0opX/LqSvfwHcY5lI+fEQEAKlK2AAAqUrYAACpStgAAKlK2AAAqUrYAACpStgAAKlK2AAAqUrYAACpStgAAKlK2AAAqUrYAACpStgAAKlK2AAAqUrYAACr60fd9n4c8nsViEfb7fR4P1jRNaJomjwc7HA5hvV7n8Sjb7TbM5/M8Huz9/T2klPJ4sMlkUvTvhxDCarUKT09P…czX0oP4d7mNJzaNv2y5pjp23bfNl/znd4lkqn9L3kZ0QAgIqULQCAipQtAICKlC0AgIqULQCAipQtAICKlC0AgIqULQCAipQtAICKlC0AgIqULQCAipQtAICKlC0AgIqULQCAin70fd/nIY9nsViE/X6fx4OllMLb21seM1LXdeF8PufxYLPZLEyn0zwe7Hw+h67r8viqNptN2Gw2eTxYjDG0bZvHo9z6PlziHObzeZhMJnk8WOk53IOmaULTNHk8WNd1Yblc5vEo2+02zOfzPH4ope+lz8/P8PHxkceD3cN9KDWfz8N2u83j4Xq+hRhjH0L460kp5UvyF259Dm3bflnz0SbGmG9rtO9wDm3b5svCX3Efbs/PiAAAFSlbAAAVKVsAABUpWwAAFSlbAAAVKVsAABUpWwAAFSlbAAAVKVsAABUpWwAAFSlbAAAVKVsAABUpWwAAFSlbAAAV/V8fKbAXjGbeBQAAAABJRU5ErkJggg==\n'
```

这里复制出来有截断问题 因此我们要换一个思路

Step 1：从 `.pyc` 文件中精确提取 `IMAGE_BASE64` 常量

Step 2：解码嵌套的 Base64\+Zlib，得到 PNG 图片

Step 3：分析并修复二维码

Step 4：解码得到 Flag



利用另外的反编译网站 能支持3\.10的 因为本电脑的python是3\.14 所以一直不成功 但是我不想再下载一个3

https://www\.decompiler\.com/

![QQ\_1788241503295\.png](/images/moectf-2026-2/QQ_1788241503295.png)

download这个file 打开发现可以完整显示字符串

![3e477e5204cc279a3fd6e19ca73ed61e\.png](/images/moectf-2026-2/3e477e5204cc279a3fd6e19ca73ed61e.png)

> `iVBORw0KG` 是 PNG 图片格式 的 Base64 编码特征头。这说明字符串解码后应该是一张图片。
> 
> 

我们要将这个超长字符串变为一个图片

1. 先用脚本尝试 `zlib.decompress`（Zlib 解压），结果报错。

2. 接着我们直接用 `base64.b64decode` 解码，发现得到的二进制数据开头是 `\x89PNG`（PNG 文件固定头）。

```Python
import base64

with open('extracted_base64.txt', 'r', encoding='utf-8') as f:
    b64 = f.read().strip()

png_data = base64.b64decode(b64)
with open('result.png', 'wb') as f:
    f.write(png_data)

print("图片已保存为 result.png")
```

![QQ\_1788246107757\.png](/images/moectf-2026-2/QQ_1788246107757.png)

发现这个二维码根本扫不出来

要为python安装 numpy 和 pillow 两个库，用于图像处理

```Java
pip install numpy
pip install Pillow
```

分析：

1. 看颜色：肉眼看起来像底片（黑底白块）。用像素值分析发现，图片只有 5 个灰度值（0, 55, 128, 200, 255），说明它不是自然照片，而是人为生成的数字化图片。标准 QR 只有黑白，所以必须先做颜色反转。

2. 看尺寸：603 ÷ 37 ≈ 16\.3。**QR 码的模块数必须是 37**（Version 5）。这告诉我们每个小格子大约是 16\.3 像素。（（603 就是这个 PNG 图片的宽度和高度（像素数）。

3. 看角落（核心线索）：反转后，我们用游程分析（看顶部一行黑白长度）。标准 QR 左上角应该是 `黑(1)-白(1)-黑(3)-白(1)-黑(1)` 的“回”字形。但我们发现这三个角全是 7×7 纯黑方块。

**标准要求左上角是黑，图片却是白，那就必须做颜色反转**

得到信息：颜色反了 \+ 三个定位角被涂黑了。这就是解码器拒绝识别的原因。

**QR 标准码的左上、右上、左下，三个角全是“回”字形。**

标准规定这三个角（Finder Pattern）必须是 7×7 的外黑内白结构，比例是 1:1:3:1:1（黑 1 格、白 1 格、黑 3 格、白 1 格、黑 1 格）。用矩阵表示就是：

```Java
黑 黑 黑 黑 黑 黑 黑
黑 白 白 白 白 白 黑
黑 白 黑 黑 黑 白 黑
黑 白 黑 黑 黑 白 黑
黑 白 黑 黑 黑 白 黑
黑 白 白 白 白 白 黑
黑 黑 黑 黑 黑 黑 黑
```

（这个图案是为了让解码器不管怎么旋转扫描都能一眼认出二维码的位置。）

接下来我们要修复这个二维码图像

1. 替换角图案：既然三个角是纯黑，我们就用 QR 国际标准（ISO 18004）里规定的标准 7×7 “回”字图案（`1 1 1... / 1 0 0...`）把它们硬换掉。

2. 修复格式信息（Format Info）：QR 码除了数据，还在特定位置存了 15 位“格式信息”（包含纠错等级和掩码）。题目把这些位置清零了。但标准规定只有 32 种 合法的格式信息组合。暴力试了 32 种，发现只有 `0x`。

### 为什么 Format Info 被清零了？

这 15 位格式信息在 QR 码里被写在固定的位置（比如左上角附近）。出题人为了让题更难，把这 15 个位置的像素全部涂成了 0（白色）。所以解码器读不到这两条关键信息，直接报错。

### 为什么是 32 种？0x1CE7 又是什么？

因为**纠错等级有 4 种 × 掩码模式有 8 种 = 32 种排列组合。**

虽然我们不知道出题人当初用的是什么组合，但无非就是这 32 种之一。

写一个程序，把这 32 种组合（写成二进制 15 位数字，比如 `0x1CE7` 就是其中一个）逐个填进那 15 个被清空的像素位置。每填一次，就拿给解码器试一次。

- 当填到 `0x1CE7` 时，解码器通过了数学校验（Reed\-Solomon 纠错校验），并且读出来的数据长度恰好符合 V5 版本的容量限制（38 字节）。

- 而填其他 31 个时，要么数学校验失败报错，要么读出来的数据长度不对（比如多出几个乱码字节）。

所以 `0x1CE7` 就是我们通过暴力测试找到的唯一正确答案。它对应的实际含义是：纠错等级 L \+ 掩码模式 0。



- 颜色反转

- 采样成 37×37 模块

- 替换三个定位图案为标准「回」字

- 填入正确的格式信息（`0x1CE7`）

```Python
import numpy as np
from PIL import Image

# 读取图片并二值化
img = np.array(Image.open('result.png').convert('L'))
inv = 255 - img
binary = (inv < 128).astype(np.uint8)

# 采样到 37x37
M, off = 16.3, 0.1
matrix = np.zeros((37, 37), dtype=np.uint8)
for y in range(37):
    for x in range(37):
        cy = int(off + (y + 0.5) * M)
        cx = int(off + (x + 0.5) * M)
        if 0 <= cy < 603 and 0 <= cx < 603:
            matrix[y, x] = binary[cy, cx]

# 标准 finder pattern (1:1:3:1:1)
finder = np.array([
    [1,1,1,1,1,1,1],
    [1,0,0,0,0,0,1],
    [1,0,1,1,1,0,1],
    [1,0,1,1,1,0,1],
    [1,0,1,1,1,0,1],
    [1,0,0,0,0,0,1],
    [1,1,1,1,1,1,1]
])
matrix[0:7, 0:7] = finder
matrix[0:7, 30:37] = finder
matrix[30:37, 0:7] = finder

# 格式信息 0x1CE7
code = 0x1CE7
zx_x = [0,1,2,3,4,5,7,8,8,8,8,8,8,8,8]
zx_y = [8,8,8,8,8,8,8,8,7,5,4,3,2,1,0]
for i in range(15):
    matrix[zx_y[i], zx_x[i]] = (code >> i) & 1
for i in range(7):
    matrix[36-i, 8] = (code >> i) & 1
for i in range(8):
    matrix[8, 29+i] = (code >> (7+i)) & 1

# 保存为正常黑白图（方便扫码）
out = (1 - matrix) * 255
Image.fromarray(out.astype(np.uint8)).save('fixed_qr.png')
print("✅ 修复后的二维码已保存为 fixed_qr.png")
```

得到二维码

![QQ\_1788246352532\.png](/images/moectf-2026-2/QQ_1788246352532.png)

用标准qr解码器解码即可 

使用手机端扫一扫其实就行 得到：moectf\{PYC\_p1us\_QRc0dE\_M1ssing\_c0rN3r\}

## **Ultato Polosion Xptra \-\-?**

加壳了

```Java
upx -d C:\Users\hp\Downloads\chall9.3
```

![a9c781d87c468a9d72ae7f990676f04d\.png](/images/moectf-2026-2/a9c781d87c468a9d72ae7f990676f04d.png)

![e4eaecfa2bc8664925e0cdfc06a105ee\.png](/images/moectf-2026-2/e4eaecfa2bc8664925e0cdfc06a105ee.png)

用upx脱壳居然失败了。！

> 这是 文件在 UPX 加壳之后，被人为修改过（比如改写了壳的头部校验字节，或者在文件末尾额外附加了数据），目的是专门阻止你用 `upx -d` 直接脱壳。这在 CTF 逆向题或恶意软件加壳中非常常见。
> 
> 



![QQ\_1787836041923\.png](/images/moectf-2026-2/QQ_1787836041923.png)























## 广晨风语录

flag:moectf\{Ea5y\_4ndroiD\_Nativ3\}

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

其实事实上没啥用。

![4b7311cee46f24ff59ba6b6dbd662b6d\.png](/images/moectf-2026-2/4b7311cee46f24ff59ba6b6dbd662b6d.png)

~~做这个题做了半天全怪我想完整学一遍安卓再回来做 结果啥也没学会脑子还变得更乱了。。我服了。~~

Ghidra也是下载之后不看教程的起手就要用 结果用了一天以为自己下载有问题有遗漏 结果其实是使用方法完全错误 但是点开页面还是不对劲遂选择继续ida

摸清结构：

```Bash
unzip gcfquotes.apk -d apk/
ls apk/
# AndroidManifest.xml  classes.dex  res/  resources.arsc  lib/  META-INF/
ls apk/lib/
# arm64-v8a/  armeabi-v7a/  x86_64/   每个目录里都有 libgcquotes.so
```

**结论：典型的 Java 壳 \+ native 验证逻辑。**

mainactivity

![12fdf3aefaaae3d336550ba0e5519caa\.png](/images/moectf-2026-2/12fdf3aefaaae3d336550ba0e5519caa.png)

```Java
public class MainActivity extends Activity {
    private EditText  input;
    private boolean   nativeLoaded;
    private TextView  output;

    // 按钮点击 → synthetic 包装 → submitInput
    void submitInput() {
        if (!nativeLoaded) {
            try {
                System.loadLibrary("gcquotes");
                nativeLoaded = true;
            } catch (Throwable t) {
                output.setText("超市就是大润发");  // 加载失败提示
                return;
            }
        }
        String s = input.getText().toString();
        String r = nativeQuote(s);   // 关键 JNI 调用
        if (r != null && r.length() != 0) {
            output.setText(r);
        } else {
            output.setText("电车就是问界");  // 验证失败提示
        }
    }
}
```

> **重点：**
> 
> - **输入框内容 → ****`nativeQuote(s)`**** → 输出**
> 
> - **`nativeQuote`**** 是 native 方法，实现在 ****`libgcquotes.so`**
> 
> - **三条中文 quote 看起来是干扰项，下面会看到它们和验证逻辑有关**
> 
> 

submitInput函数最为重要：

```Java
System.loadLibrary("gcquotes");  // ← 这说明逻辑在 .so 里
String r = nativeQuote(s);       // ← 我们输入 s，它返回 r
if (r != null) {
    output.setText(r);           // ← 如果返回的不是空，就显示结果
}
```

ghidra学了半天~~跟狗屎一样~~ 后面慢慢学吧。。

问了ai居然两个用途真差不多。。

![aa57370f532785448b80ea348d0e6e7f\.png](/images/moectf-2026-2/aa57370f532785448b80ea348d0e6e7f.png)

![36979390cf683c1ecd267c536366ccd9\.png](/images/moectf-2026-2/36979390cf683c1ecd267c536366ccd9.png)

submitInput与nativeQuote

> - `submitInput` 是 APP 的“大门”（Java 层入口）
> 
>     - 这是你点击按钮时，Android 系统第一个调用的 Java 函数。
> 
>     - 它负责：获取你输入的文字 \-\> 加载 `.so` 库 \-\> 调用 `nativeQuote` \-\> 把结果显示在屏幕上。
> 
> - `nativeQuote` 是 Native 层的“房门”（JNI 入口）
> 
>     - 这是 Java 代码跨过边境（JNI 边界），进入 C/C\+\+ 世界（`.so` 文件）的第一个函数。
> 
>     - 它是连接 Java 和 C\+\+ 的“桥梁”。
> 
> 

为什么重点函数要找 `process`

![c77f04ab64ae72059ef54bbb73bab9df\.png](/images/moectf-2026-2/c77f04ab64ae72059ef54bbb73bab9df.png)

process中最后调用了vertify和prepare

![QQ\_1787833133054\.png](/images/moectf-2026-2/QQ_1787833133054.png)

![863042c2d9d7cbaf3d7c011f67a34caa\.png](/images/moectf-2026-2/863042c2d9d7cbaf3d7c011f67a34caa.png)

![c31fad81f60e0ba61360e4fb87a43fb4\.png](/images/moectf-2026-2/c31fad81f60e0ba61360e4fb87a43fb4.png)

```Java
unsigned char ida_chars[] =
{
  0xC7, 0xE7, 0x0D, 0x31, 0x4A, 0x73, 0x87, 0x8D, 0xB3, 0x89, 
  0xAF, 0xEF, 0x44, 0x65, 0x8E, 0xA3, 0xC3, 0xE5, 0x2E, 0x6E, 
  0xBF, 0xE1, 0x1A, 0x4C, 0x65, 0xD9, 0x1B, 0x00
};
```

transform和compare

![a56859ba79be05bd545fa1dc18816ee3\.png](/images/moectf-2026-2/a56859ba79be05bd545fa1dc18816ee3.png)

![d3babf5b0327beebcbade32def0fe1fc\.png](/images/moectf-2026-2/d3babf5b0327beebcbade32def0fe1fc.png)

### 总结

- Java 层（MainActivity） = 饮料机的投币口和按钮（你输入字符串，点击提交）。

- `nativeQuote` 入口 = 饮料机的内部管道入口（你把钱和选择传进去）。

- `process` 函数 = 饮料机的中央调配室（所有原料在这里混合）。

- `verify` 函数 = 饮料机的质检员（检查调配出来的饮料对不对）。

- `byte_3020`（target 数组） = 质检员手里的“标准口味配方卡”（他拿这个比对，对的就放行）。

- `transform` 函数 = 调配室里的“搅拌机”（把你的输入搅成另一种形态）。

**脚本**

- 设 `in[i]` 是变换前的第 i 个字节。

- 设 `out[i]` 是变换后的第 i 个字节。

正向加密过程（代码在做的）：

1. `out[0] = in[0]`（第一个字节不变）。

2. `out[i] = in[i] ^ (out[i-1] + 0x28) ^ 0x67`（重点：这里的 `out[i-1]` 是已经变过的前一个字节）。

```Python
# 这就是 WriteUp 里说的，在 .so 文件里找到的那 27 个“标准答案”字节
target = [0xc7,0xe7,0x0d,0x31,0x4a,0x73,0x87,0x8d,0xb3,0x89,0xaf,0xef,
          0x44,0x65,0x8e,0xa3,0xc3,0xe5,0x2e,0x6e,0xbf,0xe1,0x1a,0x4c,
          0x65,0xd9,0x1b]

# 第一步：反向推导 transform 算法（把加密过程倒过来）
Q = [0] * 27
Q[0] = target[0]  # 第一个字节不变
for i in range(1, 27):
    # 这就是反推那个异或公式
    Q[i] = target[i] ^ ((target[i-1] + 0x28) & 0xFF) ^ 0x67

# 第二步：反向推导 prepare 算法（把第一个字节的异或 0xAA 退回去）
flag_bytes = [0] * 27
flag_bytes[0] = Q[0] ^ 0xAA
for i in range(1, 27):
    flag_bytes[i] = Q[i]

# 第三步：把这串数字变成我们能读的字符串
flag = bytes(flag_bytes).decode('utf-8')
print("Flag 是：", flag)
```



### 一些小问题的学习

#### 如何锁定 `submitInput`？

因为“点击按钮”这个动作，最终一定会调用它。

> 你在 Java 代码里找 `setOnClickListener`（设置点击监听器），这是 Android 里“按钮被点击”的固定写法。
> 
> - 你在代码里会看到：`((Button) findViewById(R.id.submit)).setOnClickListener(...)`
> 
> - 这意味着“当 submit 按钮被点击时，执行括号里的代码”。
> 
> - 括号里写着：`MainActivity.this.submitInput();`
> 
> 

#### 为什么 `System.loadLibrary("gcquotes")` 说明逻辑在 \.so 里？

这句中文翻译过来就是“系统，去给我加载那个叫 gcquotes 的‘外挂包’”。

- `loadLibrary` 的英文直译就是 加载（load） 库（Library）。

- 安卓里的 `.so` 文件（Shared Object），就是 C/C\+\+ 编译好的“外挂包”。

- 如果 Java 代码里没有这句话，那么下面那个 `nativeQuote` 方法一运行，APP 就会直接崩溃，因为找不到地方执行。

#### 为什么 `String r = nativeQuote(s);` 表示输入 s 返回 r？

这是 Java 语法规定的“等号传递”。

- `s` 是括号里的东西（`nativeQuote(s)`），表示“我要把这个东西传进去”。

- `r` 在等号左边（`String r =`），表示“函数执行完后，会吐出来一个结果，我用 `r` 这个盒子接住它”。

![QQ\_1787740871581\.png](/images/moectf-2026-2/QQ_1787740871581.png)

## 请fanchai喝茶  

flag:moectf\{Tre4t\_f4ncha1\_W1tH\_xxtea\_Wh4t\_A\_g00d\_Id3a\_HahaHAh4hAH4ha\}

![QQ\_1788333180983\.png](/images/moectf-2026-2/QQ_1788333180983.png)

进了主函数部分发现逻辑中有很多复杂的运算

首先输入16个整数块

![QQ\_1788333452637\.png](/images/moectf-2026-2/QQ_1788333452637.png)

接着对其做一些复杂的运算 主要就是xxtea的魔改版 **本质上是在做一个对称加密 **这是主要逻辑处

循环结束之后 将这16个整数拼成4组 分别对应v27 v26 v28 v29

这四组数分别与硬编码异或 2030 2040 2050 2060

如果四组异或的结果均为0的话 则说明计算后的结果等于硬编码常量 则输出correct 为正确flag



发现有两个不太熟悉的指令： \_mm\_or\_si128 和  \_mm\_xor\_si128

- 它是 **SSE 指令**（Intel 的 128 位单指令多数据流扩展），操作对象是 16 个字节（128 位）。

- `_mm_xor_si128(A, B)`：把 A 和 B 的 16 个字节逐位异或。

- `_mm_or_si128(A, B)`：把 A 和 B 的 16 个字节逐位或。

数学性质：

如果A与B完全相同的话，则A xor B = 0

如果我们把好几组 `XOR` 的结果用 `OR` 串起来，只要其中有一组 `XOR` 结果不是 0（即某个字节不匹配），那么最终的 `OR` 结果就一定不是 0。

只有当所有组的xor结果都是0时，最后or的结果才能为0

**总结**：看到 `XOR` \+ `OR` 连用，直接按 `if (A==B && C==D)` 解读就行

现在提取异或的硬编码：

```C
unsigned char ida_chars[] =  //2030
{
  0x7C, 0x08, 0xEA, 0x8E, 0xE5, 0xCE, 0xF3, 0x99, 0xF3, 0x5A, 
  0xAA, 0x60, 0x27, 0x4D, 0x9F, 0x8D
};
unsigned char ida_chars[] =  //2040
{
  221, 223, 235, 132, 88, 227, 107, 100, 152, 131, 
  119, 55, 88, 165, 208, 196
};
unsigned char ida_chars[] =  //2050
{
  0xE8, 0xD1, 0x4A, 0x82, 0xE5, 0xE9, 0xFE, 0xC3, 0xE9, 0xEA, 
  0xE5, 0xC4, 0x00, 0x88, 0x60, 0x08
};
unsigned char ida_chars[] =  //2060
{
  0xF4, 0x25, 0xF4, 0x89, 0x97, 0x94, 0x77, 0x59, 0xC3, 0x37, 
  0xF5, 0x45, 0x54, 0x99, 0x9B, 0x22
};
```

加密循环体变量更新的顺序是：

`v25 → v24 → v20 → v19 → v18 → v23 → v22 → v21 → v8 → v9 → v10 → v11 → v12 → v13 → v14 → v7`

解密顺序就是反过来的：
`v7 → v14 → v13 → v12 → v11 → v10 → v9 → v8 → v21 → v22 → v23 → v18 → v19 → v20 → v24 → v25`

并且所有的 `+=` 都变成 `-=`，因为我们要撤销加密时的加法。

**注意**：写脚本时**每一行末尾加上 ****`& 0xFFFFFFFF`** 保证 32 位溢出（因为 C 的 `unsigned int` 会自动截断）。

### Exp

```Python
import struct

K = [0x4D4F4543, 0x54463230, 0x32365858, 0x54454121]

cipher_bytes = [
    bytes([0x7C,0x08,0xEA,0x8E,0xE5,0xCE,0xF3,0x99,0xF3,0x5A,0xAA,0x60,0x27,0x4D,0x9F,0x8D]),
    bytes([0xDD,0xDF,0xEB,0x84,0x58,0xE3,0x6B,0x64,0x98,0x83,0x77,0x37,0x58,0xA5,0xD0,0xC4]),
    bytes([0xE8,0xD1,0x4A,0x82,0xE5,0xE9,0xFE,0xC3,0xE9,0xEA,0xE5,0xC4,0x00,0x88,0x60,0x08]),
    bytes([0xF4,0x25,0xF4,0x89,0x97,0x94,0x77,0x59,0xC3,0x37,0xF5,0x45,0x54,0x99,0x9B,0x22])
]

def to_u32(b, endian):
    return [int.from_bytes(b[i:i+4], endian) for i in range(0, 16, 4)]

def decrypt(use_before_sub, variant, endian):
    if variant == 0:
        v18, v23, v22, v21 = to_u32(cipher_bytes[0], endian)
        v25, v24, v20, v19 = to_u32(cipher_bytes[1], endian)
        v12, v13, v14, v7  = to_u32(cipher_bytes[2], endian)
        v8,  v9,  v10, v11 = to_u32(cipher_bytes[3], endian)
    else:
        v25, v24, v20, v19 = to_u32(cipher_bytes[0], endian)
        v18, v23, v22, v21 = to_u32(cipher_bytes[1], endian)
        v12, v13, v14, v7  = to_u32(cipher_bytes[2], endian)
        v8,  v9,  v10, v11 = to_u32(cipher_bytes[3], endian)

    DELTA = 1597463007
    if use_before_sub:
        v6 = 1492265175
        while v6 != 0:
            idx0 = (v6 >> 2) & 3
            idx1 = ((v6 >> 2) ^ 1) & 3
            idx2 = ((v6 >> 2) ^ 2) & 3
            idx3 = (~(v6 >> 2)) & 3
            idx5 = ((v6 >> 2) ^ 5) & 3
            idx6 = ((v6 >> 2) ^ 6) & 3
            idx7 = ((v6 >> 2) ^ 7) & 3
            idx9 = ((v6 >> 2) ^ 9) & 3
            idxA = ((v6 >> 2) ^ 0xA) & 3
            idxB = ((v6 >> 2) ^ 0xB) & 3
            idxD = ((v6 >> 2) ^ 0xD) & 3
            idxE = ((v6 >> 2) ^ 0xE) & 3
            idxF = ((v6 >> 2) ^ 0xF) & 3

            v7 = (v7 - ((((16 * v14) ^ (v25 >> 3)) + ((4 * v25) ^ (v14 >> 5))) ^ ((v6 ^ v25) + (v14 ^ K[idxF])))) & 0xFFFFFFFF
            v14 = (v14 - ((((v13 >> 5) ^ (4 * v7)) + ((v7 >> 3) ^ (16 * v13))) ^ ((v7 ^ v6) + (v13 ^ K[idxE])))) & 0xFFFFFFFF
            v13 = (v13 - ((((v12 >> 5) ^ (4 * v14)) + ((v14 >> 3) ^ (16 * v12))) ^ ((v14 ^ v6) + (v12 ^ K[idxD])))) & 0xFFFFFFFF
            v12 = (v12 - ((((16 * v11) ^ (v13 >> 3)) + ((4 * v13) ^ (v11 >> 5))) ^ ((v13 ^ v6) + (v11 ^ K[idx0])))) & 0xFFFFFFFF
            v11 = (v11 - ((((16 * v10) ^ (v12 >> 3)) + ((4 * v12) ^ (v10 >> 5))) ^ ((v12 ^ v6) + (v10 ^ K[idxB])))) & 0xFFFFFFFF
            v10 = (v10 - ((((16 * v9) ^ (v11 >> 3)) + ((4 * v11) ^ (v9 >> 5))) ^ ((v11 ^ v6) + (v9 ^ K[idxA])))) & 0xFFFFFFFF
            v9 = (v9 - ((((16 * v8) ^ (v10 >> 3)) + ((4 * v10) ^ (v8 >> 5))) ^ ((v10 ^ v6) + (v8 ^ K[idx9])))) & 0xFFFFFFFF
            v8 = (v8 - ((((16 * v21) ^ (v9 >> 3)) + ((4 * v9) ^ (v21 >> 5))) ^ ((v9 ^ v6) + (v21 ^ K[idx0])))) & 0xFFFFFFFF
            v21 = (v21 - ((((16 * v22) ^ (v8 >> 3)) + ((4 * v8) ^ (v22 >> 5))) ^ ((v8 ^ v6) + (v22 ^ K[idx7])))) & 0xFFFFFFFF
            v22 = (v22 - ((((16 * v23) ^ (v21 >> 3)) + ((4 * v21) ^ (v23 >> 5))) ^ ((v21 ^ v6) + (v23 ^ K[idx6])))) & 0xFFFFFFFF
            v23 = (v23 - ((((16 * v18) ^ (v22 >> 3)) + ((4 * v22) ^ (v18 >> 5))) ^ ((v22 ^ v6) + (v18 ^ K[idx5])))) & 0xFFFFFFFF
            v18 = (v18 - ((((16 * v19) ^ (v23 >> 3)) + ((4 * v23) ^ (v19 >> 5))) ^ ((v23 ^ v6) + (v19 ^ K[idx0])))) & 0xFFFFFFFF
            v19 = (v19 - ((((16 * v20) ^ (v18 >> 3)) + ((4 * v18) ^ (v20 >> 5))) ^ ((v18 ^ v6) + (v20 ^ K[idx3])))) & 0xFFFFFFFF
            v20 = (v20 - ((((16 * v24) ^ (v19 >> 3)) + ((4 * v19) ^ (v24 >> 5))) ^ ((v19 ^ v6) + (v24 ^ K[idx2])))) & 0xFFFFFFFF
            v24 = (v24 - ((((16 * v25) ^ (v20 >> 3)) + ((4 * v20) ^ (v25 >> 5))) ^ ((v20 ^ v6) + (v25 ^ K[idx1])))) & 0xFFFFFFFF
            v25 = (v25 - (((v6 ^ v24) + (v7 ^ K[idx0])) ^ (((4 * v24) ^ (v7 >> 5)) + ((16 * v7) ^ (v24 >> 3))))) & 0xFFFFFFFF

            v6 = (v6 - DELTA) & 0xFFFFFFFF
    else:
        v6 = 1492265175
        while v6 != 0:
            v6 = (v6 - DELTA) & 0xFFFFFFFF
            idx0 = (v6 >> 2) & 3
            idx1 = ((v6 >> 2) ^ 1) & 3
            idx2 = ((v6 >> 2) ^ 2) & 3
            idx3 = (~(v6 >> 2)) & 3
            idx5 = ((v6 >> 2) ^ 5) & 3
            idx6 = ((v6 >> 2) ^ 6) & 3
            idx7 = ((v6 >> 2) ^ 7) & 3
            idx9 = ((v6 >> 2) ^ 9) & 3
            idxA = ((v6 >> 2) ^ 0xA) & 3
            idxB = ((v6 >> 2) ^ 0xB) & 3
            idxD = ((v6 >> 2) ^ 0xD) & 3
            idxE = ((v6 >> 2) ^ 0xE) & 3
            idxF = ((v6 >> 2) ^ 0xF) & 3

            v7 = (v7 - ((((16 * v14) ^ (v25 >> 3)) + ((4 * v25) ^ (v14 >> 5))) ^ ((v6 ^ v25) + (v14 ^ K[idxF])))) & 0xFFFFFFFF
            v14 = (v14 - ((((v13 >> 5) ^ (4 * v7)) + ((v7 >> 3) ^ (16 * v13))) ^ ((v7 ^ v6) + (v13 ^ K[idxE])))) & 0xFFFFFFFF
            v13 = (v13 - ((((v12 >> 5) ^ (4 * v14)) + ((v14 >> 3) ^ (16 * v12))) ^ ((v14 ^ v6) + (v12 ^ K[idxD])))) & 0xFFFFFFFF
            v12 = (v12 - ((((16 * v11) ^ (v13 >> 3)) + ((4 * v13) ^ (v11 >> 5))) ^ ((v13 ^ v6) + (v11 ^ K[idx0])))) & 0xFFFFFFFF
            v11 = (v11 - ((((16 * v10) ^ (v12 >> 3)) + ((4 * v12) ^ (v10 >> 5))) ^ ((v12 ^ v6) + (v10 ^ K[idxB])))) & 0xFFFFFFFF
            v10 = (v10 - ((((16 * v9) ^ (v11 >> 3)) + ((4 * v11) ^ (v9 >> 5))) ^ ((v11 ^ v6) + (v9 ^ K[idxA])))) & 0xFFFFFFFF
            v9 = (v9 - ((((16 * v8) ^ (v10 >> 3)) + ((4 * v10) ^ (v8 >> 5))) ^ ((v10 ^ v6) + (v8 ^ K[idx9])))) & 0xFFFFFFFF
            v8 = (v8 - ((((16 * v21) ^ (v9 >> 3)) + ((4 * v9) ^ (v21 >> 5))) ^ ((v9 ^ v6) + (v21 ^ K[idx0])))) & 0xFFFFFFFF
            v21 = (v21 - ((((16 * v22) ^ (v8 >> 3)) + ((4 * v8) ^ (v22 >> 5))) ^ ((v8 ^ v6) + (v22 ^ K[idx7])))) & 0xFFFFFFFF
            v22 = (v22 - ((((16 * v23) ^ (v21 >> 3)) + ((4 * v21) ^ (v23 >> 5))) ^ ((v21 ^ v6) + (v23 ^ K[idx6])))) & 0xFFFFFFFF
            v23 = (v23 - ((((16 * v18) ^ (v22 >> 3)) + ((4 * v22) ^ (v18 >> 5))) ^ ((v22 ^ v6) + (v18 ^ K[idx5])))) & 0xFFFFFFFF
            v18 = (v18 - ((((16 * v19) ^ (v23 >> 3)) + ((4 * v23) ^ (v19 >> 5))) ^ ((v23 ^ v6) + (v19 ^ K[idx0])))) & 0xFFFFFFFF
            v19 = (v19 - ((((16 * v20) ^ (v18 >> 3)) + ((4 * v18) ^ (v20 >> 5))) ^ ((v18 ^ v6) + (v20 ^ K[idx3])))) & 0xFFFFFFFF
            v20 = (v20 - ((((16 * v24) ^ (v19 >> 3)) + ((4 * v19) ^ (v24 >> 5))) ^ ((v19 ^ v6) + (v24 ^ K[idx2])))) & 0xFFFFFFFF
            v24 = (v24 - ((((16 * v25) ^ (v20 >> 3)) + ((4 * v20) ^ (v25 >> 5))) ^ ((v20 ^ v6) + (v25 ^ K[idx1])))) & 0xFFFFFFFF
            v25 = (v25 - (((v6 ^ v24) + (v7 ^ K[idx0])) ^ (((4 * v24) ^ (v7 >> 5)) + ((16 * v7) ^ (v24 >> 3))))) & 0xFFFFFFFF

    # 打包
    if endian == 'little':
        plain = struct.pack('<16I', v25, v24, v20, v19, v18, v23, v22, v21, v8, v9, v10, v11, v12, v13, v14, v7)
    else:
        plain = struct.pack('>16I', v25, v24, v20, v19, v18, v23, v22, v21, v8, v9, v10, v11, v12, v13, v14, v7)
    return plain

def try_all():
    for use_before in [True, False]:
        for var in [0, 1]:
            for endian in ['little', 'big']:
                plain = decrypt(use_before, var, endian)
                hex_str = plain.hex()
                try:
                    ascii_part = plain[:20].decode('ascii', errors='ignore')
                except:
                    ascii_part = ''
                # 检查是否包含常见 flag 前缀
                if 'flag' in ascii_part.lower() or 'ctf' in ascii_part.lower():
                    print(f"   Found! use_before={use_before}, var={var}, endian={endian}")
                    print(f"   Full Hex: {hex_str}")
                    print(f"   Decoded: {plain.decode('utf-8', errors='ignore')}")
                    return
                else:
                    print(f"   use_before={use_before}, var={var}, endian={endian} -> {hex_str[:32]}... (ASCII: {ascii_part})")
    print("None found.")

try_all()
```

得到flag:moectf\{Tre4t\_f4ncha1\_W1tH\_xxtea\_Wh4t\_A\_g00d\_Id3a\_HahaHAh4hAH4ha\}
