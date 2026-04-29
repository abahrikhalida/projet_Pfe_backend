from rest_framework.permissions import BasePermission


def get_role(user):
    return str(getattr(user, 'role', '')).lower().strip()


class IsDirecteur(BasePermission):
    def has_permission(self, request, view):
        return get_role(request.user) == 'directeur'


class IsDivisionnaire(BasePermission):
    def has_permission(self, request, view):
        return get_role(request.user) == 'divisionnaire'




class IsChef(BasePermission):
    def has_permission(self, request, view):
        return get_role(request.user) == 'chef'
class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return get_role(request.user) == 'admin'



class IsAgent(BasePermission):
    """Tous les rôles authentifiés"""
    def has_permission(self, request, view):
        return get_role(request.user) == 'agent'

        # return get_role(request.user) in (
        #     'directeur',
        #     'directeur_region',
        #     'divisionnaire',
        #     'chef',
        #     'responsable_structure',
        #     'agent',
        # )
class IsAll(BasePermission):
    """Tous les rôles authentifiés"""
    def has_permission(self, request, view):

        return get_role(request.user) in (
            'directeur',
            'directeur_region',
            'divisionnaire',
            'chef',
            'responsable_structure',
            'agent',
        )
    
class IsUser(BasePermission):
    """Tous les rôles authentifiés"""
    def has_permission(self, request, view):
        return get_role(request.user) in (
            'admin',
            'responsable_structure'
        )
class IsResponsableStructure(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and getattr(request.user, 'role', None) == 'responsable_structure'
        )
class IsResponsableDepartement(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and getattr(request.user, 'role', None) == 'responsable_departement'
        )
     

# permissions.py — ajouter ce qui manque
class IsDirecteurRegion(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and getattr(request.user, 'role', None) == 'directeur_region'
        )
class IsDirecteurDirection(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and getattr(request.user, 'role', None) == 'directeur_direction'
        )