import json
import time
import pytest
from lost_deal_analyzer.cli import main
from lost_deal_analyzer.fixtures import generate


def test_run_completes_on_fixture(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    start = time.perf_counter()
    assert main(['fixtures', '--out', 'demo']) == 0
    assert main(['run', '--input', 'demo']) == 0
    assert main(['report', '--format', 'md']) == 0
    assert time.perf_counter() - start < 5
    assert 'DATA PROVENANCE' in capsys.readouterr().out


def test_empty_input_renders_without_traceback(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    (tmp_path / 'empty').mkdir()
    assert main(['run', '--input', 'empty']) == 0
    assert main(['report']) == 0
    assert 'Records: 0' in capsys.readouterr().out


def test_malformed_input_named_error(tmp_path, capsys):
    (tmp_path / 'bad.json').write_text('{\n"records": !}', encoding='utf-8')
    assert main(['audit', '--input', str(tmp_path)]) == 2
    error = capsys.readouterr().err
    assert 'ParseError: bad.json: line 2' in error


def test_determinism_byte_identical(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    generate('demo')
    main(['run', '--input', 'demo'])
    before = (tmp_path / '.lda/result.json').read_bytes()
    main(['run', '--input', 'demo'])
    assert before == (tmp_path / '.lda/result.json').read_bytes()
    main(['report', '--out', 'a.md'])
    main(['report', '--out', 'b.md'])
    assert (tmp_path / 'a.md').read_bytes() == (tmp_path / 'b.md').read_bytes()


def test_cli_smoke_all_subcommands(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    for command in ('fixtures', 'run', 'report', 'reasons', 'audit'):
        with pytest.raises(SystemExit) as exc:
            main([command, '--help'])
        assert exc.value.code == 0
    assert main(['fixtures', '--out', 'demo']) == 0
    for command in ('run', 'reasons', 'audit'):
        assert main([command, '--input', 'demo']) == 0
    assert main(['report', '--format', 'json']) == 0


def test_missing_input_and_atomic_write_failure(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    assert main(['run', '--input', 'missing']) == 2
    assert 'MissingInput' in capsys.readouterr().err
    generate('demo')
    assert main(['run', '--input', 'demo']) == 0
    assert main(['report', '--out', 'absent/report.md']) == 2
    assert 'WriteError' in capsys.readouterr().err
    assert not (tmp_path / 'absent').exists()


def test_duplicate_json_keys(tmp_path, capsys):
    (tmp_path / 'bad.json').write_text('{"synthetic":true,"synthetic":false}')
    assert main(['audit', '--input', str(tmp_path)]) == 2
    assert 'duplicate JSON field' in capsys.readouterr().err
