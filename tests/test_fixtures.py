import json
from lost_deal_analyzer.fixtures import generate, expectations
from lost_deal_analyzer.core import analyze
from lost_deal_analyzer.cli import load_inputs


def test_fixtures_labelled_synthetic(tmp_path):
    generate(tmp_path)
    for path in tmp_path.glob('*.json'):
        assert json.loads(path.read_text())['synthetic'] is True
    assert 'Synthetic' in (tmp_path / 'SYNTHETIC.md').read_text()


def test_fixture_ground_truth_matches_hand_computed(tmp_path):
    generate(tmp_path)
    result = analyze(load_inputs(tmp_path))
    for key, value in expectations().items():
        if key not in ('synthetic', 'label'):
            assert result[key] == value
