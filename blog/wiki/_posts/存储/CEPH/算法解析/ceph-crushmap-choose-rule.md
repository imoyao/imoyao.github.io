---
title: ceph crushmap choose 规则分析.md
toc: true
date: 2020-05-23 11:02:28
tags:
- ceph

---
# 1. Placement Rules
## 1.1 模拟代码
```shell
tack(a)
choose
    choose firstn {num} type {bucket-type}
    chooseleaf firstn {num} type {bucket-type}
        if {num} == 0, choose pool-num-replicas buckets (all available).
        if {num} > 0 && < pool-num-replicas, choose that many buckets.
        if {num} < 0, it means pool-num-replicas - {num}.
emit
```

## 1.2 Placement Rules 的执行流程
1. take 操作选择一个 bucket, 一般是 root 类型的 bucket.
2. choose 操作有不同的选择方式，其输入都是上一步的输出：
    a. choose firstn 深度优先选择出 num 个类型为 bucket-type 个的子 bucket.
    b. chooseleaf 先选择出 num 个类型为 bucket-type 个子 bucket,然后递归到叶节点，选择一个 OSD 设备：
      - 如果 num 为 0， num 就为 pool 设置的副本数。
      - 如果 num 大于 0， 小于 pool 的副本数，那么久选择出 num 个。
      - 如果 num 小于 0，就选择出 pool 的副本数减去 num 的绝对值。
3. emit 输出结果

# 2. 实战模拟演练
## 2.1 演练列表
ruleset_id | choose num |  chooseleaf_num | 结论 |
---|---|---|---|
0 | firstn 0 type pod | firstn 0 type rack | pg 三个副本分布: <br/> - 同一个 pod 下 <br/> - 不同 rack 下 |
1 | firstn 1 type pod | firstn 0 type rack | pg 三个副本分布: <br/> - 同一个 pod 下 <br/> - 不同 rack 下 |
2 | firstn 2 type pod | firstn 0 type rack | pg 三个副本分布: <br/> - 同一个 pod 下 <br/> - 不同 rack 下 |
3 | firstn 3 type pod | firstn 0 type rack | pg 三个副本分布: <br/> - 同一个 pod 下 <br/> - 不同 rack 下 |
4 | firstn 4 type pod | firstn 0 type rack | pg 三个副本分布: <br/> - 同一个 pod 下 <br/> - 不同 rack 下 |
5 | firstn 1 type pod | firstn 1 type rack | pg 三个副本分布: <br/> - 同一个 pod 下 <br/> - 不同 rack 下 |
6 | firstn 1 type pod | firstn 2 type rack | pg 三个副本分布: <br/> - 同一个 pod 下 <br/> - 不同 rack 下 |
7 | firstn 1 type pod | firstn 3 type rack | pg 三个副本分布: <br/> - 同一个 pod 下 <br/> - 不同 rack 下 |
8 | firstn 1 type pod | firstn 4 type rack | pg 三个副本分布: <br/> - 同一个 pod 下 <br/> - 不同 rack 下 |
9 |  | firstn 0 type pod | pg 三个副本分布: <br/> - 不同 pod 下 |
10 |  | firstn 0 type rack | pg 三个副本分布: <br/> - 不同 rack 下 |
