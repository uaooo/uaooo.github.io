+++
title = 'Android'
date = '2026-08-28T12:00:00+08:00'
draft = false
summary = ''
tags = []
showtoc = true
+++

## 下载工具

### JDK

JDK是Java的环境。很多工具（包括 Ghidra、Apktool）都依赖 Java，必须最先装。

![QQ\_1787641682128\.png](/images/android-reverse/QQ_1787641682128.png)

![QQ\_1787641761298\.png](/images/android-reverse/QQ_1787641761298.png)

### apktool

![QQ\_1787664092595\.png](/images/android-reverse/QQ_1787664092595.png)

![ed68030782a29cb974a3f1566a57bec2\.png](/images/android-reverse/ed68030782a29cb974a3f1566a57bec2.png)

- 它是干嘛的：**它能把 APK 拆成 Smali 汇编代码（比 Java 更底层）和图片、布局文件；修改后还能重新打包成 APK（比如去广告、破解内购常用）。**

- 怎么用它（命令）：

    - **解包：****`apktool d your_app.apk`****（会生成一个文件夹）**

    - **回编译：****`apktool b 文件夹名 -o new_app.apk`**

- 什么情况用：当你需要**修改 AndroidManifest\.xml、去除签名校验，或者想修改 Smali 逻辑**（比如把 `if-eqz` 改成 `if-nez` 强制绕过验证），且改完后要重新安装时。

### adb\-\-Android Debug Bridge

![e38949cad93b71f0059cffefb5c64e10\.png](/images/android-reverse/e38949cad93b71f0059cffefb5c64e10.png)

- 它是干嘛的：**让你的电脑和手机/模拟器通信的工具。装应用、看日志（Logcat）、传文件、执行 Shell 命令全靠它。**

- 怎么用它（命令）：

    - 连接设备：`adb devices`（看到设备号即成功）

    - 安装 APK：`adb install -r app.apk`

    - 查看实时日志：`adb logcat`

    - 进入手机命令行：`adb shell`

- 什么情况用：每次连接真机或模拟器进行动态调试、看崩溃日志时必用。

### 7zip

其实原来已经有了bandi zip 但是还是也下一下吧

![22e3aa7991eb1c2b92f56e49c4a6fdca\.png](/images/android-reverse/22e3aa7991eb1c2b92f56e49c4a6fdca.png)

APK 本质就是个压缩包。用 7\-Zip 可以直接右键解压 APK，瞬间拿到里面的 `lib` 文件夹、`AndroidManifest.xml` 等资源，比改后缀为 `.zip` 再解压快得多。

### Frida

![QQ\_1787662781256\.png](/images/android-reverse/QQ_1787662781256.png)

![QQ\_1787662844505\.png](/images/android-reverse/QQ_1787662844505.png)

**Frida \(动态插桩/热补丁——大招\)**

- 它是干嘛的：在不重启 App 的情况下，**把你写的 JS 代码“注入”到 APP 进程中，直接偷看函数的输入输出、篡改返回值（比如把 ****`false`**** 改成 ****`true`****）、甚至主动调用 Native 函数。**

- 怎么用它：电脑端装好（`pip install frida-tools`），手机端也要装对应版本的 `frida-server` 并运行，然后用 `frida -U -f 包名 -l hook.js` 启动。

- 什么情况用：当静态分析看不懂、或者加密逻辑太复杂不想逆时，直接 Hook 入口，让它把解密后的 Flag 打印出来。

### Ghidra

![QQ\_1787652928105\.png](/images/android-reverse/QQ_1787652928105.png)

![QQ\_1787652931687\.png](/images/android-reverse/QQ_1787652931687.png)

- 它是干嘛的：把看不懂的 `0x01 0x02` 机器码，按 F5 **一键变成近乎 C 语言的伪代码**。

- 怎么用它：打开 `ghidraRun.bat` \-\> 新建项目 \-\> 拖入 `.so` 文件 \-\> 双击打开 \-\> 左侧找 `Exports` \-\> 双击 `Java_com_xxx` 函数 \-\> 按键盘 `F5` 看伪代码。

- 什么情况用：分析 Native 层（\.so 文件）逻辑时必用。

## Java基础语法

### 1\.1 第一个程序

