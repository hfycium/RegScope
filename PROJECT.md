# RegScope

## 1. 项目定位

面向接口服务的、可解释的混合式变更影响分析与精准回归平台。

核心关键词：

- 接口级
- 静态 + 动态
- 可验证


## 2. 要解决的问题

代码发生变更后：

1. 哪些函数受到影响？
2. 哪些 API 受到影响？
3. 哪些测试必须重新执行？
4. 如何证明减少测试数量后没有明显增加漏测？


## 3. 核心链路

Git Diff
→ Changed Function
→ Call Graph
→ Affected API
→ Coverage Mapping
→ Selected Tests
→ Evaluation


## 4. MVP

第一版只支持：

- Python
- FastAPI
- pytest
- 单仓库分析（一次只分析一个目标仓库，不做跨仓库依赖分析）
- Git commit / diff
- 函数级变更分析
- API 级影响分析
- per-test coverage
- 回归测试选择
- Recall / Reduction Ratio / Time


## 5. 暂不做

- 多语言
- UI 自动化
- 分布式执行
- CI 平台完整集成
- AI 自动生成测试
- 大模型故障归因
- 企业级权限系统

## 6. 已确定技术边界

当前确定：

- Python
- FastAPI
- pytest
- coverage.py
- Git

静态分析候选：

- Python AST
- Tree-sitter（是否需要后续验证）

持久化：

- MVP 初期优先使用最简单方案
- 是否需要 MySQL，在产生真实持久化需求后决定

缓存：

- MVP 默认不使用 Redis
- 出现明确性能或缓存需求后再评估

## 7. 项目成功标准

必须能够回答：

- 为什么选择这个测试？
- 为什么没有选择那个测试？
- 测试减少了多少？
- 是否出现漏测？
- 比简单路径匹配好在哪里？