# authentication_service/utils_archivage.py
import requests
import logging
from django.conf import settings
from .discovery import discover_service

logger = logging.getLogger(__name__)

ARCHIVE_APP_NAME     = 'ARCHIVAGE-SERVICE'
INTER_SERVICE_SECRET = getattr(settings, 'INTER_SERVICE_SECRET', 'changeme-secret')


def get_archive_url() -> str:
    from django.core.cache import cache
    cache_key = f'eureka_url_{ARCHIVE_APP_NAME}'
    cached = cache.get(cache_key)
    if cached:
        return cached
    url = discover_service(ARCHIVE_APP_NAME)
    cache.set(cache_key, url, timeout=30)
    return url


def archive_user(user, reason: str, archived_by_id: int = None) -> bool:
    """
    Envoie un User au service ARCHIVAGE-SERVICE (port 8004).
    À appeler AVANT user.delete() ou lors de is_active = False.
    """
    payload = {
        'original_id':    user.id,
        'email':          user.email,
        'nom':            user.nom,
        'prenom':         user.prenom,
        'role':           user.role,
        'region_id':      str(user.region_id)      if user.region_id      else None,
        'structure_id':   str(user.structure_id)   if user.structure_id   else None,
        'direction_id':   str(user.direction_id)   if user.direction_id   else None,
        'departement_id': str(user.departement_id) if user.departement_id else None,
        'archive_reason': reason,
        'archived_by_id': archived_by_id,
        'full_snapshot': {
            'id':           user.id,
            'email':        user.email,
            'nom':          user.nom,
            'prenom':       user.prenom,
            'role':         user.role,
            'matricule':    user.matricule,
            'telephone':    user.telephone,
            'poste':        user.poste,
            'is_active':    user.is_active,
            'region_id':    str(user.region_id)      if user.region_id      else None,
            'structure_id': str(user.structure_id)   if user.structure_id   else None,
            'direction_id': str(user.direction_id)   if user.direction_id   else None,
            'departement_id': str(user.departement_id) if user.departement_id else None,
        },
    }

    try:
        base_url = get_archive_url()
        response = requests.post(
            f'{base_url}/archive/users/',
            json=payload,
            headers={
                'Content-Type':     'application/json',
                'X-Service-Secret': INTER_SERVICE_SECRET,
            },
            timeout=5,
        )

        if response.status_code == 201:
            logger.info(f"[archivage] User {user.email} archivé")
            return True

        logger.error(
            f"[archivage] Échec user {user.email}: "
            f"HTTP {response.status_code} — {response.text[:200]}"
        )
        return False

    except requests.exceptions.Timeout:
        logger.error(f"[archivage] Timeout — ARCHIVAGE-SERVICE (8004)")
        return False
    except requests.exceptions.RequestException as e:
        logger.error(f"[archivage] Service indisponible: {e}")
        return False