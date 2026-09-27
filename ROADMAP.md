# RegScope Roadmap

## V0 — 建立被测系统

### 这一版解决什么问题

RegScope 以后需要分析一个真实的后端项目。

所以第一步先做一个足够小、但具有真实结构的 FastAPI 服务，
作为后续所有实验的“被测对象”。

这一阶段暂时不做精准回归。

### 要做出的东西

建立一个简单订单系统，包含：

- 用户
- 商品
- 订单

大约 10~15 个 API。

代码至少包含基本分层：

API / Router
↓
Service
↓
Repository / Data

并使用 pytest 编写接口测试。

### 我需要在这一版学会

HTTP 请求最基本概念

FastAPI 中：
- API / Endpoint 是什么
- Router 是什么
- Service 是什么

pytest 中：
- 一个测试是怎么运行的
- assert 是什么
- fixture 是什么

暂时不用深入学习框架原理。

### 完成标准

能够启动 FastAPI 服务。

能够访问例如：

POST /orders

GET /orders/{id}

能够运行：

pytest

并且所有测试通过。

不同测试之间不会因为运行顺序不同而失败。

---

## V1 — 知道测试执行过哪些代码

### 这一版解决什么问题

现在虽然有很多测试，

但 RegScope 不知道：

test_order_create

到底执行过哪些函数。

这一版建立：

Test
→ Code

的关系。

### 示例

运行：

test_order_create

记录它执行了：

order_service.create_order()

price_service.calculate_price()

inventory_service.check_stock()

最终能够查询：

test_order_create
→ create_order
→ calculate_price
→ check_stock

### 我需要在这一版理解

什么叫：

代码覆盖率

函数调用

运行时信息

pytest 执行测试的大致过程

### 完成标准

运行测试后，

系统能够保存：

test → function

的映射。

并能够根据一个测试名称查询它执行过哪些函数。

---

## V2 — 找到代码发生了什么变化

### 这一版解决什么问题

V1 已经知道：

测试运行了什么代码。

但现在还不知道：

这次提交到底修改了什么。

因此这一版处理：

Git Diff
→ Changed Function

### 示例

修改：

price_service.py

Git diff 发现：

calculate_price()

发生变化。

系统输出：

changed file:
price_service.py

changed function:
calculate_price

### 我需要在这一版理解

Git commit

Git diff

函数在源代码中的位置

如何根据 diff 判断修改落在哪个函数里

### 完成标准

给定两个 Git commit，

系统能够输出：

Changed Files

Changed Functions。

---

## V3 — 从修改函数找到受影响 API

### 这一版解决什么问题

现在已经知道：

calculate_price() 被修改了。

但测试人员真正关心的是：

哪些接口可能受到影响？

因此建立：

Changed Function
↓
Caller
↓
Service
↓
Endpoint

### 示例

calculate_price
↑
create_order
↑
POST /orders

最终输出：

Changed Function:
calculate_price

Affected API:
POST /orders

Impact Path:

POST /orders
→ create_order
→ calculate_price

### 我需要在这一版理解

函数调用关系

Caller / Callee

调用图

FastAPI Endpoint 和 Python 函数之间的关系

### 完成标准

修改一个 Service 函数后，

系统能够找到至少一个受影响 API，

并给出：

为什么认为它受影响的调用路径。

---

## V4 — 精准选择测试

### 这一版解决什么问题

现在已经有两类信息：

静态分析：

Changed Function
→ Affected API

动态信息：

Test
→ Executed Function

将两者结合，

决定本次修改应该运行哪些测试。

### 示例

calculate_price 被修改。

系统发现：

POST /orders
受到影响。

历史运行记录发现：

test_order_create
test_order_discount

覆盖相关代码。

因此输出：

Selected Tests:

test_order_create
test_order_discount

### 完成标准

给定一次 Git 修改，

系统可以自动输出：

Changed Functions

Affected APIs

Selected Tests

并解释测试为什么被选择。

---

## V5 — 验证 RegScope 是否真的有效

### 这一版解决什么问题

不能只证明系统“能跑”。

还需要证明：

精准回归是否真的能够减少测试，
同时尽量不漏掉问题。

### 对比方法

Full Regression

Path Match

Dynamic Coverage Only

RegScope Hybrid

### 指标

Recall

Reduction Ratio

Regression Time

### 我需要理解

为什么精准回归可能漏测试

Recall 是什么

Reduction Ratio 是什么

Baseline 是什么

### 完成标准

能够运行一组实验，

输出类似：

Full Regression:
100 tests

RegScope:
32 tests

Reduction:
68%

Fault Recall:
100%

并能够解释结果。

---

## V6 — 增强实验

在核心系统完成以后再考虑。

可能加入：

Mutation Testing

少量人工构造真实缺陷

更复杂调用关系

缓存 / 异步调用等场景

这一阶段不属于 MVP。


## 测试输入与被测系统

RegScope 不负责从零生成完整测试集。

核心输入是已有的、可独立执行的 pytest 测试。

测试用例应尽量满足：

- 每个测试具有稳定标识
- 测试之间尽量相互独立
- 包含明确断言
- 不同测试覆盖不同执行路径
- 能建立稳定的 test → code mapping

RegScope 与测试来源解耦。

测试可以来自：

1. 项目已有 pytest 测试
2. RegScope 自带的小型可控 Demo
3. 外部真实 FastAPI 项目
4. 后续通过 OpenAPI / Schemathesis 等方式自动生成或扩充的测试

自动生成测试不是 RegScope MVP 的核心能力。
RegScope 的核心问题是：

已有测试集
→ 代码发生变化
→ 识别受影响范围
→ 选择需要重新执行的测试
→ 验证选择效果

---

## 延后评估 — RepoMind AST 能力复用

当前 V1 使用 Python 标准库 `ast` 完成最小的“覆盖率行号 → 函数标识”映射，目的是先理解输入、输出与误差边界，不提前耦合其他项目。

在 V3 之后、扩展调用关系与跨文件符号解析前，评估是否复用 RepoMind 中基于 Tree-sitter 的 repomap、relation processor 与 symbol resolver。评估重点是：依赖成本、Python/FastAPI 解析准确性，以及是否能替代当前 MVP 而不破坏已有测试与映射格式。
