# Installation dans Termux

## Préparer Termux

1. Installe Termux depuis une source maintenue, puis ouvre l'application.
2. À l'invite `$`, copie la commande suivante :

   ```sh
   pkg update -y && pkg install -y git python && git clone https://github.com/HappyCoding-thebest/PrS.git && cd PrS && bash install.sh
   ```

3. Accepte les mises à jour proposées par `pkg`. Le script affiche cinq étapes :
   vérification, connexion, environnement Python, dépendances, initialisation.
4. À la première installation, choisis et confirme un mot de passe local. Il
   n'est ni envoyé ni écrit en clair.
5. Après l'installation, l'écran CONSTANT demande ce mot de passe avant le menu.

La commande `git clone` suppose que le dossier `PrS` n'existe pas déjà. Pour un
clone déjà présent, utilise la procédure de mise à jour ci-dessous.

## En cas d'échec

- Python ou Git absent : `pkg install -y python git`
- Paquets Termux à actualiser : `pkg update -y && pkg upgrade -y`
- Dépendance Python absente : depuis `~/PrS`, relance `bash install.sh`
- Installation interrompue : relance `bash install.sh`; les dossiers et le
  mot de passe locaux ne sont pas supprimés.

Le script exige Python 3.10 ou plus récent et une connexion à GitHub. Il ne
télécharge aucun fichier de configuration contenant des secrets.

## Désinstaller

Sauvegarde d'abord les liens ou rapports que tu veux conserver. Pour retirer le
clone et son environnement :

```sh
rm -rf "$HOME/PrS"
```

Les données privées restent volontairement séparées du clone. Pour les effacer
également, suis les étapes de [SECURITE.md](SECURITE.md).

## Lancer l'application

```sh
cd ~/PrS
bash launch.sh
```

Le lancement direct équivalent est :

```sh
cd ~/PrS
.venv/bin/python -m principale.main
```

## Mettre à jour un clone

Depuis `~/PrS`, utilise `[13] Mettre à jour CONSTANT` ou exécute :

```sh
git pull --ff-only
bash install.sh
```

`--ff-only` évite de créer un merge automatique. En cas de modifications
locales, sauvegarde-les avant la mise à jour et résous les conflits manuellement.
