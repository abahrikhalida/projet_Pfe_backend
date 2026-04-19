import requests
import xmltodict

EUREKA_BASE = 'http://localhost:8761/eureka'

def discover_service(app_name: str) -> str:
    """
    Retourne la homePageUrl de la première instance UP de l'application Eureka.
    """
    url = f"{EUREKA_BASE}/apps/{app_name}"
    resp = requests.get(url, timeout=5)
    resp.raise_for_status()
    data = xmltodict.parse(resp.content)

    # Selon qu'il y ait une ou plusieurs instances
    instances = data['application']['instance']
    first = instances[0] if isinstance(instances, list) else instances

    home_url = first['homePageUrl']
    return home_url.rstrip('/')