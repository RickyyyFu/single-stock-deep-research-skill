"""Auditable conditional valuation arithmetic; no data feed, agent, or price predictor.

Python 3.11+, standard library only. Every amount is in base currency units;
share counts are individual shares, never millions. Input assertions are not
independently verified by this program. See references/11-scenario-valuation.md.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import sys
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

VERSION = "3.5.0"
SCHEMA_VERSION = "1.0.0"
MAX_BYTES = 2_000_000
CLAIMS = {"FACT", "GUIDANCE", "CONSENSUS", "MODEL", "INFERENCE", "UNKNOWN"}
SOURCES = {"PRIMARY", "CONSENSUS_PROVIDER", "USER_SUPPLIED", "ASSUMPTION", "SIMULATION", "ILLUSTRATIVE"}


class InputError(ValueError):
    """An explicit input gap, unsupported model, or inconsistent contract."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise InputError(message)


def text(value: Any, label: str) -> str:
    require(isinstance(value, str) and bool(value.strip()), f"{label}: nonempty text required")
    return value


def obj(value: Any, label: str) -> dict:
    require(isinstance(value, dict), f"{label}: object required")
    return value


def items(value: Any, label: str, allow_empty: bool = False) -> list:
    require(isinstance(value, list) and (allow_empty or bool(value)), f"{label}: list required")
    return value


