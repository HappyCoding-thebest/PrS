"""Authentification locale de démonstration, sans compte Instagram."""

from __future__ import annotations

import base64
import hashlib
import hmac
import os
from collections.abc import Callable
from getpass import getpass
from typing import Any

PASSWORD_ITERATIONS = 310_000
MAX_ATTEMPTS = 3


def password_is_configured(config: dict[str, Any]) -> bool:
    security = config.get("security", {})
    return bool(security.get("password_salt") and security.get("password_hash"))


def set_local_password(config: dict[str, Any], password: str) -> None:
    if len(password) < 8:
        raise ValueError("Le mot de passe local doit contenir au moins 8 caractères.")
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, PASSWORD_ITERATIONS)
    config.setdefault("security", {})["password_salt"] = base64.b64encode(salt).decode("ascii")
    config["security"]["password_hash"] = base64.b64encode(digest).decode("ascii")


def verify_local_password(config: dict[str, Any], candidate: str) -> bool:
    security = config.get("security", {})
    try:
        salt = base64.b64decode(security["password_salt"], validate=True)
        expected = base64.b64decode(security["password_hash"], validate=True)
    except (KeyError, TypeError, ValueError):
        return False
    actual = hashlib.pbkdf2_hmac("sha256", candidate.encode("utf-8"), salt, PASSWORD_ITERATIONS)
    return hmac.compare_digest(actual, expected)


def demo_license_status(config: dict[str, Any]) -> dict[str, str | bool]:
    return {
        "mode": "démo locale",
        "valid": password_is_configured(config),
        "notice": "Cette protection locale n'est pas une licence commerciale ni une sécurité serveur.",
    }


def configure_local_password(
    config: dict[str, Any],
    prompt: Callable[[str], str] = getpass,
) -> None:
    for _ in range(MAX_ATTEMPTS):
        first = prompt("Choisis un mot de passe local (8 caractères minimum) : ")
        second = prompt("Confirme le mot de passe : ")
        if first != second:
            print("Les deux saisies ne correspondent pas.")
            continue
        try:
            set_local_password(config, first)
        except ValueError as exc:
            print(exc)
            continue
        return
    raise RuntimeError("Configuration du mot de passe annulée après plusieurs erreurs.")


def login(
    config: dict[str, Any],
    prompt: Callable[[str], str] = getpass,
) -> bool:
    for attempt in range(1, MAX_ATTEMPTS + 1):
        if verify_local_password(config, prompt("Mot de passe CONSTANT : ")):
            return True
        remaining = MAX_ATTEMPTS - attempt
        if remaining:
            print(f"Mot de passe incorrect. Tentatives restantes : {remaining}.")
    return False
