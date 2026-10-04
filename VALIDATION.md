# 验证说明 · single-stock-deep-research v3.5.0

版本日期：2026-10-04。软件规则测试与预测效果验收严格分开。

## 验证范围

原有20项文档合同测试继续保留，检查拥挤度、SI/Short Volume、13F、GEX、DMI/ADX、转型/SOTP等规则没有遗漏。新增测试检查经营盈利到普通股 EPS、全 EV 口径 SOTP、年度 FCFF DCF、融资公允发行不变式、单位/期间/非有限值、少数权益和重复稀释、来源时点/证据依赖/模拟隔离、情景局部阻断、文件输出不覆盖及打包一致性。

实际执行记录见 `tests/release-validation.txt`。记录必须由测试命令真实生成；它不是预测准确率、券商连接或宿主验收报告。历史测试记录仅保留在仓库，不代表本版本已通过。

## 复现

```sh
python -m unittest discover -s tests -v
python scripts/validate_bundle.py
python scripts/package_skill.py
python scripts/package_skill.py --check
```

使用 Python 3.11+ 标准库。再将版本 ZIP 解压到独立目录，在单技能根目录重复 unittest 和 validator；包内所有源文件逐个与 PACKAGE-MANIFEST.json 的 SHA256 对照。程序只读取测试/示例，不要求任何模型 API key。环境只测试过的 Python 版本见执行记录，不能将语言最低版本要求理解为所有版本已实测。

## 未执行 / 未证实

未验证真实 MiroFish、独立智能体互动、HTTP集成、市场数据自动提取、宿主遵循规则的稳定性、实时券商/借券/GEX、任何历史交易回测或前瞻预测收益。导入器测试使用合成文本，不冒充真实模拟。示例 DEMO_CO 完全虚构，不能用于投资。

RESEARCH 模式只检查调用者提供的来源与核验声明，不会访问网址鉴真，也不会自动判断假设是否经济合理。输入可审查、可复算不等于预测准确。需要独立的资料复核、模型适用性审查和[事前对照评价](references/13-prediction-evaluation.md)。

持续集成执行状态应读取对应 GitHub Actions 运行记录；不能以本地测试通过代替远程 CI 成功。仓库侧栏、标签与 Release 也需要分别确认，不能由 ZIP 生成推定已发布。
