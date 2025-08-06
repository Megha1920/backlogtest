from rest_framework.permissions import BasePermission

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and hasattr(request.user, 'role') and request.user.role == 'admin')


class IsManager(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == 'manager'

class IsTeamMember(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == 'member'

class IsManagerOrAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.role in ['admin', 'manager']
