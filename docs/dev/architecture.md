# Architecture de collecte-pro

Créé le 9 Décembre 2019 - Des choses ayant pu changé depuis lors, désolé :)
Merci d'ajouter une date lorsque vous modifiez une section de ce document. Placer la
date directement dans la section mise à jour.

Le fichier README.md contient également des informations sur comment les choses
fonctionnent, jetez-y un oeil.

## Base de données

La base de données utilisée est postgreSQL. La structure est automatiquement définie via
les modèles Django. Vous pouvez regarder :
https://github.com/SocialGouve/ecollecte/blob/develop/control/models.py et
https://github.com/SocialGouve/ecollecte/blob/develop/user_profiles/models.py pour les
tables principales.

Voici un schéma de la base qui date de décembre 2019 :
https://github.com/SocialGouve/ecollecte/blob/develop/docs/dev/ecollecte-database.png

## Partie serveur

La partie serveur est en Python et utilise le framework Django. Elle est séparée en
plusieurs applis Django.

Il existe aussi une API via Django Rest Framework. Vous pouvez obtenir de l'aide sur
l'API à cette URL : */api/docs*. Il existe aussi une documentation obsolète de
l'application de départ e-contrôle :
https://github.com/SocialGouve/ecollecte/blob/develop/docs/dev/ecollecte_API_30-06-2020.pdf.

### ecc

