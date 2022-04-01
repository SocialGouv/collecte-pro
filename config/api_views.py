from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site

from rest_framework import viewsets
from rest_framework.response import Response


class ConfigViewSet(viewsets.ViewSet):

    def list(self, request):
        config = {
            'expected_inspector_email_endings': settings.EXPECTED_INSPECTOR_EMAIL_ENDINGS,
            'site_url': f'https://{get_current_site(request).domain}',
            'static_files_url': settings.STATIC_URL,
            'env_name': settings.ENV_NAME
        }
        return Response(config)
