from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsRedactorOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.method in SAFE_METHODS or
            request.user and request.user.is_staff
        )


class IsAuthorOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.method in SAFE_METHODS or
            request.user and view.get_object() == request.user
        )
