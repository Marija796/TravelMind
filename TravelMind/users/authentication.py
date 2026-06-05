from rest_framework_simplejwt.authentication import JWTAuthentication


class SilentJWTAuthentication(JWTAuthentication):
    """
    Like JWTAuthentication but treats invalid/expired tokens as anonymous
    instead of raising AuthenticationFailed (401). This allows AllowAny
    views to remain accessible when the client sends a stale token.
    """
    def authenticate(self, request):
        try:
            return super().authenticate(request)
        except Exception:
            return None