```Java
public class Hello {
    public static void main(String[] args) {
        System.out.println("Hello, RE!");
    }
}
```

要点：

- `public class Hello` —— **类名必须和文件名一致**

- `public static void main(String[] args)` —— 程序入口

- `System.out.println` —— 打印到控制台

### 1\.2 变量与数据类型

Java 是强类型语言，每个变量必须声明类型。

```Java
public class DataType {
    public static void main(String[] args) {
        // 整型
        byte b = 127;                // 1 字节 -128 ~ 127
        short s = 32000;             // 2 字节
        int i = 2147483647;          // 4 字节（最常用）
        long l = 9223372036854775807L; // 8 字节（注意 L 后缀）
        
        // 浮点
        float f = 3.14f;             // 4 字节（注意 f 后缀）
        double d = 3.14;             // 8 字节（默认）
        
        // 字符与布尔
        char c = 'A';                // 2 字节，Unicode
        boolean flag = true;
        
       ** // 字符串（注意：String 是类，不是基本类型）**
        String str = "Hello";
        
        System.out.println("i = " + i);
    }
}
```

- `int` 占 4 字节，能表示的范围 \-2^31 \~ 2^31\-1

- `char` 在 Java 里是 2 字节（不是 1 字节！），可以存中文

- **`String`**** 不是基本类型，是类**

### 1\.3 运算符

```Java
public class Op {
    public static void main(String[] args) {
        int a = 10, b = 3;
        
        // 算术
        System.out.println(a + b);  // 13
        System.out.println(a - b);  // 7
        System.out.println(a * b);  // 30
        System.out.println(a / b);  // 3（整数除法！截断）
        System.out.println(a % b);  // 1（取模）
        
        // 比较
        System.out.println(a > b);  // true
        System.out.println(a == b); // false**（注意 == 比较的是值，对象比较要用 equals）**
        
        // 逻辑
        boolean x = true, y = false;
        System.out.println(x && y); // false
        System.out.println(x || y); // true
        System.out.println(!x);     // false
        
        // 位运算（re 高频）
        System.out.println(a & b);  // 2  (1010 & 0011 = 0010)
        System.out.println(a | b);  // 11 (1010 | 0011 = 1011)
        System.out.println(a ^ b);  // 9  (异或)
        System.out.println(~a);     // -11（按位取反）
        System.out.println(a << 1);// 20 (左移 1 位 = 乘 2)
        System.out.println(a >> 1);// 5  (右移 1 位 = 除 2)
    }
}
```

- 整数除法截断（不是四舍五入）

- **字符串比较用 ****`.equals()`**** 而不是 ****`==`**

## 面向对象

### 2\.1 类与对象

> 这一节是你看 jadx 伪代码的最关键基础。RE 反编译出来的 80% 都是类和对象，不懂这块就看不懂代码。
> 
> 

```Java
// 文件：Dog.java
public class Dog {
    // 字段（成员变量）
    String name;
    int age;
    
    // 构造方法
    public Dog(String name, int age) {
        this.name = name;  // this 指代当前对象
        this.age = age;
    }
    
    // 方法
    public void bark() {
        System.out.println(name + " 汪！");
    }
    
    public static void main(String[] args) {
        Dog d = new Dog("旺财", 3);  // new 一个对象
        d.bark();                     // 调用方法
        System.out.println(d.age);    // 访问字段
    }
}
```

### 2\.2 static（静态）

**`static`**** 修饰的成员属于类本身，不属于某个对象。**RE 里非常常见。

一共有3个级别：

1. **对象级别（实例级别）**

属于具体对象

每个对象一份，互不影响

关键字：无（默认）

**访问：对象名\.成员**

2. **类级别（静态级别）**

属于类本身

全类共享一份

关键字：static

**访问：类名\.成员**

3. **方法 / 局部级别（块级别）**

属于方法内部或代码块

方法调用时创建，结束后销毁

关键字：无（写在方法里）

**只能在方法内部访问**

```Java
public class Counter {
    **static int count = 0;  // 静态变量，所有对象共享**
    int id;                 // 实例变量，每个对象独立
    
    public Counter() {
        count++;
        id = count;
    }
    
    public static void showCount() {  // 静态方法
        System.out.println("Total: " + count);
    }
    
    public static void main(String[] args) {
        Counter c1 = new Counter();
        Counter c2 = new Counter();
        Counter c3 = new Counter();
        
        System.out.println(c1.id);   // 1
        System.out.println(c2.id);   // 2
        System.out.println(c3.id);   // 3
        System.out.println(Counter.count); // 3（共享）
        
        Counter.showCount();  // 直接通过类名调用
    }
}
```

