"""Composants de terminal adaptatifs pour CONSTANT."""

from __future__ import annotations

import os
import time
from collections.abc import Iterable

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt
from rich.table import Table
from rich.text import Text

from . import __version__

console = Console(highlight=False, soft_wrap=True)

MENU_OPTIONS = (
    (1, "👤 Ajouter un compte Instagram"),
    (2, "📋 Afficher mes comptes"),
    (3, "🔗 Choisir un compte actif"),
    (4, "🗑️ Supprimer un compte"),
    (5, "📥 Importer des liens Instagram"),
    (6, "🔎 Consulter les liens enregistrés"),
    (7, "🧪 Obtenir des liens de démonstration"),
    (8, "❤️ Ouvrir les publications à aimer"),
    (9, "➕ Ouvrir les profils à suivre"),
    (10, "▶️ Démarrer une simulation d'actions"),
    (11, "📊 Consulter l'historique"),
    (12, "⚙️ Paramètres"),
    (13, "🔄 Mettre à jour CONSTANT"),
    (14, "📖 Aide et documentation"),
)


def _logo() -> str:
    width = console.size.width
    if width < 48:
        return "CONSTANT"
    try:
        from pyfiglet import Figlet

        return Figlet(font="small", width=min(width - 4, 70)).renderText("CONSTANT").rstrip()
    except (ImportError, OSError):
        return "C O N S T A N T"


def show_banner(*, animations: bool = True) -> None:
    if animations and console.is_terminal and os.environ.get("CONSTANT_NO_ANIMATIONS") != "1":
        with Progress(
            SpinnerColumn(style="bright_cyan"),
            TextColumn("[cyan]Préparation de CONSTANT…"),
            transient=True,
            console=console,
        ) as progress:
            progress.add_task("chargement", total=None)
            time.sleep(0.25)
    title = Text(_logo(), style="bold bright_cyan", justify="center")
    subtitle = Text(f"GESTIONNAIRE INSTAGRAM  •  VERSION {__version__}", style="bold magenta", justify="center")
    console.print(Panel.fit(Text.assemble(title, "\n", subtitle), border_style="bright_cyan", padding=(1, 2)))


def begin_page(title: str | None = None, *, animations: bool = False) -> None:
    if console.is_terminal:
        console.clear(home=True)
    show_banner(animations=animations)
    if title:
        console.print(Text(title, style="bold bright_magenta"))


def show_dashboard(
    *,
    account_count: int,
    active_account: str | None,
    publication_count: int,
    profile_count: int,
    online: bool,
) -> None:
    console.print("[bold green]● Session active[/bold green]")
    table = Table(box=box.SIMPLE, show_header=False, pad_edge=False)
    table.add_column("État", style="cyan")
    table.add_column("Valeur", style="white")
    table.add_row("Comptes locaux", f"{account_count} / 10")
    table.add_row("Compte sélectionné", f"@{active_account}" if active_account else "Aucun")
    table.add_row("Liens enregistrés", f"{publication_count} publication(s) • {profile_count} profil(s)")
    table.add_row("Connexion Internet", "[green]● disponible[/green]" if online else "[yellow]● indisponible[/yellow]")
    console.print(table)
    console.print("[dim]Les comptes affichés sont des profils locaux ; OAuth Instagram n'est pas configuré.[/dim]")


def show_menu() -> None:
    console.print("\n[bold bright_cyan]MENU PRINCIPAL[/bold bright_cyan]")
    table = Table(box=None, show_header=False, pad_edge=False, collapse_padding=True)
    table.add_column("Choix", style="bold bright_cyan", width=6, justify="right")
    table.add_column("Option", style="white")
    for number, label in MENU_OPTIONS:
        table.add_row(f"[{number:02d}]", label)
    table.add_row("[00]", "Se déconnecter ou quitter")
    console.print(table)


def prompt_choice() -> int | None:
    value = Prompt.ask("\n[bold cyan]Ton choix[/bold cyan]").strip()
    try:
        return int(value)
    except ValueError:
        console.print("[yellow]Saisie invalide : entre le numéro d'une option.[/yellow]")
        return None


def confirm(message: str, *, default: bool = False) -> bool:
    answer = Prompt.ask(
        f"{message} [dim](o/n)[/dim]",
        choices=["o", "n"],
        default="o" if default else "n",
        show_choices=False,
    )
    return answer == "o"


def show_list(title: str, values: Iterable[str]) -> None:
    rows = list(values)
    console.print(f"\n[bold cyan]{title}[/bold cyan]")
    if not rows:
        console.print("[dim]Aucun élément enregistré.[/dim]")
        return
    table = Table(box=box.SIMPLE, show_header=True, header_style="bold magenta", expand=True)
    table.add_column("N°", width=4, justify="right")
    table.add_column("Lien", overflow="fold")
    for index, value in enumerate(rows, start=1):
        table.add_row(str(index), value)
    console.print(table)


def pause() -> None:
    Prompt.ask("\n[dim]Appuie sur Entrée pour continuer[/dim]", default="")


def message(text: str, style: str = "white") -> None:
    console.print(f"[{style}]{text}[/{style}]")
