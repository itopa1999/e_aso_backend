# third party imports
from rest_framework import permissions
from rest_framework.permissions import BasePermission
from administrator.models import User


class IsOwnerOrReadOnly(BasePermission):
    """
    Custom permission to allow users to edit their own object.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.user == request.user


class IsCDSLeaderPermission(BasePermission):

    def has_permission(self, request, view):
        user = request.user

        if not user.is_authenticated:
            return False

        if not user.is_superuser and not user.is_cds_leader:
            self.message = "Your account doesn't have enough. Please contact support."
            return False

        return True
    

class CanPostPermission(BasePermission):

    def has_permission(self, request, view):
        user = request.user

        if not user.is_authenticated:
            return False

        if not user.is_superuser and not user.can_post:
            self.message = "Your access has been blocked. Please contact support."
            return False

        return True
    
    

class CanPostPermission(BasePermission):

    def has_permission(self, request, view):
        user = request.user

        if not user.is_authenticated:
            return False

        if not user.is_superuser and not user.can_chat:
            self.message = "Your access has been blocked. Please contact support."
            return False

        return True
    
    
    
    
    
class CanCommentPermission(BasePermission):

    def has_permission(self, request, view):
        user = request.user

        if not user.is_authenticated:
            return False

        if not user.is_superuser and not user.can_comment:
            self.message = "Your access has been blocked. Please contact support."
            return False

        return True
    
    
    
class IsSuperAdminPermission(BasePermission):

    def has_permission(self, request, view):
        user = request.user

        if not user.is_authenticated:
            return False

        if not user.is_superuser:
            self.message = "Your access has been blocked. Please contact support."
            return False

        return True