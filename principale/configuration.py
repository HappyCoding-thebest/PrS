"""Configuration locale et chemins privés de CONSTANT."""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any


class ConfigurationError(ValueError):
    """Erreur explicite de lecture ou de validation de la configuration."""


def data_directory() -> Path:
    override = os.environ.get("CONSTANT_HOME")
    if override:
        return Path(override).expanduser()

    if os.name == "nt" and os.environ.get("LOCALAPPDATA"):
        return Path(os.environ["LOCALAPPDATA"]) / "CONSTANT"

    return Path.home() / ".local" / "share" / "constant"


def paths() -> dict[str, Path]:
    root = data_directory()
    return {
        "root": root,
        "config": root / "config.json",
        "publications": root / "publications.txt",
        "profiles": root / "profils.txt",
        "journal": root / "journal.jsonl",
        "reports": root / "rapports",
    }


def ensure_private_directories() -> dict[str, Path]:
    result = paths()
    for key in ("root", "reports"):
        result[key].mkdir(parents=True, exist_ok=True)
        if os.name != "nt":
            result[key].chmod(0o700)
    return result


def default_config() -> dict[str, Any]:
    return {
        "schema_version": 1,
        "ui": {"animations": True},
        "security": {"password_salt": None, "password_hash": None},
        "active_account": None,
        "accounts": [],
    }


def _atomic_json_write(destination: Path, data: dict[str, Any]) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    temp_name: str | None = None
    try:
        with tempfile.NamedTemporaryFile(
            "w",
            encoding="utf-8",
            dir=destination.parent,
            prefix=f".{destination.name}.",
            suffix=".tmp",
            delete=False,
        ) as stream:
            temp_name = stream.name
            json.dump(data, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
        temp_path = Path(temp_name)
        if os.name != "nt":
            temp_path.chmod(0o600)
        os.replace(temp_path, destination)
        if os.name != "nt":
            destination.chmod(0o600)
    finally:
        if temp_name:
            Path(temp_name).unlink(missing_ok=True)


def save_config(config: dict[str, Any]) -> None:
    if config.get("schema_version") != 1:
        raise ConfigurationError("Version de configuration non prise en charge.")
    if not isinstance(config.get("ui"), dict) or not isinstance(config.get("security"), dict):
        raise ConfigurationError("La configuration locale est invalide.")
    if not isinstance(config.get("accounts"), list):
        raise ConfigurationError("La liste locale des comptes est invalide.")
    _atomic_json_write(ensure_private_directories()["config"], config)


def load_config() -> dict[str, Any]:
    config_path = ensure_private_directories()["config"]
    if not config_path.exists():
        config = default_config()
        save_config(config)
        return config

    try:
        with config_path.open("r", encoding="utf-8") as stream:
            config = json.load(stream)
    except (OSError, json.JSONDecodeError) as exc:
        raise ConfigurationError(
            f"Impossible de lire {config_path}. Corrige ou sauvegarde ce fichier avant de relancer."
        ) from exc

    if not isinstance(config, dict):
        raise ConfigurationError("La configuration locale doit être un objet JSON.")
    if config.get("schema_version") != 1:
        raise ConfigurationError("Version de configuration non prise en charge.")
    if not isinstance(config.get("ui"), dict) or not isinstance(config.get("security"), dict):
        raise ConfigurationError("La configuration locale est incomplète ou invalide.")
    if not isinstance(config.get("accounts"), list):
        raise ConfigurationError("La liste locale des comptes est invalide.")
    return config