- `static` 方法反编译后调用形式是 `ClassName.method()`，不依赖对象

- 看到 `static final` 常常是常量定义，比如 `static final String KEY = "abc123";`

### 2\.3 final

**final 表示"不可修改"。**

```Java
java public class FinalDemo { final int x = 10; // 常量，构造后不能再改
```

```Java
final void method() {    // 方法不能被重写
    System.out.println("final method");
}
```

```Java
// final 参数：方法内不能修改
void print(final int n) {    
    // n = 5;  // 错误！不能改    
    System.out.println(n);
}
```

### 2\.4 继承

```Java
// 父类
class Animal {    
   String name;   
        
   public Animal(String name) {        
   this.name = name;    
   }       
    
   public void speak() {        
      System.out.println("动物叫");    
      }
}
// 子类
class Dog extends Animal {    
   public Dog(String name) {        
   super(name);  // 调用父类构造方法    
   }   
     
   @Override    
   public void speak() {  // 重写父类方法        
      System.out.println(name + " 汪汪");    
      }        
   public void fetch() {  // 子类自己的方法        
   System.out.println(name + " 叼拖鞋");    
   }
}
public class InheritanceDemo {    
   public static void main(String[] args) {        
   Dog d = new Dog("旺财");        
   d.speak();   // "旺财 汪汪"        
   d.fetch();   // "旺财 叼拖鞋"    
   }
}
```

![QQ\_1787728407385\.png](/images/android-reverse/QQ_1787728407385.png)

**那如果“子类要调用父类”应该怎么写？**（终极总结）

![QQ\_1787731322298\.png](/images/android-reverse/QQ_1787731322298.png)

- 看到 `extends` 就是继承

- 看到 `super(...)` 就是调父类构造

- `@Override` 注解表示重写（

### 2\.5 抽象类

```Java
abstract class Shape {
    String color;
    
    public Shape(String color) {
        this.color = color;
    }
    
    **// 抽象方法：只有声明，没有实现**
    public abstract double area();
    
    // 普通方法
    public void describe() {
        System.out.println("A " + color + " shape, area=" + area());
    }
}

class Circle extends Shape {
    double r;
    
    public Circle(String color, double r) {
        super(color);
        this.r = r;
    }
    
    @Override
    public double area() {
        return 3.14 * r * r;
    }
}
```

**限定了每一个子类都必须在自己的代码里重新实现（Override）这个方法，以防万一漏写了具体逻辑，导致主程序调用时找不到函数而崩溃。**

### 2\.6 接口

接口是一组方法签名的集合。Java 8 以后可以有 default 方法。

```Java
interface Flyable {
    void fly();  // 默认 public abstract
}

interface Swimmable {
    void swim();
}

class Duck implements Flyable, Swimmable {
    @Override
    public void fly() {
        System.out.println("鸭飞");
    }
    
    @Override
    public void swim() {
        System.out.println("鸭游");
    }
}
```

- 接口在反编译后常常是一些**没有实现的抽象类**

- 看到 **`implements`**` A, B, C` 说明类实现了多个接口

- 回调/监听器在 Android 里全是接口（比如 **`OnClickListener`**）

抽象类（`abstract class`）：是 “是什么”（身份认定）。比如“你是动物”。

接口（`interface`）：是 “有没有资格做”（技能证书）。比如“你会飞”。

Java 的设计铁律： 一个人只能有一个“身份”（单继承），但可以有无数个“技能证书”（多实现）。



ai举的例子 展示接口重要性

![5e2809e004ef5b758dd96a30b295433a\.png](/images/android-reverse/5e2809e004ef5b758dd96a30b295433a.png)

### 2\.7内部类（高频）

内部类在 Android 里极其常见。所有 `setOnClickListener` 这种都是匿名内部类。

