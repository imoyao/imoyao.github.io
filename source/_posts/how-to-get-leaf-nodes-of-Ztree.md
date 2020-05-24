---
title: 如何获取 Ztree 的所有叶子节点？
date: 2019-01-30 15:06:19
tags:
- zTree
- 前端

categories:
- 工作日常
---
使用`Ztree`时，`treeNode.children`只能获取到子节点，该如何拿到节点的叶子节点呢？

<!--more-->

## 创建初始化设置
```javascript
var setting = {
    data: {
        simpleData: {
            enable: true
        }
    },
    callback: {
        onCheck:onCheck,
    }
};
```

## 创建点击响应事件

```javascript
function onCheck(event, treeId, treeNode, clickFlag) {
        var treeObj = $(ELT).fn.zTree.getZTreeObj("datarecdirs");
        var str = "";
        str = getAllChildNodes(treeNode,str);
        // // 加上被选择节点自身
        // str = str + ',' + treeNode.id;
        // 去掉最前面的逗号
        var ids = str.substring(1, str.length);
        // 得到所有节点ID 的数组
        var idsArray = ids.split(',');
        // 过滤掉序列中的空元素 [1,2,'3',"", ''] >>> [1,2,'3']   (javascript 1.6 and above)
        var filterArr = idsArray.filter(function(n){return n});       
        // 得到节点总数量
        var leafNodesLen = filterArr.length;
        if(filterArr){
            var nodeChecked = treeNode.checked;
            if(nodeChecked){
                for (var i=0; i < leafNodesLen; i++) {
                    var idVal = filterArr[i];
                    var node = treeObj.getNodeByParam("id", idVal, null);
                    treeObj.setChkDisabled(node,true,false,true);
                }
            }else{
                for (var j=0; j < leafNodesLen; j++) {
                    idVal = filterArr[j];
                    // 按照id获取节点，see:https://www.oschina.net/question/222309_131001
                    node = treeObj.getNodeByParam("id", idVal, null);       // 注意：此处不可使用getNodeByTId()方法
                    treeObj.setChkDisabled(node,false,false,true);  //取消禁用时，影响到子节点
                }
                var nodes = treeObj.getCheckedNodes();
                console.log(nodes);
                if (nodes.length>0) {
                    for(var c=0;c<nodes.length;c++){
                        treeObj.checkNode(nodes[c],false,true);     //注意，此处不可使用cancelSelectedNode()
                    }
                }
            }
        }
    }
 
// 递归，获取所有子节点
function getAllChildNodes(treeNode,result){     // 获取节点的所有叶子节点
    if (treeNode.isParent) {
        var childrenNodes = treeNode.children;
        if (childrenNodes) {
            for (var i = 0; i < childrenNodes.length; i++) {
                result += ',' + childrenNodes[i].id;
                result = getAllChildNodes(childrenNodes[i], result);
            }
        }
    }
    return result;
}
```
{% label 注意 danger %}

> zTree 里严格区分了选中和勾选这两个概念，选中是指节点被选择背景颜色有变化，因此 cancelSelectedNode()只是把你选择的节点，变成不选择状态，也就是节点的背景色发生变化。
而勾选是指节点的勾选框被选中，你要将节点的勾选状态由勾选变为不勾选，就不能使用 cancelSelectedNode()方法，只能使用 checknode()方法！

## 参考来源

* [zTree 插件 - 获取当前选择节点下的全部子节点](https://blog.csdn.net/qq_15071263/article/details/82797734) 
* [为什么 cancelSelectedNode()取消不了节点的选中状态？](https://tieba.baidu.com/p/4157358359?red_tag=3393089686) 
