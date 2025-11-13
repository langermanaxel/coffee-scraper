from scraper.database import init_db
from scraper.scraper_bs import scrape_carrefour
from scraper.utils import export_to_csv

if __name__ == "__main__":
    print("🕸️ Iniciando scraper de precios de supermercado...")
    init_db()
    data = scrape_carrefour()
    export_to_csv()
    print(f"✅ Proceso finalizado. Se guardaron {len(data)} registros.")
