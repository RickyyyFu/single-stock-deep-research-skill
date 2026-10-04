# MIGRATION

## v3.4.0 → v3.4.1
本次为文档与分发包修订，研究规则和数据配置不变。下载新版 ZIP，保留完整技能文件夹；既有研究结果无需迁移。

## v3.3.0 → v3.4.0
无需迁移账户、行情或估值配置。技术章节新增DMI/ADX：默认14周期，+DI/-DI判方向、ADX判强度；历史报告若无可靠DMI数据保持UNKNOWN，不回填估算值。DMI只影响技术确认与执行条件，不回写DCF、主要矛盾或Positioning结论。

从v3.1升级：完整报告增加企业类型路由、7A Transition（适用时）和8A Positioning。旧DCF结果若与高质量交易锚显著冲突，不能直接继承“高估/低估”结论，必须Model Conflict Review。旧报告缺SI/borrow数据不得补0，写UNKNOWN。


## 2026-10-02：独立仓库迁移

从 RickyyyFu/GammaLens 的 feat/equity-research-skills-v1 分支（2c2de5790f93a698b25b31660bc5c5fe1ea97dbe）完整复制 skills/single-stock-deep-research 到本仓库根目录。版本仍为 v3.3.0。扩充中英文 README，新增来源校验清单、测试记录及 CI。未改变研究规则、模板或运行时依赖；无需安装另一 Skill。GammaLens 未修改。
