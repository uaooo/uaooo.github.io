+++
title = 'Frida-hook'
date = '2026-09-03T12:00:00+08:00'
draft = false
summary = ''
tags = []
showtoc = true
+++

前言：

组长说hdctf有这个考点 猛然想起面试的时候说这个很重要 遂学

## frida介绍

Frida 是一个强大的动态二进制插桩（dynamic instrumentation）工具，主要用于逆向工程、安全研究、App 调试和分析等领域。

它允许你在运行时对本地应用程序（包括 Android、iOS、Windows、macOS、Linux 的原生和托管程序）**进行动态修改或观察**，无需修改原始二进制。

> Frida\-Hook 就是：在不修改APK源码、不重新打包安装的情况下，把你自己写的JS代码“注入”到正在运行的应用进程里，然后“偷换”掉某个函数的入口或出口，让你能看参数、改返回值、甚至完全替换函数逻辑。
> 
> 

其主要功能如下：

- 动态 Hook：可以在运行时 hook 任何函数（Java, native C/C\+\+, Obj\-C）

- 跨平台支持\*：支持 Android、iOS、Windows、Linux、macOS 等平台

- 无须 Root/Jailbreak（可选）：有些场景下 Frida 可以在无 root 环境下工作（需绕过限制）

- 脚本化 ：支持 JavaScript 和 Python 编写 hook 脚本

- 远程调试 ：可连接远程设备并注入目标程序进行分析

运行原理：

```Plain Text
+--------------+         +------------------+
| 你写的脚本(JS/Py) |<=====>|  Frida Server (on target) |
+--------------+         +------------------+
        |                        |
        |------ Hook ----------->|
        |<---- Data / Log -------|

```

## frida安装

https://www\.kucoding\.com/article/351\.html\#2

这篇文章里面介绍的很详细



之前浅浅学了一丢丢的安卓逆向 所以frida和adb安装了

![QQ\_1788967968327\.png](/images/frida-hook/QQ_1788967968327.png)

安装一个逍遥模拟器

![65e4f365c1a5a00866986eb1825dd429\.png](/images/frida-hook/65e4f365c1a5a00866986eb1825dd429.png)

![QQ\_1789032963689\.png](/images/frida-hook/QQ_1789032963689.png)

到此即环境搭建完成

## frida开发环境搭建

使用frida工具进行开发工作时，最简洁易用的便是js，所以这里介绍一下如何搭建它的开发环境。

没有代码提示写js是一件很痛苦的事情，因此最终实现的效果就是：

1. 有代码提示信息

2. 可以分模块开发



编辑器使用的vscode，除此之外还需要**`node`**环境：

Node\.js 是让 JavaScript 代码可以在浏览器之外（比如你的电脑、服务器上）运行的“独立引擎”。

它主要有三大作用：

1. 给 JS 代码提示（你截图里的核心目的）
在 Node 出现之前，JavaScript 只能写在网页里。有了 Node，VS Code 就能借助它来“读懂”你写的代码，**给我们提供 ****`Java.perform`****、****`Interceptor.attach`**** 这些方法的自动补全。**

2. 充当“包管理器”（npm）
Node 附带了一个极其强大的工具叫 `npm`（Node Package Manager）。刚才看到的 Frida 官方教程，让我们装 `@types/frida-gum`，就是靠 npm 一键下载别人写好的类型提示。

安装frida代码提示的包：

```Plain Text
**npm i @types/frida-gum**
```

![QQ\_1789033648837\.png](/images/frida-hook/QQ_1789033648837.png)

js代码本身是没有类型提示的，很多时候看不到函数参数用起来很麻烦，所以我们还可以安装一下**`TypeScript`**，它的使用与**`JavaScript`**基本一样，但它有类型提示，用起来更加舒服。

```Plain Text
**npm i ts-loader typescript -D**
```

后面的**`-D`**意思是只在开发环境下使用它。

![QQ\_1789033974546\.png](/images/frida-hook/QQ_1789033974546.png)

因为其工作原理是将**TypeScript**代码重新编译成为**JavaScript**代码，我们最终运行的依旧只能是js代码，所以最后的结果是不需要这两个包的。
每次自己手动编译也很麻烦，所以还需要一个**webpack**工具，它可以将这一个过程自动化。
不仅如此，它更强大的作用其实是可以让我们分模块开发不同功能的代码，然后最后将其打包成为一个js文件。

```Plain Text
**npm i webpack webpack-cli -D**
```

