from django.conf import settings
from django.shortcuts import reverse
from pytest import mark


pytestmark = mark.django_db


def test_production_environment(client):
    settings.ENV_NAME = "production"
    url = reverse("login")
    response = client.get(url)
    assert "Vous êtes actuellement sur un environnement de test" not in response.content.decode(response.charset)


def test_recette_environment(client):
    settings.ENV_NAME = "recette"
    url = reverse("login")
    response = client.get(url)
    assert "Vous êtes actuellement sur un environnement de test" in response.content.decode(response.charset)
    assert "recette" in response.content.decode(response.charset)


def test_no_environment(client):
    settings.ENV_NAME = ""
    url = reverse("login")
    response = client.get(url)
    assert "Vous êtes actuellement sur un environnement de test" not in response.content.decode(response.charset)
