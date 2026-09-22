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
```
RegScope/
│
├── README.md
│   给别人看：现在项目是什么状态
│
├── PROJECT.md
│   管项目定义、MVP和总体边界
│
├── ROADMAP.md
│   管版本推进顺序
│
├── TASK.md
│   管现在这一小步
│
├── AGENTS.md
│   管AI行为
│
├── docs/
│   └── decisions/
│       只记录真正重要的技术决策
│
└── src/

PROJECT
“我们去哪？”

↓

ROADMAP
“分几站去？”

↓

TASK
“现在走哪一步？”

↓

AGENTS
“AI走路的时候遵守什么规则？”

↓

README
“目前已经走到哪里了？”
```
