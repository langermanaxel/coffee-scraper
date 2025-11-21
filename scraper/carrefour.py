import requests
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from requests.adapters import HTTPAdapter, Retry
import os


# --------------------------------------
# 1) Sesión HTTP con retries
# --------------------------------------
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


# --------------------------------------
# 2) Parseo seguro de productos
# --------------------------------------
def parse_product(product: dict, category: str) -> Optional[Tuple[str, float, str, str]]:
    """Devuelve (nombre, precio, fuente, fecha) o None si el producto no sirve."""
    name = product.get("productName")
    if not name:
        return None

    try:
        price = product["items"][0]["sellers"][0]["commertialOffer"]["Price"]
        price = float(price)
    except (KeyError, IndexError, TypeError, ValueError):
        return None

    scraped_at = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    return (name, price, "Carrefour", scraped_at)


# --------------------------------------
# 3) Scraping de una categoría
# --------------------------------------
def scrape_category(session: requests.Session, category: str, url: str) -> List[Tuple]:
    # Si hay proxy → usarlo
    api_key = os.getenv("SCRAPER_API_KEY")
    if api_key:
        target_url = f"http://api.scraperapi.com/?api_key={api_key}&url={url}"
    else:
        target_url = url

    print(f"[Request] {target_url}")

    try:
        response = session.get(target_url, timeout=20)
    except Exception as e:
        print(f"[Error] Conexión fallida: {e}")
        return []

    print("Status:", response.status_code)

    # Carrefour bloqueado → HTML → no es JSON
    if "application/json" not in response.headers.get("Content-Type", ""):
        print("❌ Carrefour devolvió HTML o CAPTCHA (bloqueado).")
        print("Preview:", response.text[:300])
        return []

    try:
        data = response.json()
    except Exception as e:
        print("❌ Error parseando JSON:", e)
        print("Preview:", response.text[:300])
        return []

    results = [parse_product(p, category) for p in data if parse_product(p, category)]
    return results



# --------------------------------------
# 4) Scraping principal de Carrefour
# --------------------------------------
def scrape_carrefour() -> List[Tuple]:
    """Scrapea productos desde Carrefour AR y devuelve lista de tuplas."""
    
    api_urls: Dict[str, str] = {
        "Café":   "https://www.carrefour.com.ar/api/catalog_system/pub/products/search/cafe",
        "Leche":  "https://www.carrefour.com.ar/api/catalog_system/pub/products/search/leche",
        "Azúcar": "https://www.carrefour.com.ar/api/catalog_system/pub/products/search/azucar"
    }

    session = get_http_session()
    all_results: List[Tuple] = []

    print("🔍 Iniciando scraping de Carrefour...")

    for category, url in api_urls.items():
        print(f"🛒 Consultando categoría: {category}")
        products = scrape_category(session, category, url)
        print(f"   → {len(products)} productos encontrados.")
        all_results.extend(products)

    print(f"📦 Total productos scrapeados: {len(all_results)}")

    return all_results
