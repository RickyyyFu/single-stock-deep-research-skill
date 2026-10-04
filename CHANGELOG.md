# CHANGELOG

## 3.5.0 · 2026-10-04
- 新增事件—参与者—经营—资本—价格的结构化情景流程；默认多视角分析，不冒充独立智能体运行。
- 第一屏分开当前内在价值、明确目标日的保守/基准/乐观价位与技术行动位；增加形成路径、触发、失效及反证更新。
- 新增标准库盈利倍数、年度FCFF DCF、全EV口径SOTP计算器；校验口径、普通股盈利归属、股数、融资净现金、少数权益、现金消耗、单位、期间与证据截止。
- 新增可选文件级MiroFish报告隔离导入：保留原文/哈希/声明运行标识，SIMULATION保持MODEL/UNVERIFIED，不进入数字/概率自动转换。不含HTTP客户端，未真实运行MiroFish。
- 新增预测事前登记与旧版/多视角/动态模拟对照方案；未宣称预测准确率或收益改善。
- 保留原有财务、毛选式研究、护城河、转型、拥挤度、DMI/ADX和期权纪律；配置、中英文README、模板、验证及迁移说明同步。
- 新增回归测试、显式打包白名单、可复现ZIP、包内逐文件SHA256与ZIP校验文件；历史ZIP和迁移记录保留，不覆盖。
- About建议文案纳入ABOUT.md；侧栏需独立授权更新，不以文档替代实际设置完成状态。

## 3.4.1 · 2026-10-04
- 仅修正文档：区分单技能 ZIP 与仓库 ZIP、解压路径及附件使用与本地安装。
- 说明规则日期、分发日期和历史迁移记录；发布新的版本 ZIP，研究规则不变。

## 3.4.0 · 2026-10-02
- 新增DMI/ADX趋势确认层：默认14周期，+DI/-DI判方向，ADX判趋势强度。
- 强制区分方向与强度：ADX上升不等于上涨；-DI占优且ADX上升代表空头趋势增强。
- DMI交叉不得单独触发买卖，必须与MA20/40、价格结构和量能交叉验证。
- 完整报告技术章节、配置、完整性检查、validator与合同测试同步加入DMI规则。
- DMI只调整技术确认度与执行条件，不替代主要矛盾、估值、催化或Positioning。

## 3.3.0 · 2026-10-02
- 合并状态跃迁/战略资产估值：企业类型路由、SOTP、Growth/Maintenance CapEx、利用率、Normalized Earnings、State Tree、Real Option、Transaction Anchors、Model Conflict Review、Milestones。
- 新增Positioning/Crowding/Squeeze：Short squeeze、Long unwind/多杀多、two-sided crowding、borrow/float/options/supply/catalyst。
- 强制Short Interest与daily short volume分离；13F与GEX限制写入核心规则。
- 报告在催化和技术之间增加8A Positioning Risk Card。

## 3.2.0
- 设计层升级：针对INTC类状态跃迁公司，不再以单一路径DCF作为默认中心估值。

## 2026-10-02：独立仓库迁移

从 RickyyyFu/GammaLens 的 feat/equity-research-skills-v1 分支（2c2de5790f93a698b25b31660bc5c5fe1ea97dbe）完整复制 skills/single-stock-deep-research 到本仓库根目录。版本仍为 v3.3.0。扩充中英文 README，新增来源校验清单、测试记录及 CI。未改变研究规则、模板或运行时依赖；无需安装另一 Skill。GammaLens 未修改。
