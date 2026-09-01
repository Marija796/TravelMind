from rest_framework.permissions import BasePermission


class IsAdminRole(BasePermission):
    """
    Gates every admin-only endpoint. Checks the explicit CustomUser.role
    field (not is_staff/is_superuser, which are reserved for Django's own
    /admin/ site and kept separate from this app's role concept).
    """
    message = 'This action requires administrator privileges.'

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == 'admin')
