# Single-stock deep research · v3.4.0

Updated: 2026-10-02. Independently maintained. [中文](README.md)

## Purpose and scope
Research each specified company independently: key contradictions, five-year financials, moat, valuation, catalysts and conditional actions.

No default market-wide scan or buy ranking. Small lists are researched in input order; peers are comparisons. The screening skill is not required.

## Use a ZIP package (no Git required)

1. [Download the ZIP package](downloads/single-stock-deep-research-v3.4.0.zip?raw=true), or select **Code → Download ZIP** on the repository page.
2. Upload it to an agent that can extract ZIP archives and read the bundled files.
3. Paste this instruction and replace the task at the end:

```text
Extract the uploaded skill archive, find and read its root SKILL.md, and confirm the skill name is single-stock-deep-research. Read the references required by the entry point and use the assets templates to complete the task. First confirm that you can access the bundled files; explicitly report any extraction or reading limitation. Mark missing data UNKNOWN/LIMITED and do not invent data.
Task: Run complete single-stock research for AAPL with data timestamps, key contradictions, three scenarios, crowding, action conditions and strongest counterevidence.
```

If the agent cannot extract ZIP files, extract locally and upload the complete folder where supported, or use the platform's local skill loading mechanism. The GitHub download folder is usually `single-stock-deep-research-skill-main`; rename it to `single-stock-deep-research` if the platform requires the folder to match the skill name. Preserve all files and relative paths.

An attachment lets the agent follow the bundled rules for the current task; it does not necessarily install a persistent skill. Live research requires web access, authorized data sources, or user-provided data. The package includes no market data service, credentials, or subscription.

## Installation
```sh
git clone https://github.com/RickyyyFu/single-stock-deep-research-skill.git single-stock-deep-research
```
Place the entire cloned directory in your host's configured skill location or load its root SKILL.md through the host's local skill mechanism. Preserve all relative references, assets, scripts and tests; do not copy only SKILL.md. The host determines the loading location. No credentials, data subscription or trading service are included.

## Usage
Example request:

> Run complete single-stock research for AAPL with data timestamps, key contradictions, three scenarios, crowding, action conditions and strongest counterevidence.

Read [SKILL.md](SKILL.md) and required references, then use the assets templates. Adapt `assets/config.example.json` and `assets/evidence-ledger.example.json` in a working copy; examples are not market data. The host supplies authorized sources.

## Methodology
Company-type routing → facts and key contradictions → five-year financials and moat → valuation and three scenarios → catalysts → two-sided crowding → technical and conditional actions (including DMI/ADX confirmation). Transition/strategic assets add SOTP, Growth vs Maintenance CapEx, State Tree, Transaction Anchor, Real Option and Model Conflict Review.

DMI/ADX is a technical confirmation layer: +DI/-DI describe direction while ADX describes strength. Rising ADX does not mean price is rising, and DI crossovers are never standalone trade signals.

Positioning / Crowding / Squeeze is a path-risk overlay, not a replacement for quality or valuation. High SI is Fuel, not automatically a Trigger or buy ranking. Record sources, timestamps, counterevidence, triggers and invalidation conditions.

## Data and risk boundaries
Research methods and conditional models, not personalized investment advice. No broker connection, automatic trading or background service. Financials, prices, Short Interest, borrow and options data come from authorized host sources. Missing inputs are UNKNOWN/LIMITED, never zero or fabricated market-wide coverage. Short Interest is distinct from daily Short Volume. 13F is delayed and omits complete hedges; GEX is a model, not a dealer ledger; Call OI does not prove new bullish positions. Crowding does not automatically change DCF or long-term margins. Transaction anchors are not hard floors; 1−Delta is not an option loss probability. Passing tests does not establish excess returns.

## Directory structure
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

## Version maintenance
Default branch: `main`. Use independent semantic versions; synchronize SKILL.md metadata, README, CHANGELOG and MIGRATION when changing versions. Review changes through branches and PRs; after validation, tag the intended commit with `vX.Y.Z` and publish a Release. Do not casually move published tags. `shared_rules_version` labels bundled rules, not an external runtime dependency. This migration preserves v3.4.0 and the 2026-10-02 rule update date.

## Tests
Python 3; standard library only. Run from repository root:
```sh
python -m unittest discover -s tests -v
python scripts/validate_bundle.py
```
Recorded output: `tests/migration-test-results.txt` and `tests/migration-validation-results.txt`. Tests verify documentation contracts and bundle integrity, not host execution, live data or investment performance. See [VALIDATION.md](VALIDATION.md).

## Provenance
Complete directory copied from [GammaLens](https://github.com/RickyyyFu/GammaLens/tree/2c2de5790f93a698b25b31660bc5c5fe1ea97dbe/skills/single-stock-deep-research), branch `feat/equity-research-skills-v1`, commit `2c2de5790f93a698b25b31660bc5c5fe1ea97dbe`, into the new repository root. All source files remain present; READMEs are expanded and migration records and CI are added. See [MIGRATION.md](MIGRATION.md) and MIGRATION-PROVENANCE.json. GammaLens remains unchanged.

## Maintaining versioned ZIP packages

`downloads/` stores standalone versioned skill ZIPs. The initial package uses the existing skill version. When bundled rules, templates, scripts, or documentation change, bump the version in SKILL.md and synchronize both READMEs, CHANGELOG, and MIGRATION. Update both download links, run `python scripts/validate_bundle.py`, then `python scripts/package_skill.py` from the repository root. Commit the new ZIP with the source and documentation, and verify its download link and extracted contents.

Published ZIPs are immutable: retain historical versions and never overwrite an existing version with different content. The packaging script verifies every bundled file and rejects conflicting same-version packages. Include no private data, credentials, or generated research results.
