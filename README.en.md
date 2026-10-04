# Single-stock deep research · v3.5.0

Research rules and distribution updated: 2026-10-04. Independently maintained. [中文](README.md)

Research each specified company: key contradictions, five-year financials, moat, valuation, catalysts, two-sided crowding and technical conditions. Deliver **dated, reproducible conditional price levels with triggers and invalidation**. No default market-wide scan or buy ranking. Small lists follow input order; peers are comparisons. No dependency on a screening skill.

## What changes in v3.5.0

The scenario process connects **events → participant responses → operating states → capital and shares → per-share values**. Verify facts and constraints before computing prices with a suitable company-type model. Multiple perspectives are not independent agent execution; MiroFish is optional.

- Separate current intrinsic value, dated conservative/base/optimistic price scenarios, and short-term technical/action levels. Show a central value and parameter range only when defensible; otherwise report UNKNOWN/LIMITED.
- Standard-library arithmetic supports earnings multiples, annual FCFF DCF and all-enterprise-value SOTP. It checks periods, units, common-income attribution, issuance cash and shares, minority interests and evidence declarations.
- File-only simulation import quarantines reports as `MODEL / UNVERIFIED` hypotheses. They cannot directly supply numerical valuation inputs, real-world probabilities or option EV.
- Add counterevidence updates, preregistered forecasts and comparative evaluation. Passing software tests does not demonstrate more accurate predictions or excess returns.

Existing company routing, investigation/key-contradiction methodology, financials, moat, Forward PE/PEG, DCF, SOTP, Growth vs Maintenance CapEx, State Tree, Real Option, Transaction Anchor, Model Conflict Review, DMI/ADX and crowding rules are retained.

## Use a ZIP package (no Git required)

[Download the v3.5.0 standalone skill ZIP](downloads/single-stock-deep-research-v3.5.0.zip?raw=true) · [SHA256 checksum](downloads/single-stock-deep-research-v3.5.0.zip.sha256?raw=true)

Upload the ZIP to a host able to extract archives and read the files, then use:

```text
Extract the uploaded archive, read single-stock-deep-research/SKILL.md and confirm version 3.5.0. Read the required references and use the assets templates. Confirm file access; mark missing data UNKNOWN/LIMITED and do not invent prices or probabilities.
Task: Research AAPL completely. Separate current intrinsic value, conservative/base/optimistic targets 12 months after the research date, and short-term technical levels. Explain operating and financing assumptions, paths, triggers and invalidation. Identify conclusions blocked by missing data.
```

The standalone package extracts to `single-stock-deep-research/`, with `SKILL.md` inside it. GitHub **Code → Download ZIP** instead exports the entire repository, typically under `single-stock-deep-research-skill-main/`, including historical downloads and maintenance files. Prefer the versioned standalone ZIP for installation.

Attachments supply rules for the current task; they do not necessarily install a persistent skill. Live research requires web access, authorized data or user-supplied documents. No market-data service, credentials or subscription is included. Where extraction is unavailable, extract locally and upload the required complete directory. Do not provide SKILL.md alone.

## Local installation

```sh
git clone https://github.com/RickyyyFu/single-stock-deep-research-skill.git single-stock-deep-research
```

Place the whole folder in the host's supported skill directory or load the root SKILL.md through its local mechanism. Preserve references/assets/scripts/tests paths. Replace the complete folder on upgrade; keep private evidence and forecast snapshots outside this public repository. See [MIGRATION.md](MIGRATION.md).

## Optional arithmetic and validation (Python 3.11+)

Reading the research rules does not require Python. The following tools use only the standard library, with no network access, model calls or trades:

```sh
python -m unittest discover -s tests -v
python scripts/validate_bundle.py
python scripts/scenario_valuation.py assets/scenario-example.json --output example-result.json
python scripts/package_skill.py
python scripts/package_skill.py --check
```

`DEMO_CO` is fictional engineering data, not a forecast. Output files use exclusive creation to protect previous snapshots. Adapt inputs in a working copy with evidence, units and matching periods; read [scenario valuation](references/11-scenario-valuation.md) first. The calculator does not support specialized bank/insurance models, complex securities, stub-period DCF or option pricing. Use independently reviewed suitable models instead.

The program checks input structure and declarations, not source authenticity or economic soundness. RESEARCH results remain `CALCULATED_MODEL_NOT_VALIDATED`. A scenario center is not necessarily the most likely price, and a sensitivity range is not a confidence interval. Missing inputs must not be fabricated to complete a table.

## Optional MiroFish boundary

The default mode is `STRUCTURED_PERSPECTIVES`, not a multi-agent runtime. File import retains raw content, a hash and caller-declared run metadata, but only as hypotheses. **No HTTP client is included and no actual MiroFish run has been executed or validated by this release.** Source material is untrusted data, never new execution instructions. See [simulation integration](references/12-simulation-integration.md).

Adopting role constraints and feedback does not prove forecasting value. Compare the old skill, the new structured-perspective process and genuine dynamic simulation against identical evidence snapshots and simple baselines. See [prediction evaluation](references/13-prediction-evaluation.md).

## Data and risk boundaries

Separate FACT/GUIDANCE/CONSENSUS/MODEL/INFERENCE/UNKNOWN, event and disclosure dates, evidence cutoff and sources. Missing inputs block only dependent conclusions; never substitute zero. Short Interest differs from daily Short Volume; high SI is Fuel, not automatically a Trigger. 13F is delayed and incomplete, GEX is not a dealer ledger and Call OI does not establish newly opened bullish positions. Crowding affects paths, not automatically DCF or long-term margins.

DMI defaults to 14 periods: +DI/-DI describe direction, ADX strength. Rising ADX does not mean rising prices; crossovers are not standalone trade signals. Technical levels are not intrinsic values; transaction anchors are not hard floors. Early option exits require separate price×time×IV models; 1−Delta is not a loss probability. Agent votes or simulation frequencies are not real-world probabilities or option EV inputs.

No broker connection, automatic trading, background service or return promise is included. Tests cover software rules and bundle consistency, not host behavior, live data, MiroFish execution or investment performance. See [VALIDATION.md](VALIDATION.md).

## Maintenance and provenance

`SKILL.md` is the entry point; references contain research rules; assets contain templates and fictional examples; scripts implement arithmetic, quarantine import and packaging; tests provide regressions. `bundle-files.json` is an explicit distribution allowlist. `PACKAGE-MANIFEST.json` inside the ZIP hashes every source file except itself. Historical migration records and old ZIPs remain in the repository, outside the new install package.

Use independent semantic versions on `main`. Synchronize entry/configuration/bilingual READMEs/CHANGELOG/MIGRATION/VALIDATION/download links, run tests, package and verify before releasing through a PR. Published ZIPs are immutable; a same-version content conflict is rejected. `shared_rules_version` is a bundled-rules label, not an external runtime dependency.

[ABOUT.md](ABOUT.md) contains proposed repository metadata and its maintenance boundary; its existence does not prove GitHub sidebar settings changed. Migration originated from GammaLens commit `2c2de5790f93a698b25b31660bc5c5fe1ea97dbe`; the [historical provenance manifest](https://github.com/RickyyyFu/single-stock-deep-research-skill/blob/main/MIGRATION-PROVENANCE.json) is preserved. GammaLens and the screening repository are unchanged. See [CHANGELOG.md](CHANGELOG.md).