![QQ\_1789034362455\.png](/images/frida-hook/QQ_1789034362455.png)

安装完成后，输入**`code .`**，用vscode打开这个文件夹，新建一个文件**`webpack.config.js`**，这是打包工具**`webpack`**的配置文件，我们需要用它来配置一些选项。

具体选项和选项作用：https://www\.webpackjs\.com/

然后TypeScript也需要一个配置文件，名字为**`tsconfig.json`**：https://www\.typescriptlang\.org/

进入这个包管理文件，写一个脚本命令，让webpack能够实时监视我们的目录变化，自动编译：

```JavaScript
"scripts": {
    "watch": "webpack --config webpack.config.js"
  },
```

最后 我们的环境终于搭建好啦！！！！

![QQ\_1789034847998\.png](/images/frida-hook/QQ_1789034847998.png)

总结：

“手机端”到底指什么？

在安卓逆向里，“手机端”指的就是运行目标APP的那个安卓系统。
你用逍遥模拟器，模拟器就是你的“手机”。所以，你在电脑上敲的 `adb push`、`chmod` 等命令，其实是隔着电脑屏幕，在给这个“虚拟手机”装软件。

刚才到底在“手机端”装了什么？

你装的是 `frida-server`。它不是应用商店里的普通APP（不是 \.apk 文件），它是一个命令行程序（二进制文件）。
它的作用是潜伏在安卓系统的底层，随时等待你电脑发来的指令。

在真实手机上做逆向，流程是一模一样的：也是下个 `frida-server`，用数据线（adb）传进手机，然后用Root权限运行它。只不过真机需要解BL锁、刷Magisk，极其痛苦；而逍遥模拟器自带Root，直接把最麻烦的一步省了。

## Java层hook

### 静态分析找目标

找到要hook的类和方法

```TypeScript
package com.example.crypto;
public class MainActivity {
    private String encrypt(String data) { ... }
}
```

类名：com\.example\.crypto\.Mainactivity

方法：encrypt\(String\)

### 编写Frida js脚本（hook\_java\.js）

```JavaScript
Java.perform(function () {
    console.log("[*] 开始 Hook Java 方法");
 
    // 1. 获取目标类
    var MainActivity = Java.use("com.example.crypto.MainActivity");
 
    // 2. Hook 方法（参数类型要匹配）
    MainActivity.encrypt.implementation = function (data) {
        console.log("[+] 原方法被调用，参数：" + data);
 
        // 调用原方法
        var result = this.encrypt(data);
 
        console.log("[+] 原方法返回值：" + result);
 
        // 可篡改返回值
        // return "fake_data";
        return result;
    };
});
 
```

#### 分析

##### 最关键的一步：`.implementation = function`

```C
MainActivity.encrypt.implementation = function (data) {
```

- 原本 APP 运行到 `encrypt` 函数时，会跑它自己原有的代码。但是现在，你强行把你的 JS 函数塞了进去。

- 以后 APP 每次调用 `encrypt`，都会先跑到你这段代码里来。

- `data` 就是原本 APP 传进来的参数（比如用户输入的密码）。

##### 偷看机密：`console.log(...)`

```JavaScript
console.log("[+] 原方法被调用，参数: " + data);
var result = this.encrypt(data); // 调用原方法
console.log("[+] 原方法返回值: " + result);
```

- 意思：既然我们已经劫持了这个函数，那我们当然要偷偷看看传进来的 `data` 是什么，以及原本的函数计算出来的 `result` 是什么。

- 重点：`var result = this.encrypt(data);` 这一句非常重要！因为你虽然劫持了它，但你不知道它原本的逻辑是什么。这行代码就是“让原本的函数继续跑一遍”，拿到它真实的返回值。

##### 狸猫换太子（最终目的）：`return`

```C
// 可篡改返回值
        // return "fake_data";
        return result;
    };
});
```

- 代码里写了 `return result;`，意思是“我看完之后，原封不动把真实的返回值交还给它”。

- 但是如果把上面的注释取消掉，写成 `return "fake_data";`。那么不管 APP 原本算出来什么，不管你输入什么密码，这个函数永远都会返回 `"fake_data"`！

- 这招通常用来绕过注册码校验、修改金额、或者绕开加密。

### 运行脚本

将frida\-server端口转发到本地

```C
# frida-server 默认端口为 27042
adb forward tcp:27042 tcp:27042
```

然后用脚本去frida app

### Eg

jadx反编译APK，定位目标类/方法：

