import pandas as pd
import sqlite3
from pathlib import Path

def export_to_csv(
    db_path: str = "data/prices.sqlite",
    table_name: str = "prices",
    output_csv: str = "data/prices.csv"
):
    """
    Exporta una tabla de SQLite a CSV.
    
    Args:
        db_path: Ruta a la base de datos SQLite.
        table_name: Nombre de la tabla a exportar.
        output_csv: Ruta donde guardar el CSV generado.
    """
    
    db_path = Path(db_path)
    output_csv = Path(output_csv)

    # Crear carpeta destino si no existe
    output_csv.parent.mkdir(parents=True, exist_ok=True)

    # Verificar existencia del archivo de DB
    if not db_path.exists():
        print(f"❌ No existe la base de datos: {db_path}")
        return

    try:
        con = sqlite3.connect(db_path)
        
        # Verificar si la tabla existe
        query = f"""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='{table_name}'
        """
        exists = pd.read_sql_query(query, con)

        if exists.empty:
            print(f"❌ No existe la tabla '{table_name}' en la base {db_path}")
            return
        
        # Exportar
        df = pd.read_sql_query(f"SELECT * FROM {table_name}", con)
        df.to_csv(output_csv, index=False)

        print(f"✅ Exportado a {output_csv} ({len(df)} filas)")

    except Exception as e:
        print(f"❌ Error durante la exportación: {e}")

    finally:
        try:
            con.close()
        except:
            pass

