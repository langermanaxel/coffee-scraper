from flask import Blueprint, jsonify, request, send_file
import sqlite3
import pandas as pd
from pathlib import Path
import config
from scraper.exporter import export_all

api_bp = Blueprint("api", __name__, url_prefix="/api")


def get_connection():
    con = sqlite3.connect(config.DB_PATH)
    con.row_factory = sqlite3.Row
    return con


def fetch_all(sql, params=()):
    con = get_connection()
    cur = con.cursor()
    cur.execute(sql, params)
    rows = cur.fetchall()
    con.close()
    return [dict(r) for r in rows]


# -----------------------------
# ENDPOINTS API (JSON)
# -----------------------------

@api_bp.get("/prices")
def api_prices():
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


@api_bp.get("/prices/latest")
def api_prices_latest():
    sql = "SELECT * FROM prices ORDER BY scraped_at DESC LIMIT 20"
    return jsonify(fetch_all(sql))


@api_bp.get("/product/<product>/history")
def api_product_history(product):
    sql = """
    SELECT scraped_at, price 
    FROM prices 
    WHERE product_name = ? 
    ORDER BY scraped_at ASC
    """
    return jsonify(fetch_all(sql, (product,)))


@api_bp.get("/export")
def api_export():
    fmt = request.args.get("format", "csv").lower()

    try:
        # Exporta CSV, Excel y JSON automáticamente
        files = export_all(config.DB_PATH, config.EXPORT_DIR, prefix="carrefour")
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    # Buscar el archivo correspondiente según 'format'
    file_path = files.get(fmt)
    if not file_path:
        return jsonify({"error": "Formato no soportado (usa csv, xlsx, json)"}), 400

    return send_file(file_path, as_attachment=True)

