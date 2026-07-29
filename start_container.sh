#!/bin/bash

# On lance les migrations au lancement du conteneur
python manage.py migrate

# Lancement de l’application
python manage.py runserver 0:8080
