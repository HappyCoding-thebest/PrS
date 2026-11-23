"""Point d'entrée et orchestration du menu CONSTANT."""

from __future__ import annotations

import argparse
import random
import socket
import subprocess
import sys
import time
from pathlib import Path

from rich.progress import BarColumn, Progress, TextColumn
from rich.table import Table
from rich.prompt import Prompt

from . import auth, comptes, configuration, interface, instagram_api, journal, liens, simulation


def _online() -> bool:
    try:
        with socket.create_connection(("www.instagram.com", 443), timeout=1.2):
            return True
    except OSError:
        return False


def _save(config: dict) -> None:
    configuration.save_config(config)


def _show_accounts(config: dict) -> None:
    accounts = comptes.list_accounts(config)
    if not accounts:
        interface.message("Aucun profil local. Ajoute un profil depuis le menu principal.", "yellow")
        return
    table = Table(title="Profils locaux", header_style="bold magenta")
    table.add_column("État", style="cyan")
    table.add_column("Identifiant", style="white")
    table.add_column("Connexion Instagram", style="yellow")
    for account in accounts:
        active = "● actif" if account["username"] == comptes.active_account(config) else ""
        table.add_row(active, f"@{account['username']}", "Non connecté — OAuth officiel non configuré")
    interface.console.print(table)
    interface.message(instagram_api.official_api_status(), "dim")


def _add_account(config: dict) -> None:
    username = Prompt.ask("Identifiant Instagram (sans mot de passe)").strip()
    try:
        account = comptes.add_account(config, username)
    except comptes.AccountError as exc:
        interface.message(str(exc), "yellow")
        return
    _save(config)
    interface.message(
        f"@{account['username']} est enregistré comme profil local. Aucun accès Instagram n'a été créé.",
        "green",
    )
    interface.message(instagram_api.official_api_status(), "dim")


def _choose_account(config: dict) -> None:
    accounts = comptes.list_accounts(config)
    if not accounts:
        interface.message("Ajoute d'abord un profil local.", "yellow")
        return
    _show_accounts(config)
    username = Prompt.ask("Identifiant du profil à sélectionner").strip()
    try:
        account = comptes.choose_account(config, username)
    except comptes.AccountError as exc:
        interface.message(str(exc), "yellow")
        return
    _save(config)
    interface.message(f"Profil local actif : @{account['username']}.", "green")


def _remove_account(config: dict) -> None:
    accounts = comptes.list_accounts(config)
    if not accounts:
        interface.message("Aucun profil local à supprimer.", "yellow")
        return
    _show_accounts(config)
    username = Prompt.ask("Identifiant du profil à supprimer").strip()
    match = next(
        (item for item in accounts if item["username"].casefold() == username.lstrip("@").casefold()),
        None,
    )
    if match is None:
        interface.message("Profil introuvable.", "yellow")
        return
    if not interface.confirm(f"Supprimer le profil local @{match['username']} ?"):
        interface.message("Suppression annulée.", "dim")
        return
    comptes.remove_account(config, match["username"])
    _save(config)
    interface.message("Profil local supprimé.", "green")


def _kind_prompt() -> str | None:
    value = Prompt.ask(
        "Type de lien : publication [p], profil [r], retour [q]",
        choices=["p", "r", "q"],
        default="q",
        show_choices=False,
    )
    return {"p": "publication", "r": "profil"}.get(value)


def _import_links() -> None:
    action = Prompt.ask(
        "Ajouter un lien [a], [i]mporter un fichier ou [q]uitter",
        choices=["a", "i", "q"],
        default="q",
        show_choices=False,
    )
    if action == "q":
        return
    interface.begin_page("Ajouter un lien" if action == "a" else "Importer des liens")
    kind = _kind_prompt()
    if kind is None:
        return
    if action == "a":
        value = Prompt.ask("URL Instagram").strip()
        try:
            added = liens.add_link(kind, value)
        except liens.LinkError as exc:
            interface.message(str(exc), "yellow")
            return
        interface.message("Lien ajouté." if added else "Ce lien est déjà enregistré.", "green" if added else "yellow")
        return
    source = Path(Prompt.ask("Chemin du fichier texte à importer").strip()).expanduser()
    try:
        accepted, rejected = liens.import_links(kind, source)
    except (OSError, UnicodeError) as exc:
        interface.message(f"Import impossible : {exc}", "red")
        return
    interface.message(
        f"Import terminé : {accepted} lien(s) ajouté(s), {rejected} ligne(s) rejetée(s) ou déjà enregistrée(s).",
        "green",
    )


