from flask import Flask
from api.routes import api_bp
from web.routes import web_bp
import os

app = Flask(__name__)

# Registrar blueprints
app.register_blueprint(api_bp)
app.register_blueprint(web_bp)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
