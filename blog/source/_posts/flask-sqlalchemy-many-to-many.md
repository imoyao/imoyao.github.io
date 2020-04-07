---
title: flask-sqlalchemy 中的多对多关系模型问题记录
date: 2019-07-03 20:08:21
tags:
- Flask
- SqlAlchemy

categories:
- 工作日常
---

## 问题

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
    #                            back_populates='tags'
)
```
### 解释

当您使用`backref`时，`SQLAlchemy`会自动创建向后关联，因此它（`backref`）**只应该**在关系的一侧使用。所以应该删除上面其中的一句定义。

参见这里👉 [when-do-i-need-to-use-sqlalchemy-back-populates](https://stackoverflow.com/questions/39869793/when-do-i-need-to-use-sqlalchemy-back-populates)

## 问题
```bash
sqlalchemy.orm.exc.StaleDataError: DELETE statement on table 'iy_post_tags' expected to delete 4 row(s); Only 24 were matched.
```
### 处理过程
出现这个问题原因是在多对多关系的关联表中，出现了重复数据。
书上说
> 将某个 Book 的 Writer 属性设置为 None,就会解除与 Writer 对象的关系。

```python
post_obj = Article.query.filter(Article.post_id == post_id).one()
if post_obj:
    body_id = post_obj.body_id
    post_obj.tags = None
    db.session.commit()
```
失败！😞

再次参考👉 [How to delete a Many-to-Many relationship in Flask-SQLAlchemy](https://seagullbird.xyz/posts/how-to-delete-many-to-many-in-sqlalchemy/)
作者提到可能是因为对数据手动处理的问题。
### 验证

查询数据表中是否存在重复数据：
```sql
mysql> delete from iy_post_tags where post_id=26;
Query OK, 2 rows affected (0.22 sec)

mysql> select * from iy_post_tags;
+---------+--------+
| post_id | tag_id |
+---------+--------+
|      20 |      7 |
|      21 |      7 |
|      22 |      7 |
|      23 |      7 |
|      24 |      7 |
|      24 |      7 |
|      20 |      7 |
|      25 |      7 |
|      27 |      7 |    -- 注意这两行，表中出现同一篇文章，标签相同记录两次的情况，此时删除操作就会报错
|      27 |      7 |
+---------+--------+

```
的确存在重复数据，可以手动删除。

如果无法删除，可以参考[这里](https://stackoverflow.com/questions/36002638/how-to-fix-sqlalchemy-sawarning-delete-statement-on-table-expected-to-delete-1)的方案：修改表结构，解除确认删除。

### 利用代码限制永久解决

利用主键唯一约束，在创建中间表的时候进行限制
```python
# 设置： primary_key=True
article_tag_rel = sa.Table('article_tag_rel', Base.metadata,
    sa.Column('tag_id', sa.Integer, ForeignKey('tag.id'), primary_key=True),
    sa.Column('article_id', sa.Integer, ForeignKey('article.id'), primary_key=True)
)
```
```python
# 上面的一种简便写法
import db
posts_tags_table = db.Table('iy_post_tags', db.Model.metadata,
                            db.Column('post_id', db.Integer, db.ForeignKey('iy_article.post_id')),
                            db.Column('tag_id', db.Integer, db.ForeignKey('iy_tag.id')),
                            db.PrimaryKeyConstraint('tag_id', 'post_id')
                            )
```
- 参见[这里](https://github.com/kvesteri/sqlalchemy-continuum/issues/65)
- 还有[这里](https://stackoverflow.com/questions/36002638/how-to-fix-sqlalchemy-sawarning-delete-statement-on-table-expected-to-delete-1)是修改表结构；
- [这里](https://stackoverflow.com/questions/41941273/deleting-from-a-sqlalchemy-many-to-many-matches-the-wrong-number-of-rows)

出现这个问题，可能是因为删除主键字段的时候，`tags` 含有对 `post_id` 的引用。
具体讨论参见[这里](https://groups.google.com/forum/#!topic/sqlalchemy/vfoTsQkqfHI)

{%blockquote Robert A. Heinlein,《时间足够你爱》%}
A human being should be able to change a diaper, plan an invasion, butcher a hog, conn a ship, design a building, write a sonnet, balance accounts, build a wall, set a bone, comfort the dying, take orders, give orders, cooperate, act alone, solve equations, analyze a new problem, pitch manure, program a computer, cook a tasty meal, fight efficiently, die gallantly. Specialization is for insects.

一个人应该能够换尿布，策划战争，杀猪，开船，设计房子，写十四行诗，结算账户，砌墙，接脱臼的骨头，安慰濒死的人，服从命令，发布号令，携手合作，独立行动，解数学方程，分析新问题，铲粪，电脑编程，做出可口的饭，善打架，勇敢地死去。只有昆虫才囿于一门。
{%endblockquote%}
