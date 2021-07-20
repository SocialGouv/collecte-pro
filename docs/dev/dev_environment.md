# Environnement de développement

## Variables d'environnement

Certaines variables d'environnement doivent être positionnées pour que l'application
fonctionne.

On définit les variables d'environnement dans le fichier `.env`.
On peut utiliser le fichier d'exemple comme ceci:

    cp .env.sample .env

Les variables d'environnement sont automatiquement intégrées au process uWSGI via le
fichier `ecc/wsgi.py` - de même pour le fichier `ecc/manage.py`.

## Postgres

Installer postgres, et créer un user nommé `ecc` et une database nommée `ecc`.

## Node

Installer node et npm.

Installer les dependances node : `npm install`

Builder le front : `npm bun build-all` (pour developper par la suite, on pourra utiliser
les commandes `watch` qui rebuildent au fur et à mesure des modifications. Voir
`package.json`)

## Python et Django

Installer Python 3.7 minimum.

Installer un environnement virtuel python (venv) : `python3 -m venv venv`

Activer l'environnement : `source venv/bin/activate`

Installer les dépendences python : `pip install -r requirements.txt`

Dans le fichier `.env`, modifier l'adresse de la db :
```
export DATABASE_URL=postgres://ecc:ecc@localhost:5432/ecc
. .env
```

Puis sourcer l'environnement : `source .env`

Migrer la db : `python manage.py migrate`

Collecter les fichiers statiques : `python manage.py collectstatic --noinput`

Lancer le serveur local sur le port 8080 : `python manage.py runserver 0:8080`

Aller sur `http://localhost:8080/admin` et se logger avec un des utilisateurs mentionnés
ci-dessous.


# Restaurer/Sauvegarder la base de données en dev

Aucun dump n'est actuellement fourni par défaut car l'ancien était obsolète.

## Charger le dump dans la base

    psql -h localhost -U ecc -d ecc < db.dump

Le mot de passe est `ecc` (créé plus haut)

Voilà des utilisateurs admin qui existent par défaut quand on utilise le dump :
- Admin: admin@demo.com / demo12345
- Controlé: robert@demo.com / demo12345
- Contrôleur: martine@demo.com / demo12345

Note : Pour créer un nouveau dump :

    pg_dump --verbose --clean --no-acl --no-owner -h postgres -U ecc -d ecc > db.dump

Ensuite, ajouter les fichiers de `media.zip` dans un dossier `media` à la racine de ce
projet.

# Login et envoi d'emails

Les utlisateurs admin peuvent se logger sans envoi d'email à http://localhost:8080/admin.

Les utilisateurs non-admin doivent d'abord être créés via un utilisateur admin.

## Serveur d'email en local

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


# libmagic

Le serveur Django utilise libmagic (pour vérifier les types des fichiers uploadés), qui
doit être présent sur la machine. Vous pouvez essayer de démarrer sans, et si le serveur
lève une erreur c'est qu'il faut l'installer à la main sur votre machine.

Instructions d'installation données par django-magic, le package que nous utilisons :
https://github.com/ahupp/python-magic#installation


# Des commandes utiles

    # lancer les tests unitaires :
    pytest


# Définition des locales

Cette plateforme utilise l'encodage UTF-8 à plusieurs endroit, notamment pour les nom de
fichiers uploadés.

Pour que cela fonctionne, il faut configurer correctement les 'locales', par exemple
comme ceci :

    localedef -c -f UTF-8 -i fr_FR fr_FR.UTF-8
    export LANG=fr_FR.UTF-8
    export LC_ALL=fr_FR.UTF-8

# Envoi d'emails périodiques

On utilise Celery Beat et Redis pour gérer l'envoi d'emails périodiques.

La fréquence des envois est configurée dans django admin, avec l'applicaiton
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

    yum -y install redis
    systemctl start redis
    systemctl enable redis
    redis-cli ping

# uWSGI

Le server d'application uWSGI est utilisé sur Heroku.
Pour plus de détail : https://uwsgi-docs.readthedocs.io/en/latest/

# Parcel : Bundler JS

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


# Tests

## Backend tests

Lancer les tests :

    `pytest`

ou

    `pytest -s <dossier>`

(le flag -s sert a laisser le debugger prendre le controle si besoin).


## Frontend tests

Ils se situent dans `static/src/` avec le code, dans des dossiers `test`. Ce sont des
tests Jest, pour trouver de la doc googler "test Vue with Jest" par exemple.

Lancer les tests : `npm test`

Tester un fichier en particulier :

`npm test <tout ou partie du nom de fichier>`.

Par exemple : `npm test Metadata` trouve le fichier
`static/src/questionnaires/test/QuestionnaireMetadataCreate.spec.js`.

Debugger un test : plusieurs debuggers sont possibles, dont Chrome Dev Tools et
Webstorm/Pycharm. Voir https://jestjs.io/docs/en/troubleshooting

Vous pouvez également utiliser VSCode, voir la doc complète :
https://code.visualstudio.com/docs/editor/debugging
