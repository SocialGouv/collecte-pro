from random import choice

from django.views.generic import TemplateView
from django.shortcuts import render

from utils.email import send_email


class Accueil(TemplateView):
    template_name = "presentation/accueil.html"


class Presentation(TemplateView):
    template_name = "presentation/presentation.html"


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
