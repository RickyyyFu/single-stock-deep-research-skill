"""Fictional data for engineering tests only; never an investment forecast."""
from copy import deepcopy

TARGET = '2027-10-04'
PERIOD = 'FY2027'


def number(value, unit='USD', period=PERIOD):
    return {'value': value, 'unit': unit, 'period': period,
            'rationale': 'Fictional engineering input, not a forecast.',
            'evidence_ids': ['synthetic-1']}


def capital(target=TARGET):
    result = {'as_of': target, 'share_basis': 'period_end_economic',
              'equity_scope': 'parent_common', 'burn_already_in_ev': False,
              'capital_notes': 'Fictional common equity only; no contingent rights.'}
    for key, value, unit in [('cash', 100_000_000, 'USD'), ('debt', 200_000_000, 'USD'),
                             ('preferred', 0, 'USD'), ('noncontrolling', 0, 'USD'),
                             ('other_claims', 0, 'USD'), ('economic_shares', 100_000_000, 'shares'),
                             ('new_common_shares', 0, 'shares'), ('issue_price', 0, 'USD/share'),
                             ('issuance_fee_rate', 0, 'ratio'), ('incremental_burn', 0, 'USD')]:
        result[key] = number(value, unit, target)
    return result


def earnings():
    return {'method': 'earnings_multiple', 'applicability': 'Fictional profitable company test.',
            'earnings_basis': 'GAAP', 'multiple_basis': 'GAAP',
            'share_basis': 'diluted_weighted_average', 'earnings_period': PERIOD,
            'period_months': 12, 'multiple_period': PERIOD,
            'multiple_rationale': 'Illustrative PE, not sourced market valuation.',
            'consolidation': 'external_only',
            'segments': [{'name': 'external', 'revenue': number(1_000_000_000),
                          'operating_margin': number(.2, 'ratio')}],
            'net_interest_expense': number(20_000_000), 'other_pretax_income': number(0),
            'tax_rate': number(.2, 'ratio'), 'noncontrolling_net_income': number(0),
            'preferred_dividends': number(0), 'diluted_shares': number(100_000_000, 'shares'),
            'pe': number(20, 'multiple')}


def sotp():
    return {'method': 'sotp', 'applicability': 'Fictional all-EV segments for arithmetic tests.',
            'segments': [{'name': 'base', 'value_basis': 'enterprise_value',
                          'enterprise_value': number(2_000_000_000, period=TARGET)},
                         {'name': 'new', 'value_basis': 'enterprise_value',
                          'enterprise_value': number(200_000_000, period=TARGET)}],
            'intersegment_ev_elimination': number(100_000_000, period=TARGET),
            'capital': capital()}


def dcf():
    flows = []
    for year in range(2028, 2033):
        period = f'{year}-10-04'
        row = {'date': period}
        for key, value in [('ebit', 200_000_000), ('cash_operating_tax', 40_000_000),
                           ('da', 30_000_000), ('capex', 50_000_000), ('change_nwc', 10_000_000)]:
            row[key] = number(value, period=period)
        flows.append(row)
    return {'method': 'fcff_dcf', 'applicability': 'Fictional annual FCFF test, normalized final year.',
            'cashflow_basis': 'FCFF', 'wacc': number(.1, 'ratio', TARGET),
            'terminal_growth': number(.02, 'ratio', TARGET),
            'annual_cashflows': flows, 'capital': capital()}


def payload(method='earnings_multiple'):
    model = {'earnings_multiple': earnings, 'sotp': sotp, 'fcff_dcf': dcf}[method]()
    return {'schema_version': '1.0.0', 'input_mode': 'ILLUSTRATIVE',
            'research_id': 'FICTIONAL-ENGINEERING-EXAMPLE', 'symbol': 'DEMO_CO', 'currency': 'USD',
            'data_cutoff': '2026-10-04T18:00:00+08:00',
            'evidence': [{'id': 'synthetic-1', 'source_type': 'ILLUSTRATIVE', 'claim_type': 'MODEL',
                          'verification_status': 'UNVERIFIED', 'source': 'urn:example:fictional',
                          'published_at': '2026-10-04T09:00:00Z', 'data_as_of': '2026-10-04T09:00:00Z',
                          'parent_ids': [], 'limitation': 'All inputs fictional; no live stock, agency or market data.'}],
            'scenarios': [{'id': 'base', 'label': '虚构公司：基础参数验算，不是预测',
                           'target_date': TARGET, 'price_kind': 'DATED_SCENARIO', 'probability': None,
                           'conditions': ['Fictional operating and capital assumptions hold.'],
                           'invalidation': ['Actual verified inputs differ; replace this example entirely.'],
                           'path': [{'event': 'Fictional demand remains at the assumed level.',
                                     'participant': 'Hypothetical customer', 'constraint': 'Fixed budget',
                                     'response': 'Maintain purchases', 'model_variable': 'segments.external.revenue',
                                     'falsifier': 'Verified order cancellations', 'observe_by': '2027-07-01'}],
                           'model': model}]}


def three_scenarios():
    p = payload()
    base = p['scenarios'][0]
    bear, bull = deepcopy(base), deepcopy(base)
    bear.update(id='bear', label='虚构公司：压力参数验算，不是预测')
    bear['model']['segments'][0]['operating_margin']['value'] = .15
    bear['model']['pe']['value'] = 15
    bull.update(id='bull', label='虚构公司：较强参数验算，不是预测')
    bull['model']['segments'][0]['operating_margin']['value'] = .25
    bull['model']['pe']['value'] = 25
    low, high = deepcopy(base['model']), deepcopy(base['model'])
    low['pe']['value'], high['pe']['value'] = 18, 22
    base['sensitivity_models'] = [low, high]
    p['scenarios'] = [bear, base, bull]
    return p
