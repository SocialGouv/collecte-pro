from django.contrib.auth.models import Group
from mozilla_django_oidc.auth import OIDCAuthenticationBackend
from user_profiles.models import UserProfile


class EccOIDCAuthenticationBackend(OIDCAuthenticationBackend):
    def create_user(self, claims):
        user = super(EccOIDCAuthenticationBackend, self).create_user(claims)
        self.user_ecollecte(user, claims)
        return user

    def update_user(self, user, claims):
        self.user_ecollecte(user, claims)
        return user

    def user_ecollecte(self, user, claims):
        """
        Mise à jour des utilisateurs depuis les informations KeyCloak.
        """
        user.first_name = claims.get("given_name", "")
        user.last_name = claims.get("family_name", "")
        user.username = claims.get("email", "")
        # Gestion des droits administrateurs
        if "superuser" in claims.get("roles", []):
            user.is_superuser = True
            user.is_staff = True
        else:
            user.is_superuser = False
            user.is_staff = False
        if "admin" in claims.get("roles", []):
            user.is_staff = True
            user.groups.add(Group.objects.filter(name="admin_metier").first())
        else:
            if not user.is_superuser:
                user.is_staff = False
            user.groups.remove(Group.objects.filter(name="admin_metier").first())
        user.save()
        # Gestion des droits métier
        user.profile.profile_type = UserProfile.AUDITED
        if UserProfile.INSPECTOR in claims.get("roles", []):
            user.profile.profile_type = UserProfile.INSPECTOR
        user.profile.save()
