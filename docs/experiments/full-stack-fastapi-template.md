# full-stack-fastapi-template 实仓评估记录

## 目的与状态

验证 RegScope 能否接入一个真实、公开的 FastAPI + pytest 仓库，并确认后续回归选择实验的运行前置条件。

**状态：完成 5 个受控缺陷场景。** 原有 3 例在 `items.py`；新增 2 例分别位于 `users.py` 和 `login.py`。五个已知失败都被 Hybrid 选中，但这仍是同一真实仓库中的少量人工注入缺陷，不代表普遍效果。

## 固定对象

- 仓库：<https://github.com/fastapi/full-stack-fastapi-template>
- 本地目录：`F:/大学/大三上/full-stack-fastapi-template`
- 检出 commit：`e99fbaeba3b55190156ebae525ad9d481d76677e`
- 分析目标：`backend/`
- 实验分支：`regscope-eval/read-item-not-found`、`regscope-eval/delete-item-permission`、`regscope-eval/create-item-response`、`regscope-eval/cross-module-users`、`regscope-eval/cross-module-login`
- 缺陷 head：`1bdcd0f`、`c524494`、`da5e28e`（各场景见下表）
- Python：仓库要求 Python 3.14；本次通过 uv 管理的 CPython 3.14.3 安装后端依赖。
- 测试：后端 `pytest`，测试配置和应用导入依赖根目录 `.env`；测试 fixture 初始化 PostgreSQL。
- 结果目录：`F:/大学/大三上/_regscope-full-stack-eval/`

## 已执行检查

| 检查 | 结果 | 说明 |
|---|---|---|
| 克隆仓库 | 通过 | 固定在上述 commit。 |
| `uv sync --project backend` | 通过 | 使用 Python 3.14.3 安装 78 个包；普通沙箱网络受限，依赖下载经授权后完成。 |
| pytest 收集 | 通过 | 在 `backend/` 执行 `uv run pytest --collect-only -q -o addopts=`，收集到 58 个测试。RegScope `discover_test_ids()` 也得到相同数量。 |
| RegScope 静态 AST 扫描 | 部分通过 | 用 Python 3.14 解析出 23 个 route 装饰函数和 64 个函数。 |
| PostgreSQL / migrations | 通过 | 本机 `127.0.0.1:5432` 可连接；确认目标数据库无现存表后执行 `uv run alembic upgrade head`。 |
| 基线全量测试 | 通过 | 基线 `e99fbaeb`：`58 passed`。 |
| 缺陷测试验证 | 通过 | 三个 head 各自独立触发对应的一条已知失败测试。 |
| RegScope 测试发现 | 通过 | 收集到 58 个稳定 pytest node ID。 |
| RegScope 覆盖采集 | 通过 | 每个 node ID 独立运行并生成覆盖映射；预期失败测试的覆盖也被保留。 |
| RegScope 影响分析 | 修复后通过 | 识别 `app.api.routes.items:read_item`，并输出 `GET /{id}` 的局部路由影响路径。 |
| 策略对比 | 通过 | full-suite、file-level-coverage、dynamic-only、hybrid 均在同一组 58 个测试上评估。 |
| RegScope 平台测试 | 通过 | 修改后全量平台测试 `47 passed`。 |

### 缺陷场景结果

五个场景都以干净基线 `e99fbaeb` 采集的同一份 58 项覆盖映射进行比较。

| 场景 / head | 已知失败 | 策略 | 选择数 | 缩减率 | 召回率 |
|---|---|---|---:|---:|---:|
| `read_item` / `1bdcd0f` | `test_read_item_not_found` | Full suite | 58 / 58 | 0.00% | 100% |
|  |  | File-level coverage | 11 / 58 | 81.03% | 100% |
|  |  | Dynamic-only | 3 / 58 | 94.83% | 100% |
|  |  | RegScope Hybrid | 3 / 58 | 94.83% | 100% |
| `delete_item` / `c524494` | `test_delete_item_not_enough_permissions` | Full suite | 58 / 58 | 0.00% | 100% |
|  |  | File-level coverage | 11 / 58 | 81.03% | 100% |
|  |  | Dynamic-only | 3 / 58 | 94.83% | 100% |
|  |  | RegScope Hybrid | 3 / 58 | 94.83% | 100% |
| `create_item` / `da5e28e` | `test_create_item` | Full suite | 58 / 58 | 0.00% | 100% |
|  |  | File-level coverage | 11 / 58 | 81.03% | 100% |
|  |  | Dynamic-only | 1 / 58 | 98.28% | 100% |
|  |  | RegScope Hybrid | 1 / 58 | 98.28% | 100% |
| `users.py` / `5633b93` | `test_get_existing_user_permissions_error` | Full suite | 58 / 58 | 0.00% | 100% |
|  |  | File-level coverage | 25 / 58 | 56.90% | 100% |
|  |  | Dynamic-only | 5 / 58 | 91.38% | 100% |
|  |  | RegScope Hybrid | 5 / 58 | 91.38% | 100% |
| `login.py` / `7b3da14` | `test_get_access_token_incorrect_password` | Full suite | 58 / 58 | 0.00% | 100% |
|  |  | File-level coverage | 45 / 58 | 22.41% | 100% |
|  |  | Dynamic-only | 45 / 58 | 22.41% | 100% |
|  |  | RegScope Hybrid | 45 / 58 | 22.41% | 100% |