![image\.png](/images/frida-hook/image%202.png)

选中相应的函数复制为frida片段

![image\.png](/images/frida-hook/image.png)

构造hook代码

![image\.png](/images/frida-hook/image%201.png)

frida注入脚本，观察日志/篡改返回值

```C
frida -U -f com.example.crypto -l hook_java.js
```

有时候，\-f（spawn 模式）会在 App 刚启动时注入，容易触发崩溃，改用附加模式：

- 先在模拟器里手动打开 App，让它运行起来

- 用 frida\-ps \-U 查看进程 PID

- 用附加模式注入脚本：

```C
frida -U -p <pid> -l hook.js
```

## Native层hook（so库）

场景：app用so库做加密/校验，需要hook JNI 函数或者导出函数

> JNI函数 Hook是指在**Java层通过修改JNI函数的指针，来拦截或修改JNI函数的执行流程**。 简单来说，就是通过修改JNI函数的地址，使其跳转到我们自己编写的函数中，从而达到拦截或修改函数执行的目的。 在Android系统中，Java层通过JNI调用本地C/C\+\+代码时，实际上是通过JNI接口来找到对应的本地函数并执行。
> 
> 

### 脚本模板

```JavaScript
setImmediate(function () {
    Java.perform(function () {
        console.log("[*] 等待 libxxx.so 加载...");
        // 监听 so 加载
        var System = Java.use("java.lang.System");
        System.loadLibrary.implementation = function (libname) {
            this.loadLibrary(libname);
            if (libname === "xxx") { // libxxx.so
                console.log("[+] libxxx.so 已加载，开始 Hook");
                hookNativeFunc();
            }
        };
    });
});
 
function hookNativeFunc() {
    // 1. 找导出函数地址
    var funcPtr = Module.findExportByName("libxxx.so", "Java_com_example_crypto_MainActivity_nativeEncrypt");
    if (!funcPtr) {
        console.log("[-] 未找到函数");
        return;
    }
    console.log("[*] 函数地址：" + funcPtr);
 
    // 2. Hook
    Interceptor.attach(funcPtr, {
        onEnter: function (args) {
            console.log("[+] Native 方法进入");
            // args[0] = JNIEnv*, args[1] = jobject, args[2] = 参数1
            // 读取字符串参数
            var data = Java.vm.getEnv().getStringUtfChars(args[2], null);
            console.log("[+] 参数：" + data.readCString());
        },
        onLeave: function (retval) {
            console.log("[+] Native 返回值：" + retval);
            // 篡改返回值
            // retval.replace(0);
        }
    });
}
```

#### 第一步

```JavaScript
setImmediate(function () {
    Java.perform(function () {
        var System = Java.use("java.lang.System");
        System.loadLibrary.implementation = function (libname) {
            this.loadLibrary(libname); // 先让系统正常加载
            if (libname === "xxx") {   // 如果加载的是 libxxx.so
                console.log("[+] libxxx.so 已加载，开始 Hook");
                hookNativeFunc();      // 立刻触发Hook
            }
        };
    });
});
```

- 操作：Hook了Java层的 `System.loadLibrary`。每次APP加载 `.so` 时，都会被你的脚本拦截下来看一眼。

- 关键：必须写 `this.loadLibrary(libname);`。这是放行，让APP把原本该做的加载操作做完。一旦加载完成，`.so` 就存在于内存里了，这时候再去Hook就不会失败。

- 注意：`libname === "xxx"` 里面的字符串可能是 `"xxx"`，也可能是 `"libxxx.so"`，具体看APP里 `System.loadLibrary("xxx")` 传的是什么。

#### 第二步：定位与拦截

```C
var funcPtr = Module.findExportByName("libxxx.so", "Java_com_example_crypto_MainActivity_nativeEncrypt");
if (!funcPtr) { console.log("[-] 未找到函数"); return; }
```

- 找地址：`.so` 里的函数在编译成机器码后，名字会被保留。Java层调用的Native方法，通常命名规则是 `Java_包名_类名_方法名`。`Module.findExportByName` 就是去 `.so` 的导出表里查这个函数在内存中的绝对地址。

- 坑点1：如果APP做了混淆，这个函数名可能不是标准格式，或者被 `RegisterNatives` 动态注册了。如果是动态注册，`findExportByName` 就会返回 `null`，你需要用其他方式找地址（比如遍历内存特征码）。

