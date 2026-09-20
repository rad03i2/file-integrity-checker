from __future__ import annotations

import hashlib
import json
import os
import tempfile
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

SCHEMA_VERSION = 1


@dataclass(frozen=True)
class FileRecord:
    path: str
    size: int
    mtime_ns: int
    sha256: str


@dataclass(frozen=True)
class Change:
    path: str
    status: str
    expected_sha256: str | None = None
    actual_sha256: str | None = None


def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _hidden(relative: Path) -> bool:
    return any(part.startswith(".") for part in relative.parts)


def iter_files(root: Path, include_hidden: bool = False) -> Iterable[Path]:
    root = root.resolve()
    for current, dirs, files in os.walk(root, followlinks=False):
        current_path = Path(current)
        dirs[:] = [d for d in dirs if not (current_path / d).is_symlink()]
        if not include_hidden:
            dirs[:] = [d for d in dirs if not d.startswith(".")]
        for name in files:
            path = current_path / name
            relative = path.relative_to(root)
            if path.is_symlink() or (not include_hidden and _hidden(relative)):
                continue
            if path.is_file():
                yield path


def build_baseline(root: Path, include_hidden: bool = False) -> dict:
    root = root.expanduser().resolve()
    if not root.is_dir():
        raise ValueError(f"Not a directory: {root}")
    records = []
    for path in sorted(iter_files(root, include_hidden), key=lambda p: p.as_posix().lower()):
        stat = path.stat()
        records.append(FileRecord(path.relative_to(root).as_posix(), stat.st_size, stat.st_mtime_ns, sha256_file(path)))
    return {
        "schema_version": SCHEMA_VERSION,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "root": str(root),
        "algorithm": "sha256",
        "files": [asdict(record) for record in records],
    }


def save_baseline(data: dict, destination: Path, overwrite: bool = False) -> None:
    destination = destination.expanduser().resolve()
    if destination.exists() and not overwrite:
        raise FileExistsError(f"Baseline already exists: {destination}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(data, indent=2, ensure_ascii=False, sort_keys=True) + "\n"
    fd, temp_name = tempfile.mkstemp(prefix=f".{destination.name}.", dir=destination.parent, text=True)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_name, destination)
    except Exception:
        try:
            os.unlink(temp_name)
        except FileNotFoundError:
            pass
        raise


def load_baseline(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("schema_version") != SCHEMA_VERSION or data.get("algorithm") != "sha256":
        raise ValueError("Unsupported or invalid baseline format")
    if not isinstance(data.get("files"), list) or not isinstance(data.get("root"), str):
        raise ValueError("Malformed baseline")
    return data


def verify(baseline: dict, root: Path | None = None, include_hidden: bool = False) -> list[Change]:
    target = (root or Path(baseline["root"])).expanduser().resolve()
    if not target.is_dir():
        raise ValueError(f"Not a directory: {target}")
    expected = {item["path"]: item for item in baseline["files"]}
    actual_paths = {p.relative_to(target).as_posix(): p for p in iter_files(target, include_hidden)}
    changes: list[Change] = []
    for relative, item in expected.items():
        path = actual_paths.pop(relative, None)
        if path is None:
            changes.append(Change(relative, "missing", item["sha256"], None))
            continue
        digest = sha256_file(path)
        if digest != item["sha256"]:
            changes.append(Change(relative, "modified", item["sha256"], digest))
    for relative, path in actual_paths.items():
        changes.append(Change(relative, "added", None, sha256_file(path)))
    return sorted(changes, key=lambda c: (c.path.lower(), c.status))


def report_dict(changes: list[Change]) -> dict:
    counts = {"added": 0, "modified": 0, "missing": 0}
    for change in changes:
        counts[change.status] += 1
    return {"ok": not changes, "summary": counts, "changes": [asdict(c) for c in changes]}
