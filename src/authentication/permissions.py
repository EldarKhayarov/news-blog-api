from rest_framework.permissions import BasePermission


class IsSelf(BasePermission):
    def has_permission(self, request, view):
        user = view.get_object()
        return bool(request.user and request.user == user)


class IsSelfOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        # Raw
        user = view.get_object()
        return False
