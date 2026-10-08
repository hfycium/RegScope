# RegScope 项目 Wiki

> 面向 Python / FastAPI 服务的变更影响驱动回归测试选择原型。

## 这是什么

RegScope 接收一个目标 Git 仓库和两个 commit，分析代码变更可能影响的 API，再结合 pytest 测试的历史代码覆盖记录，给出建议重跑的测试及选择依据。

目标业务场景是 PR 回归：减少不必要的测试执行，让开发者更快收到反馈。当前版本是本地 CLI 原型，尚未接入 CI，也没有真实团队使用数据；因此它验证了技术流程，不代表已经证明实际业务收益。

## 为什么需要它

全量回归测试会随着项目规模增长而变慢。只按改动文件选测试又比较粗：一个 API 可能通过多层调用使用另一个文件中的函数，文件匹配未必能表示这种影响关系。

RegScope 尝试把两类信息结合起来：

- 静态影响分析：从 Git diff 定位改动函数，并沿可解析的调用关系追到 API。
- 动态覆盖映射：记录每个 pytest 用例实际执行过哪些应用函数。

交集结果用于选择候选测试。当前实现是可解释的原型算法，不是完整 Python 调用图，也没有证明优于所有常见选测方法。

## 一次分析如何工作

```text
目标仓库 + base/head commit
        │
        ├── pytest + coverage.py ──> test ID → 执行过的 app 函数
        │
        └── Git diff + Python AST ──> 改动函数 → 可能受影响的 API
                                      │
                                      ▼
                             覆盖映射与影响范围求交
                                      │
                                      ▼
                    selected tests + 选择理由 + 评估报告
```

主要阶段：

1. **发现测试**：用 pytest 收集稳定的 node ID，例如 `tests/test_orders.py::test_create_order`。
2. **采集覆盖**：逐个运行测试，通过 coverage.py 记录执行行，再用 AST 将行映射到函数。
3. **分析变更**：用 Git 比较 base 和 head 的改动行，并映射到 head 代码中的函数。
4. **追踪 API 影响**：发现 FastAPI 路由和有限范围内的直接调用路径。
5. **选择并评估**：选择覆盖了改动函数或相关 API 入口的测试，输出 JSON 和 Markdown 结果。

## 关键实现

| 模块 | 职责 |
| --- | --- |
| `test_discovery.py` | 发现 pytest node ID，并解析目标 Python 解释器 |
| `coverage_collector.py` | 逐测试调用 pytest 和 coverage.py，保存覆盖映射 |
| `function_mapper.py`、`coverage_mapper.py` | 将覆盖行转换成应用函数 ID |
| `git_diff.py`、`change_mapper.py` | 解析 commit 差异，将改动行映射到函数或模块级变更 |
| `static_analysis.py`、`impact_analysis.py` | 发现 FastAPI endpoint、构造有限调用图并输出影响路径 |
| `selector.py` | 组合改动影响与测试覆盖，生成所选及未选测试和理由 |
| `evaluation.py`、`experiment.py` | 评估选中测试；比较文件级、函数级和混合策略 |
| `cli.py`、`pipeline.py` | 提供 `run` 命令并串起完整流程 |

### 保守回退

如果变更落在无法安全映射到函数的模块级代码，或影响分析给出 warning，选择器会退回执行全部已发现测试。这样会减少优化收益，但避免在证据不足时假装选得很准。

**空选择已有安全处理。** 对实际变更没有匹配测试时，选择器会保守地选择全量测试；评估阶段也会阻止空列表意外触发 pytest 自动发现。对照实验中的空基线则会明确标为 0 个候选并跳过执行。

## 技术栈与边界

- Python 3.12、标准库 `ast`、Git
- pytest、第三方 `coverage.py`
- FastAPI 作为目标服务类型；RegScope 不负责启动目标服务
- JSON 和 Markdown 本地结果文件；无数据库、Web UI 或 CI Action

