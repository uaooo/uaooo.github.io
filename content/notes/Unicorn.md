+++
title = 'Unicorn'
date = '2026-10-15T12:00:00+08:00'
draft = false
summary = ''
tags = []
showtoc = true
+++
参考文章：[技术工具：Unicorn 引擎 —— 逆向工程师的 “模拟神器“\_unicorn python\-CSDN博客](https://blog.csdn.net/m0_57836225/article/details/154300825)

在逆向工程与二进制分析领域，Unicorn 引擎以其 "轻量、跨平台、多架构" 的特性，成为继 QEMU 之后最受推崇的 CPU  模拟器。它不仅是恶意代码安全研究员的得力助手，更是嵌入式开发、恶意代码分析、漏洞挖掘等场景的核心工具。

## Unicorn引擎核心认知

### 引擎定位与发展历程

Unicorn 是一款开源跨平台** CPU 模拟器框架**，由越南安全研究员 Nguyen Anh Quynh（知名逆向 工具 Radare2 核心开发者）于 2015 年发起，旨在解决传统模拟器 "笨重、API 复杂、扩展性差" 的痛点。其核心代码基于 QEMU 的 CPU 模拟层，但剥离了 QEMU 的设备模拟与操作系统依赖，仅保留最纯粹的指令集模拟能力，因此更轻量、更灵活。

官方网站：https://www\.unicorn\-engine\.org/

核心优势：支持 x86、ARM、MIPS、PowerPC 等 7 种架构，提供 Python/Java/Go/C\# 等 10 \+ 语言绑定，单文件核心库仅 200\-500KB（视架构而定）。



**逆向场景首选 Unicorn 的原因**：

1. **无需启动完整系统，直接加载二进制代码即可模拟**，适合快速验证漏洞；

2. 支持在模拟过程中随时中断、修改寄存器 / 内存，便于调试加密算法、壳程序；

3. 多语言 API 降低使用门槛（尤其 Python 绑定，适合快速编写脚本）。

### 核心应用场景

恶意代码分析：**在隔离环境中模拟执行病毒、木马，记录其文件操作、网络行为，避免真实系统感染；**

固件逆向：模拟路由器、物联网设备的 MIPS/ARM 架构代码，挖掘命令注入、缓冲区溢出等漏洞；

**加密算法还原**：模拟执行二进制中的加密函数，通过修改内存 / 寄存器值，逆向推导密钥生成逻辑；

漏洞利用验证：在模拟环境中测试 Exploit，观察内存布局变化，无需真实靶机即可验证利用链；

嵌入式开发调试：在 PC 上模拟嵌入式芯片（如 ARM Cortex\-M）的指令执行，加速固件开发流程。

## 环境搭建

### 安装

```Bash
pip install unicorn
```



验证安装

```Python
import unicorn
 
# 打印支持的架构
print("支持的架构：", [name for name in dir(unicorn) if name.startswith("UC_ARCH_")])
# 预期输出包含：UC_ARCH_X86、UC_ARCH_ARM、UC_ARCH_MIPS等
```

### 源码编译

若需要修改引擎核心代码（如添加自定指令支持），需从源码编译

```Bash
# 克隆仓库
git clone https://github.com/unicorn-engine/unicorn.git
cd unicorn
 
# 初始化子模块（依赖QEMU源码）
git submodule update --init --recursive
 
# 编译（以Linux为例）
./make.sh
sudo ./make.sh install
 
# 安装Python绑定
cd bindings/python
python setup.py install
```

## 核心API详解

\-\-unicorn的操作手册

Unicorn 的 API 设计遵循 "初始化→配置→执行→清理" 的流程，核心操作围绕**模拟器实例、内存管理、寄存器操作、执行控制**四大模块展开。

### 模拟器初始化

**核心函数\-\-**`Uc()`**

创建特定架构的模拟器实例，是所有操作的起点

```Python
from unicorn import Uc, UC_ARCH_X86, UC_MODE_32
 
# 创建x86 32位架构的模拟器
mu = Uc(UC_ARCH_X86, UC_MODE_32)
```

1. `from unicorn import Uc, UC_ARCH_X86, UC_MODE_32`

这行是“从工具箱里拿工具”：

- `Uc`：Unicorn 的核心类。你需要用它来创建模拟器。

- `UC_ARCH_X86`：告诉模拟器，我们要模拟的是 x86 架构（也就是常见的 Intel/AMD CPU 指令集）。

- `UC_MODE_32`：告诉模拟器，我们要模拟的是 32 位模式。

2. `mu = Uc(UC_ARCH_X86, UC_MODE_32)`

这行是“真正组装电脑”：

- `mu`：是我们给这台模拟器起的变量名（通常代表 Microprocessor Unit 或 Emulator，你叫它 `emu`、`machine` 也行，但社区里习惯叫 `mu`）。

- **`Uc(...)`**：调用构造函数，创建出一个实例。**

- 合起来的意思就是：创建一台 32 位的 x86 模拟器，并命名为 mu。

#### 常见架构与模式参数

架构                    架构参数                  模式参数（示例）

x86 32 位          UC\_ARCH\_X86             UC\_MODE\_32

x86 64 位          UC\_ARCH\_X86             UC\_MODE\_64

ARM 32 位        UC\_ARCH\_ARM        UC\_MODE\_ARM（ARM 模式）/ UC\_MODE\_THUMB（Thumb 模式）

ARM 64 位        UC\_ARCH\_ARM64        UC\_MODE\_ARM64

MIPS 32 位        UC\_ARCH\_MIPS          UC\_MODE\_MIPS32 \+ UC\_MODE\_BIG\_ENDIAN（大端序）

### 内存管理

核心函数：`mem_map()`、`mem_write()`、`mem_read()`

模拟器需要**手动分配内存并写入代码/数据**，模拟真实程序的内存布局

```Python
# 1. 分配内存（地址0x10000000，大小0x1000，权限为可读可写可执行）
# 权限参数：UC_PROT_READ（0x1）、UC_PROT_WRITE（0x2）、UC_PROT_EXEC（0x4）
mu.mem_map(0x10000000, 0x1000, 0x7)  # 0x7 = 0x1|0x2|0x4
 
# 2. 写入代码（示例：x86汇编"mov eax, 1; add eax, 2"的机器码）
code = b"\xb8\x01\x00\x00\x00"  # mov eax, 1
code += b"\x83\xc0\x02"         # add eax, 2
mu.mem_write(0x10000000, code)
 
# 3. 读取内存（验证写入是否成功）
read_code = mu.mem_read(0x10000000, len(code))
print("写入的代码：", read_code.hex())  # 应与code的十六进制一致
```

> - `0x1` = 可读（Read）
> 
> - `0x2` = 可写（Write）
> 
> - `0x4` = 可执行（Execute，也就是可以当代码跑）
> 
> - **`0x7`** 就是 **`0x1 | 0x2 | 0x4`**（按位或），代表这块内存既能读，又能写，还能当代码执行。**
> 
> - 这就是为什么很多 CTF 教程里都写 `0x7`，因为要给模拟器“完全权限”。
> 
> 

**注意事项：**

- 内存地址需**按目标架构的页大小对齐**（如 x86 页大小为 4KB=0x1000）；

- 若写入 / 读取的地址未分配内存，会抛出`UC_ERR_WRITE_UNMAPPED`或`UC_ERR_READ_UNMAPPED`错误。

### 寄存器操作

**通过读写寄存器，可控制程序执行流程或获取中间结果**

```Python
from unicorn.x86_const import UC_X86_REG_EAX, UC_X86_REG_ESP
 
# 1. 写入寄存器（设置栈指针ESP，避免执行时栈错误）
mu.reg_write(UC_X86_REG_ESP, 0x20000000)  # 假设0x20000000是已分配的栈内存
 
# 2. 执行代码（从0x10000000开始，执行len(code)长度）
mu.emu_start(0x10000000, 0x10000000 + len(code))
 
# 3. 读取寄存器（获取EAX的值，预期结果为3）
result = mu.reg_read(UC_X86_REG_EAX)
print("EAX =", result)  # 输出：EAX = 3
```

寄存器常量：不同架构的寄存器常量定义在对应的模块中（如 x86 对应unicorn\.x86\_const，ARM 对应unicorn\.arm\_const），常用寄存器如下：

x86：EAX/EBX/ECX/EDX（通用寄存器）、ESP/EBP（栈指针）、EIP（指令指针）；

ARM：R0\-R15（通用寄存器，R15 是 PC 程序计数器）、CPSR（状态寄存器）。

### 执行控制

**核心函数：**`emu_start()`**、**`emu_stop()`**、钩子机制**

`emu_start()`是**执行模拟的核心函数**，支持设置起始地址、结束地址、超时时间等参数；钩子机制则允许在**执行过程中插入自定义逻辑**（如监控内存访问、指令执行）。

#### 基础执行控制

```Python
# 执行从0x10000000开始，到0x10000005结束的代码，超时时间1000ms
mu.emu_start(0x10000000, 0x10000005, timeout=1000)
 
# 强制停止模拟（通常在钩子中使用）
# mu.emu_stop()
```

#### 钩子机制\-\-监控指令实行

通过`hook_add()`注册钩子，可在指令执行前/后，内存读写时**触发自定义函数**

```Python
def hook_code(uc, address, size, user_data):
    # 打印当前执行的指令地址和大小
    print(f"执行指令：地址=0x{address:x}，大小={size}字节")
 
# 注册指令执行钩子（UC_HOOK_CODE表示监控指令执行）
hook_handle = mu.hook_add(UC_HOOK_CODE, hook_code)
 
# 执行代码（此时会触发hook_code函数）
mu.emu_start(0x10000000, 0x10000000 + len(code))
 
# 移除钩子（不再需要时）
mu.hook_del(hook_handle)
```

**常用钩子类型**：

- `UC_HOOK_CODE`：指令执行时触发，表示监控指令实行；

- `UC_HOOK_MEM_READ/WRITE`：内存读写时触发；

- `UC_HOOK_BLOCK`：基本块（Block）执行前触发（适合性能分析）；

- `UC_HOOK_INTR`：中断发生时触发（如 x86 的 INT 指令）。

## 实战案例：用unicorn破解迷宫式加密函数

前置背景介绍：

假设我们逆向得到一段 x86 汇编加密函数（机器码），功能是对输入的 4 字节数据进行加密，输出 4 字节密文，但**加密逻辑通过复杂的条件跳转（类似 "迷宫"）隐藏**。我们可以用 Unicorn 模拟执行，通过遍历输入快速找到密钥。

### 目标函数分析

机密函数机器码（简化）：

```Assembly language
; 输入：EAX = 明文（4字节）
; 输出：EAX = 密文（4字节）
; 逻辑：通过多次条件跳转修改EAX，最终结果与密钥相关
0x10000000: 83 c0 01        add eax, 1         ; EAX += 1
0x10000003: 83 f8 05        cmp eax, 5         ; 比较EAX与5
0x10000006: 7e 03           jle 0x1000000b     ; 若EAX <=5，跳至0x1000000b
0x10000008: 83 c0 02        add eax, 2         ; 否则EAX +=2
0x1000000b: 83 c0 03        add eax, 3         ; EAX +=3
0x1000000e: c3              ret                ; 返回
```

已知当明文为`0x12345678`时，密文为`0x1234567f`，我们需要通过模拟找到加密逻辑的数学表达式。

### 用unicorn模拟执行并逆向加密逻辑

```Python
from unicorn import Uc, UC_ARCH_X86, UC_MODE_32, UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_EAX, UC_X86_REG_ESP
 
# 加密函数机器码
CODE = b"\x83\xc0\x01\x83\xf8\x05\x7e\x03\x83\xc0\x02\x83\xc0\x03\xc3"
CODE_ADDR = 0x10000000  # 代码加载地址
STACK_ADDR = 0x20000000  # 栈地址
 
def test_encrypt(plaintext):
    try:
       ** # 初始化x86 32位模拟器**
**        mu = Uc(UC_ARCH_X86, UC_MODE_32)**
        
        # 分配代码段和栈段内存
        mu.mem_map(CODE_ADDR, 0x1000, 0x7)  # 可读可写可执行
        mu.mem_map(STACK_ADDR, 0x1000, 0x3)  # 可读可写
        
        # 写入代码
**        mu.mem_write(CODE_ADDR, CODE)**
        
        # 设置寄存器：EAX=明文，ESP=栈地址
**        mu.reg_write(UC_X86_REG_EAX, plaintext)**
**        mu.reg_write(UC_X86_REG_ESP, STACK_ADDR + 0x800)**  # 栈指针指向栈中部
        
        # 执行加密函数（从CODE_ADDR开始，到ret指令结束）
        mu.emu_start(CODE_ADDR, CODE_ADDR + len(CODE))
        
        # 返回加密后的EAX值（密文）
        return mu.reg_read(UC_X86_REG_EAX)
    except Exception as e:
        print(f"模拟出错：{e}")
        return None
 
# 测试多个明文，观察密文规律
test_inputs = [0x0, 0x5, 0x6, 0x12345678]
for plain in test_inputs:
**    cipher = test_encrypt(plain)**
**    print(f"明文=0x{plain:x} → 密文=0x{cipher:x}")**
```

### 执行结果与目标推导

```Python
明文=0x0 → 密文=0x4    # 0+1=1 ≤5 → 1+3=4
明文=0x5 → 密文=0x9    #5+1=6 >5 →6+2=8 →8+3=11（0xb？此处需重新计算，实际应为5+1=6>5→6+2=8+3=11=0xb，示例仅为演示）
明文=0x6 → 密文=0xc    #6+1=7>5→7+2=9+3=12=0xc
明文=0x12345678 → 密文=0x1234567f  # 符合已知结果
```

通过模拟不同输入，可推导出加密逻辑：

`if (plaintext + 1) ≤5 → cipher = plaintext + 1 + 3 = plaintext +4else → cipher = plaintext +1 +2 +3 = plaintext +6`

## unicorn的进阶用法

### 对抗反调试

模拟执行反调试代码

许多恶意软件会通过`IsDebuggerPresent`、检查`TracerPid`等手段检测调试环境，**用 Unicorn 可直接修改内存 / 寄存器绕过：**

示例：**Hook Windows API IsDebuggerPresent，使其返回0（无调试器）**

```Python
# 示例：Hook Windows API IsDebuggerPresent，使其返回0（无调试器）
from unicorn.x86_const import UC_X86_REG_EAX
 
def hook_is_debugger_present(uc, address, size, user_data):
    # IsDebuggerPresent的返回值存于EAX，0表示无调试器
    uc.reg_write(UC_X86_REG_EAX, 0)
    # 修改指令指针EIP，跳过原始API调用（假设API地址为0x77123456，长度5字节）
    uc.reg_write(UC_X86_REG_EIP, 0x77123456 + 5)
 
# 注册钩子，在调用IsDebuggerPresent时触发
mu.hook_add(UC_HOOK_CODE, hook_is_debugger_present, begin=0x77123456, end=0x77123456)
```

#### 小tip

```Python
# 修改指令指针EIP，跳过原始API调用（假设API地址为0x77123456，长度5字节）
uc.reg_write(UC_X86_REG_EIP, 0x77123456 + 5)
```

- 因为 `UC_HOOK_CODE` 是在指令执行前触发的。如果不修改 EIP，Unicorn 接下来依然会执行 `0x77123456` 处的真实 API 指令，我们的 EAX 修改就会被覆盖。

- 这行代码把 EIP（指令指针）直接指向了 API 后面的 `5` 字节处，相当于直接“跳过”了这个 API 的执行，直接“返回”。

```Python
mu.hook_add(UC_HOOK_CODE, hook_is_debugger_present, begin=0x77123456, end=0x77123456)
```

- 告诉 Unicorn：当执行到 `0x77123456` 这个地址的指令时，不要急着执行，先调用 `hook_is_debugger_present` 函数。

### 模拟ARM固件

模拟ARM固件，分析物联网设备漏洞

以MIPS架构路由器固件为例，**用unicorn模拟执行存在命令漏洞注入的函数**

```Python
from unicorn import Uc, UC_ARCH_MIPS, UC_MODE_MIPS32, UC_MODE_BIG_ENDIAN
from unicorn.mips_const import UC_MIPS_REG_A0  # A0寄存器用于传递第一个参数
 
# 路由器固件中存在漏洞的函数（简化）：将A0指向的字符串作为系统命令执行
VULN_FUNC_ADDR = 0x8048500
COMMAND_ADDR = 0x100000  # 命令字符串地址
 
def emulate_mips_vuln():
    mu = Uc(UC_ARCH_MIPS, UC_MODE_MIPS32 + UC_MODE_BIG_ENDIAN)
    mu.mem_map(0x8048000, 0x1000, 0x7)  # 加载漏洞函数
    mu.mem_map(COMMAND_ADDR, 0x100, 0x3)  # 加载命令字符串
    
    # 写入测试命令（含注入 payload：";reboot;"）
    command = b"ping 127.0.0.1;reboot;"
    mu.mem_write(COMMAND_ADDR, command + b"\x00")  # 字符串以0结尾
    
    # 设置参数：A0 = 命令字符串地址
    mu.reg_write(UC_MIPS_REG_A0, COMMAND_ADDR)
    
    # 执行漏洞函数，观察是否执行注入的reboot命令（需结合内存Hook监控系统调用）
    mu.emu_start(VULN_FUNC_ADDR, VULN_FUNC_ADDR + 0x50)  # 执行函数
 
emulate_mips_vuln()  #调用执行上述函数
```

### 性能优化

提升模拟速度的技巧：

- **减少钩子粒度**：**避免对每一条指令都设置钩子，优先用**`UC_HOOK_BLOCK`**监控基本块；**

- **内存预分配**：一次性分配大内存块，避免频繁调用`mem_map()`；

- **使用 C 语言绑定**：对性能敏感的场景（如模拟大型固件），用 C 语言编写代码，比 Python 快 10\-100 倍。

## 常见问题

![](/images/Unicorn/QQ_1791360647771.png)



总结：

Unicorn 引擎的核心价值，在于它**将复杂的 CPU 指令集模拟抽象为简洁的 API，让逆向工程师无需深入硬件细节即可专注于代码逻辑分析**。无论是破解加密算法、挖掘固件漏洞，还是分析恶意代码行为，Unicorn 都能提供 "安全、可控、高效" 的模拟环境。

随着物联网设备的普及与恶意代码的复杂化，Unicorn 这类轻量级模拟器的重要性将愈发凸显。掌握它，不仅能提升逆向效率，更能让我们在二进制分析的深度与广度上实现突破。



## 题目

不是复现题目 就是学习一下网上使用unicorn的场景以及他们利用unicorn的代码

### 羊城杯oddcode

题解wp：https://mp\.weixin\.qq\.com/s/bueXj9C0pUhvJMyFlDwFJQ

（题外话，这就是老一辈逆向者吗，直接爆肝到五点，我感觉我没AI就死了 我咋这么依赖AI烦死了



这道题目是因为碰到核心解密函数有大量的花指令混淆 然后利用unicorn来trace追踪函数的跳转路径

#### Exp

学习一下这个exp

```Python
from unicorn import *
from unicorn.x86_const import *

ADDRESS = 0x2E1000       # 程序加载的地址
INPUT_ADDRESS = 0x2E701D # 输入的地址
KEY_ADDRESS = 0x2E705C   # 16字节key的地址

with open('OddCode.exe', 'rb') as file:
    file.seek(0x400)
    X64_CODE = file.read(0x4269)  # 读取代码

class Unidbg:

    def __init__(self, flag):
        mu = Uc(UC_ARCH_X86, UC_MODE_64)
        # 基址为0x2E1000，分配16MB内存
        mu.mem_map(ADDRESS, 0x1000000)
        mu.mem_write(ADDRESS, X64_CODE)
        mu.mem_write(INPUT_ADDRESS, flag)        # 随便写入一个flag
        mu.mem_write(KEY_ADDRESS, b'\x90\xF0\x70\x7C\x52\x05\x91\x90\xAA\xDA\x8F\xFA\x7B\xBC\x79\x4D')
        
        # 初始化寄存器，寄存器的状态就是切换到64位模式之前的状态，可以通过动调得到
        mu.reg_write(UC_X86_REG_RAX, 1)
        mu.reg_write(UC_X86_REG_RBX, 0x51902D)
        mu.reg_write(UC_X86_REG_RCX, 0xD86649D8)
        mu.reg_write(UC_X86_REG_RDX, 0x2E701C)
        mu.reg_write(UC_X86_REG_RSI, INPUT_ADDRESS)  # input参数
        mu.reg_write(UC_X86_REG_RDI, KEY_ADDRESS)    # key参数
        mu.reg_write(UC_X86_REG_RBP, 0x6FFBBC)
        mu.reg_write(UC_X86_REG_RSP, 0x6FFBAC)
        mu.reg_write(UC_X86_REG_RIP, 0x2E1010)
        
        mu.hook_add(UC_HOOK_CODE, self.trace)        # hook代码执行，保存代码块执行轨迹
        self.mu = mu
        self.except_addr = 0
        self.traces = []        # 用来保存代码块执行轨迹

    def trace(self, mu, address, size, data):
        if address != self.except_addr:
            self.traces.append(address)
        self.except_addr = address + size

    def start(self):
        try:
            self.mu.emu_start(0x2E1010, -1)
        except:
            pass
        print([hex(addr) for addr in self.traces])

Unidbg(b'SangFor{00000000000000000000000000000000}').start()
```

> *Unicorn 申请的内存是没有操作系统的，必须要手动 mem\_write 把参数写进去，模拟真实运行时的内存数据。*
> 
> 

##### 上下文恢复

```Python
mu.reg_write(UC_X86_REG_RAX, 1) # 初始化通用寄存器
        ...
mu.reg_write(UC_X86_REG_RSI, INPUT_ADDRESS)  # input参数地址
mu.reg_write(UC_X86_REG_RDI, KEY_ADDRESS)    # key参数地址
mu.reg_write(UC_X86_REG_RBP, 0x6FFBBC)       # 栈底指针
mu.reg_write(UC_X86_REG_RSP, 0x6FFBAC)       # 栈顶指针
mu.reg_write(UC_X86_REG_RIP, 0x2E1010)       # 指令指针，程序从0x2E1010开始执行
```

*反汇编里第一句往往不是完整的程序。真实程序运行时，操作系统会初始化 **`RSP`** 指向栈顶，**`RIP`** 指向入口点。这里就是**模拟了程序加载完成那一刻的“现场”**。由于汇编里 **`RSI`** 和 **`RDI`** 往往用作函数传参（System V AMD64调用约定），这里把 flag 和 key 的内存地址直接喂给它们。*

##### hook指令对抗花指令

```Python
mu.hook_add(UC_HOOK_CODE, self.trace) # 挂钩每一条指令的执行
self.traces = [] # 用于保存真实执行轨迹

def trace(self, mu, address, size, data):
    if address != self.except_addr:
        self.traces.append(address)
    self.except_addr = address + size
```

不过unicorn虽然可以hook代码块执行，但是也是会被花指令干扰

因此我们利用一点手段：

- 正常情况下，顺序执行时，下一条指令的地址 `address` 一定等于 `上一条指令地址 + 上一条指令长度 (self.except_addr)`。

- 如果发生了跳转（或者编译器插入了花指令导致执行流跳变），下一条指令的 `address` 就会不等于 `self.except_addr`。

- 只有发生跳转时，`if address != self.except_addr:` 成立，才会记录这个跳转目标。

- 这个逻辑不仅能过滤掉永不被执行的花指令（花指令经常是跳转指令，但跳转的地址如果被逻辑绕过，就不会被记录），还能精准提取出真实代码块（Basic Block）的执行顺序。

最后会打印出对应的轨迹

##### 锁定核心代码块

But

这么多代码块一个个去手动分析不太现实，于是再加一个hook来hook输入和key的访问操作，来帮助我们**找到访问了输入和key的指令所在的代码块**，加上：

```Python
mu.hook_add(UC_HOOK_MEM_READ, self.hook_mem_read)

def hook_mem_read(self, mu, access, address, size, value, data):
    if address >= INPUT_ADDRESS and address <= INPUT_ADDRESS + 41:
        print(f'Read input[{address - INPUT_ADDRESS}] at {hex(mu.reg_read(UC_X86_REG_RIP))}')
    if address >= KEY_ADDRESS and address <= KEY_ADDRESS + 16:
        print(f'Read key[{address - KEY_ADDRESS}] at {hex(mu.reg_read(UC_X86_REG_RIP))}')
```

这是给 Unicorn 模拟器增加了一个 内存读取 Hook（UC\_HOOK\_MEM\_READ），专门用来监控程序什么时候读取了我们的**输入（flag）和密钥（key）**。

然后就能输出几个比较关键的代码块 然后我们通过这个代码块锁定核心加密函数 接下来作者继续用unicorn进行追踪函数 最后找到核心加密函数 爆破出了flag



#### 32位与64位模式的动态切换

这道题还涉及到一些微小的知识点 比如32位64位模式转换之类的 顺便学习一下好了



模式转换，也叫天堂之门（跨模式执行），在 Windows x86 环境中，32位进程默认 `CS = 0x23`，64位进程默认 `CS = 0x33`。从 32位切换到 64位，通常靠远跳转（Far Jump / Far Call / Far Ret）来实现。

> 反汇编器（如 IDA、Ghidra）默认按 PE 头里的信息解析。如果你的 PE 是 32位的，但中间通过天堂之门切到了64位，反汇编器就会“懵逼”，把64位指令强行解释成32位指令，导致乱码。
> 
> 



在这道题目中体现为：

1. 核心原理：在 Windows 中，程序可以通过**修改代码段寄存器（**`CS`**）来切换 CPU 的执行模式。当 **`CS`** 为 **`0x23`** 时，CPU 按 32位模式 解析指令；当 **`CS`** 为 **`0x33`** 时，CPU 按 64位模式 解析指令。**

2. 执行过程：`OddCode.exe` 在执行过程中，通过一个“**远跳转**”（Far Jump，通常是 `retf` 或 `jmp far`），**将 **`CS`** 切换为 **`0x33`**，然后跳到了 **`0x2E5310`** 这个地址**。

3. 意义：从 `0x2E5310` 开始，后面的所有机器码都必须按照 64位 模式来反汇编和解析，否则就会全部解析错乱。这是一种非常经典的**反调试**/防破解手段，会让很多静态反汇编工具（如 IDA 的默认分析）出现严重错位。

##### 常见形式

1. 利用`retf`远返回

```Assembly language
push 0x33                ; 压入64位的CS选择子
call $+5                 ; 压入当前指令的下一条地址，然后跳到下一条指令
add dword ptr [esp], 5   ; 修改刚刚压入的返回地址（让它指向真正的64位目标代码）
retf                     ; 远返回！此时 CPU 从栈中弹出 EIP 和 CS(0x33)，正式进入64位模式
; --- 从这里开始是 64 位代码 ---
mov rax, rbx             ; 64位指令
```

在32位模式下，无法直接 `push` 一个64位地址然后直接 `retf`，所以**通过 **`call`** 压入当前地址**，再在栈上加上偏移量，凑出真正的 64位目标地址。

2. 利用`reft`压入目标地址

```Assembly language
push 0x33                ; 64位CS
push 0x2E5310            ; 真正的64位目标地址（你图片里提到的地址）
retf                     ; 弹出CS和RIP，切换到64位并跳转
; --- 下面全是64位代码 ---
```

3. 使用远指针（少见，易被工具识别）

```Assembly language
jmp far ptr 0x33:0x2E5310
```

##### 控制机器码转化模式

- 在 IDA Pro 中：

    1. 定位到切换的地方（比如 `retf`）。

    2. 跳转到目标地址（如 `0x2E5310`）。

    3. 此时 IDA 可能把它解析成了垃圾指令。你需要选中目标地址，**按下 **`U`** 键**（取消定义），然后按 `Alt+G` 打开“Change Segment Register”（修改段寄存器）对话框。

    4. **将 **`CS`** 的值改为 **`0x33`**，然后按下 **`C`** 键（Make Code）**。如果不行，可以在目标地址右键，创建新段（Create Segment），并将段设为 64位。

    5. 终极方案：安装 IDA 插件（如 `Heaven's Gate` 或 `idapython` 脚本），一键将指定区域转换为64位解析。
