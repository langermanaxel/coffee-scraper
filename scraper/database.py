import sqlite3
from pathlib import Path
from typing import Iterable, Tuple


def get_connection(db_path: Path):
    """Devuelve una conexión SQLite con foreign_keys activado."""
    con = sqlite3.connect(db_path)
    con.execute("PRAGMA foreign_keys = 1")
    return con


def init_db(db_path: Path) -> None:
    """Crea el archivo y la tabla si no existen."""
    db_path.parent.mkdir(exist_ok=True)

    with get_connection(db_path) as con:
        con.execute("""
            CREATE TABLE IF NOT EXISTS prices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_name TEXT NOT NULL,
                price REAL NOT NULL,
                source TEXT NOT NULL,
                scraped_at TEXT NOT NULL
            )
        """)

    print(f"[OK] Base inicializada en {db_path}")


def insert_data(
    data: Iterable[Tuple[str, float, str, str]],
    db_path: Path
) -> None:
    """Inserta múltiples filas. Cada item debe ser una tupla con:
    (product_name, price, source, scraped_at)
    """

    data = list(data)

    if not data:
        print("[!] No hay datos para insertar.")
        return

    # Validación mínima
    for row in data:
        if len(row) != 4:
            raise ValueError(f"Fila inválida (se esperaban 4 columnas): {row}")

    with get_connection(db_path) as con:
        con.executemany(
            """
            INSERT INTO prices (product_name, price, source, scraped_at)
            VALUES (?, ?, ?, ?)
            """,
            data,
        )

    print(f"[OK] Guardados {len(data)} registros en la base.")
