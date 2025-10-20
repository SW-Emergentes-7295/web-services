from flask import Flask
from flasgger import Swagger

from ai_recognition.infrastructure.route import ai_recognition_bp
from home_configuration.infrastructure.route import home_configuration_bp
from iam.infrastructure.route import iam_bp
from configuration_preferences.infrastructure.route import configuration_preferences_bp

app = Flask(__name__)
app.register_blueprint(ai_recognition_bp, url_prefix="/api/v1/ai-recognition")
app.register_blueprint(home_configuration_bp, url_prefix="/api/v1/home-configuration")
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
    app.run(host="0.0.0.0", port=8000, debug=True)