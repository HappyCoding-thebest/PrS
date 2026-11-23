"""Journal local sans jetons ni mots de passe et export CSV/JSON."""

from __future__ import annotations

import csv
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .configuration import ensure_private_directories

FIELDS = ("date_utc", "compte", "operation", "url", "statut", "duree_ms", "message")


def _journal_path() -> Path:
    return ensure_private_directories()["journal"]


def record(
    *,
    account: str | None,
    operation: str,
    url: str = "",
    status: str,
    duration_ms: int = 0,
    message: str = "",
) -> dict[str, Any]:
    entry = {
        "date_utc": datetime.now(timezone.utc).isoformat(),
        "compte": account or "",
        "operation": operation[:80],
        "url": url.split("?", 1)[0].split("#", 1)[0][:500],
        "statut": status[:80],
        "duree_ms": max(0, int(duration_ms)),
        "message": message.replace("\n", " ")[:300],
    }
    path = _journal_path()
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)
    with os.fdopen(descriptor, "a", encoding="utf-8") as stream:
        stream.write(json.dumps(entry, ensure_ascii=False) + "\n")
    if os.name != "nt":
        path.chmod(0o600)
    return entry


def read_entries() -> list[dict[str, Any]]:
    path = _journal_path()
    if not path.exists():
        return []
    entries: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as stream:
        for line_number, line in enumerate(stream, start=1):
            if not line.strip():
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"Entrée de journal invalide à la ligne {line_number}.") from exc
            if isinstance(entry, dict):
                entries.append(entry)
    return entries


def export_report(format_name: str) -> Path:
    if format_name not in {"csv", "json"}:
        raise ValueError("Format d'export non pris en charge.")
    entries = read_entries()
    reports = ensure_private_directories()["reports"]
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    destination = reports / f"historique-{timestamp}.{format_name}"
    temp_name: str | None = None
    try:
        with tempfile.NamedTemporaryFile(
            "w", encoding="utf-8", newline="", dir=reports,
            prefix=".rapport.", suffix=".tmp", delete=False,
        ) as stream:
            temp_name = stream.name
            if format_name == "json":
                json.dump(entries, stream, ensure_ascii=False, indent=2)
                stream.write("\n")
            else:
                writer = csv.DictWriter(stream, fieldnames=FIELDS, extrasaction="ignore")
                writer.writeheader()
                writer.writerows(entries)
        temp_path = Path(temp_name)
        if os.name != "nt":
            temp_path.chmod(0o600)
        os.replace(temp_path, destination)
        if os.name != "nt":
            destination.chmod(0o600)
    finally:
        if temp_name:
            Path(temp_name).unlink(missing_ok=True)
    return destination
