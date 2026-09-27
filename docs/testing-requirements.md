# Test Requirements

## 目的

RegScope 需要基于已有测试建立：

Test → Code

映射，并在代码变化后从测试集中选择需要执行的测试。

因此测试集不仅需要“可以运行”，还需要满足一定条件。

## 基本要求

### 1. 稳定的测试标识

每个测试需要具有稳定且可唯一识别的 Test ID。

例如：

tests/test_orders.py::test_create_order

RegScope 将使用 Test ID 建立和保存：

Test → Code

映射。

### 2. 测试尽量相互独立

单个测试应能够独立运行。

避免：

test_B 必须在 test_A 执行之后才能通过。

否则精准回归只选择部分测试时可能产生错误结果。

### 3. 必须具有明确断言

测试不能只是调用接口。

应通过 assert 等方式判断行为是否正确。

### 4. 测试之间应具有路径差异

不同测试应覆盖不同功能和代码路径。

例如：

test_create_order
→ create_order
→ calculate_price

test_cancel_order
→ cancel_order
→ restore_stock

这样代码修改后才存在“选择部分测试”的空间。

### 5. 同一 API 最好具有不同执行路径

例如：

POST /orders

可能包含：

- 正常下单
- 库存不足
- 优惠券订单
- 非法参数

这些测试可能执行不同代码路径，
有利于验证动态覆盖分析。

### 6. 测试结果需要稳定

在相同代码和环境下重复执行，
结果不应随机变化。

否则会影响后续 Evaluation。

## 后期评测要求

为了计算 Recall 等指标，
需要存在已知会暴露缺陷的测试。

这些缺陷可以来自：

- 人工构造 Bug
- Mutation Testing
- 真实 Bug Commit

从而建立：

Bug
→ Failing Tests

作为实验 Ground Truth。

Observation:
coverage 的 executed_lines 会包含 import、类定义、应用初始化等运行时噪音。

Example:
schemas.py 可能显示 100% covered，
但这并不代表当前测试真正验证了所有 schema 的业务意义。

Implication for RegScope:
后续不能直接把 raw executed_lines 当作 test → business code，
需要在 line → function 阶段或后续过滤阶段处理噪音。