```Java
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;

public class InnerClassDemo {
    
    // 1. 成员内部类
    class Outer {
        void hello() {
            System.out.println("outer");
        }
    }
    
    public static void main(String[] args) {
        // 2. 匿名内部类（重点！）
        // 下面这行等价于"实现 ActionListener 接口的一个匿名类"
        ActionListener listener = new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {
                System.out.println("clicked");
            }
        };
        
        // 3. Lambda 表达式（JDK 8+，等价于上面的匿名类）
        ActionListener listener2 = e -> System.out.println("clicked (lambda)");
    }
}
```

反编译后长这样：

```TypeScript
// jadx 看到的
button.setOnClickListener(new View.OnClickListener() {
    @Override
    public void onClick(View v) {
        check();
    }
});
```

> 为什么出题人（或开发者）要用匿名内部类？
> 因为 Android 系统规定：当按钮被点击时，系统只会找 `OnClickListener` 接口的 `onClick` 方法。程序猿懒得去写一个单独的 `MyButtonHandler.java` 文件（外部类），就直接把逻辑塞在点击事件的括号里了。
> 
> 

### 2\.8 构造方法与方法重载

```Java
public class Point {
    int x, y;
    
    public Point() {  // 无参构造
        this(0, 0);  // 调用下面的双参构造
    }
    
    public Point(int x, int y) {
        this.x = x;
        this.y = y;
    }
    
    public Point(int x) {  **// 重载（同名不同参）**
        this(x, 0);
    }
}
```

- 多个同名方法叫重载（overload），**参数列表必须不同**

- 子类重写父类方法叫重写（override），**方法签名必须一致**

- 看到 `this(...)` 就是构造方法之间的互相调用

## 字符串与集合

### 3\.1 String 的不可变性

```TypeScript
public class StringDemo {
    public static void main(String[] args) {
        String s = "Hello";
        s.toUpperCase();  // 注意！String 不可变，这个调用返回新字符串，原串不变
        System.out.println(s);  // 还是 "Hello"
        
        s = s.toUpperCase();    // 重新赋值才对
        System.out.println(s);  // "HELLO"
    }
}
```

**改变字符必须重新赋值**

Eg\.

```Java
String input = editText.getText().toString();
input.toUpperCase();   // 这里没赋值！程序员写了个 BUG！
if (input.equals("MOECTF")) {
    // 永远进不来
}
```

这行没赋值，`input` 根本没变，它还是原来的小写，这个比较根本不可能成功！

### 3\.2 常用 String 方法

```Java
String s = "Hello, World!";

s.length();                  // 13
s.charAt(0);                 // 'H'
s.substring(0, 5);           // "Hello"
s.indexOf("World");          // 7
s.contains("World");         // true
s.startsWith("Hello");       // true
s.endsWith("!");             // true
s.toLowerCase();             // "hello, world!"
s.toUpperCase();             // "HELLO, WORLD!"
**s.trim();                    // 去首尾空白**
s.replace("World", "Java");  // "Hello, Java!"
s.split(",");                // ["Hello", " World!"]
s.equals("Hello, World!");   // true（内容比较）
s.equalsIgnoreCase("hello, world!"); // true（忽略大小写）

// 字符串拼接
String a = "Hello" + ", " + "World";  // 编译时优化为 StringBuilder

// 字符数组
char[] arr = s.toCharArray();  // ['H','e','l','l','o',','...]

// 字符和数字互转
char c = (char) 65;       // 'A'
int n = (int) 'A';         // 65
String hex = Integer.toHexString(255);  // "ff"
String bin = Integer.toBinaryString(10); // "1010"
int parsed = Integer.parseInt("123");    // 123
```

只要看到 `indexOf("某词") != -1`，就是在问 “这句话里有没有提到‘某词’？”

- `contains`：只告诉你“有”还是“没有”（返回 `true` / `false`）。就像问：“货架上有西瓜吗？” 回答：“有”。

- `indexOf`：不仅告诉你“有”，还告诉你“具体放在哪个位置”（返回索引数字）。就像问：“西瓜放在第几个格子里？” 回答：“第 7 个”。



Integer\.parseInt / toString / toHexString 是字符串\-数字转换的常用函数

看到 s\.getBytes\(\) 就是把字符串转字节数组，注意编码（默认是平台编码，re 里常常指定 UTF\-8）

### 3\.3 StringBuilder 与 StringBuffer

