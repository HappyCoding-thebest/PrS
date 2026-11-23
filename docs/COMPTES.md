# Profils Instagram

`[01] Ajouter un compte Instagram` enregistre un identifiant de profil local,
sans mot de passe. Le programme limite la liste à dix identifiants et empêche
les doublons. `[02]` affiche la liste, `[03]` choisit le profil actif et `[04]`
supprime un profil après confirmation.

**Un profil local n'est pas une session Instagram.** Il n'y a pas de connexion
OAuth officielle dans cette version : les profils affichent donc « Non
connecté ». CONSTANT ne demande, ne lit et ne conserve aucun mot de passe
Instagram, cookie ou jeton d'accès.

Une véritable connexion exigera une application Meta autorisée, des URI de
redirection enregistrées, le consentement de l'utilisateur et un stockage de
jetons sécurisé compatible avec Termux. En attendant cette intégration, aucune
fonction ne prétend vérifier ou renouveler un accès.

Pour gérer une entreprise, n'ajoute que des profils que tu possèdes ou que tu
es autorisé à gérer.
