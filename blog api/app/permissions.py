from rest_framework import permissions


class IsOwnerOrAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            return True
        else:
            if bool(request.user and request.user.is_authenticated):
                return True
        return False

    def has_object_permission(self, request, view, obj):
        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            return True
        elif request.user.is_superuser:
            return True
        else:
            if obj.owner.id == request.user.id:
                return True
        return False
