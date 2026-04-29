# import requests
# from django.core.cache import cache
# from rest_framework.authentication import BaseAuthentication
# from rest_framework.exceptions import AuthenticationFailed
# from dataclasses import dataclass
# from .discovery import discover_service  # ton fichier existant

# AUTH_APP_NAME = 'AUTHENTICATION-SERVICE'


# def get_auth_base_url() -> str:
#     cache_key = f'eureka_url_{AUTH_APP_NAME}'
#     cached = cache.get(cache_key)
#     if cached:
#         return cached
#     url = discover_service(AUTH_APP_NAME)
#     cache.set(cache_key, url, timeout=30)
#     return url


# @dataclass
# class RemoteUser:
#     id: int
#     email: str
#     role: str
#     nom_complet: str
#     is_authenticated: bool = True
#     is_active: bool = True

#     @property
#     def is_anonymous(self):
#         return False

#     def has_perm(self, perm, obj=None):
#         return True

#     def has_module_perms(self, app_label):
#         return True


# class RemoteJWTAuthentication(BaseAuthentication):
#     def authenticate(self, request):
#         auth_header = request.headers.get('Authorization', '')
#         if not auth_header.startswith('Bearer '):
#             return None

#         token = auth_header.split(' ', 1)[1].strip()

#         try:
#             base_url = get_auth_base_url()
#             resp = requests.get(
#                 f'{base_url}/api/me/',
#                 headers={'Authorization': f'Bearer {token}'},
#                 timeout=3,
#             )
#         except requests.RequestException:
#             cache.delete(f'eureka_url_{AUTH_APP_NAME}')
#             raise AuthenticationFailed('Service authentification injoignable.')

#         if resp.status_code == 401:
#             raise AuthenticationFailed('Token invalide ou expiré.')
#         if resp.status_code != 200:
#             raise AuthenticationFailed(f'Erreur auth: {resp.status_code}')

#         data = resp.json()
#         return (RemoteUser(
#             id=data['id'],
#             email=data['email'],
#             role=data.get('role', ''),
#             nom_complet=data.get('nom_complet', ''),
#         ), token)
import requests
from django.core.cache import cache
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from dataclasses import dataclass, field
from .discovery import discover_service

AUTH_APP_NAME = 'AUTHENTICATION-SERVICE'


def get_auth_base_url() -> str:
    cache_key = f'eureka_url_{AUTH_APP_NAME}'
    cached = cache.get(cache_key)
    if cached:
        return cached
    url = discover_service(AUTH_APP_NAME)
    cache.set(cache_key, url, timeout=30)
    return url


@dataclass
class RemoteUser:
    id: int
    email: str
    role: str
    nom_complet: str
    region_id: str = None       # ✅ ajouté
    structure_id: str = None    # ✅ ajouté
    direction_id: str = None      # 🔥 AJOUT
    departement_id: str = None    # 🔥 AJOUT
    is_authenticated: bool = True
    is_active: bool = True

    @property
    def is_anonymous(self):
        return False

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True


class RemoteJWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return None

        token = auth_header.split(' ', 1)[1].strip()

        try:
            base_url = get_auth_base_url()
            resp = requests.get(
                f'{base_url}/api/me/',
                headers={'Authorization': f'Bearer {token}'},
                timeout=3,
            )
        except requests.RequestException:
            cache.delete(f'eureka_url_{AUTH_APP_NAME}')
            raise AuthenticationFailed('Service authentification injoignable.')

        if resp.status_code == 401:
            raise AuthenticationFailed('Token invalide ou expiré.')
        if resp.status_code != 200:
            raise AuthenticationFailed(f'Erreur auth: {resp.status_code}')

        data = resp.json()
        return (RemoteUser(
            id=data['id'],
            email=data['email'],
            role=data.get('role', ''),
            nom_complet=data.get('nom_complet', ''),
            region_id=data.get('region_id'),        # ✅ ajouté
            structure_id=data.get('structure_id'),  # ✅ ajouté
            direction_id=data.get('direction_id'),        # 🔥 AJOUT
            departement_id=data.get('departement_id'),    # 🔥 AJOUT
        ), token)
        