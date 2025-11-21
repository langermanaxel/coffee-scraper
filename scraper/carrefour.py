import requests
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from requests.adapters import HTTPAdapter, Retry
import os


# ============================================================
# 1) OPCIONAL: PROXY con ScraperAPI (habilitado si existe la key)
# ============================================================
SCRAPER_API_KEY = os.getenv("SCRAPER_API_KEY")  # tomada desde Render

def proxify(url: str) -> str:
    """Devuelve la URL de ScraperAPI si hay KEY, si no usa la URL original."""
    if SCRAPER_API_KEY:
        return f"http://api.scraperapi.com/?api_key={SCRAPER_API_KEY}&url={url}"
    return url


# ============================================================
# 2) Sesión HTTP con headers y retries
# ============================================================
def get_http_session() -> requests.Session:
    session = requests.Session()

    retries = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
    )
    adapter = HTTPAdapter(max_retries=retries)
    session.mount("https://", adapter)

    # Headers reales de Chrome
    session.headers.update({
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/122.0.0.0 Safari/537.36"
        ),
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "es-AR,es;q=0.9,en;q=0.8",
        "Referer": "https://www.carrefour.com.ar/",
        "Origin": "https://www.carrefour.com.ar",
        "sec-ch-ua": "\"Google Chrome\";v=\"122\", \"Chromium\";v=\"122\", \"Not=A?Brand\";v=\"99\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
    })

    return session


# ============================================================
# 3) Parseo seguro de productos
# ============================================================
def parse_product(product: dict, category: str) -> Optional[Tuple[str, float, str, str]]:
    name = product.get("productName")
    if not name:
        return None

    try:
        price = product["items"][0]["sellers"][0]["commertialOffer"]["Price"]
        price = float(price)
    except Exception:
        return None

    scraped_at = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    return (name, price, "Carrefour", scraped_at)


# ============================================================
# 4) Scraping por categoría (con detección de bloqueo)
# ============================================================
def scrape_category(session: requests.Session, category: str, url: str) -> List[Tuple]:
    target = proxify(url)
    print(f"\n📡 Request a: {target}")

    try:
        response = session.get(target, timeout=20)
    except Exception as e:
        print(f"[Error] Conexión fallida: {e}")
        return []

    print("→ Status:", response.status_code)

    # Si Carrefour devolvió HTML => bloqueo Cloudflare
    content_type = response.headers.get("Content-Type", "")
    if "application/json" not in content_type:
        print("❌ Respuesta NO es JSON – posible CAPTCHA o bloqueo.")
        print("Preview:", response.text[:200])
        return []

    try:
        data = response.json()
    except Exception as e:
        print(f"❌ Error JSON: {e}")
        print("Raw:", response.text[:200])
        return []

    results = []
    for p in data:
        row = parse_product(p, category)
        if row:
            results.append(row)

    return results


# ============================================================
# 5) Scraping principal
# ============================================================
def scrape_carrefour() -> List[Tuple]:
    api_urls: Dict[str, str] = {
        "Café":   "https://www.carrefour.com.ar/api/catalog_system/pub/products/search/cafe",
        "Leche":  "https://www.carrefour.com.ar/api/catalog_system/pub/products/search/leche",
        "Azúcar": "https://www.carrefour.com.ar/api/catalog_system/pub/products/search/azucar"
    }

    session = get_http_session()
    all_results: List[Tuple] = []

    print("\n🔍 Iniciando scraping Carrefour...\n")

    for category, url in api_urls.items():
        print(f"🛒 Categoría: {category}")
        products = scrape_category(session, category, url)
        print(f"   → {len(products)} productos obtenidos\n")
        all_results.extend(products)

    print(f"📦 Total Productos Scrapeados: {len(all_results)}")
    return all_results
