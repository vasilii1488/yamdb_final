from rest_framework import permissions


class IsAdministrator(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_admin


class IsAuthorOrStaffOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        is_staff = (request.user.is_authenticated
                    and (request.user.is_admin
                         or request.user.is_moderator))
        return (request.method in permissions.SAFE_METHODS
                or obj.author == request.user or is_staff)


class IsAdministratorOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        is_admin = (request.user.is_authenticated
                    and request.user.is_admin)
        return request.method in permissions.SAFE_METHODS or is_admin
