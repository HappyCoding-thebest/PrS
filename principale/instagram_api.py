"""Accès manuel aux liens et état honnête des fonctions API officielles."""

from __future__ import annotations

import shutil
import subprocess
import webbrowser


class OfficialOAuthUnavailable(RuntimeError):
    """L'application ne possède pas encore de client OAuth Meta configuré."""


def official_api_status() -> str:
    return (
        "Connexion OAuth officielle non configurée : aucun jeton n'est demandé ou stocké. "
        "Les interactions avec des tiers restent manuelles."
    )


def connect_official_account() -> None:
    raise OfficialOAuthUnavailable(
        "OAuth Instagram officiel indisponible : il faut d'abord une application Meta approuvée "
        "et une URI de redirection configurée. CONSTANT ne demande jamais le mot de passe Instagram."
    )


def open_instagram_url(url: str) -> bool:
    termux_open = shutil.which("termux-open-url")
    if termux_open:
        result = subprocess.run([termux_open, url], check=False, capture_output=True, text=True)
        return result.returncode == 0
    return bool(webbrowser.open(url, new=2, autoraise=False))
