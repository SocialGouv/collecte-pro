
from random import choice

from django.views.generic import TemplateView
from django.shortcuts import render

from utils.email import send_email
from alerte.models import Alert
from datetime import datetime
from django.db.models import Q

from django.http import HttpResponse, JsonResponse

from django.conf import settings

from django.views.decorators.csrf import csrf_exempt

import requests
import json
import base64

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


def simple_captcha_endpoint(request):
    try:
        oauth_token = get_oauth_token()

        if not oauth_token:
            return JsonResponse({"error": "Failed to obtain OAuth token."}, status=500)

        headers = {
            'Authorization': 'Bearer ' + oauth_token,
            'Content-Type': 'application/json'
        }
        
        all_params = request.GET.dict()
        get_param = all_params.get('get')
        
        print(f"[CAPTCHA] Request GET param: {get_param}")
        
        # L'API v2 n'accepte que 'image' ou 'sound'
        # Ignorer les demandes de 'script-include' (compatible v1)
        if get_param == 'script-include':
            print("[CAPTCHA] Ignoring script-include request")
            return HttpResponse('', content_type='text/javascript')
        
        if get_param not in ['image', 'sound']:
            return JsonResponse({"error": "Invalid get parameter. Must be 'image' or 'sound'."}, status=400)
        
        # Filtrer les paramètres pour ne passer que ceux acceptés par l'API v2
        api_params = {'get': get_param}
        if 'c' in all_params:  # Nom du captcha
            api_params['c'] = all_params['c']
        if 't' in all_params:  # UUID du captcha pour le son
            api_params['t'] = all_params['t']
        
        print(f"[CAPTCHA] Sending to API: {api_params}")
        
        response = requests.get(settings.SIMPLE_CAPTCHA_ENDPOINT_URL, headers=headers, params=api_params)

        if response.status_code == 200:
            # API v2 retourne un JSON avec {uuid, imageb64} ou audio
            if get_param == 'image':
                try:
                    data = response.json()
                    captcha_uuid = data.get('uuid')
                    image_base64 = data.get('imageb64')
                    
                    print(f"[CAPTCHA SUCCESS] UUID: {captcha_uuid}")
                    print(f"[CAPTCHA SUCCESS] Image base64 length: {len(image_base64) if image_base64 else 0}")
                    print(f"[CAPTCHA SUCCESS] Image base64 starts with: {image_base64[:50] if image_base64 else 'NULL'}")
                    
                    if not image_base64:
                        print("[CAPTCHA ERROR] No imageb64 in response")
                        return JsonResponse({"error": "No image data in response"}, status=500)
                    
                    # Stocker la base64 dans la session pour récupération ultérieure
                    request.session[f'captcha_image_{captcha_uuid}'] = image_base64
                    # Aussi stocker l'UUID du captcha pour la validation
                    request.session[f'captcha_uuid_{captcha_uuid}'] = captcha_uuid
                    request.session.save()
                    
                    # Retourner uniquement l'UUID
                    response_data = {'uuid': captcha_uuid}
                    return JsonResponse(response_data)
                except ValueError as e:
                    print(f"[CAPTCHA JSON ERROR] {str(e)}")
                    print(f"[CAPTCHA RAW RESPONSE] {response.text[:500]}")
                    return JsonResponse({"error": "Invalid JSON response from API"}, status=500)
            elif get_param == 'sound':
                # Pour le son, retourner directement l'audio
                print(f"[CAPTCHA] Returning audio ({len(response.content)} bytes)")
                return HttpResponse(response.content, content_type='audio/wav')
        else:
            print(f"[CAPTCHA ERROR] Status Code: {response.status_code}")
            print(f"[CAPTCHA ERROR] Response Content: {response.text}")
            print(f"[CAPTCHA ERROR] Request Params: {api_params}")
            response.raise_for_status()
    except requests.RequestException as e:
        print(f"[CAPTCHA EXCEPTION] Exception Type: {type(e).__name__}")
        print(f"[CAPTCHA EXCEPTION] Exception Details: {str(e)}")
        return JsonResponse({"error": str(e)}, status=500)
    except Exception as e:
        print(f"[CAPTCHA GENERAL EXCEPTION] {type(e).__name__}: {str(e)}")
        return JsonResponse({"error": str(e)}, status=500)


