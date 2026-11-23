# CONSTANT

Gestionnaire de liens Instagram en français, conçu pour le terminal Android
Termux. CONSTANT aide à organiser des profils locaux, des URL et un historique.
Il n'automatise ni les mentions J'aime ni les abonnements.

## Important : fonctions réellement disponibles

- Les profils sont enregistrés localement comme des identifiants. Ils ne sont
  pas connectés à Instagram.
- L'intégration OAuth officielle Instagram n'est pas configurée dans cette
  version. Aucun mot de passe Instagram, jeton ou cookie n'est demandé ou stocké.
- L'ouverture d'une publication ou d'un profil lance le navigateur. Toute action
  éventuelle est faite manuellement par l'utilisateur dans Instagram.
- La simulation est locale et n'envoie aucune requête d'interaction à Instagram.
- Les données personnelles de l'application restent dans le dossier privé
  utilisateur et ne doivent pas être ajoutées à Git.

Une intégration OAuth réelle nécessitera une application Meta enregistrée et
autorisée, ses URI de redirection et une implémentation officielle vérifiée.
CONSTANT ne prétend pas disposer de cette intégration.

## Installation Termux depuis zéro

Installe Termux depuis une source maintenue, ouvre-le, puis copie cette commande :

```sh
pkg update -y && pkg install -y git python && git clone https://github.com/HappyCoding-thebest/PrS.git && cd PrS && bash install.sh
```

Le script vérifie Termux, Python, Git et la connexion, crée `.venv`, installe les
dépendances et initialise le mot de passe local à la première installation.
Il est relançable sans remplacer la configuration ni les données existantes.

## Lancement et mise à jour

```sh
cd ~/PrS && bash launch.sh
```

Pour mettre à jour un clone existant, utilise l'option `[13]` du menu, ou :

```sh
cd ~/PrS && git pull --ff-only && bash install.sh
```

## Menu

Les options sont numérotées `[01]` à `[14]`; `[00]` déconnecte et quitte.
L'écran d'aide intégré et les guides du dossier `docs/` décrivent chaque option.

## Tests

Les tests sont séparés des dépendances nécessaires à l'application :

```sh
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python -m pytest
```

## Données locales

Sur Termux, les réglages, les liens, l'historique et les exports sont conservés
dans `~/.local/share/constant/` avec des permissions privées. Ce dossier n'est
pas dans le dépôt. La configuration locale ne contient qu'un hachage du mot de
passe CONSTANT; ce mot de passe sert à verrouiller l'interface locale, pas à
authentifier un compte Instagram ni à valider une licence commerciale.

Consulte [docs/INSTALLATION.md](docs/INSTALLATION.md),
[docs/SECURITE.md](docs/SECURITE.md) et les autres guides pour les détails.
