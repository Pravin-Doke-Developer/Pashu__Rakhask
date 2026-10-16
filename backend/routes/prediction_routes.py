import os
from datetime import datetime, timezone

from flask import Blueprint, current_app, jsonify, request

from utils.image_utils import save_uploaded_image, validate_image_file

prediction_bp = Blueprint('prediction_bp', __name__)


@prediction_bp.route('/predict/disease', methods=['POST'])
def predict_disease():
    return _predict_image('disease')


@prediction_bp.route('/predict/breed', methods=['POST'])
def predict_breed():
    return _predict_image('breed')


@prediction_bp.route('/history', methods=['GET'])
def get_history():
    history_service = current_app.extensions['history_service']
    return jsonify({
        'status': 'ok',
        'history': history_service.get_history(),
    })


def _predict_image(model_type: str):
    model_service = current_app.extensions['model_service']
    history_service = current_app.extensions['history_service']
    if 'image' not in request.files:
        return jsonify({'status': 'error', 'error': 'No image file was uploaded.'}), 400

    file_storage = request.files['image']
    max_size_mb = int(current_app.config.get('MAX_IMAGE_SIZE_MB', 10))
    valid, error = validate_image_file(file_storage, max_size_mb=max_size_mb)

    if not valid:
        return jsonify({'status': 'error', 'error': error}), 400

    # Reset the upload stream after validation so the entire image is saved.
    file_storage.stream.seek(0)

    if not model_service.is_available(model_type):
        return jsonify({
            'status': 'error',
            'error': model_service.get_errors().get(
                model_type, f'The {model_type} model is not configured.'
            ),
            'model_type': model_type,
            'supported_classes': model_service.get_supported_classes(model_type),
        }), 503

    filename = file_storage.filename
    dest_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], model_type)
    image_path = save_uploaded_image(file_storage, dest_dir)

    try:
        result = model_service.predict(model_type, image_path)
        if result.get('status') != 'ok':
            return jsonify(result), 500

        entry = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'model_type': model_type,
            'filename': filename,
            'class_name': result.get('class_name'),
            'confidence': result.get('confidence'),
            'source': 'api_inference',
        }
        history_service.add_entry(entry)
        return jsonify(result), 200
    except Exception as exc:  # pragma: no cover - defensive guard
        return jsonify({
            'status': 'error',
            'error': f'Prediction failed: {exc}',
            'model_type': model_type,
        }), 500
