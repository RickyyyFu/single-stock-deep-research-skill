# CHANGELOG

## 3.3.0 · 2026-10-02
- 合并状态跃迁/战略资产估值：企业类型路由、SOTP、Growth/Maintenance CapEx、利用率、Normalized Earnings、State Tree、Real Option、Transaction Anchors、Model Conflict Review、Milestones。
- 新增Positioning/Crowding/Squeeze：Short squeeze、Long unwind/多杀多、two-sided crowding、borrow/float/options/supply/catalyst。
- 强制Short Interest与daily short volume分离；13F与GEX限制写入核心规则。
- 报告在催化和技术之间增加8A Positioning Risk Card。

## 3.2.0
- 设计层升级：针对INTC类状态跃迁公司，不再以单一路径DCF作为默认中心估值。


## 2026-10-02：独立仓库迁移

从 RickyyyFu/GammaLens 的 feat/equity-research-skills-v1 分支（2c2de5790f93a698b25b31660bc5c5fe1ea97dbe）完整复制 skills/single-stock-deep-research 到本仓库根目录。版本仍为 v3.3.0。扩充中英文 README，新增来源校验清单、测试记录及 CI。未改变研究规则、模板或运行时依赖；无需安装另一 Skill。GammaLens 未修改。
