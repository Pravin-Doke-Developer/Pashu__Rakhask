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


@health_bp.route('/warmup', methods=['POST'])
def warmup_models():
    """Preload models to avoid first-request latency."""
    model_service = current_app.extensions['model_service']
    
    results = {}
    
    # Try to preload disease model
    try:
        if model_service._ensure_model_loaded('disease'):
            results['disease'] = 'loaded'
        else:
            results['disease'] = 'failed'
    except Exception as e:
        results['disease'] = f'error: {str(e)}'
    
    # Try to preload animal_type model (needed for breed prediction)
    try:
        if model_service._ensure_model_loaded('animal_type'):
            results['animal_type'] = 'loaded'
        else:
            results['animal_type'] = 'failed'
    except Exception as e:
        results['animal_type'] = f'error: {str(e)}'
    
    return jsonify({
        'status': 'ok',
        'warmup_results': results,
        'message': 'Model warmup completed. First predictions will be faster.',
    })
