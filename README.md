# 单标的深度研究 · v3.5.0

研究规则与分发包更新：2026-10-04。独立维护。 [English](README.en.md)

对指定公司逐家研究主要矛盾、五年财务、护城河、估值、催化、双向拥挤度与技术位置，并给出**明确日期、可复算的条件价位、触发和失效条件**。不默认扫描全市场或进行买入排名；小清单按输入顺序报告，同行只用于比较，无需安装选股 Skill。

## v3.5.0 新增什么

新增“事件 → 参与者反应 → 经营状态 → 资本与股数 → 每股价位”推演；先验证事实和约束，再用适合企业类型的模型计算。多视角分析不是独立智能体执行，MiroFish 不是必需依赖。

- 第一屏分开呈现**当前内在价值、指定日期三情景目标价、短期技术与行动价位**；有依据时给中心价位与参数范围，缺失则标 UNKNOWN/LIMITED。
- 标准库计算器支持盈利倍数、年度 FCFF DCF 和全 EV 口径 SOTP，检查财年/期间、单位、普通股利润归属、融资现金与股数、少数权益及证据来源。
- 模拟报告只能文件级隔离导入为 `MODEL / UNVERIFIED` 假设；不能直接成为估值数字、现实概率或期权 EV。
- 新增反证更新、事前预测登记和对照评价规则；程序测试通过不代表预测更准或具有超额收益。

原有企业类型路由、毛选式研究、五年财务、护城河、Forward PE/PEG、DCF、SOTP、Growth vs Maintenance CapEx、State Tree、Real Option、Transaction Anchor、Model Conflict Review、DMI/ADX 和拥挤度规则全部保留。

## 压缩包使用（无需 Git）

