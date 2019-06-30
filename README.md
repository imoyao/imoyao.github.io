## 本分支主要存放站点的`sources`文件

来源[@砖用冰西瓜](http://www.jianshu.com/p/beb8d611340a)

具体的操作步骤：

克隆gitHub上面生成的静态文件到本地
```shell
git clone https://github.com/yourname/hexo-test.github.io.git
```
把克隆到本地的文件除了git的文件都删掉，找不到git的文件的话就到删了吧。不要用`hexo init`初始化。

将之前使用hexo写博客时候的整个目录（所有文件）搬过来。把该忽略的文件忽略了
```shell
touch .gitignore
```
- 创建一个叫hexo的分支
```shell
git checkout -b hexo
```
- 提交复制过来的文件到暂存区
```shell
git add --all
git commit -m "create hexo branch"
```
- 推送分支到github
```shell
git push --set-upstream origin hexo
```
到这里基本上就搞定了，以后再推就可以直接`git push`了，`hexo`的操作跟以前一样。

今后无论什么时候想要在其他电脑上面用hexo写博客，就直接把创建的分支克隆下来，`npm install`安装依赖之后就可以用了。

- 克隆分支的操作
```shell
git clone -b hexo https://github.com/yourname/hexo-test.github.io.git
```
因为上面创建的是一个名字叫hexo的分支，所以这里-b后面的是hexo，再把后面的gitHub的地址换成你自己的博客的地址就可以了。

## `LaTex` 在线公式编辑器

- [国内版](http://latex.91maths.com/)
- [国际版](http://latex.codecogs.com/eqneditor/editor.php)

## lint 工具

使用[lint-md](https://github.com/hustcc/lint-md) 检查并修复博客中的`md`文件