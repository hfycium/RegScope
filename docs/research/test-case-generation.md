# Test Case Generation Research

## 1. 调研目的

RegScope 的核心问题是：

已有代码发生变化后，如何从测试集中选择真正需要重新执行的测试。

因此，在开发 RegScope 之前，需要明确：

* 测试用例从哪里获得；
* 是否需要人工编写；
* 是否可以自动生成；
* 如何兼顾低成本验证、真实性和工程化程度。

当前倾向不是只采用一种测试来源，而是随着项目成熟度逐步升级。

---

## 2. 阶段一：AI 构建可控测试集

### 用途

用于 RegScope 开发初期的低成本验证。

让 AI 为一个小型 FastAPI 被测系统构建：

* API；
* Service 调用关系；
* pytest 测试；
* 不同执行路径；
* 部分共享代码路径。

### 为什么这样做

初期的重点不是证明 RegScope 对真实世界所有项目都有效，而是快速验证：

Git Diff
→ Changed Function
→ Affected API
→ Selected Tests

这条核心链路能否跑通。

自己控制的测试系统具有以下优势：

* 结构简单；
* 调用关系已知；
* 测试覆盖关系可控；
* 出问题时容易 Debug；
* 可以主动设计适合精准回归实验的场景。

### 定位

仅作为 Controlled Dataset。

不能作为 RegScope 最终有效性的主要证据。

---

## 3. 阶段二：采用官方 / 权威项目已有测试

### 优先候选

FastAPI 官方 Full Stack FastAPI Template。

该项目本身包含：

* FastAPI 后端；
* pytest 测试；
* 数据库；
* 用户认证；
* CRUD；
* Coverage；
* CI。

### 用途

用于验证：

RegScope 是否能够脱离自己构建的 Demo，
接入具有真实工程结构的 FastAPI 项目。

### 价值

相较于自己构造的数据：

* 项目来源更加权威；
* 测试并非为了迎合 RegScope 而设计；
* 更接近真实项目；
* 可以减少“自己出题自己考试”的问题。

后续还可以继续寻找其他具有稳定 pytest 测试集的 FastAPI 开源项目。

---

## 4. 阶段三：基于 OpenAPI 自动生成测试

### 重点候选：Schemathesis

FastAPI 可以自动产生 OpenAPI Schema。

因此可以形成：

FastAPI
→ OpenAPI Schema
→ Schemathesis
→ 自动生成 API Tests

Schemathesis 可以根据 API Schema 自动生成大量不同输入，包括：

* 正常输入；
* 边界输入；
* 非法输入；
* Property-Based Tests；
* 多 API 状态流程。

并且可以直接与 pytest 集成。

### 为什么这个方向适合 RegScope

它可以让测试集构建从：

人工编写几十个测试

逐渐变成：

发现 API
→ 自动读取 Schema
→ 自动生成测试
→ 自动运行
→ 建立 Test → Code Mapping

这更加符合 RegScope 希望体现的工程化与自动化能力。

---

## 5. 一个需要重点验证的问题

Schemathesis 的 pytest 测试通常以 API Operation 为稳定测试项，例如：

test_api[POST /orders]

但在这个测试内部，
Hypothesis 会动态生成多组具体输入。

因此需要后续实验确定 RegScope 的测试粒度：

方案 A：

API Operation 级

POST /orders
→ Coverage

方案 B：

具体 Generated Case 级

POST /orders + Input #1
→ Coverage

POST /orders + Input #2
→ Coverage

前者更加稳定、实现成本低。

后者更加精细，但需要解决动态测试 Case 的稳定标识、持久化和复现问题。

该问题在真正接入 Schemathesis 时再进行技术选型。

---

## 6. 当前推荐路线

V0：

AI 构建小型 FastAPI SUT + pytest。

目标：

快速、低成本跑通 RegScope 核心链路。

↓

中期：

接入 FastAPI 官方 Full Stack Template 等真实项目已有测试。

目标：

验证 RegScope 不依赖人为设计的 Demo。

↓

后期：

接入 OpenAPI + Schemathesis。

目标：

实现自动发现 API 和自动扩充测试集，
进一步体现平台自动化和工程化能力。

最终测试来源不应与 RegScope 核心算法绑定。

RegScope 应能够接受：

AI 构建测试
+
项目已有 pytest
+
自动生成 API 测试

并统一进入后续的：

Test → Code Mapping
→ Change Impact Analysis
→ Regression Test Selection
→ Evaluation
流程。

## 7. 当前结论

当前不计划自行研发一套测试生成算法。

优先策略：

初期使用 AI 降低验证成本；

中期使用官方 / 权威项目提高可信度；

后期复用成熟 OpenAPI 自动测试工具提高工程化程度。

测试生成是 RegScope 的输入能力之一，
而不是 RegScope 的核心研究问题。
