from django.contrib.auth import get_user_model
from django.dispatch import Signal
from django.conf import settings
from django.db.models import Q

from rest_framework import serializers, status
from rest_framework.exceptions import PermissionDenied, ValidationError

from control.models import Control

from .models import UserProfile, Access

from keycloak import KeycloakAdmin
from keycloak.exceptions import KeycloakError
import json
import logging
import re

logger = logging.getLogger(__name__)

# Caractères interdits par Keycloak (sur-ensemble de la validation Django, inclut '!')
_KEYCLOAK_FORBIDDEN_CHARS = re.compile(r'[!*(){}@#$%^&\[\]=+\\|;:\'",<>?/~`]')


def validate_keycloak_name(value: str, field_label: str):
    """
    Validation locale qui mime les règles Keycloak pour firstName/lastName.
    Utilisée quand l'utilisateur est absent de Keycloak (fallback).
    """
    if not value:
        return
    found = _KEYCLOAK_FORBIDDEN_CHARS.findall(value)
    if found:
        unique = ', '.join(set(found))
        raise ValidationError({
            'keycloak_error': f'Le {field_label} contient un caractère non autorisé : {unique}',
            'error_code': 'error-person-name-invalid-character',
        })


# Mapping des codes d'erreur Keycloak vers des messages lisibles
KEYCLOAK_ERROR_MESSAGES = {
    'error-person-name-invalid-character': 'Le prénom ou le nom contient un ou plusieurs caractères non autorisés.',
    'error-invalid-email': "L'adresse email est invalide.",
    'User exists with same username': 'Un utilisateur avec ce username existe déjà.',
    'User exists with same email': 'Un utilisateur avec cet email existe déjà.',
}


def handle_keycloak_error(e: KeycloakError):
    """
    Convertit une KeycloakError en ValidationError DRF (HTTP 400)
    avec un message lisible pour le frontend.
    """
    logger.error("Erreur Keycloak : %s", str(e), exc_info=True)
    error_code = None
    try:
        body = json.loads(e.response_body)
        error_code = body.get('errorMessage') or body.get('error')
    except Exception:
        error_code = getattr(e, 'error_message', None) or str(e)

    message = KEYCLOAK_ERROR_MESSAGES.get(
        error_code,
        f"Erreur lors de la création/mise à jour de l'utilisateur (code : {error_code})."
    )
    raise ValidationError({'keycloak_error': message, 'error_code': error_code})


User = get_user_model()

# These signals are triggered after the user is created/updated via the API
user_api_post_add = Signal()
user_api_post_update = Signal()


def validate_special_characters(value, field_name):
    """
    Validate that the given value does not contain forbidden special characters.
    
    Args:
        value: The string to validate
        field_name: The name of the field being validated (for error message)
    
    Raises:
        ValidationError: If forbidden characters are found
    """
    if not value:
        return value
    
    # Pattern for forbidden special characters
    forbidden_chars_pattern = r'[*(){}@#$%^&\[\]=+\\|;:\'",<>?/~`]'
    found_chars = re.findall(forbidden_chars_pattern, value)
    
    if found_chars:
        unique_chars = ', '.join(set(found_chars))
        raise ValidationError(
            f"Le champ '{field_name}' contient des caractères spéciaux non autorisés : {unique_chars}"
        )
    
    return value


class RemoveControlSerializer(serializers.Serializer):
    control = serializers.PrimaryKeyRelatedField(queryset=Control.objects.all())


