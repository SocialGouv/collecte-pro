# Installation de l'application

## Mise à jour de la distribution

    sudo apt-get update
    sudo apt-get upgrade


## Installation des programmes nécessaires

    sudo apt-get install git python3 python3-pip python3-venv curl build-essential redis-server nginx


## Création de la base et du compte

    CREATE USER ecc PASSWORD 'ecc';
    CREATE DATABASE ecc OWNER ecc;
    \q


## Connexion au serveur web avec un utilisateur ecollecte

    cd ~


## Installation de l'environnement virtuel et activation

    python3 -m venv venv
    source venv/bin/activate
    python3 -m pip install --upgrade pip


## On récupère les sources

    git clone --depth 1 --single-branch --branch main https://github.com/SocialGouv/ecollecte.git
    cd ecollecte


## Installation de la partie node via npm

    npm install
    npm run build-all


## Installation des librairies

    pip install -r requirements.txt


## Création du fichier .env et édition pour prise en compte de la base de données

    cp .env.sample .env
    vi .env

Retirer le commentaire devant la ligne et spécifier le serveur à utiliser

    # export DATABASE_URL=postgres://ecc:ecc@localhost:5432/ecc

Spécifier le port à utilier

    export PORT=8000

Configurer l'environnement sécurisé

    export DEBUG=False
    export SECRET_KEY="entrer une chaine de caractères au hasard"

Puis sourcer le fichier

    source .env


## Migration de la base de données

    python3 manage.py migrate


## Collecte des fichiers statiques

    python3 manage.py collectstatic --noinput


## Création d'un super utilisateur

    python3 manage.py createsuperuser
    # J'utilise admin / admin


## Mise en place des services spécifiques à ecollecte

Création d'un lien symbolique vers le fichier de configuration de l'application

    ln -s /home/ecollecte/ecollecte/deploy/conf/ecollecte.service /etc/systemd/system
    ln -s /home/ecollecte/ecollecte/deploy/conf/celery.service /etc/systemd/system


## Lancer les services

    systemctl ecollecte start
    systemctl celery start


## Configurer le reverse proxy nginx

    ln -s ~/ecollecte/deploy/conf/ecollecte.conf /etc/nginx/sites-enabled
    nginx -


## Vérifier que le site est bien lancé

    https://localhost/


# Mise à jour de l'application


## Récupérer la dernière version du code source

    cd ~/ecollecte
    git pull


## Sourcer l'environnement

    source .env
    source ../venv/bin/activate


## Mettre à jour les librairies

    pip install -r requirements.txt
    npm install
    npm run build-all


## Mettre la base à jour

    python3 manage.py migrate


## Collecter les fichiers statiques

    python3 manage.py collectstatic --noinput


## Redémarrer les services

    systemctl ecollecte restart
    systemctl celery restart
