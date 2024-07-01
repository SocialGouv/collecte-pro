from random import choice

from django.http import HttpResponse, JsonResponse
from django.views.generic import TemplateView
from django.shortcuts import render
import requests

#from ecc import settings
from django.conf import settings
from utils.email import send_email
from alerte.models import Alert
from datetime import datetime
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt

class Accueil(TemplateView):
    template_name = "presentation/accueil.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now = datetime.now()
        alerte = Alert.objects.filter(
            Q(start_date__lt=now) | Q(start_date=None)
        ).filter(
            Q(end_date__gt=now) | Q(end_date=None)
        ).first()
        context['alerte'] = alerte
        return context


class Presentation(TemplateView):
    template_name = "presentation/presentation.html"


#START CAPTCHA
def simple_captcha_endpoint(request):
    try:
        oauth_token = get_oauth_token()
        
        if not oauth_token:
            return JsonResponse({"error": "Failed to obtain OAuth token."}, status=500)
        
        headers = {
            'Authorization': 'Bearer ' + oauth_token,
            'Content-Type': 'application/json'
        }
        
        params = request.GET.dict()
        
        response = requests.get(settings.SIMPLE_CAPTCHA_ENDPOINT_URL, headers=headers, params=params)
        
        if response.status_code == 200:
            return HttpResponse(response.content, content_type=response.headers['Content-Type'])
        else:
            response.raise_for_status()
    
    except request.RequestException as e:
        error_message="Internal Server Error."
        return JsonResponse({"error": error_message}, status=500)
    
def get_oauth_token():
    data = {
        "grant_type": settings.GRANT_TYPE,
        "client_id": settings.CLIENT_ID,
        "client_secret": settings.CLIENT_SECRET,
        #"scope": settings.SCOPE,
    }

    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    
    try:
        response = requests.post(settings.OAUTH_URL, data=data, headers=headers)
        response.raise_for_status()
        token_data = response.json()
        access_token = token_data.get("access_token")
        return access_token
    except requests.RequestException as e:
        print("Failed to retrieve OAuth token:", e)
        return None

@csrf_exempt
def validationFormulaire(request):
    if request.method == 'POST':
        post_data = request.POST
        user_entered_captcha_code = post_data.get('userEnteredCaptchaCode')
        captcha_id = post_data.get('captchaId')

        oauth_token = get_oauth_token()
        if not oauth_token:
            return JsonResponse({"error": "Failed to obtain OAuth token."}, status=500)

        headers = {
            'Authorization': 'Bearer ' + oauth_token,
            'Content-Type': 'application/json'
        }

        data = {
            'id': captcha_id,
            'code': user_entered_captcha_code
        }

        try:
            response = requests.post(settings.VALIDER_CAPTCHA_URL, json=data, headers=headers)
            response.raise_for_status()  
            response_data = response.json()
            return JsonResponse(response_data, safe=False)
        except requests.RequestException as e:
            error_message = {"error": "Error validating captcha"}
            return JsonResponse(error_message, status=500)
#END CAPTCHA

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
