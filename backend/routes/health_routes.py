from flask import Blueprint, current_app, jsonify

health_bp = Blueprint('health_bp', __name__)


@health_bp.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'ok',
        'service': 'animal-health-ai-api',
        'message': 'Backend is running.',
    })


@health_bp.route('/status', methods=['GET'])
def models_status():
    model_service = current_app.extensions['model_service']
    return jsonify({
        'status': 'ok',
        'models': model_service.get_status(),
        'errors': model_service.get_errors(),
    })
