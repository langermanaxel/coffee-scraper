import sqlite3
from datetime import datetime
import os

DB_PATH = "data/prices.sqlite"

def init_db():
    os.makedirs("data", exist_ok=True)
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS prices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_name TEXT,
        price REAL,
        source TEXT,
        scraped_at TEXT
    )
    """)
    con.commit()
    con.close()

def insert_data(data):
    if not data:
        print("[!] No hay datos para insertar.")
        return
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.executemany("""
    INSERT INTO prices (product_name, price, source, scraped_at)
    VALUES (?, ?, ?, ?)
    """, data)
    con.commit()
    con.close()
    print(f"[OK] Guardados {len(data)} registros en la base.")