当前静态分析识别直接声明的 `@app` / `@router` 路由，并支持部分同模块调用、`self.method()` 和带类型标注参数的方法调用。复杂依赖注入、动态分派、别名、继承及跨仓库调用不在覆盖范围内。源代码分析聚焦目标项目的 `app/` Python 文件。

## 运行示例

在 RegScope 仓库根目录执行。目标 Python 环境需安装 pytest 和 coverage.py；示例复用本地 `order-service` 的虚拟环境。

```powershell
$env:PYTHONPATH = "src"
& .\.venv\Scripts\python.exe -m regscope.cli run `
  ..\_regscope-fixture `
  9047fa4 `
  4262c0c `
  --python ..\order-service\.venv\Scripts\python.exe `
  --known-failing tests/test_orders.py::test_create_order_applies_threshold_cut_after_discounts `
  --output .pytest-tmp\regscope-wiki-demo
```

命令会在输出目录生成覆盖数据、`impact.json`、`selection.json`、`evaluation.json` 和 `evaluation.md`。当前工具从目标目录的工作树读取源码，因此运行时应确保工作树检出到指定的 head commit；现有 CLI 尚未自动校验这一点。

需要复用已有覆盖映射时，可在 `run` 命令中添加 `--mapping <coverage-mapping.json>`。若用于 PR CI，再加 `--selected-only`，就会跳过覆盖采集和全量测试对照，只执行被选中的测试；CLI 会将被选测试的退出码传回调用方。默认仍保留全量对照，适合实验评估。输出目录会保留本次使用的映射。映射会记录基线 commit、Python/系统/依赖配置指纹和测试清单指纹；复用时会校验这些信息和当前发现的测试 ID。有任一项不匹配或旧映射缺少元数据时，RegScope 会保守回退为运行当前全部测试。跨 CI runner 使用时仍应显式传入目标解释器 `--python`。

主分支更新后，可用 `python -m regscope.cli collect <目标目录> --output <coverage-mapping.json>` 单独生成基线覆盖映射；该命令会逐个运行目标测试采集覆盖，不做变更分析或测试对比。运行 `collect` 前需确保目标工作树检出到要作为基线的版本。

## 已验证结果

小型合成 fixture 有 10 个 pytest 测试和 4 个独立故障变更。混合策略在四个已知失败场景均命中故障测试；函数体变更场景选择 8/10，模块级变更安全回退到 10/10。文件级基线选择 9/10；改动函数基线在两个模块级变更中漏掉故障。

此外，在真实 FastAPI 模板上以 58 项测试建立干净基线，并在 `items.py`、`users.py`、`login.py` 三个 route 模块分别注入共 5 个故障。Hybrid 命中 5/5 个已知失败；`users.py` 场景选择 5/58，`login.py` 场景选择 45/58，缩减效果并不恒定。详见[真实仓库实验报告](../experiments/full-stack-fastapi-template.md)。

平台测试为 **64 项通过**。这些准确率/召回率数据来自少量人工注入故障，不能推断为一般项目的可靠性。覆盖采集会逐个运行全部测试，且尚无足够重复计时；测试数量减少比例**不能直接当作端到端耗时节省**。

## 当前状态与下一步

端到端 MVP、合成对照实验和一个真实 FastAPI 仓库的 5 个故障场景已完成。后续可增加其他真实项目与跨层变更样本，重复计时并将覆盖采集开销纳入端到端性能评估。项目目前仍是本地 CLI，没有 CI 配置，也未集成到目标项目的 PR 流程。

## 面试介绍

> 我做 RegScope 是想探索 CI 回归测试能否根据代码影响缩小范围。我实现了从 Git diff、AST 影响分析到 pytest 覆盖映射和测试选择的端到端原型；在一个 10 项测试的合成 fixture 和一个 58 项测试的真实 FastAPI 仓库上，分别评估了 4 个和 5 个受控故障变更，Hybrid 都命中已知失败。真实仓库里，新增的 users 场景选 5/58，login 场景选 45/58，说明效果依变更而异。项目还没有 CI 集成，也未证明实际团队中的净耗时收益。
