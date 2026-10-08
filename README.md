# RegScope

> Change-aware regression test selection for API services.

RegScope 是一个面向接口服务的、
基于代码变更影响分析的精准回归测试平台。

核心目标：

Git Diff
→ Changed Function
→ Affected API
→ Selected Tests

项目重点研究：

- 静态变更影响分析
- 运行时测试覆盖关系
- Static + Dynamic 混合测试选择
- Regression Test Selection 的效果评估

## Status

✅ End-to-end MVP implemented; further validation and analysis coverage remain.

当前版本支持 Python / FastAPI / pytest 项目的本地分析：从 Git 变更识别函数与受影响 API，结合测试覆盖映射选择回归测试，并生成评估结果。

验证分为两组：小型合成 fixture 有 10 个测试、4 个受控故障变更，Hybrid 命中 4/4；真实 FastAPI 模板基线有 58 个测试，5 个受控故障分别位于 `items.py`、`users.py` 和 `login.py`，Hybrid 命中 5/5。真实仓库两例新增场景分别选择 5/58 和 45/58 项，说明缩减幅度依变更而异。样本仍小，不能据此推断普遍效果或端到端提速。详见[真实仓库实验](./docs/experiments/full-stack-fastapi-template.md)。

当前平台测试为 **64 项通过**。早期合成实验和实现记录见 [MVP 迭代记录](./docs/iterations/001-end-to-end-mvp.md)、[初始 MVP 实验](./docs/experiments/mvp-baseline.md) 和 [扩展对照实验](./docs/experiments/comparative-evidence.md)。

### 当前边界与待完成项

- 静态分析基于 Python AST，调用图仅覆盖有限的直接调用场景；不支持完整的动态调用、依赖注入和跨仓库分析。
- 合成与真实仓库实验均提供了策略对照；当前未证明端到端提速，覆盖采集开销及重复计时仍需评估。
- OpenSpec 任务 3.5 的影响分析边界测试已补齐：覆盖直接调用、no-impact 变更、嵌套函数、async endpoint 和保守回退行为。
- 目前是本地 CLI 原型，尚无 UI 或生产部署。FastAPI 模板侧已有可选 GitHub Actions 工作流草案；发布 RegScope 版本、配置目标仓库变量并完成托管端验证后，才能启用该集成。

## Roadmap

见 [ROADMAP.md](./ROADMAP.md)

## 项目 Wiki

快速了解项目目标、核心流程、实现边界和实验结果： [RegScope 项目 Wiki](./docs/wiki/regscope.md)

## 仓库划分

RegScope 平台代码与被测服务分别放在两个仓库，互不包含：

```text
F:\大学\大三上\
│
├── RegScope/                 平台仓库：分析逻辑与项目文档
│   ├── README.md             给别人看：现在项目是什么状态
│   ├── PROJECT.md            管项目定义、MVP 和总体边界
│   ├── ROADMAP.md            管版本推进顺序
│   ├── TASK.md               管现在这一小步
│   ├── AGENT.md              管 AI 行为
│   ├── docs/
│   │   ├── decisions/        只记录真正重要的技术决策
│   │   └── research/         调研记录
│   └── src/                  平台代码（V1 开始写）
│
└── order-service/            被测服务仓库：用户、商品、订单
    ├── app/                  FastAPI 服务，分 api / service / repository 三层
    └── tests/                pytest 接口测试
```

被测服务不在 RegScope 目录内，RegScope 通过路径参数指向它。
这样以后分析别的项目时，不用改动 RegScope 自身结构。

文档的阅读顺序：

```text
PROJECT   “我们去哪？”
   ↓
ROADMAP   “分几站去？”
   ↓
TASK      “现在走哪一步？”
   ↓
AGENT     “AI 走路的时候遵守什么规则？”
   ↓
README    “目前已经走到哪里了？”
```
