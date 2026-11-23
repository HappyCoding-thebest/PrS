#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

ROOT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PYTHON="$ROOT_DIR/.venv/bin/python"

if [[ ! -x "$PYTHON" ]]; then
  printf 'Environnement absent. Depuis le dossier du projet, lance : bash install.sh\n' >&2
  exit 1
fi

exec "$PYTHON" -m principale.main "$@"
