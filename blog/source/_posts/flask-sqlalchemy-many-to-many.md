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

```bash
sqlalchemy.orm.exc.StaleDataError: DELETE statement on table 'iy_post_tags' expected to delete 4 row(s); Only 24 were matched.
```
### 处理过程
书上说“将某个Book的Writer属性设置为None,就会解除与Writer对象的关系。”
```python
post_obj = Article.query.filter(Article.post_id == post_id).one()
if post_obj:
    body_id = post_obj.body_id
    post_obj.tags = None
    db.session.commit()
```
失败！！！

再次参考[How to delete a Many-to-Many relationship in Flask-SQLAlchemy](https://seagullbird.xyz/posts/how-to-delete-many-to-many-in-sqlalchemy/)
作者提到可能是因为对数据手动处理的问题，TODO：验证！

还有[这里](https://stackoverflow.com/questions/36002638/how-to-fix-sqlalchemy-sawarning-delete-statement-on-table-expected-to-delete-1)是修改表结构

[这里](https://stackoverflow.com/questions/41941273/deleting-from-a-sqlalchemy-many-to-many-matches-the-wrong-number-of-rows)
```python
db.PrimaryKeyConstraint('tag_id', 'post_id')
```
出现这个问题，可能是因为删除主键字段的时候，tags含有对post_id的引用。
参见[这里](https://groups.google.com/forum/#!topic/sqlalchemy/vfoTsQkqfHI)