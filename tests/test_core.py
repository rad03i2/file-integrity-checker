import json
from pathlib import Path

import pytest

from file_integrity_checker.core import build_baseline, load_baseline, report_dict, save_baseline, verify


def test_clean_then_detect_all_change_types(tmp_path: Path):
    root = tmp_path / "data"
    root.mkdir()
    (root / "same.txt").write_text("same", encoding="utf-8")
    (root / "modify.txt").write_text("before", encoding="utf-8")
    (root / "remove.txt").write_text("gone", encoding="utf-8")
    baseline = build_baseline(root)
    assert verify(baseline, root) == []

    (root / "modify.txt").write_text("after", encoding="utf-8")
    (root / "remove.txt").unlink()
    (root / "new.txt").write_text("new", encoding="utf-8")
    changes = verify(baseline, root)
    assert {(c.path, c.status) for c in changes} == {
        ("modify.txt", "modified"), ("remove.txt", "missing"), ("new.txt", "added")
    }
    report = report_dict(changes)
    assert report["ok"] is False
    assert report["summary"] == {"added": 1, "modified": 1, "missing": 1}


def test_hidden_and_symlink_are_safe_by_default(tmp_path: Path):
    root = tmp_path / "data"
    root.mkdir()
    (root / "visible.txt").write_text("v", encoding="utf-8")
    (root / ".secret").write_text("s", encoding="utf-8")
    baseline = build_baseline(root)
    assert [f["path"] for f in baseline["files"]] == ["visible.txt"]
    assert {f["path"] for f in build_baseline(root, True)["files"]} == {"visible.txt", ".secret"}


def test_save_load_and_overwrite_guard(tmp_path: Path):
    root = tmp_path / "data"
    root.mkdir()
    (root / "a.bin").write_bytes(b"abc")
    baseline = build_baseline(root)
    output = tmp_path / "baseline.json"
    save_baseline(baseline, output)
    assert load_baseline(output)["files"] == baseline["files"]
    with pytest.raises(FileExistsError):
        save_baseline(baseline, output)
    save_baseline(baseline, output, overwrite=True)
    json.loads(output.read_text(encoding="utf-8"))


def test_rejects_invalid_baseline(tmp_path: Path):
    path = tmp_path / "bad.json"
    path.write_text('{"schema_version": 99, "algorithm": "md5", "files": []}', encoding="utf-8")
    with pytest.raises(ValueError):
        load_baseline(path)


def test_root_override_verifies_copy(tmp_path: Path):
    original = tmp_path / "original"
    copy = tmp_path / "copy"
    original.mkdir(); copy.mkdir()
    (original / "a.txt").write_text("content", encoding="utf-8")
    (copy / "a.txt").write_text("content", encoding="utf-8")
    assert verify(build_baseline(original), copy) == []