```TypeScript
public class SB {
    public static void main(String[] args) {
        StringBuilder sb = new StringBuilder();
        sb.append("Hello");
        sb.append(", ");
        sb.append("World");
        sb.append("!");
        System.out.println(sb.toString());  // "Hello, World!"
        
        // 反转
        sb.reverse();
        System.out.println(sb.toString());  // "!dlroW ,olleH"
        
        // 删除
        sb.delete(0, 1);  // 删除 [0, 1) 的字符
    }
}
```

- **StringBuilder 是可变字符串**

- StringBuffer 是 StringBuilder 的线程安全版，反编译里会看到 `synchronized` 关键字



```Java
sb.reverse(); // 直接把白板上的字倒过来！"!dlrow ,olleH"
sb.delete(0, 1); // 删除 0 号索引，即删除 '!'，剩下 "dlrow ,olleH"
```

### 3\.4 HashMap（高频）

```Java
import java.util.HashMap;
import java.util.Map;

public class MapDemo {
    public static void main(String[] args) {
        Map<String, Integer> map = new HashMap<>();
        map.put("apple", 1);
        map.put("banana", 2);
        
        map.get("apple");          // 1
        map.containsKey("apple");  // true
        map.size();                // 2
        
       ** // 遍历 **
        for (Map.Entry<String, Integer> e : map.entrySet()) {
            System.out.println(e.getKey() + " = " + e.getValue());
        }
    }
}
```

- 看到 `new HashMap<>()` 就是键值对

- 看到 `map.put(k, v)` 和 `map.get(k)`，认成"查表"就行

- 一些"查表替换"算法就是预先建表然后循环替换

`Map<String, Integer>` 意思是：

- **“键”（Key） 只能是 字符串（****`String`****） 类型**，比如 `"apple"` 或 `"banana"`。

- **“值”（Value） 只能是 整数（****`Integer`****） 类型**，比如 `1` 或 `2`。

这相当于快递柜系统设定：“取件码必须用汉字或字母（String），格

ai举的例子：

![QQ\_1788019981541\.png](/images/android-reverse/QQ_1788019981541.png)

### 3\.5 数组

```C++
public class ArrayDemo {
    public static void main(String[] args) {
        // 静态初始化
        int[] a = {1, 2, 3, 4, 5};
        
        // 动态初始化
        int[] b = new int[10];   // 长度 10，默认全 0
        String[] c = new String[5]; // 默认全 null
        
        // 多维
        int[][] d = {{1, 2}, {3, 4}};
        
        // 常用属性
        a.length;  // 5（数组 length 是属性，不是方法）
        "abc".length();  // 3（String length 是方法）
        
        // 拷贝
        int[] e = a.clone();
        int[] f = java.util.Arrays.copyOf(a, 3);  // [1,2,3]
        int[] g = java.util.Arrays.copyOfRange(a, 1, 4); // [2,3,4]
        
        // 排序
        java.util.Arrays.sort(a);  // 原地排序
        
        // 转字符串
        System.out.println(java.util.Arrays.toString(a));
    }
}
```

- **`array.length`**** 没有括号（属性）**

- **`string.length()`**** 有括号（方法）**

- 二维数组的写法 `[][]`

- 字节数组 `byte[]` 在 re 里超级常见

## 位运算（RE 高频考点）

位运算是 re 必考内容。

### 4\.1 与、或、异或、取反

```Plain Text
&  按位与：两个都是 1 才是 1
|  按位或：有一个是 1 就是 1
^  按位异或：不同才是 1（相同为 0）
~  按位取反：1 变 0，0 变 1
```

- **`a ^ a = 0`****（自己异或自己是 0）**

- **`a ^ 0 = a`****（异或 0 等于自己）**

- `a ^ b ^ a = b`（异或满足交换律，常用于"还原"）

- 异或常用于简单加密（因为可以"自逆"）

### 4\.2 移位

```Java
a << n   左移 n 位 = a * 2^n（最低位补 0）
a >> n   算术右移 n 位 = a / 2^n（最高位补符号位，保留正负）
a >>> n  逻辑右移 n 位（最高位补 0，常用于无符号）
```

### 4\.3 异或加密

