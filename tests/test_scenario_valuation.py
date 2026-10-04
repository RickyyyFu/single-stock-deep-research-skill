import contextlib
import copy
import io
import json
import math
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.scenario_valuation import InputError, evaluate, load_json, main, write_json
from scenario_fixtures import TARGET, payload, three_scenarios


class ValuationTests(unittest.TestCase):
    def result(self, p):
        return evaluate(p)['results'][0]

    def blocked(self, p, part=None):
        r = self.result(p)
        self.assertEqual(r['status'], 'BLOCKED')
        self.assertIsNone(r['center_price'])
        if part:
            self.assertIn(part, r['error'])

    def change(self, key, value):
        p = payload()
        p['scenarios'][0]['model'][key] = value
        return p

    def test_earnings_from_operations(self):
        r = self.result(payload())
        self.assertEqual(r['status'], 'ILLUSTRATIVE_NOT_FORECAST')
        self.assertAlmostEqual(r['calculation']['diluted_eps'], 1.44)
        self.assertAlmostEqual(r['center_price'], 28.8)

    def test_common_income_excludes_nci_and_preferred(self):
        p = payload()
        m = p['scenarios'][0]['model']
        m['noncontrolling_net_income']['value'] = 10_000_000
        m['preferred_dividends']['value'] = 2_000_000
        self.assertAlmostEqual(self.result(p)['center_price'], 26.4)

    def test_attribution_must_be_explicit(self):
        p = payload()
        del p['scenarios'][0]['model']['noncontrolling_net_income']
        self.blocked(p, 'noncontrolling_net_income')

    def test_invalid_ntm_date(self):
        self.blocked(self.change('earnings_period', 'NTM@2027-02-31'), 'invalid date')

    def test_profit_growth_with_multiple_compression(self):
        p = payload()
        m = p['scenarios'][0]['model']
        m['segments'][0]['operating_margin']['value'] = .24
        m['pe']['value'] = 14
        self.assertGreater(self.result(p)['calculation']['net_income'], 144_000_000)
        self.assertLess(self.result(p)['center_price'], 28.8)

    def test_three_dated_scenarios(self):
        r = evaluate(three_scenarios())
        self.assertEqual(len(r['results']), 3)
        self.assertEqual(r['external_model_calls'], 0)
        self.assertEqual(r['prediction_validation'], 'NOT_PERFORMED')
        self.assertTrue(all(x['target_date'] == TARGET for x in r['results']))

    def test_sensitivity_not_confidence_interval(self):
        r = evaluate(three_scenarios())['results'][1]['sensitivity']
        self.assertEqual(r['status'], 'PARAMETER_RANGE_NOT_CONFIDENCE_INTERVAL')
        self.assertAlmostEqual(r['low'], 25.92)
        self.assertAlmostEqual(r['high'], 31.68)
        self.assertTrue(r['central_is_not_a_mode'])

    def test_bad_sensitivity_does_not_destroy_center(self):
        p = three_scenarios()
        p['scenarios'][1]['sensitivity_models'][0]['pe']['value'] = None
        r = evaluate(p)['results'][1]
        self.assertEqual(r['status'], 'ILLUSTRATIVE_NOT_FORECAST')
        self.assertEqual(r['sensitivity']['status'], 'BLOCKED')

    def test_quarter_not_annual(self):
        self.blocked(self.change('earnings_period', 'Q12027'), 'annual')

    def test_twelve_months_required(self):
        self.blocked(self.change('period_months', 3), '12 months')

    def test_pe_period_must_match(self):
        self.blocked(self.change('multiple_period', 'FY2028'), 'periods')

    def test_pe_basis_must_match(self):
        self.blocked(self.change('multiple_basis', 'ADJUSTED'), 'GAAP')

    def test_earnings_share_basis(self):
        self.blocked(self.change('share_basis', 'basic'), 'weighted-average')

    def test_no_double_dilution(self):
        self.blocked(self.change('capital', {}), 'second capital')

    def test_intersegment_sales_excluded(self):
        self.blocked(self.change('consolidation', 'gross'), 'intersegment')

    def test_no_missing_to_zero(self):
        p = payload()
        del p['scenarios'][0]['model']['net_interest_expense']
        self.blocked(p)

    def test_no_implicit_millions(self):
        p = payload()
        p['scenarios'][0]['model']['segments'][0]['revenue']['unit'] = 'USD millions'
        self.blocked(p, 'unit')

    def test_no_boolean_number(self):
        p = payload()
        p['scenarios'][0]['model']['pe']['value'] = True
        self.blocked(p, 'numeric')

    def test_no_nan(self):
        p = payload()
        p['scenarios'][0]['model']['pe']['value'] = float('nan')
        self.blocked(p, 'finite')

    def test_no_infinite_input(self):
        p = payload()
        p['scenarios'][0]['model']['pe']['value'] = float('inf')
        self.blocked(p, 'finite')

    def test_no_zero_shares(self):
        p = payload()
        p['scenarios'][0]['model']['diluted_shares']['value'] = 0
        self.blocked(p, 'positive')

    def test_pe_rejects_losses(self):
        p = payload()
        p['scenarios'][0]['model']['segments'][0]['operating_margin']['value'] = -.1
        self.blocked(p, 'nonpositive')

    def test_no_negative_pe(self):
        p = payload()
        p['scenarios'][0]['model']['pe']['value'] = -1
        self.blocked(p, 'positive')

    def test_margin_cannot_exceed_one(self):
        p = payload()
        p['scenarios'][0]['model']['segments'][0]['operating_margin']['value'] = 1.2
        self.blocked(p, 'maximum')

    def test_no_duplicate_segments(self):
        p = payload()
        m = p['scenarios'][0]['model']
        m['segments'] *= 2
        self.blocked(p, 'duplicate segment')

    def test_sotp_ev_bridge(self):
        r = self.result(payload('sotp'))
        self.assertAlmostEqual(r['center_price'], 20)
        self.assertEqual(r['calculation']['operating_ev'], 2_100_000_000)

    def test_sotp_no_mixed_equity_ev(self):
        p = payload('sotp')
        p['scenarios'][0]['model']['segments'][0]['value_basis'] = 'equity_value'
        self.blocked(p, 'EV basis')

    def test_sotp_date_mismatch(self):
        p = payload('sotp')
        p['scenarios'][0]['model']['segments'][0]['enterprise_value']['period'] = '2026-10-04'
        self.blocked(p, 'valuation date')

    def test_fair_value_financing_invariant(self):
        p = payload('sotp')
        c = p['scenarios'][0]['model']['capital']
        c['new_common_shares']['value'] = 20_000_000
        c['issue_price']['value'] = 20
        self.assertAlmostEqual(self.result(p)['center_price'], 20)

    def test_discounted_financing_reduces_price(self):
        p = payload('sotp')
        c = p['scenarios'][0]['model']['capital']
        c['new_common_shares']['value'] = 20_000_000
        c['issue_price']['value'] = 10
        self.assertAlmostEqual(self.result(p)['center_price'], 2_200_000_000 / 120_000_000)

    def test_financing_costs_reduce_price(self):
        p = payload('sotp')
        c = p['scenarios'][0]['model']['capital']
        c['new_common_shares']['value'] = 20_000_000
        c['issue_price']['value'] = 20
        c['issuance_fee_rate']['value'] = .02
        self.assertAlmostEqual(self.result(p)['calculation']['net_issuance_proceeds'], 392_000_000)

    def test_burn_not_twice(self):
        p = payload('sotp')
        c = p['scenarios'][0]['model']['capital']
        c['incremental_burn']['value'] = 1
        c['burn_already_in_ev'] = True
        self.blocked(p, 'again')

    def test_total_economic_no_duplicate_nci(self):
        p = payload('sotp')
        c = p['scenarios'][0]['model']['capital']
        c['equity_scope'] = 'total_economic'
        c['noncontrolling']['value'] = 1
        self.blocked(p, 'NCI')

    def test_distress_not_negative_stock_price(self):
        p = payload('sotp')
        p['scenarios'][0]['model']['capital']['debt']['value'] = 9_000_000_000
        self.blocked(p, 'distress')

    def test_capital_date_matches_target(self):
        p = payload('sotp')
        p['scenarios'][0]['model']['capital']['as_of'] = '2026-10-04'
        self.blocked(p, 'valuation date')

    def test_positive_issuance_needs_price(self):
        p = payload('sotp')
        p['scenarios'][0]['model']['capital']['new_common_shares']['value'] = 1
        self.blocked(p, 'issue price')

    def test_fcff_discount_matches_independent_formula(self):
        r = self.result(payload('fcff_dcf'))
        times = [(date(y, 10, 4) - date(2027, 10, 4)).days / 365.25 for y in range(2028, 2033)]
        ev = sum(130_000_000 / 1.1**t for t in times) + (130_000_000*1.02/.08)/1.1**times[-1]
        self.assertAlmostEqual(r['center_price'], (ev-100_000_000)/100_000_000)
        self.assertEqual(r['calculation']['cashflows'][0]['fcff'], 130_000_000)

    def test_terminal_growth_below_wacc(self):
        p = payload('fcff_dcf')
        p['scenarios'][0]['model']['terminal_growth']['value'] = .1
        self.blocked(p, 'below WACC')

    def test_fcfe_rejected_in_wacc_model(self):
        p = payload('fcff_dcf')
        p['scenarios'][0]['model']['cashflow_basis'] = 'FCFE'
        self.blocked(p, 'FCFF')

    def test_dcf_rejects_cashflow_before_target(self):
        p = payload('fcff_dcf')
        p['scenarios'][0]['model']['annual_cashflows'][0]['date'] = '2027-01-01'
        self.blocked(p, 'after valuation')

    def test_dcf_no_quarter_as_annual(self):
        p = payload('fcff_dcf')
        p['scenarios'][0]['model']['annual_cashflows'][0]['date'] = '2028-01-04'
        self.blocked(p, 'annual periods')

    def test_no_automatic_loss_tax_shield(self):
        p = payload('fcff_dcf')
        p['scenarios'][0]['model']['annual_cashflows'][0]['cash_operating_tax']['value'] = -1
        self.blocked(p, 'minimum')

    def test_nonpositive_terminal_fcff(self):
        p = payload('fcff_dcf')
        p['scenarios'][0]['model']['annual_cashflows'][-1]['capex']['value'] = 1_000_000_000
        self.blocked(p, 'normalized terminal')

    def test_current_intrinsic_uses_research_date(self):
        p = payload()
        s = p['scenarios'][0]
        s.update(price_kind='CURRENT_INTRINSIC', target_date='2026-10-04', path=[])
        self.assertEqual(self.result(p)['status'], 'ILLUSTRATIVE_NOT_FORECAST')

    def test_current_intrinsic_future_rejected(self):
        p = payload()
        p['scenarios'][0]['price_kind'] = 'CURRENT_INTRINSIC'
        self.blocked(p, 'research date')

    def test_technical_level_not_valuation(self):
        p = payload()
        p['scenarios'][0]['price_kind'] = 'TECHNICAL_SUPPORT'
        self.blocked(p, 'technical')

    def test_dated_target_must_be_future(self):
        p = payload()
        p['scenarios'][0]['target_date'] = '2026-10-04'
        self.blocked(p, 'future')

    def test_no_probability_from_votes(self):
        p = payload()
        p['scenarios'][0]['probability'] = .7
        self.blocked(p, 'probabilities')

    def test_dated_scenario_needs_path(self):
        p = payload()
        p['scenarios'][0]['path'] = []
        self.blocked(p, 'path')

    def test_checkpoint_cannot_follow_target(self):
        p = payload()
        p['scenarios'][0]['path'][0]['observe_by'] = '2028-01-01'
        self.blocked(p, 'checkpoint')

    def test_missing_condition_blocked(self):
        p = payload()
        p['scenarios'][0]['conditions'] = []
        self.blocked(p, 'conditions')

    def test_missing_invalidation_blocked(self):
        p = payload()
        p['scenarios'][0]['invalidation'] = []
        self.blocked(p, 'invalidation')

    def test_block_is_local_to_scenario(self):
        p = three_scenarios()
        p['scenarios'][0]['model']['pe']['value'] = None
        r = evaluate(p)['results']
        self.assertEqual(r[0]['status'], 'BLOCKED')
        self.assertEqual(r[1]['status'], 'ILLUSTRATIVE_NOT_FORECAST')
        self.assertEqual(r[2]['status'], 'ILLUSTRATIVE_NOT_FORECAST')

    def test_unknown_method_blocked(self):
        self.blocked(self.change('method', 'bank_fcff'), 'unsupported')

    def test_published_after_cutoff_rejected(self):
        p = payload()
        p['evidence'][0]['published_at'] = '2026-10-05T01:00:00Z'
        with self.assertRaisesRegex(InputError, 'publication'):
            evaluate(p)

    def test_cutoff_requires_timezone(self):
        p = payload()
        p['data_cutoff'] = '2026-10-04T10:00:00'
        with self.assertRaisesRegex(InputError, 'timezone'):
            evaluate(p)

    def test_duplicate_evidence_id(self):
        p = payload()
        p['evidence'] *= 2
        with self.assertRaisesRegex(InputError, 'duplicate evidence'):
            evaluate(p)

    def test_cyclic_provenance(self):
        p = payload()
        p['evidence'][0]['parent_ids'] = ['synthetic-1']
        with self.assertRaisesRegex(InputError, 'cyclic'):
            evaluate(p)

    def test_unknown_evidence_ref(self):
        p = payload()
        p['scenarios'][0]['model']['pe']['evidence_ids'] = ['missing']
        self.blocked(p, 'unknown evidence')

    def test_simulation_cannot_become_fact(self):
        p = payload()
        p['evidence'][0].update(source_type='SIMULATION', claim_type='FACT')
        with self.assertRaisesRegex(InputError, 'MODEL'):
            evaluate(p)

    def test_simulation_cannot_supply_numeric_input(self):
        p = payload()
        p['evidence'][0]['source_type'] = 'SIMULATION'
        self.blocked(p, 'hypothesis-only')

    def test_illustrative_cannot_enter_research(self):
        p = payload()
        p['input_mode'] = 'RESEARCH'
        with self.assertRaisesRegex(InputError, 'illustrative'):
            evaluate(p)

    def test_research_does_not_claim_source_verified_by_program(self):
        p = payload()
        p['input_mode'] = 'RESEARCH'
        p['evidence'][0].update(source_type='PRIMARY', claim_type='FACT', verification_status='VERIFIED')
        r = evaluate(p)
        self.assertEqual(r['results'][0]['status'], 'CALCULATED_MODEL_NOT_VALIDATED')
        self.assertEqual(r['real_world_source_verification'], 'NOT_PERFORMED_BY_CALCULATOR')

    def test_assumption_requires_independent_grounding(self):
        p = payload()
        p['evidence'][0].update(source_type='ASSUMPTION', verification_status='REVIEWED_ASSUMPTION', rationale='Test')
        self.blocked(p, 'grounding')

    def test_reviewed_assumption_with_primary_parent(self):
        p = payload()
        p['input_mode'] = 'RESEARCH'
        parent = copy.deepcopy(p['evidence'][0])
        parent.update(id='primary', source_type='PRIMARY', claim_type='GUIDANCE', verification_status='VERIFIED')
        p['evidence'][0].update(source_type='ASSUMPTION', verification_status='REVIEWED_ASSUMPTION',
                                rationale='Explicitly reviewed fictional test assumption', parent_ids=['primary'])
        p['evidence'].append(parent)
        self.assertEqual(self.result(p)['status'], 'CALCULATED_MODEL_NOT_VALIDATED')

    def test_duplicate_json_keys_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td)/'a.json'
            path.write_text('{"a":1,"a":2}')
            with self.assertRaisesRegex(InputError, 'duplicate'):
                load_json(path)

    def test_json_nan_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td)/'a.json'
            path.write_text('{"a":NaN}')
            with self.assertRaisesRegex(InputError, 'nonfinite'):
                load_json(path)

    def test_snapshot_not_overwritten(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td)/'out.json'
            write_json(path, {'a': 1})
            with self.assertRaises(FileExistsError):
                write_json(path, {'a': 2})
            self.assertEqual(json.loads(path.read_text()), {'a': 1})

    def test_cli_synthetic_example_success(self):
        with tempfile.TemporaryDirectory() as td:
            path, out = Path(td)/'in.json', Path(td)/'out.json'
            path.write_text(json.dumps(payload()))
            self.assertEqual(main([str(path), '--output', str(out)]), 0)
            self.assertEqual(len(json.loads(out.read_text())['input_sha256']), 64)

    def test_cli_rejects_overwrite(self):
        with tempfile.TemporaryDirectory() as td, contextlib.redirect_stderr(io.StringIO()):
            path, out = Path(td)/'in.json', Path(td)/'out.json'
            path.write_text(json.dumps(payload()))
            out.write_text('keep')
            self.assertEqual(main([str(path), '--output', str(out)]), 2)
            self.assertEqual(out.read_text(), 'keep')

    def test_cli_blocked_sensitivity_exit_two(self):
        with tempfile.TemporaryDirectory() as td:
            p = three_scenarios()
            p['scenarios'][1]['sensitivity_models'][0]['pe']['value'] = -1
            path, out = Path(td)/'in.json', Path(td)/'out.json'
            path.write_text(json.dumps(p))
            self.assertEqual(main([str(path), '--output', str(out)]), 2)


if __name__ == '__main__':
    unittest.main()