def _browse_links() -> None:
    kind = _kind_prompt()
    if kind is None:
        return
    title = "Publications enregistrées" if kind == "publication" else "Profils enregistrés"
    notice: tuple[str, str] | None = None
    while True:
        interface.begin_page(title)
        if notice:
            interface.message(notice[0], notice[1])
            notice = None
        items = liens.read_links(kind)
        interface.show_list(title, items)
        action = Prompt.ask(
            "Action : [r]etirer un lien ou [q]uitter",
            choices=["r", "q"],
            default="q",
            show_choices=False,
        )
        if action == "q":
            return
        value = Prompt.ask("URL exacte à retirer").strip()
        try:
            removed = liens.remove_link(kind, value)
        except liens.LinkError as exc:
            notice = (str(exc), "yellow")
            continue
        notice = (
            "Lien retiré." if removed else "Ce lien n'est pas enregistré.",
            "green" if removed else "yellow",
        )


def _show_demo_links() -> None:
    kind = _kind_prompt()
    if kind is None:
        return
    interface.begin_page("Liens de démonstration")
    examples = liens.demo_links(kind)
    interface.message(
        "Ces liens utilisent le domaine réservé .invalid : ils sont fictifs, ne mènent pas à Instagram et ne sont pas enregistrés.",
        "yellow",
    )
    interface.show_list("Exemples fictifs", examples)


def _manual_action(kind: str, config: dict) -> None:
    entries = liens.read_links(kind)
    if not entries:
        label = "publications" if kind == "publication" else "profils"
        interface.message(f"Aucun lien {label} enregistré. Ajoute un lien ou importe un fichier.", "yellow")
        return
    url = random.choice(entries)
    account_name = comptes.active_account(config)
    manual_instruction = (
        "mettre manuellement un J’aime sur la publication"
        if kind == "publication"
        else "t’abonner manuellement à ce profil"
    )
    interface.console.print(f"\n[bold cyan]Lien choisi[/bold cyan] : {url}")
    interface.console.print(f"[bold cyan]Compte actif[/bold cyan] : {('@' + account_name) if account_name else 'aucun'}")
    interface.message(
        "CONSTANT ne réalise aucune action à ta place. Tu peux "
        f"{manual_instruction} dans Instagram.",
        "yellow",
    )
    started = time.monotonic()
    if not interface.confirm("Ouvrir ce lien dans le navigateur ?"):
        journal.record(account=account_name, operation=f"ouverture_manuelle_{kind}", url=url, status="annulée")
        interface.message("Ouverture annulée.", "dim")
        return
    opened = instagram_api.open_instagram_url(url)
    if not opened:
        journal.record(account=account_name, operation=f"ouverture_manuelle_{kind}", url=url, status="échec_ouverture")
        interface.message("Impossible d'ouvrir le navigateur. Copie l'URL affichée pour l'ouvrir manuellement.", "red")
        return
    interface.message("Lien ouvert. Après ton action manuelle, confirme ci-dessous si tu le souhaites.", "green")
    completed = interface.confirm("As-tu effectué cette action manuellement ?")
    status = "confirmée_par_utilisateur" if completed else "ouverte_non_confirmée"
    journal.record(
        account=account_name,
        operation=f"action_manuelle_{kind}",
        url=url,
        status=status,
        duration_ms=int((time.monotonic() - started) * 1000),
        message="Confirmation déclarative; aucune action exécutée par CONSTANT.",
    )
    interface.message(
        "Ta confirmation a été enregistrée. CONSTANT n'a effectué aucune action Instagram.",
        "dim",
    )


def _simulate() -> None:
    choice = Prompt.ask(
        "Simuler avec [e]xemples fictifs ou [l]iens enregistrés ?",
        choices=["e", "l", "q"],
        default="e",
        show_choices=False,
    )
    if choice == "q":
        return
    if choice == "e":
        entries = liens.demo_links("publication", 5) + liens.demo_links("profil", 5)
    else:
        entries = liens.read_links("publication") + liens.read_links("profil")
        if not entries:
            interface.message("Aucun lien enregistré. Simulation annulée.", "yellow")
            return
    entries = entries[:100]
    interface.message("MODE SIMULATION — aucune action Instagram réelle n'est effectuée.", "bold red")
    with Progress(
        TextColumn("[cyan]Simulation"),
        BarColumn(),
        TextColumn("{task.completed}/{task.total}"),
        console=interface.console,
    ) as progress:
        task = progress.add_task("simulation", total=len(entries))

        def advance(_index: int, _url: str, _status: str) -> None:
            progress.update(task, advance=1)

        result = simulation.run_simulation(entries, error_rate=0.1, delay=0.08, on_item=advance)
    config = configuration.load_config()
    account_name = comptes.active_account(config)
    for url, status in result.details:
        journal.record(
            account=account_name,
            operation="simulation",
            url=url,
            status=status,
            duration_ms=int(result.duree_secondes * 1000 / max(result.total, 1)),
            message="Mode local; aucune interaction réelle.",
        )
    table = Table(title="Résumé de la simulation", box=None)
    table.add_column("Éléments", style="cyan")
    table.add_column("Traités", style="green")
    table.add_column("Ignorés", style="yellow")
    table.add_column("Erreurs simulées", style="red")
    table.add_row(str(result.total), str(result.traite), str(result.ignores), str(result.erreurs))
    interface.console.print(table)
    interface.message(f"Temps écoulé : {result.duree_secondes:.2f} s. Rien n'a été envoyé à Instagram.", "dim")


