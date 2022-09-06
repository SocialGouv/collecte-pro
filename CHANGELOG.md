# Journal des modifications

Toutes les modifications notables de ce projet sont documentées dans ce fichier.

Ce format se base sur [keep a changelog](https://keepachangelog.com/fr/1.0.0/), et ce
projet adhère à [la Gestion sémantique de version](https://semver.org/lang/fr/spec/v2.0.0.html).

## [En cours]
### Ajouts
- Ajout d'une page de statistiques pour les Administrateurs

### Modifications
- Les modifications de l'application ne sont plus gérées par version mais dans ce fichier unique

### Corrections
- Le filtre par date est basé sur une date à minuit

### Suppressions
- Suppression des fichiers de version


## [2.1.10] - 2022-08-30
## Corrections
- Les mails envoyés n'ajoutent pas de préfixe pour l'environnement de production


## [2.1.9] - 2022-08-30
## Corrections
- La date de dépôt des fichiers affichée dans l'export est désormais localisée


## [2.1.8] - 2022-08-30
### Modifications
- Si l'environnement n'est pas celui de production, un bandeau d'alerte est affiché en haut de toutes les pages

### Corrections
- Le mois d'octobre est affiché correctement dans l'explorateur de fichiers
- Les questions trop longues sont coupées sur plusieurs lignes pour un meilleur affichage


## [2.1.7] - 2022-08-30
### Corrections
- Les question trop longues sont affichées sur plusieurs lignes
- L'animation d'attente de téléchargement est visible via l'explorateur de fichiers
- Le pied de page est au format du Design System de l'Etat


## [2.1.6] - 2022-08-30
### Corrections
- Améliorations liées aux RGAA
- Le filtre des documents par date se base sur la date sans prendre en compte l'heure


## [2.1.5] - 2022-08-30
### Corrections
- Le composant pytz ne pousse pas la mise à jour de tzdata. Il est désormais forcé dans les composants requis.


## [2.1.4] - 2022-08-26
### Ajouts
- Il est désormais possible de déposer des fichiers quelle que soit la taille du nom du fichier, celui-ci sera tronqué si nécessaire

### Modifications
- Les filtres de l'explorateur de fichiers ont été réduits afin de pouvoir être présentés au mieux
- Les fichiers dont le nom est trop long ont été tronqués à l'affichage

### Corrections
- Il est désormais possible de déposer des fichiers quelle que soit la taille du nom du fichier, celui-ci sera tronqué si nécessaire
- Firefox ne gêne plus la création d'espaces de dépôt


## [2.1.3] - 2022-08-02
### Modifications
- Il est désormais possible de déposer des fichiers avec des noms plus longs (jusque 100 caractères)
- Le message de réinitialisation du mot de passe Keycloak est plus accueillant

### Corrections
- En cas de nom trop long, un seul message cohérent est renvoyé à l'utilisateur

### Suppressions
- Suppression de la page de documentation de l'administration en mode DEBUG


## [2.1.2] - 2022-07-19
### Sécurité
- Retour à une ancienne version de librairie pour éviter les incompatibilités

### Corrections
- Correction sur la mise à jour du statut des questionnaires


## [2.1.1] - 2022-07-13
### Ajouts
- Création d'un thème Keycloak permettant un meilleur rapport avec l'application
- Les éléments sélectionnables ont une infobulle

### Modifications
- Désormais tous les utilisateurs (Demandeurs et Répondants) recevront les notifications de dépôts de fichier
- La page de l'explorateur de fichiers a été revue
- La navigation au clavier est utilisable sur l'explorateur de fichiers; la sélection multiple n'est pas encore possible

### Corrections
- La limitation de la taille du nom des fichiers déposés est plus explicite et correcte
- Les métadonnées des fichiers déposés ne sont plus modifiées
- La limite de 25 caractères est gérée pour les codes de références des espaces de dépôt
- Le filtre de l'explorateur liste désormais tous les utilisateurs ayant déposé des fichiers sur l'espace de dépôt


## [2.1.0] - 2022-06-14
### Ajouts
- Mise en place d'un explorateur de réponses
- Ajout d'une partie promotionnelle sur la page d'accueil

### Modifications
- L'adresse de support est désormais paramétrable

### Sécurité
- Limitation de l'administration fonctionnelle pour plus de sécurité


## [2.0.5] - 2022-07-01
### Corrections
- Les fichiers téléversés ne sont plus modifiés


## [2.0.4] - 2022-05-19
### Corrections
- Les pages FAQ et Accessibilité sont de nouveau disponibles


## [2.0.3] - 2022-04-05
### Ajouts
- Ajout d'un message d'attente lors de l'export d'un espace de dépôt
- Le mail de publication d'un questionnaire est désormais envoyé à tous les Demandeurs de l'espace de dépôt

### Modifications
- Remplacement de l'icône au format PNG pour une meilleure compatibilité
- Les boutons d'export et de duplication ne sont visibles que si des questionnaires sont présents
- L'adresse mail de contact/support est désormais un paramètre de l'application
- L'export d'un espace de dépôt spécifie les fichiers annexes et ceux à la corbeille
- La notion de Groupe n'était pas manipulable par le Super Utilisateur
- Adaptation des couleurs pour le respect du RGAA
- Utilisation de la langue française au lieu de la langue anglaise pour le respect du RGAA
- Mise à jour du document Word d'export du questionnaire vers collecte-pro
- La page est rafraichie après création/duplication d'un espace de dépôt

### Sécurité
- Remplacement de la librairie obsolète soft-delete par django-soft-delete

### Corrections
- Remise à zéro des questionnaires sélectionnés lorsqu'on referme une modale
- La suppression d'un questionnaire n'était plus possible
- Les espaces de dépôt ne pouvaient plus être désactivés
- Les adresses mails des destinataires lors de la publication d'un questionnaire sont séparées par des ";"
- Le nom des fichiers téléchargés un par un est désormais préfixé
- Le nom de l'espace de dépôt apparait en lieu et place de celui de la procédure lors de la suppression de l'espace de dépôt
- Les statuts "Répondu" et "Finalisé" des questionnaires sont mieux gérés


## [2.0.2] - 2022-03-11
### Corrections
- Correction de la déclaration de conformité au RGAA
- Correction de la mise à jour de la base de données


## [2.0.1] - 2022-03-08
### Corrections
- Correction sur l'accessibilité au clavier


## [2.0.0] - 2022-03-04
### Ajouts
- Ajout d'une page de non conformité au RGAA

### Modifications
- Passage de l'application sous le nom collecte-pro
- Reprise des dernières évolutions de la solution mère e-contrôle

### Sécurité
- Mises à jour de sécurité sur l'ensemble des composants python
- Passage de Django 2.2 à Django 3.2
- Mises à jour de sécurité sur l'ensemble des composants javascript


## [1.3.1] - 2021-10-29
### Corrections
- La migration de la base, et donc l'attribution des permissions par défaut, s'effectue désormais sans souci


## [1.3.0] - 2021-10-26
### Ajouts
- Il est désormais possible d'ajouter des liens dans le pied de page
- Ajout de la gestion des paramètres de l'application au niveau de l'administration
- Ajout d'un lien vers l'administration si l'utilisateur a les droits

### Modifications
- Les administrateurs peuvent modifier les informations du site (nom et url) qui sont utilisés dans les messages de l'application

### Corrections
- Nettoyage et correction du souci de connexion lié à l'ajout de KeyCloak

### Suppressions
- Limitation des droits d'administration pour les administrateurs qui ne peuvent plus tout voir et/ou tout modifier


## [1.2.0] - 2021-10-04
### Ajouts
- Les CGU sont désormais modifiables par les administrateurs
- Ajout du paramètre ENV_NAME utilisé dans les titres des e-mails afin de pouvoir spécifier l'environnement utilisé
- KeyCloak est désormais utilisable pour gérer les connexions des utilisateurs; une documentation est rajoutée concernant la configuration de KeyCloak

### Modifications
- Quelques modifications de design mineures


## [1.1.1] - 2021-09-06
### Ajouts
- Ajout des informations de release

### Corrections
- Correction du lien vers les informations de release


## [1.1.0] - 2021-09-06
### Modifications
- Vocabulaire interministériel et générique mis en place
- Charte État mise en place par défaut


## [1.0.0] - 2021-08-17
### Ajouts
- Ajout d'un paramètre permettant de conditionner l'enrgistrement des adresses IP des utilisateurs

### Modifications
- Reprise de l'application e-contrôle et passage sous le nom e-collecte
- Authentification Django basée sur le module auth par défaut de Django
- Mise en paramètre des logos et image d'accueil permettant l'utilisation de plusieurs instances

### Corrections
- Remise au propre du code source et de la documentation associée

### Suppressions
- Serveur Webdav et partie connexion
- Partie LDAP permettant à des demandeurs de se connecter sans compte