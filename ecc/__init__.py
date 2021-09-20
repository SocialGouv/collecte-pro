from django.conf import settings
from django.utils.http import urlencode

default_app_config = 'ecc.apps.EccConfig'

def provider_logout(request):
    return settings.OIDC_OP_LOGOUT_ENDPOINT + '?' + urlencode({
        'redirect_uri': request.build_absolute_uri(settings.LOGOUT_REDIRECT_URL),
        'client_id': settings.OIDC_RP_CLIENT_ID
    })