def _history() -> None:
    try:
        entries = journal.read_entries()
    except (OSError, ValueError) as exc:
        interface.message(f"Lecture du journal impossible : {exc}", "red")
        return
    if not entries:
        interface.message("L'historique est vide.", "dim")
    else:
        table = Table(title="Historique local (les simulations sont indiquées)", header_style="bold magenta")
        for heading in ("Date UTC", "Compte", "Opération", "Statut", "URL"):
            table.add_column(heading, overflow="fold")
        for entry in entries[-30:]:
            table.add_row(
                str(entry.get("date_utc", "")),
                str(entry.get("compte", "")),
                str(entry.get("operation", "")),
                str(entry.get("statut", "")),
                str(entry.get("url", "")),
            )
        interface.console.print(table)
    export = Prompt.ask(
        "Exporter en [c]SV, en [j]SON ou [n]on ?",
        choices=["n", "c", "j"],
        default="n",
        show_choices=False,
    )
    if export in {"c", "j"}:
        try:
            destination = journal.export_report("csv" if export == "c" else "json")
        except (OSError, ValueError) as exc:
            interface.message(f"Export impossible : {exc}", "red")
        else:
            interface.message(f"Rapport privé créé : {destination}", "green")


def _settings(config: dict) -> None:
    animations = bool(config.get("ui", {}).get("animations", True))
    interface.console.print(f"Animations de lancement : {'activées' if animations else 'désactivées'}")
    action = Prompt.ask(
        "Animations : [a]ctiver/désactiver, changer le [m]ot de passe ou [q]uitter",
        choices=["a", "m", "q"],
        default="q",
        show_choices=False,
    )
    if action == "q":
        return
    if action == "a":
        config.setdefault("ui", {})["animations"] = not animations
        _save(config)
        interface.message("Préférence enregistrée.", "green")
        return
    from getpass import getpass

    if not auth.verify_local_password(config, getpass("Mot de passe actuel : ")):
        interface.message("Mot de passe incorrect.", "red")
        return
    try:
        auth.configure_local_password(config)
    except RuntimeError as exc:
        interface.message(str(exc), "yellow")
        return
    _save(config)
    interface.message("Mot de passe local modifié.", "green")


