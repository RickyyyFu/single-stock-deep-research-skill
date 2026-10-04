# MIGRATION

## v3.4.1 → v3.5.0

这是研究流程、可选计算脚本和分发格式升级。使用完整新版目录，避免只替换SKILL.md。入口版本3.5.0、配置3.5.0、随包规则标识1.3.0；不存在对另一选股Skill的运行依赖。

已有五年财务、主要矛盾、护城河、估值、Transition/Positioning和DMI/ADX研究继续使用。新增核心必读references/11-scenario-valuation.md与报告8B节。外部模拟默认关闭，只有用户提供实际报告时加载references/12-simulation-integration.md；无MiroFish凭证不阻断正常研究。

旧报告保留原时点与结论，不能事后改写成“已预测”。下一次研究再添加事件—经营—资本—价格路径、三类价格分栏和反证更新。旧工程实验的现价比例、主观权益比例、真实ticker测试价不得迁入正式模型。缺乏来源、股本或财务校准时，仅阻断受影响价位，不回填数字。

原assets/config.example.json需合并新增scenario和external_simulation配置；risk字段仍默认未获批准，账户数据不能随包发布。旧证据账本保留，新增字段id/unit/period/basis/source_type/parent_ids/rationale/模拟运行信息，不能把未知值自动设为零。`evidence-ledger.example.json`是研究台账模板；计算器输入是独立的schema_version1.0.0合同，不可不经适配直接把台账传给计算器。

MiroFish适配为文件隔离，不是HTTP服务；运行标识来自调用者声明，未核实运行真实性。默认多视角分析也不是独立Agent执行。程序退出码2表示输入/输出错误或受影响情景、敏感性范围被阻断；读取已生成输出的逐情景原因，不能把退出0等同投资模型已验证。

打包改用bundle-files.json白名单和固定ZIP元数据，新增PACKAGE-MANIFEST.json与ZIP SHA256。历史迁移清单和旧运行日志仍在仓库中，但不再进入安装ZIP；它们记录旧构建而非当前源码校验。原v3.4.0/v3.4.1压缩包保留原字节，不重打包。

## v3.4.0 → v3.4.1
本次为文档与分发包修订，研究规则和数据配置不变。下载新版 ZIP，保留完整技能文件夹；既有研究结果无需迁移。

## v3.3.0 → v3.4.0
无需迁移账户、行情或估值配置。技术章节新增DMI/ADX：默认14周期，+DI/-DI判方向、ADX判强度；历史报告若无可靠DMI数据保持UNKNOWN，不回填估算值。DMI只影响技术确认与执行条件，不回写DCF、主要矛盾或Positioning结论。

从v3.1升级：完整报告增加企业类型路由、7A Transition（适用时）和8A Positioning。旧DCF结果若与高质量交易锚显著冲突，不能直接继承“高估/低估”结论，必须Model Conflict Review。旧报告缺SI/borrow数据不得补0，写UNKNOWN。

## 2026-10-02：独立仓库迁移

从 RickyyyFu/GammaLens 的 feat/equity-research-skills-v1 分支（2c2de5790f93a698b25b31660bc5c5fe1ea97dbe）完整复制 skills/single-stock-deep-research 到本仓库根目录。版本仍为 v3.3.0。扩充中英文 README，新增来源校验清单、测试记录及 CI。未改变研究规则、模板或运行时依赖；无需安装另一 Skill。GammaLens 未修改。原始[来源清单](https://github.com/RickyyyFu/single-stock-deep-research-skill/blob/main/MIGRATION-PROVENANCE.json)保持为历史快照，不重写成当前文件哈希。