def captcha_image_endpoint(request):
    """Endpoint qui retourne l'image PNG binaire pour contourner les restrictions CSP."""
    uuid = request.GET.get('uuid')
    
    if not uuid:
        return HttpResponse('Missing UUID', status=400)
    
    # Récupérer la base64 stockée dans la session
    session_key = f'captcha_image_{uuid}'
    image_base64 = request.session.get(session_key)
    
    if not image_base64:
        return HttpResponse('CAPTCHA expired or not found', status=404)
    
    try:
        # Extraire les données base64 (enlever le préfixe data:image/png;base64,)
        if image_base64.startswith('data:image/png;base64,'):
            image_base64 = image_base64.replace('data:image/png;base64,', '')
        
        # Décoder la base64 en binaire
        image_binary = base64.b64decode(image_base64)
        
        print(f"[CAPTCHA IMAGE] Serving binary PNG for UUID {uuid}, size: {len(image_binary)} bytes")
        
        # Retourner l'image binaire avec le bon Content-Type
        return HttpResponse(image_binary, content_type='image/png')
    except Exception as e:
        print(f"[CAPTCHA IMAGE ERROR] {str(e)}")
        return HttpResponse('Error decoding image', status=500)


@csrf_exempt
def validationFormulaire(request):
    if request.method == 'POST':
        post_data = request.POST
        user_entered_captcha_code = post_data.get('userEnteredCaptchaCode')
        captcha_id = post_data.get('captchaId')

        print(f"[VALIDATION] Captcha ID: {captcha_id}")
        print(f"[VALIDATION] User entered code: {user_entered_captcha_code}")

        oauth_token = get_oauth_token()
        if not oauth_token:
            return JsonResponse({"error": "Failed to obtain OAuth token."}, status=500)

        headers = {
            'Authorization': 'Bearer ' + oauth_token,
            'Content-Type': 'application/json'
        }

        data = {
            'uuid': captcha_id,
            'code': user_entered_captcha_code
        }

        try:
            print(f"[VALIDATION] Sending to URL: {settings.VALIDER_CAPTCHA_URL}")
            print(f"[VALIDATION] Data: {data}")
            response = requests.post(settings.VALIDER_CAPTCHA_URL, json=data, headers=headers)
            print(f"[VALIDATION] Response Status: {response.status_code}")
            print(f"[VALIDATION] Response Content: {response.text}")
            
            # Ne pas lever d'exception, gérer tous les status codes
            if response.status_code == 200:
                response_data = response.json()
                print(f"[VALIDATION] Response Data: {response_data}")
                return JsonResponse(response_data, safe=False)
            else:
                # L'API retourne une erreur (ex: 400, 404, etc.)
                error_text = response.text
                print(f"[VALIDATION ERROR] API returned error: {error_text}")
                return JsonResponse({
                    "success": False,
                    "error": error_text if error_text else f"Erreur {response.status_code}"
                }, status=200)  # Retourner 200 pour que le frontend puisse lire la réponse
                
        except requests.RequestException as e:
            print(f"[VALIDATION ERROR] Exception Type: {type(e).__name__}")
            print(f"[VALIDATION ERROR] Exception Details: {str(e)}")
            error_message = {"success": False, "error": "Erreur de connexion au service de validation"}
            return JsonResponse(error_message, status=200)
     
def get_oauth_token():
    
    data = {
        "grant_type": settings.GRANT_TYPE,
        "client_id": settings.CLIENT_ID,
        "client_secret": settings.CLIENT_SECRET,
        "scope": settings.SCOPE,
    }
            
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    try:
        print(f"[OAUTH DEBUG] Request URL: {settings.OAUTH_URL}")
        print(f"[OAUTH DEBUG] Request Data: {data}")
        response = requests.post(settings.OAUTH_URL, data=data, headers=headers)
        print(f"[OAUTH DEBUG] Response Status: {response.status_code}")
        print(f"[OAUTH DEBUG] Response Content: {response.text}")
        response.raise_for_status()
        token_data = response.json()
        print(f"[OAUTH DEBUG] Token Data: {token_data}")
        access_token = token_data.get("access_token")
        return access_token
    except requests.RequestException as e:
        print("Failed to retrieve OAuth token:", e)
        return None
   
@csrf_exempt
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
        contact = (request.POST.get("contact", False) == "on") or (request.POST.get("contact", False) == "true")
        access = (request.POST.get("access", False) == "on") or (request.POST.get("access", False) == "true")
        message = request.POST["message"]
        
        
        recipients = ["contact@collecte-pro.gouv.fr", ]
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
        send_email(
            to=recipients,
            subject="collecte-pro - Formulaire de contact",
            html_template='presentation/email_contact.html',
            text_template='presentation/email_contact.txt',
            extra_context=context,
        )
        if access:
            return render(request, "presentation/access.html", choice(accounts))
        return render(request, "presentation/access.html")
    return render(request, "presentation/demo.html")
    