def timestamp(value: Any, label: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(text(value, label).replace("Z", "+00:00"))
    except (ValueError, TypeError) as exc:
        raise InputError(f"{label}: ISO timestamp required") from exc
    require(parsed.tzinfo is not None, f"{label}: timezone required")
    return parsed.astimezone(timezone.utc)


def day(value: Any, label: str) -> date:
    require(isinstance(value, str) and bool(re.fullmatch(r"\d{4}-\d{2}-\d{2}", value)), f"{label}: YYYY-MM-DD required")
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise InputError(f"{label}: invalid date") from exc


def finite(value: Any, label: str) -> float:
    require(type(value) in (int, float), f"{label}: numeric value required; missing data is not zero")
    try:
        number = float(value)
    except (ValueError, OverflowError) as exc:
        raise InputError(f"{label}: number outside supported range") from exc
    require(math.isfinite(number), f"{label}: finite number required")
    return number


def unique_object(pairs: list[tuple[str, Any]]) -> dict:
    result = {}
    for key, value in pairs:
        require(key not in result, f"duplicate JSON key: {key}")
        result[key] = value
    return result


def reject_constant(value: str) -> None:
    raise InputError(f"nonfinite JSON constant: {value}")


def load_json(path: Path) -> tuple[dict, str]:
    raw = path.read_bytes()
    require(len(raw) <= MAX_BYTES, "input exceeds 2 MB")
    try:
        data = json.loads(raw.decode("utf-8"), object_pairs_hook=unique_object, parse_constant=reject_constant)
    except (UnicodeError, ValueError, RecursionError) as exc:
        raise InputError(f"invalid UTF-8 JSON: {exc}") from exc
    return obj(data, "input"), hashlib.sha256(raw).hexdigest()


class Evidence:
    def __init__(self, records: Any, cutoff: datetime, illustrative: bool):
        self.records: dict[str, dict] = {}
        self.illustrative = illustrative
        for record in items(records, "evidence"):
            record = obj(record, "evidence record")
            key = text(record.get("id"), "evidence.id")
            require(key not in self.records, f"duplicate evidence id: {key}")
            require(record.get("claim_type") in CLAIMS, f"{key}: invalid claim_type")
            require(record.get("source_type") in SOURCES, f"{key}: invalid source_type")
            text(record.get("source"), f"{key}.source")
            text(record.get("limitation"), f"{key}.limitation")
            require(timestamp(record.get("published_at"), f"{key}.published_at") <= cutoff, f"{key}: publication after cutoff")
            require(timestamp(record.get("data_as_of"), f"{key}.data_as_of") <= cutoff, f"{key}: observed data after cutoff; forecasts belong in period")
            if record["source_type"] == "SIMULATION":
                require(record["claim_type"] == "MODEL", f"{key}: simulation must remain MODEL")
                require(record.get("verification_status") == "UNVERIFIED", f"{key}: simulation is not verified real-world evidence")
            if record["source_type"] == "ILLUSTRATIVE":
                require(illustrative, f"{key}: illustrative evidence cannot enter RESEARCH")
            self.records[key] = record
        for record in self.records.values():
            for parent in items(record.get("parent_ids", []), "parent_ids", True):
                require(isinstance(parent, str) and parent in self.records, f"{record['id']}: unknown parent")
        for key in self.records:
            self._grounded(key, set())  # Validate all dependency cycles, including unused records.

    def _grounded(self, key: str, visited: set[str]) -> bool:
        require(len(visited) < 64, "evidence provenance exceeds 64 levels")
        require(key not in visited, f"{key}: cyclic evidence provenance")
        rec = self.records[key]
        visited = visited | {key}
        parent_results = [self._grounded(parent, visited) for parent in rec.get("parent_ids", [])]
        observed = (rec["source_type"] in {"PRIMARY", "CONSENSUS_PROVIDER", "USER_SUPPLIED"}
                    and rec["claim_type"] in {"FACT", "GUIDANCE", "CONSENSUS"}
                    and rec.get("verification_status") == "VERIFIED")
        return observed or any(parent_results)

    def numeric_refs(self, refs: Any, label: str) -> None:
        for key in items(refs, f"{label}.evidence_ids"):
            require(isinstance(key, str) and key in self.records, f"{label}: unknown evidence id {key!r}")
            rec = self.records[key]
            require(rec["source_type"] != "SIMULATION", f"{label}: simulation is hypothesis-only, not a numeric source")
            require(rec["claim_type"] != "UNKNOWN", f"{label}: UNKNOWN cannot substantiate a numeric input")
            if self.illustrative and rec["source_type"] == "ILLUSTRATIVE":
                continue
            if rec["source_type"] == "ASSUMPTION":
                require(rec["claim_type"] == "MODEL", f"{label}: assumption must be MODEL")
                require(rec.get("verification_status") == "REVIEWED_ASSUMPTION", f"{label}: assumption review required")
                text(rec.get("rationale"), f"{key}.rationale")
                require(self._grounded(key, set()), f"{label}: model assumption needs dated nonsimulation grounding")
            else:
                require(rec.get("verification_status") == "VERIFIED", f"{label}: unresolved evidence")
                require(self._grounded(key, set()), f"{label}: no eligible grounding")

    def number(self, spec: Any, unit: str, label: str, minimum: float | None = None,
               maximum: float | None = None, positive: bool = False) -> float:
        spec = obj(spec, label)
        require(spec.get("unit") == unit, f"{label}: expected unit {unit}, no implicit scaling or FX")
        text(spec.get("period"), f"{label}.period")
        text(spec.get("rationale"), f"{label}.rationale")
        self.numeric_refs(spec.get("evidence_ids"), label)
        number = finite(spec.get("value"), label)
        require(minimum is None or number >= minimum, f"{label}: below minimum")
        require(maximum is None or number <= maximum, f"{label}: above maximum")
        require(not positive or number > 0, f"{label}: must be positive")
        return number


def equity_bridge(ev: float, capital: Any, evidence: Evidence, currency: str, valuation_date: str) -> dict:
    c = obj(capital, "capital")
    require(c.get("as_of") == valuation_date, "capital must be measured at valuation date")
    require(c.get("share_basis") == "period_end_economic", "EV bridge requires period-end economic shares")
    require(c.get("equity_scope") in {"parent_common", "total_economic"}, "capital equity_scope required")
    text(c.get("capital_notes"), "capital_notes")
    def n(key: str, unit: str = currency, **kw: Any) -> float:
        spec = obj(c.get(key), f"capital.{key}")
        require(spec.get("period") == valuation_date, f"capital.{key}: period must match capital.as_of")
        return evidence.number(spec, unit, f"capital.{key}", **kw)
    cash, debt = n("cash", minimum=0), n("debt", minimum=0)
    preferred, nci = n("preferred", minimum=0), n("noncontrolling", minimum=0)
    other = n("other_claims", minimum=0)
    if c["equity_scope"] == "total_economic":
        require(nci == 0, "do not deduct NCI for economic units already included in denominator")
    shares = n("economic_shares", "shares", positive=True)
    new = n("new_common_shares", "shares", minimum=0)
    issue = n("issue_price", f"{currency}/share", minimum=0)
    fee = n("issuance_fee_rate", "ratio", minimum=0, maximum=1)
    burn = n("incremental_burn", minimum=0)
    require(type(c.get("burn_already_in_ev")) is bool, "burn_already_in_ev must be explicit")
    require(not (burn > 0 and c["burn_already_in_ev"]), "cash burn already included in EV must not be deducted again")
    require(new == 0 or issue > 0, "positive issuance needs a positive issue price")
    require(new > 0 or (issue == 0 and fee == 0), "without issuance, issue_price and issuance_fee_rate must be explicit zero")
    before = ev + cash - debt - preferred - nci - other
    proceeds = new * issue * (1 - fee)
    after = before + proceeds - burn
    require(after > 0, "nonpositive residual equity: review distress/option value; do not print a negative share price")
    return {"operating_ev": ev, "equity_before_new_issuance": before,
            "net_issuance_proceeds": proceeds, "equity_after_bridge": after,
            "economic_shares_after_issuance": shares + new,
            "price": after / (shares + new)}


def calculate(model: Any, evidence: Evidence, currency: str, valuation_date: str) -> dict:
    model = obj(model, "model")
    method = model.get("method")
    text(model.get("applicability"), "model.applicability")
    def n(key: str, unit: str = currency, **kw: Any) -> float:
        return evidence.number(model.get(key), unit, f"model.{key}", **kw)
    if method == "earnings_multiple":
        require("capital" not in model, "EPS already uses diluted shares; do not apply a second capital dilution bridge")
        require(model.get("earnings_basis") in {"GAAP", "ADJUSTED"}, "explicit earnings_basis required")
        require(model.get("share_basis") == "diluted_weighted_average", "earnings require diluted weighted-average shares")
        period = text(model.get("earnings_period"), "earnings_period")
        require(bool(re.fullmatch(r"FY\d{4}|NTM@\d{4}-\d{2}-\d{2}", period)), "earnings_period must be annual FYyyyy or NTM@YYYY-MM-DD, not a quarter")
        if period.startswith("NTM@"):
            require(day(period[4:], "NTM anchor") == day(valuation_date, "valuation date"), "NTM anchor must match valuation date")
        require(model.get("period_months") == 12, "earnings model requires 12 months, not a quarter")
        require(model.get("multiple_period") == period, "EPS and PE periods must match")
        require(model.get("multiple_basis") == model["earnings_basis"], "GAAP/adjusted EPS and PE must match")
        for key in ("net_interest_expense", "other_pretax_income", "tax_rate", "noncontrolling_net_income", "preferred_dividends", "diluted_shares", "pe"):
            require(obj(model.get(key), key).get("period") == period, f"{key}: input period must match earnings_period")
        text(model.get("multiple_rationale"), "multiple_rationale")
        require(model.get("consolidation") == "external_only", "earnings segments must exclude intersegment sales")
        revenue, operating = 0.0, 0.0
        names: set[str] = set()
        for segment in items(model.get("segments"), "segments"):
            segment = obj(segment, "segment")
            name = text(segment.get("name"), "segment.name")
            require(name not in names, "duplicate segment name")
            names.add(name)
            for key in ("revenue", "operating_margin"):
                require(obj(segment.get(key), key).get("period") == period, f"{name}.{key}: mismatched earnings period")
            r = evidence.number(segment.get("revenue"), currency, f"{name}.revenue", minimum=0)
            margin = evidence.number(segment.get("operating_margin"), "ratio", f"{name}.operating_margin", maximum=1)
            revenue += r
            operating += r * margin
        pretax = operating - n("net_interest_expense") + n("other_pretax_income")
        tax = n("tax_rate", "ratio", minimum=0, maximum=1)
        consolidated_net = pretax * (1 - tax)
        net = consolidated_net - n("noncontrolling_net_income") - n("preferred_dividends", minimum=0)
        require(net > 0, "PE is not applicable to nonpositive net earnings")
        shares = n("diluted_shares", "shares", positive=True)
        eps = net / shares
        pe = n("pe", "multiple", positive=True)
        result = {"method": method, "consolidated_external_revenue": revenue,
                  "operating_profit": operating, "pretax_income": pretax,
                  "consolidated_net_income": consolidated_net, "common_net_income": net,
                  "net_income": net, "diluted_eps": eps, "pe": pe, "price": eps * pe}
    elif method == "sotp":
        values = []
        names = set()
        for segment in items(model.get("segments"), "segments"):
            segment = obj(segment, "segment")
            name = text(segment.get("name"), "segment.name")
            require(name not in names, "duplicate segment name")
            names.add(name)
            require(segment.get("value_basis") == "enterprise_value", "SOTP segments must share EV basis; no mixing equity values")
            require(obj(segment.get("enterprise_value"), name).get("period") == valuation_date, "SOTP values must use valuation date")
            values.append(evidence.number(segment.get("enterprise_value"), currency, f"{name}.enterprise_value"))
        require(obj(model.get("intersegment_ev_elimination"), "elimination").get("period") == valuation_date, "SOTP elimination must use valuation date")
        elimination = n("intersegment_ev_elimination", minimum=0)
        result = {"method": method, "segment_ev_sum": sum(values), "intersegment_ev_elimination": elimination,
                  **equity_bridge(sum(values) - elimination, model.get("capital"), evidence, currency, valuation_date)}
    elif method == "fcff_dcf":
        for key in ("wacc", "terminal_growth"):
            require(obj(model.get(key), key).get("period") == valuation_date, f"{key}: valuation date required")
        wacc = n("wacc", "ratio", positive=True, maximum=1)
        g = n("terminal_growth", "ratio", minimum=-0.99)
        require(g < wacc, "terminal growth must be below WACC")
        require(model.get("cashflow_basis") == "FCFF", "WACC model accepts FCFF only, not FCFE/CFO")
        anchor = day(valuation_date, "valuation_date")
        previous = anchor
        pv, flows, last_t, last_fcff = 0.0, [], 0.0, 0.0
        for idx, row in enumerate(items(model.get("annual_cashflows"), "annual_cashflows")):
            row = obj(row, "cashflow")
            end = day(row.get("date"), "cashflow.date")
            require(end > previous, "cashflow dates must be strictly increasing and after valuation date")
            require(330 <= (end - previous).days <= 400, "v1 calculator requires approximately annual periods; use an external model for stubs")
            previous = end
            def f(key: str, **kw: Any) -> float:
                spec = obj(row.get(key), key)
                require(spec.get("period") == end.isoformat(), f"cashflow[{idx}].{key}: period must match cashflow date")
                return evidence.number(spec, currency, f"cashflow[{idx}].{key}", **kw)
            # Explicit cash operating tax avoids inventing immediate loss tax shields.
            fcff = f("ebit") - f("cash_operating_tax", minimum=0) + f("da", minimum=0) - f("capex", minimum=0) - f("change_nwc")
            years = (end - anchor).days / 365.25
            discounted = fcff / (1 + wacc) ** years
            pv += discounted
            last_t, last_fcff = years, fcff
            flows.append({"date": end.isoformat(), "fcff": fcff, "pv": discounted})
        require(last_fcff > 0, "perpetuity needs positive normalized terminal FCFF; use a longer explicit model")
        terminal = last_fcff * (1 + g) / (wacc - g)
        terminal_pv = terminal / (1 + wacc) ** last_t
        ev = pv + terminal_pv
        require(ev > 0, "nonpositive EV requires a different valuation model")
        result = {"method": method, "cashflows": flows, "explicit_pv": pv, "terminal_pv": terminal_pv,
                  "terminal_ev_share": terminal_pv / ev,
                  **equity_bridge(ev, model.get("capital"), evidence, currency, valuation_date)}
        if terminal_pv / ev >= 0.7:
            result["warning"] = "TERMINAL_VALUE_DOMINATED_LOW_CONFIDENCE"
    else:
        raise InputError(f"unsupported method {method!r}; use an independently reviewed sector model")
    require(math.isfinite(result["price"]), "computed price outside finite range")
    return result


def evaluate(payload: dict) -> dict:
    obj(payload, "input")
    require(payload.get("schema_version") == SCHEMA_VERSION, "unsupported schema_version")
    require(payload.get("input_mode") in {"ILLUSTRATIVE", "RESEARCH"}, "explicit input_mode required")
    illustrative = payload["input_mode"] == "ILLUSTRATIVE"
    cutoff = timestamp(payload.get("data_cutoff"), "data_cutoff")
    local_date = datetime.fromisoformat(payload["data_cutoff"].replace("Z", "+00:00")).date()
    symbol = text(payload.get("symbol"), "symbol")
    currency = text(payload.get("currency"), "currency")
    require(bool(re.fullmatch(r"[A-Z]{3}", currency)), "currency must be three uppercase letters")
    text(payload.get("research_id"), "research_id")
    evidence = Evidence(payload.get("evidence"), cutoff, illustrative)
    results, ids = [], set()
    for scenario in items(payload.get("scenarios"), "scenarios"):
        scenario = obj(scenario, "scenario")
        sid = text(scenario.get("id"), "scenario.id")
        require(sid not in ids, "duplicate scenario id")
        ids.add(sid)
        result = {"id": sid, "label": scenario.get("label"), "target_date": scenario.get("target_date"),
                  "price_kind": scenario.get("price_kind"), "currency": currency, "claim_type": "MODEL"}
        try:
            text(scenario.get("label"), "label")
            target = day(scenario.get("target_date"), "target_date")
            kind = scenario.get("price_kind")
            require(kind in {"CURRENT_INTRINSIC", "DATED_SCENARIO"}, "technical levels are not valuation outputs")
            require(target == local_date if kind == "CURRENT_INTRINSIC" else target > local_date,
                    "current intrinsic must use research date; dated scenario must be in the future")
            require(scenario.get("probability") is None, "probabilities/agent votes are not accepted by this calculator; no automatic EV")
            for field in ("conditions", "invalidation"):
                for val in items(scenario.get(field), field):
                    text(val, field)
            for step in items(scenario.get("path"), "path", kind == "CURRENT_INTRINSIC"):
                step = obj(step, "path step")
                for key in ("event", "participant", "constraint", "response", "model_variable", "falsifier"):
                    text(step.get(key), f"path.{key}")
                observed = day(step.get("observe_by"), "path.observe_by")
                require(local_date <= observed <= target, "path checkpoint must fall between research and target dates")
            center = calculate(scenario.get("model"), evidence, currency, target.isoformat())
            result.update(status="ILLUSTRATIVE_NOT_FORECAST" if illustrative else "CALCULATED_MODEL_NOT_VALIDATED",
                          center_price=center["price"], calculation=center,
                          conditions=scenario["conditions"], invalidation=scenario["invalidation"], path=scenario["path"])
            variants = items(scenario.get("sensitivity_models", []), "sensitivity_models", True)
            if variants:
                values, errors = [center["price"]], []
                for idx, model in enumerate(variants):
                    try:
                        values.append(calculate(model, evidence, currency, target.isoformat())["price"])
                    except (InputError, OverflowError) as exc:
                        errors.append(f"sensitivity[{idx}]: {exc}")
                result["sensitivity"] = ({"status": "BLOCKED", "errors": errors} if errors else {
                    "status": "PARAMETER_RANGE_NOT_CONFIDENCE_INTERVAL", "low": min(values), "high": max(values),
                    "evaluated_model_count": len(values), "central_is_not_a_mode": True})
        except (InputError, OverflowError) as exc:
            result.update(status="BLOCKED", center_price=None, error=str(exc))
        results.append(result)
    return {"skill_version": VERSION, "schema_version": SCHEMA_VERSION, "research_id": payload["research_id"],
            "symbol": symbol, "data_cutoff": payload["data_cutoff"], "input_mode": payload["input_mode"],
            "real_world_source_verification": "NOT_PERFORMED_BY_CALCULATOR",
            "prediction_validation": "NOT_PERFORMED", "external_model_calls": 0, "results": results}


def write_json(path: Path, value: dict) -> None:
    # Never overwrite a prior forecast snapshot implicitly.
    with path.open("x", encoding="utf-8") as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2, allow_nan=False)
        handle.write("\n")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    try:
        data, digest = load_json(args.input)
        result = evaluate(data)
        result["input_sha256"] = digest
        if args.output:
            write_json(args.output, result)
        else:
            print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))
        return 2 if any(r["status"] == "BLOCKED" or r.get("sensitivity", {}).get("status") == "BLOCKED" for r in result["results"]) else 0
    except (ValueError, OSError, TypeError, KeyError, RecursionError) as exc:
        print(f"input/output error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
