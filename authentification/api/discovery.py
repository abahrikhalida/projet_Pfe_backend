
import requests
import xmltodict
from functools import lru_cache

EUREKA_BASE  = 'http://localhost:8761/eureka'
GATEWAY_URL  = 'http://localhost:8083'  # ← toujours passer par le gateway

# Services qui s'appellent via le Gateway (pas directement)
GATEWAY_ROUTED = {
    'SERVICE-NODE-PARAM',
    # ajouter d'autres si besoin
}


@lru_cache(maxsize=10)
def discover_service(app_name: str) -> str:
    # Si le service passe par le Gateway, retourner directement le Gateway
    if app_name in GATEWAY_ROUTED:
        return GATEWAY_URL

    # Sinon, découverte normale via Eureka
    url  = f"{EUREKA_BASE}/apps/{app_name}"
    resp = requests.get(url, timeout=5)
    resp.raise_for_status()

    data      = xmltodict.parse(resp.content)
    instances = data['application']['instance']
    first     = instances[0] if isinstance(instances, list) else instances

    return first['homePageUrl'].rstrip('/')