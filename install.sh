#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

ROOT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

step() {
  printf '\n\033[1;36m[%s/%s]\033[0m %s\n' "$1" "$2" "$3"
}

if [[ -z "${PREFIX:-}" || "$PREFIX" != *"/com.termux/"* ]]; then
  printf 'Erreur : ce script est prévu pour Termux sur Android.\n' >&2
  printf 'Ouvre Termux puis relance : bash install.sh\n' >&2
  exit 1
fi

if ! command -v pkg >/dev/null 2>&1; then
  printf 'Erreur : la commande pkg est introuvable. Installe Termux depuis une source prise en charge.\n' >&2
  exit 1
fi

step 1 5 "Vérification de Python et de Git"
if ! command -v python >/dev/null 2>&1; then
  printf 'Python est absent. Lance : pkg install -y python\n' >&2
  exit 1
fi
if ! command -v git >/dev/null 2>&1; then
  printf 'Git est absent. Lance : pkg install -y git\n' >&2
  exit 1
fi
python -c 'import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)' || {
  printf 'Erreur : Python 3.10 ou plus récent est nécessaire.\n' >&2
  exit 1
}

step 2 5 "Vérification de la connexion"
python - <<'PY'
import urllib.request
try:
    with urllib.request.urlopen("https://github.com", timeout=8) as response:
        if response.status >= 400:
            raise RuntimeError(f"GitHub répond avec le statut {response.status}")
except Exception as exc:
    raise SystemExit(f"Connexion à GitHub impossible : {exc}")
print("Connexion à GitHub vérifiée.")
PY

step 3 5 "Préparation de l'environnement Python"
if [[ ! -x .venv/bin/python ]]; then
  python -m venv .venv || {
    printf 'Impossible de créer .venv. Vérifie que le paquet Python de Termux est à jour.\n' >&2
    exit 1
  }
fi

step 4 5 "Installation et vérification des bibliothèques"
.venv/bin/python -m pip install --disable-pip-version-check -r requirements.txt
.venv/bin/python -c 'import rich, pyfiglet; print("Rich et pyfiglet sont disponibles.")'

step 5 5 "Initialisation et lancement de CONSTANT"
.venv/bin/python -m principale.main --init
exec bash "$ROOT_DIR/launch.sh"
