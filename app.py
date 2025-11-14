from flask import Flask
from flask_cors import CORS
from flasgger import Swagger
from dotenv import load_dotenv

from ai_recognition.interfaces.route import ai_recognition_bp

from home_configuration.infrastructure.route import home_configuration_bp
from home_configuration.interfaces.home_controller import home_controller_bp
from home_configuration.interfaces.room_controller import room_controller_bp
from home_configuration.interfaces.path_controller import path_controller_bp

from iam.infrastructure.route import init_iam_routes

from configuration_preferences.interfaces.route import configuration_preferences_bp

from shared.infrastructure.database import db

load_dotenv()

app = Flask(__name__)
CORS(app)

# Crear la base de datos y las tablas si no existen
db.create_schemas()

app.register_blueprint(ai_recognition_bp, url_prefix="/api/v1/ai-recognition")

app.register_blueprint(home_configuration_bp, url_prefix="/api/v1/home-configuration")
app.register_blueprint(home_controller_bp, url_prefix="/api/v1/home-controller")
app.register_blueprint(room_controller_bp, url_prefix="/api/v1/room-controller")
app.register_blueprint(path_controller_bp, url_prefix="/api/v1/path-controller")

iam_bp = init_iam_routes(db.get_database())
app.register_blueprint(iam_bp, url_prefix="/api/v1/iam")

app.register_blueprint(configuration_preferences_bp, url_prefix="/api/v1/configuration-preferences")


swagger = Swagger(app, template={
    "swagger": "2.0",
    "info": {
        "title": "VisualGuide API",
        "description": "API Restful for managing the VisualGuide system.",
        "version": "1.0.0",
        "license": {
            "name": "MIT",
            "url": "https://opensource.org/licenses/MIT"
        }
    }}
)

@app.route("/routes")
def list_routes():
    routes = []
    for rule in app.url_map.iter_rules():
        routes.append({
            'endpoint': rule.endpoint,
            'methods': list(rule.methods),
            'rule': str(rule)
        })
    return {"routes": routes}


if __name__ == "__main__":
    #app.run(port=8000, debug=True)
    app.run(host="0.0.0.0", port=8000, debug=True)
