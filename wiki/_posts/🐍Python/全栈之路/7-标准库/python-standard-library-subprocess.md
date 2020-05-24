---
title: Python 标准库系列之 subprocess 模块
toc: true
date: 2020-05-23 18:21:46
tags:
- 编码
- 面向对象
top: 9

---
# Python 标准库系列之 subprocess 模块

> This module allows you to spawn processes, connect to their input/output/error pipes, and obtain their return codes.

## 常用方法实例

**call()**

执行命令，并返回状态码，状态码`0`代表命令执行成功，其他的都表示命令执行不成功

```python
>>> ret = subprocess.call(["ls", "-l"], shell=False)
total 4
-rw-r--r-- 1 root root 172 May 25 21:21 file.conf
>>> ret
0
```

另一种执行方式

```python
# shell=True表示调用原生的shell命令去执行
>>> ret = subprocess.call("ls -l", shell=True)
total 4
-rw-r--r-- 1 root root 172 May 25 21:21 file.conf
>>> ret
0
```

**check_call()**

执行命令，如果执行状态码是 0，则返回 0，否则抛异常

```python
# 执行一个正确的命令就会返回执行结果和状态码
>>> subprocess.check_call(["ls", "-l"])
total 4
-rw-r--r-- 1 root root 172 May 25 21:21 file.conf
0
# 如果执行的是一个错误的命令，那么就会返回错误信息
>>> subprocess.check_call(["ls", "a"])  
ls: cannot access a: No such file or directory
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "/usr/lib64/python2.6/subprocess.py", line 505, in check_call
    raise CalledProcessError(retcode, cmd)
subprocess.CalledProcessError: Command '['ls', 'a']' returned non-zero exit status 2
```

**check_output()**

执行命令，如果状态码是 0，则返回执行结果，否则抛异常

```python
# 执行成功就把执行的结果赋值给变量V
>>> V = subprocess.check_output("python -V", shell=True)
# 执行错误的命令就会输出异常
>>> subprocess.check_output("pasas", shell=True)
'pasas' 不是内部或外部命令，也不是可运行的程序
或批处理文件。
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "C:\Python35\lib\subprocess.py", line 629, in check_output
    **kwargs).stdout
  File "C:\Python35\lib\subprocess.py", line 711, in run
    output=stdout, stderr=stderr)
subprocess.CalledProcessError: Command 'pasas' returned non-zero exit status 1
```

以上的三种执行方式在执行命令的时候，`shell`默认等于`True`，等于`True`的时候，括号内的命令是一行的，如果`shell`等于`False`，那么`[]`内的字符串就是命令的一个元素，执行的时候会把`[]`内的字符串拼接起来执行。

**subprocess.Popen()**

`call()`、`check_call()`、`check_output()`默认内部调用的都是`subprocess.Popen()`，而`subprocess.Popen()`则用于执行更复杂的系统命令。

**参数**

|参数|说明|
|:--:|:--|
|stdin|标准输入|
|stdout|标准输出|
|stderr|错误句柄|
|cwd|用于设置子进程的当前目录|
|env|用于指定子进程的环境变量。如果 env = None，子进程的环境变量将从父进程中继承|

执行普通命令

```python
>>> subprocess.Popen("Python -V", shell=True)
<subprocess.Popen object at 0x0000025C97233C88>
# Python 3.5.1是输出出来的结果
>>> Python 3.5.1
```

执行命令分为两种：

1. 输入即可得到输出，如：ifconfig
2. 输入进行某交互式环境，依赖再输入，如：python

```python
>>> import subprocess
# 先进入'/tmp'目录，然后在创建subprocess文件夹，shell=True可有可无
>>> subprocess.Popen("mkdir subprocess", shell=True, cwd='/tmp',)
<subprocess.Popen object at 0x7f267cc3d390>
>>> import os
>>> os.system("ls /tmp")
subprocess
```

## subprocess.Popen()实例

```python
# 导入subprocess模块
import subprocess

# 执行python命令，进入python解释器，stdin标准输入、stdout标准输出、stderr错误输出，universal_newlines=True自动输入换行符
obj = subprocess.Popen(["python"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

# 执行标准输入，write后面是输入的命令
obj.stdin.write("print(1)\n")
obj.stdin.write("print(2)")
# 输入之后关闭
obj.stdin.close()

# 读取标准输出的内容，赋值给cmd_out对象
cmd_out = obj.stdout.read()
# 关闭标准输出
obj.stdout.close()

# 读取错误输出的内容，赋值给cmd_error对象
cmd_error = obj.stderr.read()

# 关闭错误输出
obj.stderr.close()

# 输出内容
print(cmd_out)
print(cmd_error)
```
执行结果
```python
C:\Python35\python.exe F:/Python_code/sublime/Week5/Day02/sub.py
1
2



Process finished with exit code 0
```


```python
# 导入subprocess模块
import subprocess

# 执行python命令，进入python解释器，stdin标准输入、stdout标准输出、stderr错误输出，universal_newlines=True自动输入换行符
obj = subprocess.Popen(["python"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

# 执行两条命令
obj.stdin.write("print(1)\n")
obj.stdin.write("print(2)")

# communicate把错误输出或者标准输出的内容赋值给out_error_list对象，如果有错误就赋值错误输出，否则就复制标准输出
out_error_list = obj.communicate()

# 输出out_error_list对象的内容
print(out_error_list)
```
执行结果
```python
C:\Python35\python.exe F:/Python_code/sublime/Week5/Day02/sub.py
('1\n2\n', '')

Process finished with exit code 0
```

```python
# 导入subprocess模块
import subprocess

# 执行python命令，进入python解释器，stdin标准输入、stdout标准输出、stderr错误输出，universal_newlines=True自动输入换行符
obj = subprocess.Popen(["python"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)


# 直接执行print("hello")命令，然后把错误或者正确的结果赋值给out_error_list对象
out_error_list = obj.communicate('print("hello")')

# 输出out_error_list对象的内容
print(out_error_list)
```

执行结果

```python
C:\Python35\python.exe F:/Python_code/sublime/Week5/Day02/sub.py
('hello\n', '')

Process finished with exit code 0
```