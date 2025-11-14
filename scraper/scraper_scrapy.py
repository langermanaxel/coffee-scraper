import scrapy
from datetime import datetime
from .database import insert_data


class CoffeeSpider(scrapy.Spider):
    name = "coffee_spider"

    custom_settings = {
        "DOWNLOAD_DELAY": 0.5,     # Evita bloqueos
        "ROBOTSTXT_OBEY": True,    # Buena práctica
    }

    start_urls = [
        "https://www.tiendasuper.com/cafe",
        "https://www.proveedorleche.com.ar/productos",
    ]

    def parse(self, response):
        """Extrae productos genéricamente usando selectores defensivos."""
        products = []

        # Más robusto: soporta diferentes nombres de clases
        items = response.css(".product-item, .item, .product")

        for item in items:
            name = (
                item.css(".product-title::text, .title::text").get()
                or item.css("h2::text, h3::text").get()
            )

            price_raw = (
                item.css(".price::text, .price-tag::text").get()
            )

            if not name or not price_raw:
                continue

            price = self.parse_price(price_raw)
            if price is None:
                continue

            products.append(
                (
                    name.strip(),
                    price,
                    response.url,
                    datetime.utcnow().isoformat(),
                )
            )

        # Guarda si hay resultados
        if products:
            insert_data(products)
            self.logger.info(f"Guardados {len(products)} items desde {response.url}")

    # -----------------------
    # 🔧 Función auxiliar limpia y reutilizable
    # -----------------------
    def parse_price(self, price_str: str):
        """Convierte '$ 1.234,56' -> float con control de errores."""
        try:
            cleaned = (
                price_str
                .replace("$", "")
                .replace(".", "")
                .replace(",", ".")
                .strip()
            )
            return float(cleaned)
        except Exception:
            return None
