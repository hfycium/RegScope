# Related Tools Research

本文记录 RegScope 开发过程中调研过的相关工具和项目。

这些工具目前仅作为参考或候选方案，
不代表 RegScope 已决定采用。

---

## coverage.py

方向：

Python 代码覆盖率采集。

与 RegScope 的关系：

可以用于建立：

Test → Code

映射。

值得关注的能力：

- branch / line coverage
- dynamic context
- 可以区分不同 test function 的覆盖信息

可能用于：

V1 动态执行映射。

状态：

重点候选。

---

## pytest-testmon

方向：

基于代码变化选择需要重新运行的 pytest 测试。

与 RegScope 的关系：

与精准回归目标高度相关。

可以作为：

- 竞品参考
- Baseline

重点研究：

它如何保存 Test → Code 依赖，
以及如何根据代码变化选择测试。

RegScope 需要明确自己与它的区别：

- 接口级影响分析
- 静态 + 动态融合
- 可解释影响路径
- Evaluation

状态：

重点竞品 / Baseline。

---

## Schemathesis

方向：

基于 OpenAPI 自动生成 API 测试。

特点：

- 可以读取 FastAPI OpenAPI Schema
- 自动生成正常、边界和非法输入
- 支持 Stateful API Testing
- 可以与 pytest 集成

与 RegScope 的关系：

不属于精准回归核心算法。

未来可用于：

自动扩充 Test Corpus。

状态：

后期实验候选。

---

## Pynguin

方向：

自动生成 Python 单元测试。

特点：

针对 Python Module / Function 自动搜索和生成测试。

与 RegScope 的关系：

偏代码级测试生成，
与 RegScope 的 API 级定位不完全一致。

状态：

参考。

---

## RESTler

方向：

基于 OpenAPI 的 REST API 自动测试 / Fuzzing。

特点：

可以分析 API 之间的 producer-consumer 关系。

例如：

POST /users
→ user_id
→ GET /users/{user_id}

与 RegScope 的关系：

其 API 依赖分析思想值得参考，

但主要目标是：

API Fuzzing / Reliability / Security Testing。

状态：

研究参考。

---

## BugsInPy

方向：

Python 真实缺陷 Benchmark。

提供：

Buggy Version
↔
Fixed Version

以及相关测试。

与 RegScope 的关系：

后期可能用于验证精准回归算法，
特别是 Recall / Fault Detection。

限制：

不是专门针对 FastAPI / REST API 项目。

状态：

V5/V6 候选实验数据。