# Collecte-pro - Environnement de développement

## Environnement de développement

Collecte-pro est une application web Django, avec un front Vue.js. Elle utilise Postgres comme base de données et keycloak pour la gestion des utilisateurs.
Postgres et keycloak sont lancées via docker-compose, et le front est servi par le serveur Django en dev.

### Code source

Cloner le dépôt :

    git clone git@github.com:SocialGouv/ecollecte.git collectepro

**Attention**, il faut avoir créer une clef SSH et l'avoir spécifiée sur github.

On se déplace dans le répertoire :

    cd collectepro

### Node

Installer node 24 et npm.

Installer les dependances node : `npm install`

Builder le front : `npm run build-all` (pour developper par la suite, on pourra utiliser
les commandes `watch` qui rebuildent au fur et à mesure des modifications. Voir
`package.json`)

### Variables d'environnement

Certaines variables d'environnement doivent être positionnées pour que l'application
fonctionne.

On définit les variables d'environnement dans le fichier `.env`.
On peut utiliser le fichier d'exemple comme ceci:

    cp .env.sample .env

Les variables d'environnement sont automatiquement intégrées au process uWSGI via le
fichier `ecc/wsgi.py` - de même pour le fichier `ecc/manage.py`.

Dans le fichier `.env`, modifier l'adresse de la db :

```
DATABASE_URL=postgres://ecc:ecc@localhost:5432/ecc
```

### Postgres et Keycloak

Lancer les conteneurs docker pour Postgres et Keycloak :

    docker-compose up -d

Keycloak est directement chargé avec un realm collecte-pro. Le compte administrateur de l’instance est «admin» avec le mot de passe «admin».
Pour créer les comptes administrateur collecte-pro ainsi que le compte administrateur du realm, if faut lancer le script `deploy/local/init_keycloak.sh` (il faut que le conteneur keycloak soit démarré).

    ./deploy/local/init_keycloak.sh

Pour charger les fonctions Postgres nécessaires pour les différents tableau de bord et les purge, il faut lancer le script `deploy/local/init_postgres.sh` (il faut que le conteneur postgres soit démarré).

    ./deploy/local/init_postgres.sh

### Python et Django

Le projet utilise Python 3.14. Cette version doit être installée sur la machine. Un venv est utilisé pour isoler les dépendances python.

    python3 -m venv venv
    source venv/bin/activate
    python3 -m pip install --upgrade pip
    pip install -r requirements.txt

Migrer la db : `python manage.py migrate`

Collecter les fichiers statiques : `python manage.py collectstatic --noinput`

Lancer le serveur local : `python manage.py runserver 0:8080`

Aller sur `http://localhost:8080/` et se logger avec le compte «admin_fonctionnel» et le mot de passe «1234».

## Création de nouvel utilisateur

### Création d’un nouvel utilisateur admin

Un nouvel utilisateur admin peut être créé via Keycloak, en se loggant sur l'interface d'administration de Keycloak avec le compte admin/admin.
Le nouvel utilisateur doit être créé dans le realm `collecte-pro`, et lui donner le rôle `admin` du client `client_1` pour qu'il puisse se logger sur l'interface d'administration de collecte-pro.

### Création d’un nouvel utilisateur répondant

Un nouveau répondant peut être créé via keycloak, en se loggant sur l'interface d'administration de Keycloak avec le compte admin/admin.
Aucun rôle n’est nécessaire pour se logger sur l’interface de collecte-pro, mais il faut que le compte soit activé et qu’il ait un mot de passe.

Il est aussi possible de créer un nouveau répondant via l’interface collecte-pro en l’ajoutant directement dans la liste des organisme interrogés.
Le compte sera créé dans keycloak et un mot de passe devras lui être ajouté.

## Restaurer/Sauvegarder la base de données en dev

Aucun dump n'est actuellement fourni par défaut car l'ancien était obsolète.

Le mot de passe est `ecc` (si créé comme signalé plus haut).

