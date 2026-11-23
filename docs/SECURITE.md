# Sécurité et confidentialité

- Ne saisis jamais ton mot de passe Instagram dans CONSTANT. Il ne sera pas
  demandé.
- Le mot de passe CONSTANT est haché avec PBKDF2-HMAC-SHA256 et un sel aléatoire.
  Il protège seulement l'interface locale; il ne constitue pas un système de
  licence ou une protection contre un appareil déjà compromis.
- Sous Termux, les dossiers locaux sont créés avec des permissions `0700` et les
  fichiers privés avec `0600` lorsque le système le permet. Les données ne sont
  pas chiffrées; protège l'appareil et son stockage.
- Aucun jeton Instagram n'est pris en charge ou stocké. Les journaux n'incluent
  ni mot de passe, ni cookie, ni jeton; les paramètres et fragments d'URL sont
  retirés des entrées journalisées.
- Les données privées restent sous `~/.local/share/constant/`. Le dépôt ignore
  les environnements, journaux, fichiers de jetons et données locales. Vérifie
  toujours `git status` avant une publication.
- La vérification locale de démonstration est modifiable par une personne ayant
  accès au téléphone. Une licence de production devra être contrôlée côté serveur,
  avec expiration et révocation, sans secret maître intégré au client.
- Pour révoquer des applications Instagram autorisées, utilise les paramètres
  de sécurité Meta/Instagram depuis le compte concerné. CONSTANT ne détient pas
  de jeton à révoquer.

## Supprimer les données locales

Depuis Termux, quitte CONSTANT puis supprime uniquement son dossier de données :

```sh
rm -rf "$HOME/.local/share/constant"
```

Cette commande efface les profils locaux, liens, préférences, journaux et
rapports. Elle ne désinstalle pas le dépôt ou Termux.