```Java
public class XorCipher {
    public static void main(String[] args) {
        String plain = "flag{test}";
        int key = 0x5A;
        
        // 加密
        StringBuilder enc = new StringBuilder();
        for (char c : plain.toCharArray()) {
            enc.append((char) (c ^ key));
        }
        System.out.println("加密: " + enc);
        
        // 异或特性：再异或一次就解密
        StringBuilder dec = new StringBuilder();
        for (char c : enc.toString().toCharArray()) {
            dec.append((char) (c ^ key));
        }
        System.out.println("解密: " + dec);
    }
}
```

## 异常与控制流（影响反编译阅读）

### 5\.1 try\-catch

```TypeScript
public class ExceptionDemo {
    public static void main(String[] args) {
        try {
            int a = 10 / 0;  // 抛 ArithmeticException
        } catch (ArithmeticException e) {
            System.out.println("除零了");
        } finally {
            System.out.println("总会执行");
        }
    }
}
```

- 反编译后，try 块常常被 `if (...) throw new ...` 取代（jvm 风格）

- 看到 `throw new RuntimeException(...)` 可能是反编译还原 try\-catch 失败

依旧ai举例：

![b898a2a229c20c11f53199d162e46d89\.png](/images/android-reverse/b898a2a229c20c11f53199d162e46d89.png)

try是代码尝试 catch是加入遇到异常程序应该做出如何反应 finally是每次结束前必须完成的动作（无论是否触发异常）。

### 5\.2 常见异常

```Java
NullPointerException             空指针
ArrayIndexOutOfBoundsException   数组越界
NumberFormatException            数字格式错
ClassCastException               类型转换错
ArithmeticException              算术异常（如除零）
```

## Java 加密与编码（识别\+复现）

### 6\.1 base64

```TypeScript
import java.util.Base64;

public class Base64Demo {
    public static void main(String[] args) {
        String src = "Hello, RE!";
        **String enc = Base64.getEncoder().encodeToString(src.getBytes());**
        System.out.println(enc);  // "SGVsbG8sIFJF!"
        
        **String dec = new String(Base64.getDecoder().decode(enc));**
        System.out.println(dec);  // "Hello, RE!"
    }
}
```

- 反编译后看到 `Base64.encodeToString(...)` / `Base64.decode(...)`

- 看到 `import java.util.Base64;` 就是 Base64

### 6\.2 MD5 / SHA

```Java
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;

public class HashDemo {
    public static void main(String[] args) throws Exception {
        String src = "flag{test}";
        
        // MD5
        MessageDigest md5 = MessageDigest.getInstance("MD5");
        byte[] hash = md5.digest(src.getBytes());
        System.out.println(bytesToHex(hash));  // 32 字符
        
        // SHA-1
        MessageDigest sha1 = MessageDigest.getInstance("SHA-1");
        byte[] h1 = sha1.digest(src.getBytes());
        System.out.println(bytesToHex(h1));  // 40 字符
        
        // SHA-256
        MessageDigest sha256 = MessageDigest.getInstance("SHA-256");
        byte[] h2 = sha256.digest(src.getBytes());
        System.out.println(bytesToHex(h2));  // 64 字符
    }
    
    static String bytesToHex(byte[] bytes) {
        StringBuilder sb = new StringBuilder();
        for (byte b : bytes) {
            sb.append(String.format("%02x", b));
        }
        return sb.toString();
    }
}
```

- 哈希结果长度固定：MD5=32, SHA1=40, SHA256=64（十六进制字符）

#### 场景 1：密码校验

```Java
String input = editText.getText().toString();
String inputHash = md5(input); // 计算你输入的 MD5

// ★ 硬编码的 MD5 值（这就是藏在代码里的“指纹卡”）
String correctHash = "e10adc3949ba59abbe56e057f20f883e"; 

if (inputHash.equals(correctHash)) {
    // 验证通过！
}
```

#### 场景 2：签名校验（反篡改、反重打包）

APP 在启动时，会计算自己的 APK 签名文件的 SHA\-256 哈希，然后和开发者预埋的哈希值比对。如果不一样，就闪退或提示“盗版”。这是我们以后做“破解”题时必须要绕过的坎。

### 6\.3 AES 对称加密

