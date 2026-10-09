from rest_framework.permissions import BasePermission


class IsAdminOrSuperAdmin(BasePermission):
    message = "شما اجازه دسترسی به این بخش را ندارید."

    def has_permission(self, request, view):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        return (
            user.is_staff
            or user.is_superuser
        )