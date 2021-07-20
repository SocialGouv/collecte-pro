# Installation de l'application

## Mise à jour de la distribution

    sudo apt-get update
    sudo apt-get upgrade

## Installation des programmes nécessaires

    sudo apt-get install git python3 python3-pip python3-venv curl build-essential

## Création de la base et du compte

    CREATE USER ecc PASSWORD 'ecc';
    CREATE DATABASE ecc OWNER ecc;
    \q

## Connexion au serveur web avec un utilisateur ecollecte

    cd ~

## Pour lequel on récupère le zip qu'on décompresse

    unzip ecollecte.zip -d ecollecte
    cd ecollecte

## Installation de la partie node via npm

    npm install
    npm run build-all

## Installation de l'environnement virtuel et activation

    python3 -m venv venv
    source venv/bin/activate
    python3 -m pip install --upgrade pip

## Installation des librairies

    pip install -r requirements.txt

## Création du fichier .env et édition pour prise en compte de la base de données

    cp .env.sample .env
    vi .env

Retirer le commentaire devant la ligne et spécifier le serveur à utiliser

    # export DATABASE_URL=postgres://ecc:ecc@localhost:5432/ecc

Puis sourcer le fichier

    source .env

## Migration de la base de données

    python3 manage.py migrate

## Collecte des fichiers statiques

    python3 manage.py collectstatic --noinput

## Création d'un super utilisateur

    python3 manage.py createsuperuser
    # J'utilise admin / admin

## Lancer le serveur après avoir spécifié le port

    export PORT=8000
    uwsgi --ini uwsgi.ini

## Vérifier que le site est bien lancé

    http://localhost:8000/
