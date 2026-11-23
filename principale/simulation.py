"""Simulation locale : aucune requête ni interaction Instagram réelle."""

from __future__ import annotations

import random
import time
from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True)
class SimulationResult:
    total: int
    traite: int
    ignores: int
    erreurs: int
    duree_secondes: float
    details: tuple[tuple[str, str], ...]


def run_simulation(
    links: list[str],
    *,
    error_rate: float = 0.1,
    delay: float = 0.0,
    random_value: Callable[[], float] | None = None,
    on_item: Callable[[int, str, str], None] | None = None,
) -> SimulationResult:
    if not 0 <= error_rate <= 1:
        raise ValueError("Le taux d'erreur doit être compris entre 0 et 1.")
    if delay < 0:
        raise ValueError("Le délai ne peut pas être négatif.")
    chooser = random_value or random.random
    started = time.monotonic()
    details: list[tuple[str, str]] = []
    ignored = 0
    errors = 0
    for index, link in enumerate(links, start=1):
        if not link.strip():
            ignored += 1
            status = "ignoré : lien vide"
        elif chooser() < error_rate:
            errors += 1
            status = "erreur simulée"
        else:
            status = "traité en simulation"
        details.append((link, status))
        if on_item:
            on_item(index, link, status)
        if delay:
            time.sleep(delay)
    elapsed = time.monotonic() - started
    return SimulationResult(
        total=len(links),
        traite=len(links) - ignored - errors,
        ignores=ignored,
        erreurs=errors,
        duree_secondes=elapsed,
        details=tuple(details),
    )
