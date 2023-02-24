from django.views.generic import TemplateView


class Accueil(TemplateView):
    template_name = "presentation/accueil.html"


class Presentation(TemplateView):
    template_name = "presentation/presentation.html"
