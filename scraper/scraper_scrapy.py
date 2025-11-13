import scrapy
from datetime import datetime
from .database import insert_data

class CoffeeSpider(scrapy.Spider):
    name = "coffee_spider"
    start_urls = [
        "https://www.tiendasuper.com/cafe",
        "https://www.proveedorleche.com.ar/productos",
    ]

    def parse(self, response):
        products = []
        for item in response.css(".product-item"):
            name = item.css(".product-title::text").get()
            price = item.css(".price::text").get()
            if name and price:
                try:
                    price_value = float(price.replace("$", "").replace(",", "").strip())
                except:
                    continue
                products.append((name, price_value, response.url, datetime.utcnow().isoformat()))

        if products:
            insert_data(products)
            self.log(f"Guardados {len(products)} items de {response.url}")