[下载 v3.5.0 仓库 ZIP（无需 Git）](https://github.com/RickyyyFu/single-stock-deep-research-skill/archive/refs/heads/release-v3.5.0.zip)

该链接下载版本分支 `release-v3.5.0` 的完整仓库；不是 `downloads/` 中的单技能 ZIP。解压后直接使用顶层目录里的 SKILL.md，或上传给支持解压的 Agent。单技能 ZIP 可用下方打包命令从源码生成；单独分发包的哈希见随包校验文件。本版本不声称 GitHub Release 或单技能 ZIP 已上传。

上传 ZIP 给支持解压并读取包内文件的 Agent，使用：

```text
请解压技能压缩包，在解压后的顶层技能/仓库目录读取 SKILL.md，确认版本为 3.5.0。按入口读取必需 references，使用 assets 模板。先确认文件可读；缺数据标 UNKNOWN/LIMITED，不编造价格或概率。
任务：对 AAPL 执行完整研究。分别列出当前内在价值、研究日后12个月的保守/基准/乐观目标价、短期技术位。每个情景写经营及融资假设、形成过程、触发和失效条件；数据不足时说明哪一部分不能计算。
```

单技能 ZIP 解压后为 `single-stock-deep-research/`，入口是该目录内的 `SKILL.md`。上方版本仓库 ZIP 通常解压为 `single-stock-deep-research-skill-release-v3.5.0/`，GitHub **Code → Download ZIP** 的 main 快照通常为 `single-stock-deep-research-skill-main/`；入口都在顶层仓库目录，额外含历史 `downloads/` 等维护文件。不要把旧版本 ZIP 当作本次版本。两种包均保留完整研究规则，单技能包更精简。

上传附件仅为当前任务提供规则，不一定自动安装成持久技能。宿主必须能够联网或读取用户提供的真实资料；本包不含行情服务、账户凭证或订阅。无法解压时，在本地解压并上传完整所需目录；不要只上传 SKILL.md。

## 本地安装

```sh
git clone https://github.com/RickyyyFu/single-stock-deep-research-skill.git single-stock-deep-research
```

将整个目录放入宿主支持的技能目录，或用宿主的本地加载方式读取根目录 SKILL.md。保留 references、assets、scripts、tests 的相对路径。更新时用完整新版替换技能目录，私人证据和研究快照另存，勿提交到公共仓库。升级说明见 [MIGRATION.md](MIGRATION.md)。

## 计算与校验（可选 Python 3.11+）

仅阅读研究规则不要求 Python。以下程序使用标准库，不会联网、调用大模型或交易：

```sh
python -m unittest discover -s tests -v
python scripts/validate_bundle.py
python scripts/scenario_valuation.py assets/scenario-example.json --output example-result.json
python scripts/package_skill.py
python scripts/package_skill.py --check
```

示例为 **DEMO_CO 虚构公司**，全部输入为工程测试数据，不是预测。输出文件采用独占创建，拒绝覆盖旧预测。实际研究需在工作副本中填写带证据、口径和期间的输入；先读 [情景估值规则](references/11-scenario-valuation.md)。当前计算器不支持银行/保险等专用模型、复杂证券权利、零碎期限 DCF 或期权定价；这些情况使用独立审查的适配模型，不强行套公式。

计算器核验输入结构与声明，不会验证来源真伪或保证假设合理。`RESEARCH` 输出也只标 `CALCULATED_MODEL_NOT_VALIDATED`。情景中心价不是最可能价格，参数敏感性范围不是置信区间。缺少依据的数字不得为填表而补出。

## MiroFish 的边界

默认流程为 `STRUCTURED_PERSPECTIVES`，不是多智能体系统。可选文件导入器保留原文、哈希及调用者声明的运行信息，并将内容隔离为假设；**不含 HTTP 客户端，未执行或验证真实 MiroFish 推演**。来源材料仍是待核验数据，不能变成新的系统指令。操作与限制见 [外部模拟接口](references/12-simulation-integration.md)。

借鉴多角色、约束和反馈思想不等于证明价格预测有效。升级后的方法需要与旧版、静态多视角和真实动态模拟在相同证据快照下对照，见 [预测效果评价](references/13-prediction-evaluation.md)。

## 数据与风险边界

`FACT / GUIDANCE / CONSENSUS / MODEL / INFERENCE / UNKNOWN` 分开，记录事件日、披露日、资料截止与来源；缺失只阻断依赖它的结论，不补零。Short Interest 与 daily Short Volume 不混用；高 SI 是 Fuel 而非自动 Trigger。13F 滞后且不含完整对冲，GEX 不是 dealer 真实账本，Call OI 不证明新开看多。拥挤度影响路径，不自动修改长期利润率或 DCF。

DMI 默认14周期，+DI/-DI描述方向，ADX描述强度；ADX上升不等于上涨，DMI交叉不得单独触发买卖。技术位不等于内在价值。交易锚不是硬底。期权提前退出要另建价格×时间×IV情景；1−Delta不是亏损概率，代理投票或模拟频率不能直接形成现实概率或 EV。

本包是研究规则与计算辅助工具，无券商连接、自动交易、后台任务或个性化收益承诺。当前测试只验证软件规则与包一致性，不验证宿主行为、实时资料、MiroFish 或投资收益，详见 [VALIDATION.md](VALIDATION.md)。

## 维护与目录

`SKILL.md` 为入口；`references/` 为研究规则；`assets/` 为模板与虚构示例；`scripts/` 为计算/隔离导入/打包/校验；`tests/` 为回归测试；`bundle-files.json` 为打包白名单。ZIP 内的 `PACKAGE-MANIFEST.json` 逐文件记录 SHA256，不包含自身哈希。历史迁移材料与旧 ZIP 只保留在仓库，不打入新版安装包。

默认分支 `main`。规则、模板、脚本或随包文档改动时递增版本，同步 SKILL、配置、中英文 README、CHANGELOG、MIGRATION、VALIDATION 和下载链接，再测试、打包、校验、通过 PR 发布。历史 ZIP 不覆盖；新的同名包内容冲突会报错。`shared_rules_version` 仅标识本包内规则，无跨仓库运行时依赖。

仓库 About 的建议文案和维护边界见 [ABOUT.md](ABOUT.md)；该文件不是侧栏设置已更新的证明。原始迁移来自 GammaLens `2c2de5790f93a698b25b31660bc5c5fe1ea97dbe`，详见 [历史来源清单](https://github.com/RickyyyFu/single-stock-deep-research-skill/blob/main/MIGRATION-PROVENANCE.json)。GammaLens 和选股仓库不随本次改动。历史变更见 [CHANGELOG.md](CHANGELOG.md)。
