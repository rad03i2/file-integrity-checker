from pathlib import Path

from file_integrity_checker.cli import main


def test_cli_round_trip_and_exit_codes(tmp_path: Path, capsys):
    root = tmp_path / "files"
    root.mkdir()
    (root / "a.txt").write_text("one", encoding="utf-8")
    baseline = tmp_path / "baseline.json"
    assert main(["init", str(root), "-o", str(baseline)]) == 0
    assert main(["check", str(baseline)]) == 0
    (root / "a.txt").write_text("two", encoding="utf-8")
    assert main(["check", str(baseline), "--json"]) == 1
    assert '"modified": 1' in capsys.readouterr().out


def test_cli_invalid_root_returns_error(tmp_path: Path):
    assert main(["init", str(tmp_path / "missing")]) == 2
