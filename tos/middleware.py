from django.shortcuts import reverse, redirect


class WelcomeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path == reverse('welcome') or \
                request.path == reverse('logout') or \
                request.path == reverse('oidc_logout') or \
                request.user.is_anonymous or \
                request.user.is_staff or \
                request.user.is_superuser or \
                request.user.profile.agreed_to_tos:
            # Don't redirect welcome, to avoid an infinite redirect loop.
            # Don't redirect logout and oidc_logout, because you should be able to log out before agreeing to TOS.
            # Don't redirect anonymous user, let them go to login page.
            # Don't redirect if admin or super_user, let them go to admin pages.
            # Don't redirect if user already agreed to TOS.
            pass
        else:
            return redirect(reverse('welcome'))

        response = self.get_response(request)

        return response

