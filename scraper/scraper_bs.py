import requests
from datetime import datetime
from .database import insert_data

def scrape_carrefour():
    """Scrapea precios reales de Carrefour Argentina desde su API pública."""
    api_urls = {
        "Café": "https://www.carrefour.com.ar/api/catalog_system/pub/products/search/cafe",
        "Leche": "https://www.carrefour.com.ar/api/catalog_system/pub/products/search/leche",
        "Azúcar": "https://www.carrefour.com.ar/api/catalog_system/pub/products/search/azucar"
    }

    all_data = []

    for categoria, url in api_urls.items():
        print(f"🛒 Consultando API {categoria}...")
        try:
            response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
            response.raise_for_status()
            products = response.json()

            for p in products:
                name = p.get("productName")
                try:
                    price_info = (
                        p["items"][0]["sellers"][0]["commertialOffer"]["Price"]
                    )
                except (IndexError, KeyError):
                    continue

                if name and price_info:
                    all_data.append((name, float(price_info), categoria, datetime.utcnow().isoformat()))

        except Exception as e:
            print(f"[Error] {categoria}: {e}")

    if all_data:
        insert_data(all_data)
    else:
        print("[!] No se obtuvieron productos de la API.")

    return all_data
