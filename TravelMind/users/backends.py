from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

UserModel = get_user_model()


class EmailOrUsernameBackend(ModelBackend):
    """
    Lets the single login form accept either a username or an email address
    in the same field - rest_framework_simplejwt's TokenObtainPairSerializer
    calls Django's authenticate(username=<value>, password=...) unchanged,
    so this only needs registering in AUTHENTICATION_BACKENDS; no view,
    serializer, or frontend field rename required.

    Email is not a unique column on CustomUser (a handful of pre-existing
    accounts share one), so a value that matches more than one account's
    email falls back to an exact username match instead of guessing which
    account to log into - it never logs into the wrong account.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get(UserModel.USERNAME_FIELD)
        if username is None or password is None:
            return None

        try:
            user = UserModel.objects.get(Q(username__iexact=username) | Q(email__iexact=username))
        except UserModel.DoesNotExist:
            return None
        except UserModel.MultipleObjectsReturned:
            try:
                user = UserModel.objects.get(username__iexact=username)
            except UserModel.DoesNotExist:
                return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