### Créer un nouveau dump

    pg_dump --verbose --clean --no-acl --no-owner -h postgres -U ecc -d ecc > db.dump

### Charger le dump dans la base

    psql -h localhost -U ecc -d ecc < db.dump

## Login et envoi d'emails

Les utlisateurs admin peuvent se logger à <http://localhost:8080/admin>.

Les utilisateurs non-admin doivent d'abord être créés via un utilisateur admin.

### Serveur d'email en local

Python contient un petit serveur SMTP, qui printe les mail dans la console au lieu de
les envoyer. C'est le plus simple pour developper.

Ajoutez les settings suivants dans `.env` :

```
export EMAIL_HOST='localhost'
export EMAIL_PORT=1025
export EMAIL_HOST_USER=''
export EMAIL_HOST_PASSWORD=''
export EMAIL_USE_TLS=False
export DEFAULT_FROM_EMAIL='testing@example.com'
```

Et lancez le serveur :
`python -m smtpd -n -c DebuggingServer localhost:1025`

## libmagic

Le serveur Django utilise libmagic (pour vérifier les types des fichiers uploadés), qui
doit être présent sur la machine. Vous pouvez essayer de démarrer sans, et si le serveur
lève une erreur c'est qu'il faut l'installer à la main sur votre machine.

Instructions d'installation données par django-magic, le package que nous utilisons :
<https://github.com/ahupp/python-magic#installation>

## Définition des locales

Cette plateforme utilise l'encodage UTF-8 à plusieurs endroit, notamment pour les nom de
fichiers uploadés.

Pour que cela fonctionne, il faut configurer correctement les 'locales', par exemple
comme ceci :

    localedef -c -f UTF-8 -i fr_FR fr_FR.UTF-8
    export LANG=fr_FR.UTF-8
    export LC_ALL=fr_FR.UTF-8

## Envoi d'emails périodiques

On utilise Celery Beat et Redis pour gérer l'envoi d'emails périodiques.

La fréquence des envois est configurée dans django admin, avec l'application
'django_celery_beat'.

Pour démarrer celery beat, il y a la commande suivante:

    celery worker --beat -A ecc -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler &

Un autre façon de faire, est d'installer un service systemd:

    ln -s /opt/e-controle/deploy/conf/celery.service /etc/systemd/system/celery.service
    systemctl daemon-reload
    systemctl start celery
    systemctl restart status
    tail /var/log/ecc-celery.log

Si le serveur Redis n'est pas fourni, on peut l'installer:

    apt-get install redis
    systemctl start redis
    systemctl enable redis
    redis-cli ping

## uWSGI

Le server d'application uWSGI est utilisé en production.
Pour plus de détail : <https://uwsgi-docs.readthedocs.io/en/latest/>

## Parcel : Bundler JS

Nous avons fait le choix d'utiliser le bundler Parcel qui est une alternative à Webpack.
Voir le fichier ``package.json`` pour plus de détails.

Quelques commandes bash utiles:

    npm install  # Pour installer les dépendences

    npm run build-all

    npm run watch-control-detail  # Pour construire le fichier bundle en mode watch
    npm run build-control-detail  # Pour construire le fichier bundle

    npm run watch-questionnaire-create
    npm run watch-questionnaire-detail
    npm run watch-session-management

## Tests

### Backend tests

Lancer les tests :

    `pytest`

ou

    `pytest -s <dossier>`

(le flag -s sert a laisser le debugger prendre le controle si besoin).

### Frontend tests

Ils se situent dans `static/src/` avec le code, dans des dossiers `test`. Ce sont des
tests Jest, pour trouver de la doc googler "test Vue with Jest" par exemple.

Lancer les tests : `npm test`

Debugger un test : plusieurs debuggers sont possibles, dont Chrome Dev Tools et
Webstorm/Pycharm. Voir <https://jestjs.io/docs/en/troubleshooting>

Vous pouvez également utiliser VSCode, voir la doc complète :
<https://code.visualstudio.com/docs/editor/debugging>
