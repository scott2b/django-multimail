from django.contrib.auth.backends import ModelBackend
from multimail.models import EmailAddress

class MultiEmailAuthenticationBackend(ModelBackend):
    """Allows to login via email address and password. username is interpreted as email address."""

    def authenticate(self, username=None, password=None):

        try:
            email = EmailAddress.objects.get(email__iexact=username)
            user = email.user
        except EmailAddress.DoesNotExist:
            return None

        if user.check_password(password):
            return user

        return None
