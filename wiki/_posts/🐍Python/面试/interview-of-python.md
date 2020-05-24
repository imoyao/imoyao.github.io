---
title: Python 面试
toc: true
date: 2020-05-23 18:21:46
tags:
- 面试

---
## [`Python`语言特性](https://github.com/imoyao/interview_python#python%E8%AF%AD%E8%A8%80%E7%89%B9%E6%80%A7)
1. [`Python`的函数参数传递](https://github.com/imoyao/interview_python#1-python%E7%9A%84%E5%87%BD%E6%95%B0%E5%8F%82%E6%95%B0%E4%BC%A0%E9%80%92)
2. [`Python`中的元类(`metaclass`)](https://github.com/imoyao/interview_python#2-python%E4%B8%AD%E7%9A%84%E5%85%83%E7%B1%BBmetaclass)
3. [`@staticmethod`和`@classmethod`](https://github.com/imoyao/interview_python#3-staticmethod%E5%92%8Cclassmethod)
4. [类变量和实例变量](https://github.com/imoyao/interview_python#4-%E7%B1%BB%E5%8F%98%E9%87%8F%E5%92%8C%E5%AE%9E%E4%BE%8B%E5%8F%98%E9%87%8F)
5. [`Python`自省](https://github.com/imoyao/interview_python#5-python%E8%87%AA%E7%9C%81)
6. [字典推导式](https://github.com/imoyao/interview_python#6-%E5%AD%97%E5%85%B8%E6%8E%A8%E5%AF%BC%E5%BC%8F) 
7. [`Python`中单下划线和双下划线](https://github.com/imoyao/interview_python#7-python%E4%B8%AD%E5%8D%95%E4%B8%8B%E5%88%92%E7%BA%BF%E5%92%8C%E5%8F%8C%E4%B8%8B%E5%88%92%E7%BA%BF)
8. [字符串格式化:\x 和.format](https://github.com/imoyao/interview_python#8-%E5%AD%97%E7%AC%A6%E4%B8%B2%E6%A0%BC%E5%BC%8F%E5%8C%96%E5%92%8Cformat)

9. [迭代器和生成器](https://github.com/imoyao/interview_python#9-%E8%BF%AD%E4%BB%A3%E5%99%A8%E5%92%8C%E7%94%9F%E6%88%90%E5%99%A8)

10. [`*args`和`**kwargs`](https://github.com/imoyao/interview_python#10-args-and-kwargs)
11. [面向切面编程`AOP`和装饰器](https://github.com/imoyao/interview_python#11-%E9%9D%A2%E5%90%91%E5%88%87%E9%9D%A2%E7%BC%96%E7%A8%8Baop%E5%92%8C%E8%A3%85%E9%A5%B0%E5%99%A8)

12. [鸭子类型](https://github.com/imoyao/interview_python#12-%E9%B8%AD%E5%AD%90%E7%B1%BB%E5%9E%8B)
13. [`Python`中重载](https://github.com/imoyao/interview_python#13-python%E4%B8%AD%E9%87%8D%E8%BD%BD)
14. [新式类和旧式类](https://github.com/imoyao/interview_python#14-%E6%96%B0%E5%BC%8F%E7%B1%BB%E5%92%8C%E6%97%A7%E5%BC%8F%E7%B1%BB)
15. [`__new__`和`__init__`的区别](https://github.com/imoyao/interview_python#15-__new__%E5%92%8C__init__%E7%9A%84%E5%8C%BA%E5%88%AB)
16. [单例模式](https://github.com/taizilongxu/interview_python#16-%E5%8D%95%E4%BE%8B%E6%A8%A1%E5%BC%8F)
	- 1. [使用`__new__`方法](https://github.com/imoyao/interview_python#1-%E4%BD%BF%E7%94%A8__new__%E6%96%B9%E6%B3%95)
	- 2. [共享属性](https://github.com/imoyao/interview_python#2-%E5%85%B1%E4%BA%AB%E5%B1%9E%E6%80%A7)
	- 3. [装饰器版本](https://github.com/imoyao/interview_python#3-%E8%A3%85%E9%A5%B0%E5%99%A8%E7%89%88%E6%9C%AC)
	- 4. [`import`方法](https://github.com/imoyao/interview_python#4-import%E6%96%B9%E6%B3%95)
	
17. [`Python`中的作用域](https://github.com/taizilongxu/interview_python#17-python%E4%B8%AD%E7%9A%84%E4%BD%9C%E7%94%A8%E5%9F%9F)
18. [`GIL`线程全局锁](https://github.com/taizilongxu/interview_python#18-gil%E7%BA%BF%E7%A8%8B%E5%85%A8%E5%B1%80%E9%94%81)

19. [协程](https://github.com/taizilongxu/interview_python#19-%E5%8D%8F%E7%A8%8B)
20. [闭包](https://github.com/taizilongxu/interview_python#20-%E9%97%AD%E5%8C%85)
21. [`lambda`函数](https://github.com/taizilongxu/interview_python#21-lambda%E5%87%BD%E6%95%B0)
22. [`Python`函数式编程](https://github.com/taizilongxu/interview_python#22-python%E5%87%BD%E6%95%B0%E5%BC%8F%E7%BC%96%E7%A8%8B)
23. [`Python`里的拷贝](https://github.com/taizilongxu/interview_python#23-python%E9%87%8C%E7%9A%84%E6%8B%B7%E8%B4%9D)
24. [`Python`垃圾回收机制](https://github.com/taizilongxu/interview_python#24-python%E5%9E%83%E5%9C%BE%E5%9B%9E%E6%94%B6%E6%9C%BA%E5%88%B6)

	- 1. [引用计数](https://github.com/imoyao/interview_python#1-%E5%BC%95%E7%94%A8%E8%AE%A1%E6%95%B0)
	
	- 2. [标记-清除机制](https://github.com/imoyao/interview_python#2-%E6%A0%87%E8%AE%B0-%E6%B8%85%E9%99%A4%E6%9C%BA%E5%88%B6)
	
	- 3. [分代技术](https://github.com/imoyao/interview_python#3-%E5%88%86%E4%BB%A3%E6%8A%80%E6%9C%AF)
	
25. [`Python`的`List`](https://github.com/imoyao/interview_python#25-python%E7%9A%84list)
26. [`Python`的`is`](https://github.com/imoyao/interview_python#26-python%E7%9A%84is)
27. [`read`,`readline`和`readlines`](https://github.com/imoyao/interview_python#27-readreadline%E5%92%8Creadlines)
28. [`Python2`和`Python3`的区别](https://github.com/imoyao/interview_python#28-python2%E5%92%8C3%E7%9A%84%E5%8C%BA%E5%88%AB)

29. [super. init](https://github.com/imoyao/interview_python#29-super-init)
30. [`range`和`xrange`](https://github.com/imoyao/interview_python#30-range-and-xrange)

## [操作系统](https://github.com/imoyao/interview_python#%E6%93%8D%E4%BD%9C%E7%B3%BB%E7%BB%9F)
1. [`select`,`poll`和`epoll`](https://github.com/imoyao/interview_python#2-%E8%B0%83%E5%BA%A6%E7%AE%97%E6%B3%95)

2. [调度算法](https://github.com/imoyao/interview_python#3-%E6%AD%BB%E9%94%81)
3. [死锁](https://github.com/imoyao/interview_python#4-%E7%A8%8B%E5%BA%8F%E7%BC%96%E8%AF%91%E4%B8%8E%E9%93%BE%E6%8E%A5)

4. [程序编译与链接](https://github.com/imoyao/interview_python#5-%E9%9D%99%E6%80%81%E9%93%BE%E6%8E%A5%E5%92%8C%E5%8A%A8%E6%80%81%E9%93%BE%E6%8E%A5)

	- 1. [预处理](https://github.com/imoyao/interview_python#1-%E9%A2%84%E5%A4%84%E7%90%86)
	- 2. [编译](https://github.com/imoyao/interview_python#2-%E7%BC%96%E8%AF%91)
	- 3. [汇编](https://github.com/imoyao/interview_python#3-%E6%B1%87%E7%BC%96)
	- 4. [链接](https://github.com/imoyao/interview_python#4-%E9%93%BE%E6%8E%A5)
5. [静态链接和动态链接](https://github.com/imoyao/interview_python#6-%E8%99%9A%E6%8B%9F%E5%86%85%E5%AD%98%E6%8A%80%E6%9C%AF)
6. [虚拟内存技术](https://github.com/imoyao/interview_python#7-%E5%88%86%E9%A1%B5%E5%92%8C%E5%88%86%E6%AE%B5)
7. [分页和分段](https://github.com/imoyao/interview_python#8-%E9%A1%B5%E9%9D%A2%E7%BD%AE%E6%8D%A2%E7%AE%97%E6%B3%95)
	- [分页与分段的主要区别](https://github.com/imoyao/interview_python#%E5%88%86%E9%A1%B5%E4%B8%8E%E5%88%86%E6%AE%B5%E7%9A%84%E4%B8%BB%E8%A6%81%E5%8C%BA%E5%88%AB)
8. [页面置换算法](https://github.com/imoyao/interview_python#9-%E8%BE%B9%E6%B2%BF%E8%A7%A6%E5%8F%91%E5%92%8C%E6%B0%B4%E5%B9%B3%E8%A7%A6%E5%8F%91)
9. [边沿触发和水平触发](https://github.com/imoyao/interview_python#1-%E4%BA%8B%E5%8A%A1)

## [数据库](https://github.com/imoyao/interview_python#%E6%95%B0%E6%8D%AE%E5%BA%93)

1. [事务](https://github.com/imoyao/interview_python#2-%E6%95%B0%E6%8D%AE%E5%BA%93%E7%B4%A2%E5%BC%95)
 
2. [数据库索引](https://github.com/imoyao/interview_python#3-redis%E5%8E%9F%E7%90%86)
3. [`Redis`原理](https://github.com/imoyao/interview_python#4-%E4%B9%90%E8%A7%82%E9%94%81%E5%92%8C%E6%82%B2%E8%A7%82%E9%94%81)

	- [`Redis`是什么？](https://github.com/imoyao/interview_python#redis%E6%98%AF%E4%BB%80%E4%B9%88)
	- [`Redis`数据库](https://github.com/imoyao/interview_python#redis%E6%95%B0%E6%8D%AE%E5%BA%93)
	- [`Redis`缺点](https://github.com/imoyao/interview_python#redis%E7%BC%BA%E7%82%B9)

4. [乐观锁和悲观锁](https://github.com/imoyao/interview_python#4-%E4%B9%90%E8%A7%82%E9%94%81%E5%92%8C%E6%82%B2%E8%A7%82%E9%94%81)
5. [MVCC](https://github.com/imoyao/interview_python#5-mvcc) 
	- [MySQL 的 innodb 引擎是如何实现 MVCC 的](https://github.com/imoyao/interview_python#mysql%E7%9A%84innodb%E5%BC%95%E6%93%8E%E6%98%AF%E5%A6%82%E4%BD%95%E5%AE%9E%E7%8E%B0mvcc%E7%9A%84)
6. [MyISAM 和 InnoDB](https://github.com/imoyao/interview_python#6-myisam%E5%92%8Cinnodb)

## [网络](https://github.com/imoyao/interview_python#%E7%BD%91%E7%BB%9C) 

1. [三次握手](https://github.com/imoyao/interview_python#1-%E4%B8%89%E6%AC%A1%E6%8F%A1%E6%89%8B)
2. [四次挥手](https://github.com/imoyao/interview_python#2-%E5%9B%9B%E6%AC%A1%E6%8C%A5%E6%89%8B)
3. [ARP 协议](https://github.com/imoyao/interview_python#3-arp%E5%8D%8F%E8%AE%AE) 
4. [urllib 和 urllib2 的区别](https://github.com/imoyao/interview_python#4-urllib%E5%92%8Curllib2%E7%9A%84%E5%8C%BA%E5%88%AB)
5. [Post 和 Get](https://github.com/imoyao/interview_python#5-post%E5%92%8Cget)
6. [Cookie 和 Session](https://github.com/imoyao/interview_python#6-cookie%E5%92%8Csession) 
7. [apache 和 nginx 的区别](https://github.com/imoyao/interview_python#7-apache%E5%92%8Cnginx%E7%9A%84%E5%8C%BA%E5%88%AB)
8. [网站用户密码保存](https://github.com/imoyao/interview_python#8-%E7%BD%91%E7%AB%99%E7%94%A8%E6%88%B7%E5%AF%86%E7%A0%81%E4%BF%9D%E5%AD%98)
9. [HTTP 和 HTTPS](https://github.com/imoyao/interview_python#9-http%E5%92%8Chttps)
10. [`XSRF`和`XSS`](https://github.com/imoyao/interview_python#10-xsrf%E5%92%8Cxss)
11. [幂等`Idempotence`](https://github.com/imoyao/interview_python#11-%E5%B9%82%E7%AD%89-idempotence)
12. [RESTful 架构(SOAP,RPC)](https://github.com/imoyao/interview_python#12-restful%E6%9E%B6%E6%9E%84soaprpc)
13. [SOAP](https://github.com/imoyao/interview_python#13-soap)
14. [RPC](https://github.com/imoyao/interview_python#14-rpc)
15. [CGI 和 WSGI](https://github.com/imoyao/interview_python#15-cgi%E5%92%8Cwsgi)
16. [中间人攻击](https://github.com/imoyao/interview_python#16-%E4%B8%AD%E9%97%B4%E4%BA%BA%E6%94%BB%E5%87%BB)
17. [`c10k`问题](https://github.com/imoyao/interview_python#17-c10k%E9%97%AE%E9%A2%98)
18. [`socket`](https://github.com/imoyao/interview_python#18-socket)
19. [浏览器缓存](https://github.com/imoyao/interview_python#19-%E6%B5%8F%E8%A7%88%E5%99%A8%E7%BC%93%E5%AD%98)
20. [HTTP1.0 和 HTTP1.1](https://github.com/imoyao/interview_python#20-http10%E5%92%8Chttp11)
21. [`Ajax`](https://github.com/imoyao/interview_python#21-ajax)
22. [当在浏览器输入某网址时，计算机内部发生了什么？](https://github.com/skyline75489/what-happens-when-zh_CN)

## [*NIX](https://github.com/imoyao/interview_python#nix)

 - [`unix`进程间通信方式(`IPC`)](https://github.com/imoyao/interview_python#unix%E8%BF%9B%E7%A8%8B%E9%97%B4%E9%80%9A%E4%BF%A1%E6%96%B9%E5%BC%8Fipc)

# TODO

## [数据结构](https://github.com/imoyao/interview_python#%E6%95%B0%E6%8D%AE%E7%BB%93%E6%9E%84)
1. [红黑树](https://github.com/imoyao/interview_python#1-%E5%8F%B0%E9%98%B6%E9%97%AE%E9%A2%98%E6%96%90%E6%B3%A2%E9%82%A3%E5%A5%91)

## [编程题](https://github.com/imoyao/interview_python#%E7%BC%96%E7%A8%8B%E9%A2%98)
1. 台阶问题/斐波那契
2. [变态台阶问题](https://github.com/imoyao/interview_python#2-%E5%8F%98%E6%80%81%E5%8F%B0%E9%98%B6%E9%97%AE%E9%A2%98)
3. [矩形覆盖](https://github.com/imoyao/interview_python#3-%E7%9F%A9%E5%BD%A2%E8%A6%86%E7%9B%96)
4. 杨氏矩阵查找
5. 去除列表中的重复元素
6. 链表成对调换
7. 创建字典的方法
	- 直接创建
	- 工厂方法
	- fromkeys()方法
8. 合并两个有序列表
9. 交叉链表求交点
10. 二分查找
11. 快排
12. 找零问题
13. 广度遍历和深度遍历二叉树
17. 前中后序遍历
18. 求最大树深
19. 求两棵树是否相同
20. 前序中序求后序
21. 单链表逆置
22. 两个字符串是否是变位词
23. 动态规划问题


## 来源
- [Interview Python](https://github.com/taizilongxu/interview_python)