```Java
import javax.crypto.Cipher;
import javax.crypto.spec.IvParameterSpec;
import javax.crypto.spec.SecretKeySpec;

public class AESDemo {
    public static void main(String[] args) throws Exception {
        String key = "1234567890123456";           // 16 字节
        String iv = "abcdefghijklmnop";            // 16 字节
        String plain = "flag{aes_test}";
        
        SecretKeySpec keySpec = new SecretKeySpec(key.getBytes(), "AES");
        IvParameterSpec ivSpec = new IvParameterSpec(iv.getBytes());
        
        // 加密
        Cipher cipher = Cipher.getInstance("AES/CBC/PKCS5Padding");
        cipher.init(Cipher.ENCRYPT_MODE, keySpec, ivSpec);
        byte[] enc = cipher.doFinal(plain.getBytes());
        System.out.println("加密: " + bytesToHex(enc));
        
        // 解密
        cipher.init(Cipher.DECRYPT_MODE, keySpec, ivSpec);
        byte[] dec = cipher.doFinal(enc);
        System.out.println("解密: " + new String(dec));
    }
    
    static String bytesToHex(byte[] bytes) {
        StringBuilder sb = new StringBuilder();
        for (byte b : bytes) {
            sb.append(String.format("%02x", b));
        }
        return sb.toString();
    }
}
```

- 看到 `Cipher.getInstance("AES/...")` 或 `Cipher.getInstance("DES/...")` 就是对称加密

- 工作模式：CBC、ECB、CTR、GCM

- 填充：PKCS5Padding、NoPadding

- key 和 IV 通常在代码里写死，直接抓出来就行

### 6\.4 RC4 自动流加密

```Java
public class RC4 {
    public static String encrypt(String key, String data) {
        byte[] keyBytes = key.getBytes();
        byte[] dataBytes = data.getBytes();
        
        int[] S = new int[256];
        for (int i = 0; i < 256; i++) S[i] = i;
        
        // KSA
        int j = 0;
        for (int i = 0; i < 256; i++) {
            j = (j + S[i] + keyBytes[i % keyBytes.length]) & 0xFF;
            int t = S[i]; S[i] = S[j]; S[j] = t;
        }
        
        // PRGA
        StringBuilder out = new StringBuilder();
        int i = 0; j = 0;
        for (byte b : dataBytes) {
            i = (i + 1) & 0xFF;
            j = (j + S[i]) & 0xFF;
            int t = S[i]; S[i] = S[j]; S[j] = t;
            out.append((char) (b ^ S[(S[i] + S[j]) & 0xFF]));
        }
        return out.toString();
    }
    
    public static void main(String[] args) {
        String enc = encrypt("key", "Hello");
        System.out.println("加密: " + enc);
        System.out.println("解密: " + encrypt("key", enc));  // 自逆
    }
}
```

## smali 语法入门

有时 jadx 反编译失败（混淆、加密 APK），需要直接看 smali。

> smali 是 Davlik 字节码 的文本表示。Java 编译后是 `.class`，Android 编译后是 `.dex`，baksmali 把 dex 反汇编成 smali。
> 
> 

对照：

```Java
// Java
int x = 10;
String s = "Hello";
if (x > 5) {
    System.out.println(s);
}
```

```Bash
# smali
const/4 v0, 0xa        # v0 = 10
const-string v1, "Hello"  # v1 = "Hello"
if-lez v0, :cond_false # if (v0 <= 0) goto :cond_false
sget-object v2, Ljava/lang/System;->out:Ljava/io/PrintStream;
invoke-virtual {v2, v1}, Ljava/io/PrintStream;->println(Ljava/lang/String;)V
:cond_false
return-void
```

### 基础指令

#### 数据定义

```TypeScript
const v0, 0x1         # v0 = 1
const/4 v0, 0xa       # v0 = 10（4 位立即数优化）
const-string v1, "abc" # v1 = "abc"
const-class v0, Ljava/lang/String;  # v0 = String.class
```

#### 方法调用

```Java
invoke-virtual       # 虚方法（普通方法）
invoke-static        # 静态方法
invoke-direct        # 私有方法、构造
invoke-super         # 父类方法
invoke-interface     # 接口方法
```

调用格式：`invoke-XXX {参数}, 类名->方法名(参数类型)返回类型`

举个例子：

```C
invoke-virtual {v0, v1}, Lcom/example/MyClass;->add(II)I
```

