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
        Updating users from keycloak informations.
        """
        user.first_name = claims.get("given_name", "")
        user.last_name = claims.get("family_name", "")
        if "admin" in claims.get("roles", []):
            user.is_staff = True
            user.is_superuser = True
        elif "admin" not in claims.get("roles", []):
            user.is_staff = False
            user.is_superuser = False
        user.save()

        if not user.is_staff:
            if UserProfile.INSPECTOR in claims.get("roles", []):
                user.profile.profile_type = UserProfile.INSPECTOR
            else:
                user.profile.profile_type = UserProfile.AUDITED
            user.profile.save()
