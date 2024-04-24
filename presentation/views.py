
from random import choice

from django.views.generic import TemplateView
from django.shortcuts import render

from utils.email import send_email

from django.http import HttpResponse, JsonResponse

import requests


class Accueil(TemplateView):
    template_name = "presentation/accueil.html"


class Presentation(TemplateView):
    template_name = "presentation/presentation.html"

import requests
from django.http import JsonResponse

def simple_captcha_endpoint(request):
    
    oauth_token = get_oauth_token()

    if not oauth_token:
        return JsonResponse({"error": "Failed to obtain OAuth token."}, status=500)

    headers = {
        'Authorization': 'Bearer ' + oauth_token,
        'Content-Type': 'application/json'
    }

    response = requests.get('https://piste.gouv.fr/piste/captcha/simple-captcha-endpoint', headers=headers)

    if response.status_code == 200:
        return JsonResponse(response.json())
    else:
        return JsonResponse({"error": "Failed to retrieve captcha from PISTE."}, status=response.status_code)



def validationFormulaire(request):
    id = 123988 # provisoire // à rempalcer par CaptchaId
    code = request.POST["captchaFormulaireExtInput"]

    if validate_captcha(id, code):
        demo(request)
        return JsonResponse({"success": True})
    else:
        return JsonResponse({"success": False})

def validate_captcha(id, code):
    oauth_token = get_oauth_token()

    headers = {
        'Authorization': 'Bearer ' + oauth_token,
        'Content-Type': 'application/json'
    }

    data = {
        'id': id,
        'code': code
    }

    url = 'https://piste.gouv.fr/piste/captcha/validate-captcha'

    response = requests.post(url, json=data, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        print("Error validating captcha:", response.text)
        return False

def get_oauth_token():
 
    data = {
        "grant_type": "client_credentials",#
        "client_id": "XXXX", # 
        "client_secret": "YYYY", # 
        "scope": "piste.captchetat"#
    }

    api_url = "https://oauth.piste.gouv.fr/api/oauth/token"

    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    response = requests.post(api_url, data=data, headers=headers)

    if response.status_code == 200:
        token_data = response.json()
        access_token = token_data.get("access_token")
        return access_token
    else:
        print("Failed to retrieve OAuth token:", response.text)
        return None


def demo(request):
    accounts = [
        {
            "demandeur": {"identifiant": "demandeur1@example.org", "mot_de_passe": "collecte-pro"},
            "repondant": {"identifiant": "repondant1@example.org", "mot_de_passe": "collecte-pro"},
        },
        {
            "demandeur": {"identifiant": "demandeur2@example.org", "mot_de_passe": "collecte-pro"},
            "repondant": {"identifiant": "repondant2@example.org", "mot_de_passe": "collecte-pro"},
        },
        {
            "demandeur": {"identifiant": "demandeur3@example.org", "mot_de_passe": "collecte-pro"},
            "repondant": {"identifiant": "repondant3@example.org", "mot_de_passe": "collecte-pro"},
        },
    ]

    if request.method == "POST":
        lastname = request.POST["lastname"]
        firstname = request.POST["firstname"]
        email = request.POST["email"]
        position = request.POST["position"]
        phone = request.POST["phone"]
        contact = request.POST.get("contact", False) == "on"
        access = request.POST.get("access", False) == "on"
        message = request.POST["message"]
        
        
        
        #recipients = ["contact@collecte-pro.gouv.fr", ]
        recipients = ["m.benhmida@cat-amania.com", ]
        context = {
            "lastname": lastname,
            "firstname": firstname,
            "email": email,
            "position": position,
            "phone": phone,
            "contact": contact,
            "access": access,
            "message": message,
        }
        """send_email(
            to=recipients,
            subject="collecte-pro - Formulaire de contact",
            html_template='presentation/email_contact.html',
            text_template='presentation/email_contact.txt',
            extra_context=context,
        )"""
        if access:
            return render(request, "presentation/access.html", choice(accounts))
        return render(request, "presentation/access.html")
    return render(request, "presentation/demo.html")
