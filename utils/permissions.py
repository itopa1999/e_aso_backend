# third party imports
from rest_framework import permissions
from rest_framework.permissions import BasePermission


class IsOwnerOrReadOnly(BasePermission):
    """
    Custom permission to allow users to edit their own object.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.user == request.user


class IsRiderPermission(BasePermission):
    message = "Access is not granted."
    def has_permission(self, request, view):
        user = request.user

        if not user.is_authenticated:
            return False

        if not user.groups.filter(name='Rider').exists():
            return False

        return True
    

class IsAdminPermission(BasePermission):
    message = "Access is not granted."
    def has_permission(self, request, view):
        user = request.user

        if not user.is_authenticated:
            return False

        if not user.groups.filter(name='Admin').exists():
            return False

        return True
    
    

class IsCustomerPermission(BasePermission):
    message = "Access is not granted."
    def has_permission(self, request, view):
        user = request.user

        if not user.is_authenticated:
            return False

        if not user.groups.filter(name='Customer').exists():
            return False

        return True