import pandas as pd
import sqlite3
import os

def export_to_csv():
    os.makedirs("data", exist_ok=True)
    con = sqlite3.connect("data/prices.sqlite")
    df = pd.read_sql_query("SELECT * FROM prices", con)
    con.close()
    df.to_csv("data/prices.csv", index=False)
    print(f"✅ Exportado a data/prices.csv ({len(df)} filas)")
