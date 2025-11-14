import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Iterable, Tuple

DB_PATH = Path("data/prices.sqlite")


def get_connection():
    """Devuelve una conexión SQLite con foreign_keys activado."""
    con = sqlite3.connect(DB_PATH)
    con.execute("PRAGMA foreign_keys = 1")
    return con


def init_db() -> None:
    """Crea el archivo y la tabla si no existen."""
    DB_PATH.parent.mkdir(exist_ok=True)

    with get_connection() as con:
        con.execute("""
            CREATE TABLE IF NOT EXISTS prices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_name TEXT NOT NULL,
                price REAL NOT NULL,
                source TEXT NOT NULL,
                scraped_at TEXT NOT NULL
            )
        """)
    print("[OK] Base inicializada.")


def insert_data(data: Iterable[Tuple[str, float, str, str]]) -> None:
    """Inserta múltiples filas. Cada item debe ser una tupla con:
    (product_name, price, source, scraped_at)
    """
    data = list(data)

    if not data:
        print("[!] No hay datos para insertar.")
        return

    # Validación superficial
    for row in data:
        if len(row) != 4:
            raise ValueError(f"Fila inválida (se esperaban 4 columnas): {row}")

    with get_connection() as con:
        con.executemany(
            """
            INSERT INTO prices (product_name, price, source, scraped_at)
            VALUES (?, ?, ?, ?)
            """,
            data,
        )
    print(f"[OK] Guardados {len(data)} registros en la base.")
