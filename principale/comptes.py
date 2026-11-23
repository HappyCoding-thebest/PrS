"""Gestion locale de profils Instagram, sans mots de passe ni jetons."""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any

MAX_ACCOUNTS = 10
USERNAME_PATTERN = re.compile(r"^[A-Za-z0-9._]{1,30}$")


class AccountError(ValueError):
    """Erreur de validation ou de gestion d'un profil local."""


def list_accounts(config: dict[str, Any]) -> list[dict[str, str]]:
    return list(config.get("accounts", []))


def add_account(config: dict[str, Any], username: str) -> dict[str, str]:
    normalized = username.strip().lstrip("@")
    if not USERNAME_PATTERN.fullmatch(normalized):
        raise AccountError("Identifiant invalide : utilise 1 à 30 lettres, chiffres, points ou tirets bas.")
    accounts = config.setdefault("accounts", [])
    if any(item.get("username", "").casefold() == normalized.casefold() for item in accounts):
        raise AccountError("Ce profil est déjà enregistré.")
    if len(accounts) >= MAX_ACCOUNTS:
        raise AccountError(f"La limite de {MAX_ACCOUNTS} profils locaux est atteinte.")
    account = {
        "username": normalized,
        "added_at": datetime.now(timezone.utc).isoformat(),
        "status": "local_non_connecte",
    }
    accounts.append(account)
    if not config.get("active_account"):
        config["active_account"] = normalized
    return account


def choose_account(config: dict[str, Any], username: str) -> dict[str, str]:
    match = next(
        (
            item
            for item in config.get("accounts", [])
            if item.get("username", "").casefold() == username.strip().lstrip("@").casefold()
        ),
        None,
    )
    if match is None:
        raise AccountError("Profil introuvable.")
    config["active_account"] = match["username"]
    return match


def remove_account(config: dict[str, Any], username: str) -> dict[str, str]:
    target = username.strip().lstrip("@").casefold()
    accounts = config.get("accounts", [])
    match = next((item for item in accounts if item.get("username", "").casefold() == target), None)
    if match is None:
        raise AccountError("Profil introuvable.")
    accounts.remove(match)
    if config.get("active_account", "").casefold() == target:
        config["active_account"] = accounts[0]["username"] if accounts else None
    return match


def active_account(config: dict[str, Any]) -> str | None:
    return config.get("active_account")
