---
name: single-stock-deep-research
description: "当用户给定公司/股票代码或明确小清单时，逐家研究主要矛盾、五年财务、护城河、估值、状态跃迁、催化、拥挤度、技术与条件式操作；以事件—经营—资本—价格链条给出明确日期的条件价位。不默认扫描市场或排名。"
compatibility: "中文Markdown；行情、财报及券商数据由宿主授权来源提供。可选Python 3.11+标准库计算；无需MiroFish、Zep或模型API，无自动交易或后台服务。"
metadata:
  version: "3.5.0"
  shared_rules_version: "1.3.0"
  language: "zh-CN"
  updated: "2026-10-04"
---

# 单标的深度研究 v3.5.0

## 默认任务与独立性
只给代码即执行完整研究；明确小清单则按输入顺序逐家独立报告，不排名。同行只用于比较。无需安装选股Skill，不修改另一仓库。先确认文件访问及数据能力；缺失写UNKNOWN/LIMITED，不虚构调用。

## 企业类型路由
先判定`mature_compounder / high_growth_profitable / cyclical / early_commercialization / transition_strategic_asset / mixed`。大额Growth CapEx、战略融资、利用率跃迁、重组或DCF与交易锚冲突时加载`references/04b-transition-strategic-asset.md`，单一路径DCF不得作为唯一中心估值。银行/保险/REIT等使用行业模型，不硬套附带工业计算器。

## 完整研究必读
`references/01-data-integrity.md` → `02-mao-research.md` → `03-financials-moat.md` → `04-valuation.md` →（适用时`04b-transition-strategic-asset.md`）→ `05-events.md` → `06-positioning-crowding.md` → `11-scenario-valuation.md` → `07-technical.md` → `10-industry.md`。
期权/真实持仓请求另读`08-risk-options.md`；更新读`09-review.md`；导入外部模拟读`12-simulation-integration.md`；评估预测改进读`13-prediction-evaluation.md`。

## 情景与价格强制交付
按`assets/report-template.md`和`assets/scenario-card.md`执行。保守/基准/乐观分别列：事实时点、预测日期、前提、参与者利益/约束与反应、模型变量、财务/资本桥接、中心价位、敏感性范围、触发、失效和下一验证。
当前内在价值、未来情景目标价、短期技术位必须分开。用户日期优先；否则主目标为研究日+12个月（闰日取当月末），注明日历日期，不冒充交易日收盘价。不能从现价任意乘百分比产生基本面目标价；无法定价的分支保留并写BLOCKED和缺口，不阻断其他研究。
默认是同一事实底稿上的结构化多视角分析，不声称实际运行了独立Agent或MiroFish。只有用户请求且有真实运行证据才升级外部动态模拟。无需API也能按规则研究。

## Positioning强制交付
完整报告在催化之后、技术之前加入Short/Long crowding、Borrow stress、Float/liquidity、13F/ETF代理、Options amplification、供给事件、Catalyst proximity、Squeeze/Unwind stage、Trigger与Invalidation。数据缺失写UNKNOWN/LIMITED。

## 关键禁区
- Short Interest与daily short volume绝不混用；高SI不等于正在轧空。
- DMI只做技术确认：+DI/-DI描述方向，ADX描述强度；ADX上升不等于上涨。DMI交叉不得单独触发买卖，须与MA20/40、结构和量能验证。
- 13F不代表实时净敞口；GEX不代表dealer真实账本；Call OI不证明新开看多。
- 拥挤度只改变路径风险与执行；无经营/融资传导证据不改DCF/长期利润率。
- Transaction Anchor不是硬底；转型估值冲突必须Model Conflict Review。
- 模拟内容始终MODEL且来源SIMULATION；角色投票、模拟频率不是现实概率，生成报告不是预测验证。
- 不把同一利好无说明同时加到收入、利润率、倍数、终值和折现率；不把未来财报泄漏进历史时点。
- 期权1−Delta不是亏损概率；提前退出按价格×时间×IV，缺可信概率不强算EV。

## 可选计算与验证
使用`assets/scenario-example.json`了解严格输入合同；它仅含虚构公司。填写真实证据和模型后，运行`python scripts/scenario_valuation.py <input.json>`。程序只检查口径并计算，不验证来源真实性，不训练/调用模型，不生成胜率。输出CALCULATED_MODEL_NOT_VALIDATED也不是投资有效性认证。
外部报告仅通过`scripts/import_simulation.py`文件导入、隔离为假设。HTTP连接与真实MiroFish推演未实现/未验证。没有Python时按相同规则展示手工算式并注明未执行程序。

## 输出结构
保留0—13节及7A/8A，新增8B。第一屏和末尾用列表/价位表给：当前价及完整时点、主预测日期、三情景、主要矛盾、Transition/Crowding状态、DMI方向/ADX强度（有数据时）、行动条件、最强反证与数据缺口。