- `{v0, v1}`：传两个参数，分别是 `v0` 和 `v1`。注意：**如果是实例方法，第一个参数默认是 ****`this`****（对象本身），所以这里 ****`v0`**** 就是 ****`this`****，****`v1`**** 才是真正的参数。**

- `Lcom/example/MyClass;`：这个类名。

- `->`：分隔符。

- `add(II)I`：**方法名 ****`add`****，参数是两个 ****`int`****（****`II`****），返回值是 ****`int`****（最后的 ****`I`****）。**

如果是静态方法，就没有 `this` 参数，直接传实参就行。

区分：

静态方法（invoke\-static）：公共厕所，不依赖任何人。走过去就能用，不需要“属于”谁。比如 `Math.abs(-5)`，你不需要 new 一个 Math 对象，直接调就行。

实例方法（invoke\-virtual / invoke\-direct）：你家的卫生间，必须依赖你这个“人”存在。如果你这个人（**对象**）都没创建出来，你家卫生间就不存在，自然没法用。

#### 字段访问

```C
iget v0, v1, Lpkg/Class;->field:I  # v0 = v1.field (int)
iput v0, v1, Lpkg/Class;->field:I  # v1.field = v0
sget v0, Lpkg/Class;->staticField:I  # 静态字段读
sput v0, Lpkg/Class;->staticField:I  # 静态字段写
```

- `i` 开头 = Instance（实例字段），必须依赖具体的对象（也就是之前说的 `this`）。

- `s` 开头 = Static（静态字段），不依赖对象，属于类本身。

- `get` = 读取（从对象里拿出来）。

- `put` = 写入（往对象里放进去）。



**注意：****`iget`**** 和 ****`iput`**** 的参数顺序是反着的！**

##### `iget`（读取）：把字段值拿出来

指令格式：`iget 目标寄存器, 对象寄存器, 字段名`

- 第一行：`iget v0, v1, Lpkg/Class;->field:I`

- 人话翻译：把 `v1` 这个对象里的 `field` 字段值，取出来放到 `v0` 里。

- Java 等价：`v0 = v1.field;`

##### `iput`（写入）：把值放进去

指令格式：`iput 来源寄存器, 对象寄存器, 字段名`

- 第二行：`iput v0, v1, Lpkg/Class;->field:I`

- 人话翻译：把 `v0` 这个值，存进 `v1` 这个对象的 `field` 字段里。

- Java 等价：`v1.field = v0;`

因为静态字段不属于某个具体对象，所以不需要传对象进去，直接用类名就行。

- `sget v0, Lpkg/Class;->staticField:I`
把类的静态字段值，读出来放进 `v0`。
Java：`v0 = Class.staticField;`

- `sput v0, Lpkg/Class;->staticField:I`
把 `v0` 的值，写进类的静态字段里。
Java：`Class.staticField = v0;`

#### 跳转

```Python
if-eq v0, v1, :label   # if (v0 == v1) goto :label
if-ne v0, v1, :label   # if (v0 != v1)
if-lt v0, v1, :label   # if (v0 < v1)
if-ge v0, v1, :label   # if (v0 >= v1)
if-lez v0, :label      # if (v0 <= 0)
if-eqz v0, :label      # if (v0 == 0)
goto :label            # 无条件跳转
```

#### 数组

```C
new-array v0, v1, [I    # v0 = new int[v1]
array-length v0, v1      # v0 = v1.length
aget v0, v1, v2          # v0 = v1[v2]
aput v0, v1, v2          # v1[v2] = v0
```

- `[` 表示“数组”（一个方括号代表一维）。

- `I` 表示 `int` 类型。、

so

- `[I` = `int[]`（整型一维数组）

- `[Ljava/lang/String;` = `String[]`（字符串数组）

- `[[I` = `int[][]`（二维整型数组）





**一套安卓题目的标准流程**

```Markdown
1. 拿到 APK
2. jadx 打开，搜 "flag"、"key"、"check"
3. 看 AndroidManifest.xml 找入口 Activity
4. 读入口 Activity 的 onCreate 和 OnClickListener
5. **定位核心 check 函数**
6. 静态分析（看代码、画流程图）
7. 写出解密脚本（Python / Java）
8. 跑脚本得到 flag
9. （如果静态搞不定）动态调试：frida hook / AS 单步
```
