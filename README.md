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

🚧 Under Development

当前阶段：V0 — 被测服务与基础测试体系

## Roadmap

见 [ROADMAP.md](./ROADMAP.md)

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
