import requests
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from requests.adapters import HTTPAdapter, Retry
from .database import insert_data


# ------------------------------
# 1) Sesión con retries automáticos
# ------------------------------
def get_http_session() -> requests.Session:
    session = requests.Session()
    retries = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
    )
    adapter = HTTPAdapter(max_retries=retries)
    session.mount("https://", adapter)
    session.headers.update({"User-Agent": "Mozilla/5.0"})
    return session


# ------------------------------
# 2) Parseo seguro de cada producto
# ------------------------------
def parse_product(product: dict, category: str) -> Optional[Tuple[str, float, str, str]]:
    """Extrae la info útil de un producto. Devuelve None si faltan datos."""
    name = product.get("productName")
    if not name:
        return None

    try:
        price = (
            product["items"][0]["sellers"][0]["commertialOffer"]["Price"]
        )
        price = float(price)
    except (KeyError, IndexError, TypeError, ValueError):
        return None

    return (
        name,
        price,
        category,
        datetime.utcnow().isoformat(),
    )


# ------------------------------
# 3) Scraping de una categoría
# ------------------------------
def scrape_category(session: requests.Session, category: str, url: str) -> List[tuple]:
    try:
        response = session.get(url, timeout=15)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print(f"[Error] No se pudo obtener {category}: {e}")
        return []

    parsed = []
    for product in data:
        row = parse_product(product, category)
        if row:
            parsed.append(row)

    return parsed


# ------------------------------
# 4) Funcion principal
# ------------------------------
def scrape_carrefour() -> List[tuple]:
    """Scrapea precios de Carrefour Argentina desde su API pública."""

    api_urls: Dict[str, str] = {
        "Café": "https://www.carrefour.com.ar/api/catalog_system/pub/products/search/cafe",
        "Leche": "https://www.carrefour.com.ar/api/catalog_system/pub/products/search/leche",
        "Azúcar": "https://www.carrefour.com.ar/api/catalog_system/pub/products/search/azucar"
    }

    session = get_http_session()
    all_results: List[tuple] = []

    for category, url in api_urls.items():
        print(f"🛒 Consultando API de {category}...")
        results = scrape_category(session, category, url)
        print(f"   → {len(results)} productos encontrados.")
        all_results.extend(results)

    if all_results:
        insert_data(all_results)
    else:
        print("[!] No se obtuvieron productos válidos.")

    return all_results
