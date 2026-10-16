import json
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image


MODEL_TYPES = ('disease', 'breed')

CLASS_INFORMATION = {
    'disease': {
        'foot-and-mouth': {
            'title': 'Foot-and-mouth disease',
            'description': (
                'A highly contagious viral disease affecting cloven-hoofed animals, '
                'including cattle.'
            ),
            'details': [
                'Possible signs include fever, blisters or sores in the mouth and on the feet, '
                'drooling, and difficulty walking.',
                'If suspected, contact a veterinarian or local animal-health authority promptly '
                'and follow their advice about limiting animal movement.',
            ],
        },
        'healthy': {
            'title': 'No supported disease pattern detected',
            'description': (
                'The model classified this image as healthy rather than one of the disease '
                'classes it was trained to recognize.'
            ),
            'details': [
                'This result does not confirm that the animal is healthy or rule out other '
                'conditions.',
                'Seek veterinary advice if the animal shows concerning signs or its condition '
                'changes.',
            ],
        },
        'lumpy': {
            'title': 'Lumpy skin disease',
            'description': (
                'A viral cattle disease that can cause skin nodules and may spread between '
                'animals, including through insect vectors.'
            ),
            'details': [
                'Possible signs include fever, firm skin nodules, swollen lymph nodes, and '
                'reduced appetite or milk production.',
                'Contact a veterinarian for assessment and advice on limiting spread; an image '
                'prediction alone cannot confirm the disease.',
            ],
        },
    },
    'breed': {
        'Ayrshire cattle': {
            'title': 'Ayrshire cattle',
            'description': (
                'A dairy breed originating in Ayrshire, Scotland, commonly recognized by its '
                'red-and-white coat.'
            ),
            'details': [
                'Known as an efficient grazing dairy breed with strong, well-attached udders.',
            ],
        },
        'Brown Swiss cattle': {
            'title': 'Brown Swiss cattle',
            'description': (
                'A dairy breed originating in Switzerland, typically with a solid brown to '
                'gray-brown coat.'
            ),
            'details': [
                'Known for adaptability and milk suited to cheese production.',
            ],
        },
        'Holstein Friesian cattle': {
            'title': 'Holstein Friesian cattle',
            'description': (
                'A dairy breed originating in the Netherlands and northern Germany, commonly '
                'recognized by its black-and-white markings.'
            ),
            'details': [
                'Widely known for high milk production under suitable management.',
            ],
        },
        'Jersey cattle': {
            'title': 'Jersey cattle',
            'description': (
                'A dairy breed originating on the island of Jersey, often with a fawn-colored '
                'coat.'
            ),
            'details': [
                'Jersey milk is commonly valued for its relatively high butterfat content.',
            ],
        },
        'Red Dane cattle': {
            'title': 'Red Dane cattle',
            'description': (
                'A Danish dairy breed generally recognized by its red coat.'
            ),
            'details': [
                'Bred primarily for dairy production.',
            ],
        },
    },
}


