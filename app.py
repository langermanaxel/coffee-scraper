from flask import Flask
from api.routes import api_bp
from web.routes import web_bp

app = Flask(__name__)

# Registrar blueprints
app.register_blueprint(api_bp)
app.register_blueprint(web_bp)

if __name__ == "__main__":
    app.run(debug=True)
