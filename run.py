from scraper.database import init_db
from scraper.scraper_bs import scrape_carrefour
from scraper.utils import export_to_csv


def main():
    print("🕸️ Iniciando scraper de precios de supermercado...")

    # 1. Inicializar base de datos
    try:
        init_db()
        print("📦 Base de datos inicializada correctamente.")
    except Exception as e:
        print(f"❌ Error al inicializar la base de datos: {e}")
        return

    # 2. Ejecutar scraping
    try:
        data = scrape_carrefour()
        if not data:
            print("⚠️ No se encontraron datos para guardar.")
            return
        print(f"📄 Se obtuvieron {len(data)} registros del scraping.")
    except Exception as e:
        print(f"❌ Error durante el scraping: {e}")
        return

    # 3. Exportar CSV
    try:
        export_to_csv(output_csv="data/prices.csv")
        print("📁 CSV exportado correctamente.")
    except Exception as e:
        print(f"❌ Error al exportar CSV: {e}")
        return

    print(f"✅ Proceso finalizado. Se guardaron {len(data)} registros.")


if __name__ == "__main__":
    main()
