from pathlib import Path
import pandas as pd
import sqlite3
from datetime import datetime


def export_all(
    db_path: Path,
    export_dir: Path,
    prefix: str = "carrefour",
):
    """
    Exporta toda la base a CSV, Excel y JSON con fecha automática.
    Devuelve un diccionario con las rutas generadas:
      { "csv": Path(...), "xlsx": Path(...), "json": Path(...) }
    """

    # Asegurar carpeta
    export_dir.mkdir(exist_ok=True, parents=True)

    # Leer base
    con = sqlite3.connect(db_path)
    df = pd.read_sql_query("SELECT * FROM prices", con)
    con.close()

    if df.empty:
        raise ValueError("La tabla 'prices' está vacía, nada para exportar.")

    # Fecha automática YYYY-MM-DD
    today = datetime.now().strftime("%Y-%m-%d")

    # Definir nombres finales
    files = {
        "csv": export_dir / f"{prefix}_{today}.csv",
        "xlsx": export_dir / f"{prefix}_{today}.xlsx",
        "json": export_dir / f"{prefix}_{today}.json",
    }

    # Exportar
    df.to_csv(files["csv"], index=False)
    df.to_excel(files["xlsx"], index=False)
    df.to_json(files["json"], indent=2, orient="records", force_ascii=False)

    return files