- 坑点2：如果你知道函数名，可以用 `Module.enumerateExports` 把 `.so` 里所有导出的函数全打印出来找。

#### 第三步：进入函数

```JavaScript
onEnter: function (args) {
    console.log("[+] Native 方法进入");
    // args[0] = JNIEnv*, args[1] = jobject, args[2] = 参数1
    var data = Java.vm.getEnv().getStringUtfChars(args[2], null);
    console.log("[+] 参数：" + data.readCString());
},
```

- args 是什么？ Native函数的参数和C语言一样，是一连串的指针。

    - `args[0]`：`JNIEnv*` 指针，JNI环境，非常重要。

    - `args[1]`：`jobject` 或 `jclass`，代表Java层调用这个Native方法的对象本身。

    - `args[2]`：**真正的第一个业务参数**（比如你输入的密码字符串，在C层是个 `jstring` 指针）。

- `Java.vm.getEnv().getStringUtfChars(...)`：这是极其经典的**JNI转换操作**。因为 `args[2]` 只是一个指针（代表Java字符串），C语言不认识。你需要通过JNI环境（`JNIEnv*`）调用它的方法，把它“翻译”成C语言能看懂的 `char*` 字符串。

#### 第四步：离开函数与篡改

```C
onLeave: function (retval) {
    console.log("[+] Native 返回值：" + retval);
    // retval.replace(0);
}
```

- retval：这是Native函数执行完返回的值。它也是一个指针（代表返回类型）。

- 坑点：如果Native函数返回的是 `jstring`（Java字符串），直接 `console.log(retval)` 打印出来是内存地址（如 `0x7fa2...`），根本不是字符串。如果你想看返回值字符串，需要再写一次 `Java.vm.getEnv().getStringUtfChars(retval, null).readCString()`。

- `retval.replace(0)`（注释掉的那行）：这是篡改返回值。

    - 如果返回类型是 `jboolean`，你可以 `retval.replace(1)` 强制让它返回真。

    - 如果返回类型是 `jint`，你可以 `retval.replace(0)` 强制返回0。

## 常用hook模板

### 打印方法调用栈

```JavaScript
Java.perform(function () {
    var stackTrace = Java.use("android.util.Log").getStackTraceString;
    Java.use("java.lang.Throwable").$init.implementation = function () {
        this.$init();
        console.log("[+] 调用栈：\n" + stackTrace(this));
    };
});
 
```

- `android.util.Log.getStackTraceString(throwable)` 是安卓系统自带的工具方法。它接收一个 `Throwable` 对象，返回一个包含当前调用堆栈的字符串（也就是“谁调用了谁”的清单）。

- 核心机制：`java.lang.Throwable` 是Java里所有错误和异常的祖宗。每当APP里 `new Throwable()` 或者 `new Exception()` 时，都会触发它的构造函数 `$init`。

- 你在构造函数里插了一脚：只要有人 new 了个异常，你就立刻拿到这个异常对象（`this`），丢给上面的“翻译官” `stackTrace()`，把当前整个方法调用链打印出来。

### hook构造方法

在 Java 里，构造函数（Constructor）是在 `new` 一个对象时最先执行的方法，用来初始化数据。

```JavaScript
Java.perform(function () {
    var Clazz = Java.use("com.example.crypto.CoinMoney");
    Clazz.$init.overload("java.lang.String", "int").implementation = function (a, b) {
        console.log("[+] 构造方法参数：" + a + ", " + b);
        return this.$init(a, b);
    };
});
```

这里有两个极其关键的知识点：

1. `$init`：Frida 里专门用来表示构造函数的固定写法（因为在底层Java字节码里，构造函数的名字就叫 `<init>`）。

2. `.overload("java.lang.String", "int")`：这是极其重要的细节！因为一个类可能有多个构造函数（比如一个空的，一个传字符串的，一个传字符串加数字的）。`.overload` 就是告诉 Frida：“我要精确劫持参数类型是 `String` 和 `int` 的那一个构造函数。” 如果不写 `overload`，脚本大概率报错。

3. `function (a, b)`：接收构造时传进来的参数。`a` 就是那个字符串，`b` 就是那个整数。

### 枚举所有类/方法

```JavaScript
Java.perform(function () {
    var classFactory = Java.classFactory;
    var classes = classFactory.enumerateClasses();
    for (var i = 0; i < classes.length; i++) {
        console.log(classes[i].getName());
    }
});
```

## 靶场题目

看的文章是：https://bbs\.kanxue\.com/thread\-289346\.htm
