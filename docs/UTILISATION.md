# Utilisation du menu

- `[01] Ajouter un compte Instagram` : ajoute un identifiant local non connecté.
- `[02] Afficher mes comptes` : montre les profils et leur état réel.
- `[03] Choisir un compte actif` : sélectionne un profil local.
- `[04] Supprimer un compte` : demande confirmation avant le retrait.
- `[05] Importer des liens Instagram` : ajoute une URL ou importe un fichier.
- `[06] Consulter les liens enregistrés` : affiche et retire les liens.
- `[07] Obtenir des liens de démonstration` : présente des URL `.invalid`
  explicitement fictives.
- `[08] Ouvrir les publications à aimer` : choisit une publication enregistrée,
  demande confirmation avant d'ouvrir le navigateur, puis demande si l'utilisateur
  a réalisé manuellement l'action. CONSTANT ne clique pas sur « J'aime ».
- `[09] Ouvrir les profils à suivre` : même principe pour un profil; tout
  abonnement éventuel reste manuel.
- `[10] Démarrer une simulation d'actions` : affiche une progression et un résumé
  d'éléments traités, ignorés et d'erreurs simulées. Aucune action réelle.
- `[11] Consulter l'historique` : affiche les derniers événements et propose un
  export CSV ou JSON local.
- `[12] Paramètres` : règle les animations ou change le mot de passe local.
- `[13] Mettre à jour CONSTANT` : lance `git pull --ff-only` après confirmation.
- `[14] Aide et documentation` : rappelle le fonctionnement et l'emplacement des
  guides.
- `[00] Se déconnecter ou quitter` : ferme la session locale.

Le menu ne fournit pas de bot. L'API officielle configurée dans cette version ne
permet aucune action d'engagement automatisée; CONSTANT ne contourne pas cette
limite.
