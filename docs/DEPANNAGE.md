# Dépannage

## `bash install.sh` indique que Termux est requis

Exécute le script dans Termux sous Android, pas dans un terminal Linux ou
Windows. Vérifie que la variable `PREFIX` contient le chemin Termux.

## Création de `.venv` ou installation pip en échec

Actualise les paquets Termux puis réessaie :

```sh
pkg update -y && pkg upgrade -y
pkg install -y python
cd ~/PrS && bash install.sh
```

Si l'espace disque est insuffisant, libère de l'espace avant de réinstaller.

## Mot de passe local oublié

Le mot de passe n'est pas récupérable à partir de son hachage. Sauvegarde les
listes de liens si tu en as besoin, puis supprime le seul fichier de configuration
locale pour relancer l'initialisation :

```sh
rm "$HOME/.local/share/constant/config.json"
```

Les liens et l'historique restent en place. Pour tout effacer, consulte
[SECURITE.md](SECURITE.md).

## Aucun lien disponible

Utilise `[05]` pour ajouter un lien ou importer un fichier texte. Vérifie que le
type choisi correspond : publication (par exemple `/p/.../`) ou profil (un
identifiant après le domaine).

## Le navigateur ne s'ouvre pas

Copie l'URL affichée et ouvre-la manuellement dans Instagram ou un navigateur.
Sur Termux, installe Termux:API si tu veux utiliser `termux-open-url`, puis
autorise le lien demandé par Android.

## Mise à jour Git refusée

Vérifie la connexion, `git status` et la configuration du remote. Sauvegarde tes
modifications locales avant toute résolution de conflit. La mise à jour utilise
`--ff-only` et ne réécrit pas les commits locaux.

## OAuth ou actions automatiques indisponibles

C'est attendu : l'intégration OAuth Meta n'est pas fournie et CONSTANT
n'automatise pas les likes ni les abonnements. Consulte [COMPTES.md](COMPTES.md).
