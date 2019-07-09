---
title: flask-sqlalchemy中的多对多关系模型问题记录
date: 2019-07-03 20:08:21
tags:
---


## 问题记录

```bash
sqlalchemy.exc.InvalidRequestError: One or more mappers failed to initialize - can't proceed with initialization of other mappers. Triggering mapper: 'mapped class Article->iy_article'. Original exception was: Error creating backref 'articles' on relationship 'Article.tags': property of that name exists on mapper 'mapped class Tag->iy_tag'
```
出现这个错误是因为两个关系表中互相定义，意思是你的代码中可能同时包含下面的语句：

```python
# class Article:

tags = db.relationship('Tag', secondary=posts_tags_table, backref=db.backref('articles', lazy='dynamic'),
                               lazy="dynamic")
# Class Tag:                            
articles = db.relationship('Article', secondary=posts_tags_table,
    #                            back_populates='tags')
```
### 解释：

当您使用`backref`时，`SQLAlchemy`会自动创建向后关联，因此它（backref）**只应该**在关系的一侧使用。所以应该删除上面其中的一句定义。

参见这里  
[when-do-i-need-to-use-sqlalchemy-back-populates](https://stackoverflow.com/questions/39869793/when-do-i-need-to-use-sqlalchemy-back-populates)