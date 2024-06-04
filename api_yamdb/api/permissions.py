from django.db.models import Model, QuerySet
from rest_framework import permissions
from rest_framework.request import Request
from rest_framework.viewsets import ModelViewSet


class IsAdminOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS or (
            request.user.is_authenticated and request.user.is_admin)


class IsAdminOrIsSuperUser(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.user.is_authenticated and (request.user.is_superuser
                                                  or request.user.is_admin)


class IsAdminOrIsSuperUserOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and (request.user.is_admin
                                                  or request.user.is_superuser
                                                  )


class IsAdminOrModeratorOrAuthorOrReadOnly(permissions.BasePermission):

    def has_permission(self, request: Request, view: QuerySet):
        user = request.user
        if not user.is_authenticated:
            return request.method in permissions.SAFE_METHODS
        return True

    def has_object_permission(self, request: Request,
                              view: ModelViewSet, obj: Model):
        user = request.user
        if not user.is_authenticated:
            return request.method in permissions.SAFE_METHODS
        return (request.method in permissions.SAFE_METHODS
                or request.method in ('POST', 'PATCH', 'DELETE')
                and (user == obj.author or user.is_moderator or user.is_admin))
