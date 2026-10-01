from copy import deepcopy
import pytest
from lost_deal_analyzer.core import analyze, InputError
from lost_deal_analyzer.fixtures import fixture_document


@pytest.mark.parametrize('field,value', [('amount_minor', -1), ('amount_minor', True), ('amount_minor', 10**16), ('closed_on', '2026-10-01'), ('name', 'x'*10001), ('reason', 'invented'), ('status', 'invalid')])
def test_rejects_adversarial_values(field, value):
    doc = fixture_document()
    doc['records'][0][field] = value
    with pytest.raises(InputError, match=field):
        analyze([('input.json', doc)])


def test_duplicate_ids_and_schema_drift():
    doc = fixture_document()
    doc['records'][1]['id'] = doc['records'][0]['id']
    with pytest.raises(InputError, match='duplicate id'):
        analyze([('input.json', doc)])
    doc = fixture_document()
    doc['unexpected'] = 1
    with pytest.raises(InputError, match='unexpected'):
        analyze([('input.json', doc)])


def test_handles_unicode_and_long_inputs():
    doc = fixture_document()
    doc['records'][0]['name'] = '客户 café C:\\Users\\henry ' + 'a'*9000
    assert analyze([('客户.json', doc)])['total_records'] == 200


def test_corrupted_ground_truth_changes_output():
    doc = fixture_document()
    before = analyze([('input.json', doc)])
    changed = deepcopy(doc)
    changed['records'][0]['reason'] = 'timing'
    changed['records'][0]['amount_minor'] = 1
    after = analyze([('input.json', changed)])
    assert after['reasons']['budget']['count'] == before['reasons']['budget']['count'] - 1
    assert after['reasons']['timing']['count'] == 21
    assert after['lost_amount_minor'] == 1190001


def test_five_record_real_input():
    doc = fixture_document()
    doc.update(synthetic=False, provenance="Henry's own data, entered by him")
    doc['records'] = [dict(id='a', name='A', status='lost', reason='budget', amount_minor=12, closed_on='2026-09-30'), dict(id='b', name='B', status='lost', reason='unknown', amount_minor=7, closed_on='2026-09-30'), dict(id='c', name='C', status='won', reason=None, amount_minor=3, closed_on='2026-09-30'), dict(id='d', name='D', status='open', reason=None, amount_minor=4, closed_on=None), dict(id='e', name='E', status='lost', reason='timing', amount_minor=9, closed_on='2026-09-30')]
    result = analyze([('real.json', doc)])
    assert result['status_counts'] == {'lost': 3, 'won': 1, 'open': 1}
    assert result['total_amount_minor'] == 35
    assert result['lost_amount_minor'] == 28
