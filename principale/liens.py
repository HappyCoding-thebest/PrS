"""Validation et stockage privé des liens Instagram."""

from __future__ import annotations

import os
import re
import tempfile
from pathlib import Path
from urllib.parse import urlsplit

from .configuration import ensure_private_directories

ALLOWED_HOSTS = {"instagram.com", "www.instagram.com", "m.instagram.com"}
POST_PATH = re.compile(r"^/(?:p|reel|reels|tv)/([A-Za-z0-9_-]+)/?$", re.IGNORECASE)
PROFILE_PATH = re.compile(r"^/([A-Za-z0-9._]{1,30})/?$")
RESERVED_PROFILES = {
    "about", "accounts", "api", "challenge", "developer", "direct", "emails",
    "explore", "legal", "login", "oauth", "p", "privacy", "reel", "reels",
    "stories", "tv",
}


class LinkError(ValueError):
    """URL absente, invalide ou incompatible avec la catégorie."""


def normalize_instagram_url(value: str, kind: str) -> str:
    if kind not in {"publication", "profil"}:
        raise LinkError("Type de lien inconnu.")
    raw = value.strip()
    if not raw:
        raise LinkError("Le lien est vide.")
    if "://" not in raw:
        raw = f"https://{raw}"
    try:
        parts = urlsplit(raw)
        hostname = (parts.hostname or "").casefold()
        port = parts.port
    except ValueError as exc:
        raise LinkError("URL mal formée.") from exc
    if parts.scheme.casefold() != "https":
        raise LinkError("Seules les URL HTTPS sont acceptées.")
    if (
        hostname not in ALLOWED_HOSTS
        or "@" in parts.netloc
        or parts.username
        or parts.password
        or port not in (None, 443)
    ):
        raise LinkError("Le domaine doit être instagram.com, sans identifiant ni port inhabituel.")

    path = parts.path or ""
    if "%" in path or "\\" in path:
        raise LinkError("Le chemin du lien contient des caractères non acceptés.")
    if kind == "publication":
        if not POST_PATH.fullmatch(path):
            raise LinkError("Attendu : un lien Instagram de publication, reel ou vidéo.")
    else:
        match = PROFILE_PATH.fullmatch(path)
        if (
            not match
            or match.group(1).casefold() in RESERVED_PROFILES
            or match.group(1).startswith(".")
            or match.group(1).endswith(".")
            or ".." in match.group(1)
        ):
            raise LinkError("Attendu : un lien vers un profil Instagram.")
    return f"https://www.instagram.com/{path.strip('/')}/"


def _link_file(kind: str) -> Path:
    file_key = {"publication": "publications", "profil": "profiles"}.get(kind)
    if file_key is None:
        raise LinkError("Type de lien inconnu.")
    return ensure_private_directories()[file_key]


def read_links(kind: str) -> list[str]:
    path = _link_file(kind)
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8") as stream:
        return list(dict.fromkeys(line.strip() for line in stream if line.strip()))


def save_links(kind: str, links: list[str]) -> None:
    path = _link_file(kind)
    unique = list(dict.fromkeys(link.strip() for link in links if link.strip()))
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_name: str | None = None
    try:
        with tempfile.NamedTemporaryFile(
            "w", encoding="utf-8", dir=path.parent, prefix=f".{path.name}.",
            suffix=".tmp", delete=False,
        ) as stream:
            temporary_name = stream.name
            for link in unique:
                stream.write(f"{link}\n")
        temporary_path = Path(temporary_name)
        if os.name != "nt":
            temporary_path.chmod(0o600)
        os.replace(temporary_path, path)
        if os.name != "nt":
            path.chmod(0o600)
    finally:
        if temporary_name:
            Path(temporary_name).unlink(missing_ok=True)


def add_link(kind: str, value: str) -> bool:
    normalized = normalize_instagram_url(value, kind)
    links = read_links(kind)
    if normalized in links:
        return False
    links.append(normalized)
    save_links(kind, links)
    return True


def import_links(kind: str, source: Path) -> tuple[int, int]:
    with source.expanduser().open("r", encoding="utf-8-sig") as stream:
        candidates = [line.strip() for line in stream if line.strip() and not line.lstrip().startswith("#")]
    existing = read_links(kind)
    accepted = 0
    rejected = 0
    for candidate in candidates:
        try:
            normalized = normalize_instagram_url(candidate, kind)
        except LinkError:
            rejected += 1
            continue
        if normalized not in existing:
            existing.append(normalized)
            accepted += 1
        else:
            rejected += 1
    save_links(kind, existing)
    return accepted, rejected


def remove_link(kind: str, value: str) -> bool:
    normalized = normalize_instagram_url(value, kind)
    links = read_links(kind)
    if normalized not in links:
        return False
    links.remove(normalized)
    save_links(kind, links)
    return True


def demo_links(kind: str, count: int = 5) -> list[str]:
    if kind not in {"publication", "profil"}:
        raise LinkError("Type de lien inconnu.")
    if not 1 <= count <= 20:
        raise LinkError("Le nombre de liens de démonstration doit être compris entre 1 et 20.")
    if kind == "publication":
        return [f"https://instagram.example.invalid/p/DEMO{i:04d}/" for i in range(1, count + 1)]
    return [f"https://instagram.example.invalid/demo_profile_{i:02d}/" for i in range(1, count + 1)]