def _update() -> None:
    root = Path(__file__).resolve().parents[1]
    if not (root / ".git").exists():
        interface.message("Mise à jour impossible : ce dossier n'est pas un clone Git.", "red")
        return
    if not interface.confirm("Récupérer la dernière version de CONSTANT avec git pull --ff-only ?"):
        return
    try:
        result = subprocess.run(
            ["git", "pull", "--ff-only"],
            cwd=root,
            check=False,
            capture_output=True,
            text=True,
            timeout=120,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        interface.message(f"Mise à jour impossible : {exc}", "red")
        return
    if result.stdout.strip():
        interface.console.print(result.stdout.rstrip())
    if result.stderr.strip():
        interface.console.print(result.stderr.rstrip(), style="dim")
    if result.returncode:
        interface.message("La mise à jour a échoué. Vérifie le réseau et l'état Git.", "red")
    else:
        if sys.prefix != sys.base_prefix:
            try:
                dependencies = subprocess.run(
                    [sys.executable, "-m", "pip", "install", "-r", str(root / "requirements.txt")],
                    cwd=root,
                    check=False,
                    capture_output=True,
                    text=True,
                    timeout=300,
                )
            except (OSError, subprocess.TimeoutExpired) as exc:
                interface.message(f"Code mis à jour, mais installation des dépendances impossible : {exc}", "red")
                return
            if dependencies.stdout.strip():
                interface.console.print(dependencies.stdout.rstrip())
            if dependencies.stderr.strip():
                interface.console.print(dependencies.stderr.rstrip(), style="dim")
            if dependencies.returncode:
                interface.message("Code récupéré, mais les dépendances n'ont pas toutes été installées.", "red")
                return
        interface.message("Mise à jour terminée. Relance CONSTANT pour charger la nouvelle version.", "green")


def _help() -> None:
    interface.console.print(
        "[bold cyan]Aide CONSTANT[/bold cyan]\n"
        "Les comptes sont des identifiants locaux, pas des sessions Instagram. "
        "Ajoute des URL publiques, ouvre-les puis effectue toute interaction manuellement. "
        "La simulation est hors ligne et ne réalise aucune action. "
        "Consulte README.md et docs/ pour l'installation, la confidentialité et le dépannage."
    )
    root = Path(__file__).resolve().parents[1]
    interface.console.print(f"Dossier du projet : {root}")
    interface.console.print("Documentation : docs/INSTALLATION.md, PREMIER_DEMARRAGE.md, COMPTES.md, LIENS.md, UTILISATION.md, SECURITE.md, DEPANNAGE.md")


def _dispatch(choice: int, config: dict) -> bool:
    if choice == 0:
        return False
    if choice == 1:
        _add_account(config)
    elif choice == 2:
        _show_accounts(config)
    elif choice == 3:
        _choose_account(config)
    elif choice == 4:
        _remove_account(config)
    elif choice == 5:
        _import_links()
    elif choice == 6:
        _browse_links()
    elif choice == 7:
        _show_demo_links()
    elif choice == 8:
        _manual_action("publication", config)
    elif choice == 9:
        _manual_action("profil", config)
    elif choice == 10:
        _simulate()
    elif choice == 11:
        _history()
    elif choice == 12:
        _settings(config)
    elif choice == 13:
        _update()
    elif choice == 14:
        _help()
    else:
        interface.message("Option inconnue.", "yellow")
    return True


def run(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Gestionnaire local CONSTANT pour Termux.")
    parser.add_argument("--init", action="store_true", help="Créer les dossiers et configurer le mot de passe local.")
    args = parser.parse_args(argv)
    try:
        config = configuration.load_config()
    except configuration.ConfigurationError as exc:
        interface.begin_page("Erreur de configuration")
        interface.message(f"Configuration invalide : {exc}", "red")
        return 2

    if args.init:
        interface.begin_page("Configuration initiale")
        if not auth.password_is_configured(config):
            interface.message("Configuration initiale : crée un mot de passe local de démonstration.", "cyan")
            try:
                auth.configure_local_password(config)
            except RuntimeError as exc:
                interface.message(str(exc), "red")
                return 1
            _save(config)
        interface.message(f"Installation locale initialisée dans {configuration.data_directory()}.", "green")
        return 0

    interface.begin_page(
        "Connexion",
        animations=bool(config.get("ui", {}).get("animations", True)),
    )
    if not auth.password_is_configured(config):
        interface.begin_page("Première configuration")
        interface.message("Première utilisation : définis un mot de passe local. Il n'est envoyé nulle part.", "cyan")
        try:
            auth.configure_local_password(config)
        except RuntimeError as exc:
            interface.message(str(exc), "red")
            return 1
        _save(config)
        interface.begin_page("Connexion")

    if not auth.login(config):
        interface.message("Session verrouillée après trois tentatives.", "red")
        return 1

    while True:
        interface.begin_page()
        interface.show_dashboard(
            account_count=len(comptes.list_accounts(config)),
            active_account=comptes.active_account(config),
            publication_count=len(liens.read_links("publication")),
            profile_count=len(liens.read_links("profil")),
            online=_online(),
        )
        interface.show_menu()
        choice = interface.prompt_choice()
        if choice is None:
            interface.pause()
            continue
        if choice == 0:
            interface.begin_page("Session terminée")
            interface.message("Déconnexion de CONSTANT.", "cyan")
            return 0
        titles = dict(interface.MENU_OPTIONS)
        if choice not in titles:
            interface.begin_page("MENU PRINCIPAL")
            interface.message("Option inconnue. Choisis un numéro affiché dans le menu.", "yellow")
            interface.pause()
            continue
        interface.begin_page(titles[choice])
        _dispatch(choice, config)
        interface.pause()


if __name__ == "__main__":
    try:
        raise SystemExit(run())
    except KeyboardInterrupt:
        interface.message("\nInterruption reçue. Aucune action automatique n'est en cours.", "yellow")
        raise SystemExit(130)
