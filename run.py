from scraper.scraper_bs import scrape_carrefour
from scraper.database import init_db, insert_data
import config

def main():
    print("🕸️ Iniciando scraper...")

    # 1. Inicializar DB
    init_db(config.DB_PATH)
    print("📦 Base de datos inicializada.")

    # 2. Ejecutar Scraper
    data = scrape_carrefour()
    if not data:
        print("⚠️ No se encontraron datos.")
        return
    print(f"📄 Se obtuvieron {len(data)} registros.")

    # 3. Guardar en la DB
    insert_data(data, config.DB_PATH)
    print(f"💾 Insertados {len(data)} registros.")

    print("✅ Proceso finalizado.")


if __name__ == "__main__":
    main()
