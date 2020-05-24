---
title: 🐍PyTricks | 如何更新一个嵌套字典的值？
date: 2019-09-25 10:35:58
tags:
- Python
categories:
- 🐍PyTricks
cover: /images/Python/Python-snake.jpg
---

```python
import collections

def update_nested_dict(orig_dict, new_dict):
    """
    更新嵌套字典
    params = {'state':'1','message':'9527','result':{'hello':'world','foo':'bar','age':32}}
    new_dict = {'name':'Peter'}
    {'state': '1', 'message': '9527', 'name': 'Peter', 'result': {'age': 32, 'foo': 'bar', 'hello': 'world'}}
    ---
    new_dict = {'result':{'foo':'baz'}}
    {'state': '1', 'message': '9527', 'result': {'age': 32, 'foo': 'baz', 'hello': 'world'}}
    new_dict = {'result':{'name':'Peter'}}
    {'state': '1', 'message': '9527', 'result': {'age': 32, 'foo': 'bar', 'hello': 'world', 'name': 'Peter'}}
    ---
    new_dict = {'result':{'hobbies':['reading','fishing','play game']}}
    {'state': '1', 'message': '9527', 'result': {'age': 32, 'foo': 'bar', 'hello': 'world', 'hobbies': ['reading', 'fishing', 'play game']}}
    ---
    params = {'state':'1','message':'9527','result':{'hello':'world','foo':'bar','age':32,'hobbies':['coding']}}
    new_dict = {'result':{'hobbies':['reading','fishing','play game']}}
    {'state': '1', 'message': '9527', 'result': {'age': 32, 'foo': 'bar', 'hello': 'world', 'hobbies': ['coding', 'reading', 'fishing', 'play game']}}

    """
    for key, val in new_dict.iteritems():
        if isinstance(val, collections.Mapping):
            tmp = update_nested_dict(orig_dict.get(key, {}), val)
            orig_dict[key] = tmp
        elif isinstance(val, list):
            orig_dict[key] = (orig_dict.get(key, []) + val)
        else:
            orig_dict[key] = new_dict[key]
    return orig_dict
```
## 参考来源

[Update value of a nested dictionary of varying depth](https://stackoverflow.com/questions/3232943/update-value-of-a-nested-dictionary-of-varying-depth)