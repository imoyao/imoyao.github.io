---
title: Angular 中如何将 Object 或者 Array 按序排列？
date: 2020-03-06 20:53:25
tags:
- Angular
- 前端
categories:
- 工作日常
cover: /images/logos/angular.svg
---
{% note warning no-icon %}
**注意：**
Angular 不再提倡使用管道，因为
(a) 它们性能堪忧
(b) 它们会阻止比较激进的代码最小化(minification)。

无论是 filter 还是 orderBy 都需要它的参数引用对象型属性。这样的管道必然是非纯管道，并且 Angular 会在几乎每一次变更检测周期中调用非纯管道。

过滤、 特别是排序是昂贵的操作。 当 Angular 每秒调用很多次这类管道函数时，即使是中等规模的列表都可能**严重降低用户体验**。
**建议：**
把你的过滤和排序逻辑挪进组件本身。 组件可以对外暴露一个 filteredHeroes 或 sortedHeroes 属性，这样它就获得控制权，以决定要用什么频度去执行其它辅助逻辑。 你原本准备实现为管道，并在整个应用中共享的那些功能，都能被改写为一个过滤/排序的服务，并注入到组件中。
{% endnote %}

---

## 前言
写前端的时候难免遇到数据展示问题，比如 form 表单，在 [使用 FormBuilder 来生成表单控件](https://angular.cn/guide/reactive-forms#generating-form-controls-with-formbuilder) 时，当 input 输入框较多的时候，我们可能希望能够自主控制表单字段顺序，此时，则需要对表单字段进行排序。那么，如何实现呢？

## 使用内置 orderBy
 ```angular2html
 <li ng-repeat="item in items | orderBy:'color'">{{ item.color }}</li>
 ```
 参见[AngularJS orderBy 使用要点 - 佣工 7001 - 博客园](https://www.cnblogs.com/dajianshi/p/4484237.html)

## 没有 orderBy 怎么办
 从 Angular 开始 orderBy 不再支持，此时无法直接使用。
 update[附录：没有 FilterPipe 或者 OrderByPipe
](https://angular.cn/guide/pipes#appendix-no-filterpipe-or-orderbypipe)
### 使用开源包 ngx-order-pipe
如果不考虑性能问题，可以使用这样的方式：
 参见 [Angular 5+ Order Pipe](https://github.com/VadimDez/ngx-order-pipe)
这个包可以实现列表式数据的排序，具体用法参见文档。
注意：可能遇到`The pipe 'orderBy' could not be found`错误，这个可以翻阅 issue 解决，我自己的实践是放在使用的组件的上一层级目录下面。如图：
![](\images\Snipaste_2020-03-06_21-21-52.png)
### 自定义 pipe 造轮子
参见 [angular2 自定义 pipe ，orderby 实现排序_JavaScript_兰色的 fire-CSDN 博客](https://blog.csdn.net/u010564430/article/details/54097236)
### 如果返回的值是 Object 怎么办
1. 使用 KeyValuePipe 组件。参考[Angular 6 - KeyValue Pipe - *ngFor Loop through Object, Map example » grokonez](https://grokonez.com/frontend/angular/angular-6/angular-6-keyvalue-pipe-ngfor-loop-through-object-map-example "")
2. 将 Object 遍历，然后排序放到列表中，代码参见：
 ```angular
    app.filter('orderObjectBy', function() {
      return function(items, field, reverse) {
        var filtered = [];
        angular.forEach(items, function(item) {
          filtered.push(item);
        });
        filtered.sort(function (a, b) {
          return (a[field] > b[field] ? 1 : -1);
        });
        if(reverse) filtered.reverse();
          return filtered;
      };
    });
 ```

## 结语
 文章写出来了才翻到官方文档中的建议，所以这篇文章意义也不大了。不过还是做一个记录吧，这也说明*使用框架前先阅读官方文档*的必要性。

顺便参考一下怎么实现数组的排序[sort()方法实现对象数组的排序](https://segmentfault.com/a/1190000015961859)

## 参考链接
1. [javascript - Angular - Can't make ng-repeat orderBy work - Stack Overflow](https://stackoverflow.com/questions/19387552/angular-cant-make-ng-repeat-orderby-work)
2. [AngularJS Filter for Ordering Objects (Hashes) with ngRepeat](https://justinklemm.com/angularjs-filter-ordering-objects-ngrepeat/)