class UserProfileSerializer(serializers.ModelSerializer, KeycloakAdmin):
    id = serializers.IntegerField(source='user.pk', read_only=True)
    control = serializers.PrimaryKeyRelatedField(
        queryset=Control.objects.all(), write_only=True, required=False)
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')
    email = serializers.EmailField(source='user.email')
    access = serializers.PrimaryKeyRelatedField(
        queryset=Access.objects.all(), write_only=True, required=False)

    class Meta:
        model = UserProfile
        fields = (
            'id', 'first_name', 'last_name', 'email', 'profile_type',
            'organization', 'control', 'is_audited', 'is_inspector', 'access')

    def validate_first_name(self, value):
        """Validate first name for special characters"""
        return validate_special_characters(value, 'Prénom')

    def validate_last_name(self, value):
        """Validate last name for special characters"""
        return validate_special_characters(value, 'Nom')

    def create(self, validated_data):
        if settings.KEYCLOAK_ACTIVE:
            keycloak_admin = KeycloakAdmin(
                server_url=settings.KEYCLOAK_URL,
                username=settings.KEYCLOAK_ADMIN_USERNAME,
                password=settings.KEYCLOAK_ADMIN_PASSWORD,
                realm_name=settings.KEYCLOAK_REALM,
                client_id=settings.OIDC_RP_CLIENT_ID,
                client_secret_key=settings.OIDC_RP_CLIENT_SECRET,
                verify=False,
            )
        profile_data = validated_data
        control = profile_data.pop('control', None)
        user_data = profile_data.pop('user')

        # lowercase the email
        email = user_data.get('email')
        if email:
            email = email.lower()
        user_data['username'] = email

        # Find if user already exists.
        profile = UserProfile.objects.filter(user__email=email).first()

        session_user = self.context['request'].user
        if control is not None and control not in session_user.profile.user_controls('demandeur'):
            e = PermissionDenied(
                detail=("Only Demandeur can create user."),
                code=status.HTTP_403_FORBIDDEN,
            )
            raise e
        if control is not None and control.is_deleted:
            e = PermissionDenied(
                detail=("Create user is only possible on active control."),
                code=status.HTTP_403_FORBIDDEN,
            )
            raise e
        inspector_role = False
        access_type = 'repondant'
       
        if settings.KEYCLOAK_ACTIVE:
            # Find keycloak inspector role
            role = keycloak_admin.get_client_role(client_id=settings.KEYCLOAK_URL_CLIENT_ID, role_name=UserProfile.INSPECTOR)
        if profile_data.get('profile_type') == UserProfile.INSPECTOR:
            inspector_role = True
            access_type = 'demandeur'
        if profile:
            if settings.KEYCLOAK_ACTIVE:
                user_id_keycloak = keycloak_admin.get_user_id(user_data['username'])
                if user_id_keycloak:
                    # Update keycloak user data if exist
                    try:
                        keycloak_admin.update_user(
                            user_id=user_id_keycloak,
                            payload={'firstName': user_data.get('first_name'),
                            'lastName': user_data.get('last_name')}
                        )
                    except KeycloakError as e:
                        handle_keycloak_error(e)
                else:
                    logger.warning(
                        "Utilisateur '%s' introuvable dans Keycloak, validation locale appliquée.",
                        user_data['username']
                    )
                    validate_keycloak_name(user_data.get('first_name', ''), 'prénom')
                    validate_keycloak_name(user_data.get('last_name', ''), 'nom')
            profile.user.first_name = user_data.get('first_name')
            profile.user.last_name = user_data.get('last_name')
            profile.organization = profile_data.get('organization')
            profile.profile_type = profile_data.get('profile_type')
            profile.send_files_report = True
            profile.user.save()
            profile.save()
        else:
            if settings.KEYCLOAK_ACTIVE:
                # Create keycloak user if doesn't exist
                try:
                    new_user = keycloak_admin.create_user(
                        {
                            "email": user_data['username'],
                            "username": user_data['username'],
                            "enabled": True,
                            "firstName": user_data['first_name'],
                            "lastName": user_data['last_name']
                        },
                        exist_ok=True
                    )
                except KeycloakError as e:
                    handle_keycloak_error(e)
            user = User.objects.create(**user_data)
            profile_data['user'] = user
            profile_data['send_files_report'] = True
            profile = UserProfile.objects.create(**profile_data)
        if control:
            access = Access.objects.filter(Q(control=control) & Q(userprofile=profile)).first()
            if access:
                access.access_type = access_type
                access.userprofile = profile
                access.control = control
                access.save()
            else:
                access = Access.objects.create(access_type=access_type, userprofile=profile, control=control)
        if control:
            user_api_post_add.send(
                sender=UserProfile, session_user=session_user, user_profile=profile,
                control=control)
        else:
            user_api_post_update.send(
                sender=UserProfile, session_user=session_user, user_profile=profile)
        return profile

class AccessSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='access.pk', read_only=True)
    access_type = serializers.CharField()
    control = serializers.PrimaryKeyRelatedField(
        queryset=Control.objects.all())
    userprofile = serializers.PrimaryKeyRelatedField(
        queryset=UserProfile.objects.all())

    class Meta:
        model = Access
        fields = ('id', 'access_type', 'control', 'userprofile')
