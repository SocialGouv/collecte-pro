from django.contrib.auth import get_user_model
from django.dispatch import Signal
from django.conf import settings
from django.db.models import Q

from rest_framework import serializers

from control.models import Control

from .models import UserProfile, Access

from keycloak import KeycloakAdmin


User = get_user_model()

# These signals are triggered after the user is created/updated via the API
user_api_post_add = Signal()
user_api_post_update = Signal()


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
        if control and control not in Control.objects.filter(access__in=self.request.user.profile.access.all()):
            raise serializers.ValidationError(
                f"{session_user} n'est pas authorisé à modifier cette procédure : {control}")
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
                # Update keycloak user data if exist
                keycloak_admin.update_user(
                    user_id=user_id_keycloak,
                    payload={'firstName': user_data.get('first_name'),
                    'lastName': user_data.get('last_name')}
                )
                if inspector_role:
                    # Assign inspector role
                    keycloak_admin.assign_client_role(
                        client_id=settings.KEYCLOAK_URL_CLIENT_ID,
                        user_id=user_id_keycloak,
                        roles=[role,],
                    )
                else:
                    # Remove inspector role
                    keycloak_admin.delete_client_roles_of_user(
                        user_id=user_id_keycloak,
                        client_id=settings.KEYCLOAK_URL_CLIENT_ID,
                        roles=[role,],
                    )
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
            user = User.objects.create(**user_data)
            profile_data['user'] = user
            profile_data['send_files_report'] = True
            profile = UserProfile.objects.create(**profile_data)
            if inspector_role and settings.KEYCLOAK_ACTIVE:
                keycloak_admin.assign_client_role(
                    client_id=settings.KEYCLOAK_URL_CLIENT_ID,
                    user_id=new_user,
                    roles=[role,],
                )
        if control:
            profile.controls.add(control) # TODO almorin - à supprimer au moment du nettoyage du user_profile_controls
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