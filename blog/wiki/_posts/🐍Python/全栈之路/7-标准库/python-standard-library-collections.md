---
title: Python 标准库系列之 collections 模块
toc: true
date: 2020-05-23 18:21:46
tags:
- 编码
- 面向对象
top: 16

---

This module implements specialized container datatypes providing alternatives to Python’s general purpose built-in containers, dict, list, set, and tuple.

> 官方文档：https://docs.python.org/3/library/collections.html

## namedtuple

工厂函数，用于创建具有命名字段的元组子类

- 语法

```python
namedtuple(typename, field_names, *, verbose=False, rename=False, module=None)
```

- Example

```python
# 导入namedtuple
>>> from collections import namedtuple
# 创建一个用户类，拥有name,age,sex属性
>>> User = namedtuple("User", ["name","age","sex"])
>>> user1 = User("as","22","男")
>>> user1
User(name='as', age='22', sex='男')
# 通过属性进行访问
>>> user1.name
'as'
>>> user1.age
'22'
>>> user1.sex
'男'
# 拆包
>>> name, age, sex = user1
>>> name, age, sex
('as', '22', '男')
# namedtuple转换为字典
>>> user1._asdict()
OrderedDict([('name', 'as'), ('age', '22'), ('sex', '男')])
# 初始化时也可以传入一个字典
>>> user_info_dict = {"name":"ansheng","age":"20","sex":"男"}
>>> User(**user_info_dict)
User(name='ansheng', age='20', sex='男')
# 传入一个可迭代的
>>> user_info_list = ["ansheng","20","女"]
>>> User(*user_info_list)
User(name='ansheng', age='20', sex='女')
>>> user_info_list = ["ansheng","20"]
>>> User(*user_info_list,"男")
User(name='ansheng', age='20', sex='男')
# _make方法
>>> User._make(["as", 20, "男"])
User(name='as', age=20, sex='男')
```

## deque

双端队列

- Example

```python
>>> from collections import deque
>>> users_deque = deque(["user1", "user2", "user3"], maxlen=10)
>>> users_deque.appendleft("user4")
>>> users_deque.append("user4")
>>> users_deque
deque(['user4', 'user1', 'user2', 'user3', 'user4'], maxlen=10)
```

## ChainMap

dict-like class for creating a single view of multiple mappings

- Example

```python
>>> from collections import ChainMap
>>> dict1 = {"a": "a", "b": "b"}
>>> dict2 = {"c": "c", "d": "d"}
>>> new_dict = ChainMap(dict1, dict2)
>>> new_dict.maps
[{'a': 'a', 'b': 'b'}, {'c': 'c', 'd': 'd'}]
>>> for key, value in new_dict.items():
...     print(key, value)
...
a a
b b
d d
c c
```


## Counter

统计元素出现的次数

- Example

```python
>>> from collections import Counter
# 拥挤英文字母出现的次数
>>> letters = ["A", "A", "B", "C", "A", "H", "D", "B"]
>>> letters_counter = Counter(letters)
>>> letters_counter.update(["A", "A"])
>>> letters_counter
Counter({'A': 5, 'B': 2, 'C': 1, 'H': 1, 'D': 1})
# 出现最多的前2个元素
>>> letters_counter.most_common(2)
[('A', 5), ('B', 2)]
# 统计字符串
>>> Counter("asdasdsczasdasdasdasd")
Counter({'s': 7, 'a': 6, 'd': 6, 'c': 1, 'z': 1})
```


## OrderedDict

dict subclass that remembers the order entries were added

- Example

```python
>>> from collections import OrderedDict
>>> user_dict = OrderedDict()
>>> user_dict["name"] = "As"
>>> user_dict["age"] = 18
>>> user_dict["sex"] = "男"
>>> user_dict
OrderedDict([('name', 'As'), ('age', 18), ('sex', '男')])
# 把name移动到最后
>>> user_dict.move_to_end("name")
>>> user_dict
OrderedDict([('age', 18), ('sex', '男'), ('name', 'As')])
# 移除最后一个元素
>>> user_dict.popitem()
('name', 'As')
>>> user_dict
OrderedDict([('age', 18), ('sex', '男')])
```

## defaultdict

当字典中 Key 不存在时，设置默认值

- 语法

```python
defaultdict(FUNC_NAME)
```

接受一个函数名称

- Code

统计列表中字母出现的次数

```python
from collections import defaultdict

letters = ["A", "A", "B", "C", "A", "H", "D", "B"]

data_dict = defaultdict(int)

for letter in letters:
    data_dict[letter] += 1
print(data_dict)
```

- Output

```plain
defaultdict(<class 'int'>, {'A': 3, 'B': 2, 'C': 1, 'H': 1, 'D': 1})
```

## UserDict

wrapper around dictionary objects for easier dict subclassing


## UserList

wrapper around list objects for easier list subclassing


## UserString

wrapper around string objects for easier string subclassing
