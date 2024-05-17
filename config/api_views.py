from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site

from rest_framework import viewsets
from rest_framework.response import Response

from parametres.models import Parametre


class ConfigViewSet(viewsets.ViewSet):

    def list(self, request):
        support_email_param = Parametre.objects.filter(code="SUPPORT_EMAIL").filter(deleted_at__isnull=True).first()

        if support_email_param:
            support_email = support_email_param.url
        else:
            support_email = None  # ou définissez une valeur par défaut

        config = {
            'expected_inspector_email_endings': settings.EXPECTED_INSPECTOR_EMAIL_ENDINGS,
            'site_url': f'https://{get_current_site(request).domain}',
            'static_files_url': settings.STATIC_URL,
            'env_name': settings.ENV_NAME,
            'support_team_email': support_email,
        }
        return Response(config)

