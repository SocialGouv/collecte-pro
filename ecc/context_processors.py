from django.contrib.sites.models import Site
from django.conf import settings


def current_site(request):
    return {'current_site': Site.objects.get_current()}

def env_name(request):
    return {'ENV_NAME': settings.ENV_NAME}