class ModelService:
    def __init__(self, project_root: Path | None = None):
        self.project_root = (project_root or Path(__file__).resolve().parents[2]).resolve()
        self.artifact_root = self.project_root / 'artifacts'
        self.model_paths = {
            'disease': self.artifact_root / 'disease_model' / 'disease_model.keras',
            'breed': self.artifact_root / 'breed_model' / 'breed_model.keras',
        }
        self.mapping_paths = {
            'disease': self.artifact_root / 'disease_model' / 'class_mapping.json',
            'breed': self.artifact_root / 'breed_model' / 'class_mapping.json',
        }
        self.metadata_paths = {
            'disease': self.artifact_root / 'disease_model' / 'metadata.json',
            'breed': self.artifact_root / 'breed_model' / 'metadata.json',
        }
        self.models: dict[str, Any] = {}
        self.class_names: dict[str, list[str]] = {}
        self.metadata: dict[str, dict] = {}
        self.model_status = {model_type: 'missing' for model_type in MODEL_TYPES}
        self.model_errors: dict[str, str] = {}
        self._tensorflow = None

        for model_type in MODEL_TYPES:
            self._load_model(model_type)

    def _load_model(self, model_type: str) -> None:
        model_path = self.model_paths[model_type]
        mapping_path = self.mapping_paths[model_type]
        metadata_path = self.metadata_paths[model_type]
        if not model_path.is_file():
            self.model_status[model_type] = 'missing'
            self.model_errors[model_type] = f'Model artifact file is missing: {model_path.name}.'
            return

        missing_files = [path for path in (mapping_path, metadata_path) if not path.is_file()]
        if missing_files:
            self.model_status[model_type] = 'unavailable'
            self.model_errors[model_type] = (
                'Required model metadata file(s) are missing: '
                + ', '.join(path.name for path in missing_files)
                + '.'
            )
            return

        try:
            class_names = self._read_class_names(mapping_path)
            metadata = self._read_metadata(metadata_path, class_names, model_type)
            self.class_names[model_type] = class_names
            self.metadata[model_type] = metadata
            if self._tensorflow is None:
                import tensorflow as tf

                self._tensorflow = tf
            model = self._tensorflow.keras.models.load_model(model_path, compile=False)
            self._validate_model_shape(model, metadata, class_names)
        except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError, ImportError) as exc:
            self.model_status[model_type] = 'unavailable'
            self.model_errors[model_type] = f'Unable to load {model_type} model: {exc}'
            return
        except Exception as exc:  # TensorFlow raises backend-specific errors for bad artifacts.
            self.model_status[model_type] = 'unavailable'
            self.model_errors[model_type] = f'Unable to load {model_type} model: {exc}'
            return

        self.models[model_type] = model
        self.model_status[model_type] = 'ready'
        self.model_errors.pop(model_type, None)

    @staticmethod
    def _read_class_names(path: Path) -> list[str]:
        with path.open('r', encoding='utf-8') as file:
            mapping = json.load(file)

        if not isinstance(mapping, dict):
            raise ValueError('Class mapping must be a JSON object.')

        index_to_class = mapping.get('index_to_class')
        class_to_index = mapping.get('class_to_index')
        if not isinstance(index_to_class, dict) or not isinstance(class_to_index, dict):
            raise ValueError('Class mapping must contain index_to_class and class_to_index.')

        try:
            indexed_classes = sorted(
                ((int(index), name) for index, name in index_to_class.items()),
                key=lambda item: item[0],
            )
        except (TypeError, ValueError) as exc:
            raise ValueError('Class indices must be integer keys.') from exc

        indices = [index for index, _ in indexed_classes]
        class_names = [name for _, name in indexed_classes]
        if indices != list(range(len(class_names))):
            raise ValueError('Class indices must be contiguous and start at zero.')
        if not class_names or not all(isinstance(name, str) and name for name in class_names):
            raise ValueError('Class names must be non-empty strings.')
        if class_to_index != {name: index for index, name in indexed_classes}:
            raise ValueError('class_to_index and index_to_class mappings disagree.')
        return class_names

    @staticmethod
    def _read_metadata(path: Path, class_names: list[str], model_type: str) -> dict:
        with path.open('r', encoding='utf-8') as file:
            metadata = json.load(file)

        if not isinstance(metadata, dict):
            raise ValueError('Model metadata must be a JSON object.')
        if metadata.get('model_type') != model_type:
            raise ValueError(f'Metadata model_type must be {model_type}.')
        if metadata.get('image_size') != [224, 224]:
            raise ValueError('Expected model metadata image_size to be [224, 224].')
        if metadata.get('input_format') != 'RGB':
            raise ValueError('Expected model metadata input_format to be RGB.')
        if metadata.get('input_range') not in ([0, 255], [0, 1]):
            raise ValueError('Model input_range must be [0, 255] or [0, 1].')
        if metadata.get('classes') != class_names:
            raise ValueError('Metadata class order does not match class_mapping.json.')
        return metadata

    @staticmethod
    def _validate_model_shape(model: Any, metadata: dict, class_names: list[str]) -> None:
        input_shape = model.input_shape
        output_shape = model.output_shape
        if isinstance(input_shape, list) or isinstance(output_shape, list):
            raise ValueError('Models must have one image input and one class-probability output.')
        if len(input_shape) != 4 or tuple(input_shape[1:]) != (224, 224, 3):
            raise ValueError(f'Model input shape {input_shape} does not match metadata.')
        if len(output_shape) != 2 or output_shape[-1] != len(class_names):
            raise ValueError(
                f'Model output shape {output_shape} does not match the class mapping.'
            )

    def get_status(self) -> dict[str, str]:
        return self.model_status.copy()

    def get_errors(self) -> dict[str, str]:
        return self.model_errors.copy()

    def is_available(self, model_type: str) -> bool:
        return self.model_status.get(model_type) == 'ready'

    def get_supported_classes(self, model_type: str) -> list[str]:
        return self.class_names.get(model_type, []).copy()

    def _has_model(self, model_type: str) -> bool:
        return self.is_available(model_type)

    def _load_class_mapping(self, model_type: str) -> list[str]:
        return self.get_supported_classes(model_type)

    def _prepare_image(self, model_type: str, image_path: str) -> np.ndarray:
        image_size = self.metadata[model_type]['image_size']
        image = Image.open(image_path).convert('RGB')
        image_array = np.asarray(image, dtype=np.float32)
        resized = self._tensorflow.image.resize(image_array, image_size)
        if self.metadata[model_type]['input_range'] == [0, 1]:
            resized = resized / 255.0
        return self._tensorflow.expand_dims(resized, axis=0)

    def predict(self, model_type: str, image_path: str) -> dict:
        if model_type not in MODEL_TYPES:
            return {'status': 'error', 'error': f'Unknown model type: {model_type}'}

        if not self._has_model(model_type):
            return {
                'status': 'error',
                'model_type': model_type,
                'error': self.model_errors.get(
                    model_type, f'The {model_type} model is not configured.'
                ),
                'supported_classes': self._load_class_mapping(model_type),
            }

        try:
            image_batch = self._prepare_image(model_type, image_path)
            prediction = np.asarray(
                self.models[model_type].predict(image_batch, verbose=0),
                dtype=np.float32,
            )
            class_names = self.class_names[model_type]
            if prediction.shape != (1, len(class_names)):
                raise ValueError(
                    f'Model returned shape {prediction.shape}; expected (1, {len(class_names)}).'
                )
            probabilities = prediction[0]
            if (
                not np.all(np.isfinite(probabilities))
                or np.any(probabilities < 0)
                or np.any(probabilities > 1)
                or not np.isclose(float(np.sum(probabilities)), 1.0, atol=1e-3)
            ):
                raise ValueError('Model returned invalid class probabilities.')

            top_index = int(np.argmax(probabilities))
            is_disease = model_type == 'disease'
            return {
                'status': 'ok',
                'model_type': model_type,
                'class_name': class_names[top_index],
                'confidence': round(float(probabilities[top_index]) * 100, 2),
                'information': CLASS_INFORMATION.get(model_type, {}).get(
                    class_names[top_index]
                ),
                'probabilities': {
                    class_name: round(float(probability) * 100, 2)
                    for class_name, probability in zip(class_names, probabilities)
                },
                'message': (
                    'Preliminary screening result only. This is not a confirmed diagnosis; '
                    'consult a qualified veterinarian.'
                    if is_disease
                    else 'Breed classification is limited to the supported classes in this model.'
                ),
                'supported_classes': class_names,
            }
        except (OSError, ValueError, TypeError) as exc:
            return {
                'status': 'error',
                'model_type': model_type,
                'error': f'Unable to process image or model output: {exc}',
            }
        except Exception as exc:  # TensorFlow may raise runtime-specific inference errors.
            return {
                'status': 'error',
                'model_type': model_type,
                'error': f'Unable to run {model_type} inference: {exc}',
            }
