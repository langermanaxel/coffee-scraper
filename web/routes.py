from flask import Blueprint, render_template, request
import requests

web_bp = Blueprint("web", __name__)


@web_bp.get("/")
def home():
    params = dict(request.args)
    try:
        prices = requests.get("http://localhost:5000/api/prices", params=params).json()
    except:
        prices = []

    # Obtener fuentes
    try:
        sources = requests.get("http://localhost:5000/api/prices").json()
        sources = sorted({p["source"] for p in sources})
    except:
        sources = []

    return render_template(
        "index.html",
        prices=prices,
        product=params.get("product", ""),
        source=params.get("source", ""),
        date=params.get("date", ""),
        sources=sources,
    )


@web_bp.get("/chart/<product>")
def chart(product):
    return render_template("chart.html", product=product)
