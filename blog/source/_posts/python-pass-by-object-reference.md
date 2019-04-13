---
title: Python传值还是传引用？| 通过对象引用传递
date: 2019-04-13 14:14:28
tags:

- Python
---
哈姆雷特不是莎士比亚写的;它只是由一个名叫莎士比亚的人写的。
Python 通过对象引用传递。

<!--more-->

本文译自 [Is Python pass-by-reference or pass-by-value?](https://robertheaton.com/2014/02/09/pythons-pass-by-object-reference-as-explained-by-philip-k-dick/)


>“假设我对 Fat 说，或 Kevin 对 Fat 说，“你没有经历过上帝。你只不过经历了一些与上帝的品质、方面、性质、力量、智慧和善良有关的事情。”这就像是关于德国人讲的一个双重抽象倾向的笑话；德国英国文学权威宣称，“哈姆雷特不是莎士比亚写的;它只是由一个名叫莎士比亚的人写的。”在英语语境中，这句话的区别只是口头的，没有实际意义，尽管德语中这种表达存在差异（这解释了德国思想的一些奇怪特征）。”
>   <p align="right"> --Valis，p71（Book-of-the-Month-Club Edition）</p>

Philip K. Dick并不以其轻松或易懂的散文而闻名。绝大多数角色都很高。就像，真的，真的，真的很高。然而，在Valis的上述引文（1981年出版）中，他对臭名昭着的`Python`参数传递范式给出了非常有远见的解释。Plus ça change, plus c’est omnomnomnom drugs.

在编程语言中参数传递的两种最广为人知且易于理解的方法是按引用传递( pass-by-reference )和按值传递 ( pass-by-value )。不幸的是，`Python`是“传递对象引用”( pass-by-object-reference )，经常说：

“对象引用按值传递。”(Object references are passed by value.)

当我第一次看到这个沾沾自喜和过于精辟的定义时，我想捶人。在从手上取下玻璃碎片并被护送出脱衣舞俱乐部后，~~我意识到所有3种范例都可以理解它们如何导致以下2个功能的表现：~~

```Python
def reassign(alist):
    alist = [0, 1]

def append(alist):
    alist.append(1)

alist = [0]
reassign(alist)
append(alist)
```
让我们来一探究竟。

## 变量不是对象

“哈姆雷特不是莎士比亚写的;它只是由一个名叫莎士比亚的人写的。” Python 和 PKD（ Philip K. Dick）都在一个东西的本质与我们用来指代那个东西的标签之间做出了至关重要的区分。 “这个名叫莎士比亚的男人”是一个具体的人。 而“莎士比亚”只是一个名字。如果我们这样做：
```Python
a = []
```
`[]`是一个空列表。 a是指向空列表的变量，但其本身并不是空列表。我画图并将变量称为包含对象的“盒子”;但无论如何你构想它，这种差异是关键。
![Pass-by-reference](https://robertheaton.com/images/Intro.jpg)

## 通过引用传递

在pass-by-reference中，box（变量）直接传递给函数，其内容（由变量表示的对象）隐性地随之而来。在函数上下文中，参数本质上是调用者传入的变量的完整别名。它们都是完全相同的盒子，因此也指向内存中完全相同的对象。
![](https://robertheaton.com/images/PBRIntro.jpg)


因此，函数对变量或它所代表的对象所做的任何操作都将对调用者可见。例如，该函数可以完全更改变量的内容，并将其指向完全不同的对象：

![](https://robertheaton.com/images/PBRReassign.jpg)

该函数还可以在不重新分配对象的情况下操作对象，效果相同：
![](https://robertheaton.com/images/PBRAppend.jpg)

重申一下，在`pass-by-reference`中，函数和调用者都使用完全相同的变量和对象。

## 通过值传递

在`pass-by-value`中，函数接收调用者传递给它的参数对象的副本，并在内存中开辟新的空间保存。

![](https://robertheaton.com/images/PBVIntro.jpg)

然后，该函数有效地提供其自己的盒子以将值放入，并且函数和调用者引用的变量或对象之间不再存在任何关系。这些对象碰巧具有相同的值，但它们完全是分开的，一个对象不会影响到另一个。如果我们再次尝试重新分配：

![](https://robertheaton.com/images/PBVReassign.jpg)

在函数之外，没有任何反应。同理：

![](https://robertheaton.com/images/PBVAppend.jpg)

调用者上下文中的变量和对象的副本是完全隔离的。

## 通过对象引用传递

在`Python`是不同的。众所周知，在`Python`中，“对象引用按值传递”（`Object references are passed by value`）。

函数接收对（并将访问）内存中与调用者使用的相同对象的引用。但是，它不会收到调用者正在存储此对象的盒子;在`pass-by-value`中，函数提供自己的筐并为自己创建一个新变量。让我们再次执行`append`：

![](https://robertheaton.com/images/PBORAppend.jpg)

函数和调用者都引用内存中的同一个对象，所以当`append`函数向列表中添加一个额外的项时，我们也会在调用者中看到这个！它们是同一个东西的不同名称;包含相同对象的不同筐。这意味着是通过值传递对象引用的——函数和调用者在内存中使用相同的对象，但是通过不同的变量访问。这意味着同一个对象被存储在多个不同的筐中，而这种隐喻会被打破。~~假定它是量子或其他东西。~~

但关键是它们真的是不同的名字和不同的盒子。在`pass-by-reference`中，它们是相同的盒子。当你试图重新分配一个变量，并将一些不同的东西放入函数的盒子中时，你也将它放入调用者的盒子中，因为它们是同一个盒子。但是，在`pass-by-object-reference`中：

![](https://robertheaton.com/images/PBORReassign.jpg)

调用者不在乎你是否重新分配方法的盒子。不同的盒子，相同的内容。

现在我们看看菲利普·K·迪克试图告诉我们的事情。名字和人是不同的东西。变量和对象是不同的东西。有了这些知识，你或许可以开始推断当你做这样的事情时会发生什么

```
listA = [0]
listB = listA
listB.append(1)
print listA
```
你可能还想了解这些概念与可变和不可变类型之间的有趣交互。但这些是另一回事了。现在，如果你能原谅我，我要去读《Dororoids Dream Of Electric Sheep？》了。 - 我对元编程有点生疏。

---

[Does Python pass by reference or value?](https://eev.ee/blog/2012/05/23/python-faq-passing/)

## 参考链接：

* http://foobarnbaz.com/2012/07/08/understanding-python-variables/ 
* http://javadude.com/articles/passbyvalue.htm
