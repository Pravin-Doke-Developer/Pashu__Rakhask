import os
from pathlib import Path

from flask import Flask
from flask_cors import CORS

from routes.health_routes import health_bp
from routes.prediction_routes import prediction_bp
from services.history_service import HistoryService
from services.model_service import ModelService


def create_app():
    app = Flask(__name__)
    app.config['MAX_IMAGE_SIZE_MB'] = int(os.getenv('MAX_IMAGE_SIZE_MB', 10))
    app.config['UPLOAD_FOLDER'] = str(Path(__file__).resolve().parent / 'uploads')
    app.extensions['model_service'] = ModelService()
    app.extensions['history_service'] = HistoryService()
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Configure CORS with explicit headers to prevent intermittent errors
    CORS(app, resources={r'/*': {
        'origins': '*',
        'methods': ['GET', 'POST', 'OPTIONS'],
        'allow_headers': ['Content-Type'],
        'max_age': 86400,
    }})
    
    app.register_blueprint(health_bp)
    app.register_blueprint(prediction_bp)
    return app


app = create_app()


if __name__ == '__main__':
    host = os.getenv('API_HOST', '127.0.0.1')
    port = int(os.getenv('API_PORT', 5000))
    app.run(host=host, port=port, debug=True, use_reloader=False)
