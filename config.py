from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

DB_PATH = BASE_DIR / "data" / "prices.sqlite"
EXPORT_DIR = BASE_DIR / "exports"