Application principale. Elle contient le fichier *urls.py*
(https://github.com/SocialGouve/ecollecte/blob/develop/ecc/urls.py) qui peut être utile
pour voir comment les vues sont mappées aux urls.

### control

Contient le modèle principal
(https://github.com/SocialGouve/ecollecte/blob/develop/control/models.py) qui peut être
utile pour appréhender les objets principaux de la base de données.

La plupart des vues sont également ici
(https://github.com/SocialGouve/ecollecte/blob/develop/control/views.py). Ce fichier
peut être utile pour comprendre comment les objets sont passés aux templates pour les
clients.

Les vues des API sont aussi ici
(https://github.com/SocialGouve/ecollecte/blob/develop/control/api_views.py)


### Autres informations

#### Templates

Les templates Django se trouvent dans *templates/*. Vue.js est aussi utilisé (voir
ci-dessous pour les détails des interactions Django-Vue).

#### Celery

Celery est exécuté régulièrement afin d'envoyer les emails.


## Partie client

### structure générale

La partie client utilise les templates django ainsi que Vue.js. Il ne s'agit pourtant
pas d'une Single Page Application.

Chaque page est chargée depuis le serveur en tant que template Django, celle-ci est
alors remplie via les données du serveur. La page servie contient également des liens
vers des fichiers javascript et CSS.

Certains des fichiers javascripts sont des librairies (bootstrap) et d'autres sont de
notre propre cru et sont embarqués dans du code Vue.js via Parcel (voir package.json
pour les commandes de build).

Les systèmes de design et de rendu sont faits via Tabler (*static/tabler*). Tabler étant
basé sur bootstrap, la plupart des classes CSS seront familières aux utilisateurs de
bootstrap.

Nous n'utilisons pas de librairies de composants : nous créons nos propres composants
Vue.js lorsque nécessaire, et utilisons les classes CSS de Tabler pour le style et les
animations.

Le CSS se trouve dans *static/css/custom.css* et dans les fichiers Vue.js (le fait que
Vue.js permet de déclarer le CSS dans les même fichiers que les composants aide au suivi
du code).

Pourquoi tant de complexité (et de bizarreries) niveua structure ? Simplement parce que
tout a débuté avec Django uniquement et que les morceaux Vue.js ont été ajoutés
graduellement lorsque le javascript se complexifiait. Une ré-écriture complète n'a pas
été engagée, mais l'utilisation de Vue.js est de plus en plus importante, donc cela
pourrait survenir un jour. Tant que ça fonctionne, pas besoin de le réparer !


### Interactions entre les templates Django et Vue.js : la page détail d'un contrôle

- Le serveur sert le template Django situé à *templates/ecc/control_detail.html*. La vue
    correspondante se trouve dans la classe ControlDetail
    (https://github.com/SocialGouve/ecollecte/blob/develop/control/views.py#L30).
- La vue django fournie les données au template : controls_json, user_json, etc...
    (tout ce qui se trouve entre double accolades : {{ }}). Puis transmet le résultat
    au client.
- Côté client, le javascript inclus (*dist/control-detail-bundle.css*) dans le HTML est
    exécuté. Il s'agit d'un composant Vue.js dont le fichier principal est
    https://github.com/SocialGouve/ecollecte/blob/develop/static/src/control-detail.js.
- Le fichier Vue.js principal charge le composant racine :
    https://github.com/SocialGouve/ecollecte/blob/develop/static/src/controls/ControlPage.vue.
    Il affiche alors les données passées en propriétés depuis le template Djang. Par
    exemple, la liste des controles passée via
    https://github.com/SocialGouve/ecollecte/blob/develop/templates/ecc/control_detail.html#L7,
    devient une propriété pour
    https://github.com/SocialGouve/ecollecte/blob/develop/static/src/controls/ControlPage.vue#L64.
- Dès lors, le code Vue.js fonctionne normalement.

Notons que sur la même page d'autres composants Vue.js sont chargés : la sidebar
(https://github.com/SocialGouve/ecollecte/blob/develop/templates/base.html#L74) qui
affiche le menu de gauche, et le gestionnaire de session
(https://github.com/SocialGouve/ecollecte/blob/develop/templates/base.html#L84) chargé
de déconnecter l'utilisateur après un certain temps d'inactivité.

Chaque composant est un fichier javascript séparé et ils sont indépendants en terme de
variables.


### Les composants Parcel

Nous utilisons des composants Parcel qui sont liés et exécutés dans différentes pages.
Les composants se trouvent dans le répertoire *src/dist*. Chaque Parcel génère des
fichiers JS et CSS qui peuvent être utilisés dans les templates Django (certains
composants n'ont qu'un fichier JS et aucun fichier CSS).

#### sidebar-bundle.js et sidebar-bundle.css

Utilisé sur chaque page. Il affiche la sidebar sur la gauche. Il récupère les données
via un appel vers le backend (via la librairie axios) pour les afficher.

#### session-management-bundle.js

Utilisé sur chaque page (via le template de base de Django
https://github.com/SocialGouve/ecollecte/blob/develop/templates/base.html#L84). Il crée un
timer qui, une fois le temps écoulé, provoque la déconnexion de l'utilisateur sauf si
celui-ci a effectué une action.

#### control-detail-bundle.js and control-detail-bundle.css

Affiche les "Espaces de dépôt".

Fichier principal :
https://github.com/SocialGouve/ecollecte/blob/develop/static/src/control-detail.js

Lorsque l'utilisateur clique sur le menu, il modifie l'espace de dépôt affiché et l'url
sans avoir à recharger la page.

Le composant récupère également la liste de tous les espaces de dépôt et les
informations de l'utilisateur connecté depuis le template Django. D'autres appels en
arrière plan sont faits pour les sous-composants, afin d'obtenir plus de données ou pour
les mettre à jour.

#### questionnaire-detail-bundle.js and questionnaire-detail-bundle.css

Affiche un questionnaire, tout simplement.

Fichier principal :
https://github.com/SocialGouve/ecollecte/blob/develop/static/src/questionnaire-detail.js

#### questionnaire-create-bundle.js and questionnaire-create-bundle.css

Affiche un Wizard de 3 étapes pour créer un questionnaire. Aucun rechargement serveur
n'alieu pendant ce Wizard.

Fichier principal :
https://github.com/SocialGouve/ecollecte/blob/develop/static/src/questionnaire-create.js


### Sous-composants

Il s'agit des composants Vue.js situés dans le répertoire *static/src*.


## WSGI

collecte-pro est une application python qui utilise une interface WSGI pour communiquer
avec le serveur proxy (Apache ou Nginx), voir le fichier *ecc/wsgi.py*.
Lorsqu'une requête arrive sur le proxy, celui-ci redirige la requête vers l'application
Django pour sa prise en compte.

Voir [la documentation Django](https://docs.djangoproject.com/en/2.2/howto/deployment/wsgi/)
pour plus de détails.
