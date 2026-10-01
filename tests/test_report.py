import json
from lost_deal_analyzer.core import analyze
from lost_deal_analyzer.fixtures import fixture_document, expectations
from lost_deal_analyzer.report import render


def result():
    return analyze([('opportunities.json', fixture_document())])


def test_report_matches_ground_truth_exact():
    report = json.loads(render(result(), 'json'))
    for key, value in expectations().items():
        if key not in ('synthetic', 'label'):
            assert report[key] == value


def test_report_zero_false_positives():
    doc = fixture_document()
    report = result()
    for reason, group in report['reasons'].items():
        expected = {r['id'] for r in doc['records'] if r['status'] == 'lost' and r['reason'] == reason}
        assert set(group['record_ids']) == expected
    assert sum(g['count'] for g in report['reasons'].values()) == 120


def test_report_carries_provenance_banner():
    for format in ('md', 'json'):
        assert 'DATA PROVENANCE:' in render(result(), format)
        assert 'synthetic fixture' in render(result(), format)


def test_hypothetical_figures_labelled():
    for format in ('md', 'json'):
        text = render(result(), format)
        assert 'Time saved and money saved are unmeasured and are not reported' in text
        assert 'not independently verified causes' in text


def test_no_em_dashes_in_outputs():
    for format in ('md', 'json'):
        assert '\u2014' not in render(result(), format)