五个场景的 Hybrid 都选中了对应失败测试。新增的 `users.py` 场景选 5/58，`login.py` 场景选 45/58；后者的影响/覆盖关系较宽，缩减有限。这初步说明 RegScope 不只在 `items.py` 生效，也显示效果依变更位置和映射范围而变。所有选择集与 full suite 的退出码均为 1，这是因为各实验 head 都包含已知缺陷。

## 发现的问题与边界

1. **分析目标必须指向 `backend/`。** pytest 配置、应用源码和 `app/` 都在该子目录；从仓库根目录启动还会使模板相对 `.env` 路径失效。
2. **应用导入需要前端目录存在。** 该目录在预检期间以空目录形式创建（被 `.gitignore` 忽略）；本实验只测后端 API，不测前端构建。
3. **测试依赖 PostgreSQL 和已应用 migrations。** 本次先确认数据库无表，再升级到模板 migration head；58 项基线测试全部通过。
4. **发现并修复嵌套项目的 Git diff 路径错误。** 首次 pipeline 将仓库顶层返回的 `backend/app/...` 当成相对 `backend/` 的路径，因而漏掉变更并错误回退到全量 58 项。RegScope 在 `git diff` 增加 `--relative`，新增嵌套目标路径回归测试；`tests/test_git_diff.py` 的 4 项测试通过。之后重新计算 impact 并以已采集的 58 项覆盖映射运行全部对比策略。
5. **API 路径只识别 endpoint 局部路径。** 影响结果是 `GET /{id}`，没有合并 `APIRouter(prefix="/items")` 和全局 `/api/v1` 前缀。当前场景仍能通过 endpoint 函数标识匹配测试，但路由展示不完整。
6. **解释器版本需要对齐。** RegScope 自身 Python 3.12 无法解析目标的 Python 3.14 语法；本次用 Python 3.14.3 跑平台，用模板 `.venv/Scripts/python.exe` 跑测试。

## 后续可复现实验步骤

各场景的原始输出保存在结果目录的 `case-01/` 至 `case-05/` 中；新增两例包括 `impact.json` 和 `comparison.json`。基线逐测试覆盖数据在 `baseline-coverage/`；汇总表和机器可读汇总分别是结果目录根部的 `README.md` 和 `summary.json`。

仍需增加跨层/CRUD 变更、无影响变更、模块级配置变更等场景，并记录人工预期、回退行为和失败注入依据。当前五例仅覆盖同一 FastAPI 仓库的三个 route 模块，不能证明对其他项目或更复杂跨层改动同样有效。

复现本场景时，先运行 pipeline 生成 coverage mapping 和 impact，再运行比较入口。输出目录放在目标仓库之外：

```powershell
$env:PYTHONPATH = 'F:\大学\大三上\RegScope\src'
& 'E:\ai-data\uv-python\cpython-3.14-windows-x86_64-none\python.exe' -m regscope.cli run `
  'F:\大学\大三上\full-stack-fastapi-template\backend' `
  e99fbaeba3b55190156ebae525ad9d481d76677e 1bdcd0f `
  --python 'F:\大学\大三上\full-stack-fastapi-template\.venv\Scripts\python.exe' `
  --known-failing 'tests/api/routes/test_items.py::test_read_item_not_found' `
  --output 'F:\大学\大三上\_regscope-full-stack-eval\case-01'

& 'E:\ai-data\uv-python\cpython-3.14-windows-x86_64-none\python.exe' -m regscope.experiment_cli `
  --mapping 'F:\大学\大三上\_regscope-full-stack-eval\case-01\coverage\coverage-mapping.json' `
  --impact 'F:\大学\大三上\_regscope-full-stack-eval\case-01\impact.json' `
  --python 'F:\大学\大三上\full-stack-fastapi-template\.venv\Scripts\python.exe' `
  --output 'F:\大学\大三上\_regscope-full-stack-eval\case-01\comparison.json'
```

## 当前结论

RegScope 已在真实 FastAPI 仓库完成五例端到端缺陷实验：干净基线 58 项通过；五例 Hybrid 均命中已知失败。新增 `users.py`、`login.py` 两例分别选择 5、45 项（缩减 91.38%、22.41%）。因此，现有证据否定了“只对 `items.py` 有效”这一说法，但尚不足以证明普遍适用；尤其登录场景缩减幅度较小。首次运行暴露并促成修复了嵌套 Git 子目录路径问题。其他限制包括样本少、均来自同一项目、router 前缀没有合并；不能外推到其他 FastAPI 项目或大型跨层变更。
