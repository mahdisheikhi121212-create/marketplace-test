from rest_framework.permissions import BasePermission


class IsVerifiedSeller(BasePermission):
    message = "فقط فروشنده تأییدشده اجازه انجام این عملیات را دارد."

    def has_permission(self, request, view):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        try:
            seller = user.seller_profile
        except AttributeError:
            return False

        return seller.is_verified
