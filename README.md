# 单标的深度研究 · v3.4.0

更新日期：2026-10-02。独立维护仓库。 [English](README.en.md)

## 定位与职责边界
对指定公司逐家研究主要矛盾、五年财务、护城河、估值、催化和条件式行动。

默认不扫描全市场、不做买入排名；小清单按输入顺序逐家报告，同行只用于比较。无需安装筛选 Skill。

## 安装
```sh
git clone https://github.com/RickyyyFu/single-stock-deep-research-skill.git single-stock-deep-research
```
将整个克隆目录放到所用宿主支持的 Skill 目录，或按宿主的本地 Skill 加载方式加载根目录的 `SKILL.md`。不要只复制 SKILL.md；保持 references、assets、scripts、tests 的相对路径。宿主加载位置由宿主配置决定。本包不含账户凭证、数据订阅或交易服务。

## 使用
示例请求：

> 对 AAPL 执行完整单标的研究，标注所有数据时点、主要矛盾、三情景、拥挤度、行动条件和最强反证。

先读取 [SKILL.md](SKILL.md) 和对应必读 references；使用 assets 中的模板。`assets/config.example.json` 是配置示例，`assets/evidence-ledger.example.json` 是证据台账示例，请根据任务在工作副本中填写，不将示例当作真实行情。宿主需要自行提供已授权的数据来源。

## 方法论
企业类型路由 → 事实与主要矛盾 → 五年财务和护城河 → 估值与三情景 → 催化 → 双向拥挤度 → 技术与条件式行动（含DMI/ADX趋势确认）。转型/战略资产公司加入 SOTP、Growth vs Maintenance CapEx、State Tree、Transaction Anchor、Real Option 和 Model Conflict Review。

DMI/ADX只用于技术确认：+DI/-DI描述方向，ADX描述强度；ADX上升不等于上涨，DI交叉不得单独作为买卖信号。

Positioning / Crowding / Squeeze 只是路径风险覆盖层，不取代公司质量或估值；高 SI 是 Fuel，不自动构成 Trigger 或买入排名。每条论点注明来源、时点、反证、触发与失效条件。

## 数据与风险边界
研究方法与条件模型，非个性化投资建议。无券商连接、自动交易或后台服务。财报、价格、Short Interest、借券、期权与宏观数据由宿主的已授权来源提供；缺失写 UNKNOWN/LIMITED，不补零或伪造全市场扫描。Short Interest 与 daily Short Volume 不混用；13F 滞后且不含完整对冲；GEX 是模型而非 dealer 真实账本；Call OI 不证明新开看多。拥挤度不自动改 DCF 或长期利润率。交易锚不代表硬底；期权 1−Delta 不是亏损概率。测试通过不证明模型有效或有超额收益。

## 目录结构
```text
SKILL.md                 # 宿主入口 / host entry point
README.md / README.en.md # 中文与英文指南 / bilingual guides
CHANGELOG.md             # 版本变化 / version history
MIGRATION.md              # 升级与仓库迁移 / migration
VALIDATION.md             # 验证范围与局限 / validation scope
references/              # 研究规则 / research rules
assets/                  # 模板、配置与证据台账 / templates and config
scripts/validate_bundle.py
tests/                  # 合同测试和运行记录 / contract tests and logs
MIGRATION-PROVENANCE.json # 来源文件校验与修改记录 / provenance
.github/workflows/validate.yml # 自动检查 / CI
```

## 版本维护
默认分支 `main`；独立使用语义版本号，修改后同步 SKILL.md metadata、README、CHANGELOG 与 MIGRATION。建议通过分支和 PR 评审；测试通过后为对应提交创建不可随意移动的 `vX.Y.Z` tag，并发布 Release。`shared_rules_version` 只是本包规则的版本标识，规则已随包提供，无跨仓库运行时依赖。当前版本和规则更新日期保留为 v3.4.0 / 2026-10-02。

## 测试
Python 3，测试和 validator 仅用标准库；从仓库根目录运行：
```sh
python -m unittest discover -s tests -v
python scripts/validate_bundle.py
```
完整输出见 `tests/migration-test-results.txt` 与 `tests/migration-validation-results.txt`。测试覆盖文档合同和包完整性，不覆盖宿主行为、实时数据或投资收益，详见 [VALIDATION.md](VALIDATION.md)。

## 迁移来源
从 [GammaLens](https://github.com/RickyyyFu/GammaLens/tree/2c2de5790f93a698b25b31660bc5c5fe1ea97dbe/skills/single-stock-deep-research) 的 `feat/equity-research-skills-v1` 分支、提交 `2c2de5790f93a698b25b31660bc5c5fe1ea97dbe` 复制完整目录到仓库根目录。原文件全部保留，README 扩充，迁移记录和 CI 新增；详见 [MIGRATION.md](MIGRATION.md) 和来源校验清单。GammaLens 未修改。
