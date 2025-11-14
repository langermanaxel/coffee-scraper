from flask import Flask, render_template, request, jsonify, send_file
from pathlib import Path
import sqlite3
import pandas as pd

# -----------------------
# Configuración básica
# -----------------------

DB_PATH = Path("data/prices.sqlite")
EXPORTS_DIR = Path("exports")

app = Flask(__name__)


# -----------------------
# Helpers
# -----------------------

def get_connection():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con


def fetch_all(sql, params=()):
    con = get_connection()
    cur = con.cursor()
    cur.execute(sql, params)
    rows = cur.fetchall()
    con.close()
    return [dict(r) for r in rows]


# -----------------------
# Rutas FRONTEND (HTML)
# -----------------------

@app.get("/")
def home():
    """
    Página principal:
    - muestra últimos precios
    - permite filtrar por producto, fuente y fecha
    """
    product = request.args.get("product", "").strip()
    source = request.args.get("source", "").strip()
    date = request.args.get("date", "").strip()

    sql = "SELECT * FROM prices WHERE 1=1"
    params = []

    if product:
        sql += " AND product_name LIKE ?"
        params.append(f"%{product}%")

    if source:
        sql += " AND source = ?"
        params.append(source)

    if date:
        # asumiendo scraped_at en formato "YYYY-MM-DD HH:MM:SS"
        sql += " AND scraped_at LIKE ?"
        params.append(f"{date}%")

    sql += " ORDER BY scraped_at DESC LIMIT 200"

    prices = fetch_all(sql, params)

    # Para los filtros de fuente en el select, etc.
    sources_sql = "SELECT DISTINCT source FROM prices ORDER BY source"
    sources = [r["source"] for r in fetch_all(sources_sql)]

    return render_template(
        "index.html",
        prices=prices,
        product=product,
        source=source,
        date=date,
        sources=sources,
    )


@app.get("/chart/<product>")
def chart(product):
    """
    Página con gráfico de evolución de un producto.
    El JS interno llama a /api/product/<product>/history
    """
    return render_template("chart.html", product=product)


# -----------------------
# Rutas API (JSON)
# -----------------------

@app.get("/api/prices")
def api_prices():
    """
    Devuelve precios en JSON, con los mismos filtros que /.
    """
    product = request.args.get("product", "").strip()
    source = request.args.get("source", "").strip()
    date = request.args.get("date", "").strip()

    sql = "SELECT * FROM prices WHERE 1=1"
    params = []

    if product:
        sql += " AND product_name LIKE ?"
        params.append(f"%{product}%")

    if source:
        sql += " AND source = ?"
        params.append(source)

    if date:
        sql += " AND scraped_at LIKE ?"
        params.append(f"{date}%")

    sql += " ORDER BY scraped_at DESC"

    return jsonify(fetch_all(sql, params))


@app.get("/api/prices/latest")
def api_prices_latest():
    """
    Devuelve los últimos 20 registros scrapeados.
    """
    sql = "SELECT * FROM prices ORDER BY scraped_at DESC LIMIT 20"
    return jsonify(fetch_all(sql))


@app.get("/api/product/<product>/history")
def api_product_history(product):
    """
    Devuelve la evolución de precios para un producto concreto.
    """
    sql = """
    SELECT scraped_at, price
    FROM prices
    WHERE product_name = ?
    ORDER BY scraped_at ASC
    """
    data = fetch_all(sql, (product,))
    return jsonify(data)


@app.get("/api/export")
def api_export():
    """
    Exporta la tabla completa a CSV / Excel / JSON.
    Ejemplo:
      /api/export?format=csv
      /api/export?format=xlsx
      /api/export?format=json
    """
    fmt = request.args.get("format", "csv").lower()
    EXPORTS_DIR.mkdir(exist_ok=True)

    if not DB_PATH.exists():
        return jsonify({"error": f"No existe la base de datos {DB_PATH}"}), 404

    con = get_connection()
    df = pd.read_sql_query("SELECT * FROM prices", con)
    con.close()

    if df.empty:
        return jsonify({"error": "La tabla 'prices' está vacía"}), 400

    # Nombre genérico; si querés, acá podés meter fecha también
    filename = f"prices_export.{fmt}"
    path = EXPORTS_DIR / filename

    if fmt == "csv":
        df.to_csv(path, index=False)
    elif fmt in ("xlsx", "xls"):
        df.to_excel(path, index=False)
    elif fmt == "json":
        df.to_json(path, orient="records", indent=2, force_ascii=False)
    else:
        return jsonify({"error": "Formato no soportado (usa csv, xlsx o json)"}), 400

    return send_file(path, as_attachment=True)


# -----------------------
# Entry point local
# -----------------------

if __name__ == "__main__":
    # Modo desarrollo local
    app.run(debug=True, host="0.0.0.0", port=5000)
