import json
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image


MODEL_TYPES = ('disease', 'breed')
ANIMAL_MODEL_KEYS = ('animal_type', 'cow_breed', 'cat_breed', 'dog_breed')
ANIMAL_TYPE_TO_BREED_MODEL = {
    'cow': 'cow_breed',
    'cat': 'cat_breed',
    'dog': 'dog_breed',
}

CLASS_INFORMATION = {
    'disease': {
        'Foot_and_Mouth_Disease': {
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
        'Lumpy_Skin_Disease': {
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
        'Mastitis_Disease': {
            'title': 'Mastitis',
            'description': (
                'An inflammatory condition of the mammary gland, commonly affecting dairy cows.'
            ),
            'details': [
                'Signs may include swollen, hot, or painful udders, and changes in milk appearance.',
                'Consult a veterinarian for proper diagnosis and treatment.',
            ],
        },
        'demodicosis': {
            'title': 'Demodicosis',
            'description': (
                'A skin condition caused by Demodex mites, affecting dogs and other animals.'
            ),
            'details': [
                'Common signs include hair loss, redness, and skin lesions.',
                'Veterinary consultation recommended for appropriate treatment.',
            ],
        },
        'dermatitis': {
            'title': 'Dermatitis',
            'description': (
                'Inflammation of the skin that can have various causes including allergies, infections, or irritants.'
            ),
            'details': [
                'Symptoms may include redness, itching, and skin lesions.',
                'Consult a veterinarian to determine the underlying cause and appropriate treatment.',
            ],
        },
        'flea_allergy': {
            'title': 'Flea allergy dermatitis',
            'description': (
                'An allergic reaction to flea saliva, commonly affecting dogs and cats.'
            ),
            'details': [
                'Signs include intense itching, redness, and skin irritation, especially near the tail base.',
                'Flea control and veterinary treatment are typically necessary.',
            ],
        },
        'fungal_infections': {
            'title': 'Fungal skin infection',
            'description': (
                'Skin infections caused by various types of fungi, affecting multiple animal species.'
            ),
            'details': [
                'May present as circular patches, hair loss, or skin scaling.',
                'Veterinary diagnosis and antifungal treatment are usually required.',
            ],
        },
        'healthy_cat': {
            'title': 'Healthy cat',
            'description': (
                'The model classified this cat as healthy with no apparent disease patterns.'
            ),
            'details': [
                'This result does not confirm the cat is completely healthy or rule out other conditions.',
                'Regular veterinary check-ups are recommended for optimal health.',
            ],
        },
        'healthy_cow': {
            'title': 'Healthy cow',
            'description': (
                'The model classified this cow as healthy with no apparent disease patterns.'
            ),
            'details': [
                'This result does not confirm the cow is completely healthy or rule out other conditions.',
                'Regular veterinary check-ups are recommended for optimal health.',
            ],
        },
        'healthy_dog': {
            'title': 'Healthy dog',
            'description': (
                'The model classified this dog as healthy with no apparent disease patterns.'
            ),
            'details': [
                'This result does not confirm the dog is completely healthy or rule out other conditions.',
                'Regular veterinary check-ups are recommended for optimal health.',
            ],
        },
        'hot_spots_disease': {
            'title': 'Hot spots (acute moist dermatitis)',
            'description': (
                'A common skin condition in dogs characterized by red, moist, and painful lesions.'
            ),
            'details': [
                'Often caused by self-trauma from scratching or licking due to underlying irritation.',
                'Veterinary treatment is recommended to address the underlying cause and promote healing.',
            ],
        },
        'ringworm_cat': {
            'title': 'Ringworm in cats',
            'description': (
                'A fungal infection of the skin, hair, or nails caused by dermatophytes.'
            ),
            'details': [
                'Appears as circular patches of hair loss with red, scaly borders.',
                'Contagious to other animals and humans; veterinary treatment is necessary.',
            ],
        },
        'ringworm_dog': {
            'title': 'Ringworm in dogs',
            'description': (
                'A fungal infection of the skin, hair, or nails caused by dermatophytes.'
            ),
            'details': [
                'Appears as circular patches of hair loss with red, scaly borders.',
                'Contagious to other animals and humans; veterinary treatment is necessary.',
            ],
        },
        'scabies': {
            'title': 'Sarcoptic mange (scabies)',
            'description': (
                'A highly contagious skin condition caused by Sarcoptes mites, affecting dogs and other animals.'
            ),
            'details': [
                'Intense itching, hair loss, and skin irritation are common symptoms.',
                'Immediate veterinary treatment is required to prevent spread and relieve discomfort.',
            ],
        },
    },
}


class ModelService:
    def __init__(self, project_root: Path | None = None):
        self.project_root = (project_root or Path(__file__).resolve().parents[2]).resolve()
        self.artifact_root = self.project_root / 'artifacts'
        breed_root = self.artifact_root / 'breed_model'
        disease_root = self.artifact_root / 'disease_model'
        self.model_paths = {
            'disease': disease_root / 'PashuRakshak_Disease_Model.keras',
            'animal_type': breed_root / 'PashuRakshak_AnimalType.keras',
            'cow_breed': breed_root / 'PashuRakshak_CowBreed_BalancedBatch.keras',
            'cat_breed': breed_root / 'PashuRakshak_CatBreed_10Class.keras',
            'dog_breed': breed_root / 'PashuRakshak_DogBreed_129_Best.keras',
        }
        self.mapping_paths = {
            'disease': disease_root / 'PashuRakshak_Class_Names.json',
            'animal_type': breed_root / 'PashuRakshak_AnimalType_Classes.json',
            'cow_breed': breed_root / 'PashuRakshak_CowBreed_BalancedBatch_Classes.json',
            'cat_breed': breed_root / 'PashuRakshak_CatBreed_10Class_Classes.json',
            'dog_breed': breed_root / 'PashuRakshak_DogBreed_129_Classes.json',
        }
        self.metadata_paths = {
            'disease': disease_root / 'metadata.json',
            'animal_type': breed_root / 'PashuRakshak_AnimalType_Metadata.json',
            'cow_breed': breed_root / 'PashuRakshak_CowBreed_BalancedBatch_Metadata.json',
            'cat_breed': breed_root / 'PashuRakshak_CatBreed_10Class_Metadata.json',
            'dog_breed': breed_root / 'PashuRakshak_DogBreed_129_Metadata.json',
        }
        self.models: dict[str, Any] = {}
        self.class_names: dict[str, list[str]] = {}
        self.metadata: dict[str, dict] = {}
        self.model_status = {model_type: 'missing' for model_type in MODEL_TYPES}
        self.model_errors: dict[str, str] = {}
        self.component_status: dict[str, str] = {}
        self.component_errors: dict[str, str] = {}
        self._tensorflow = None

        for model_key in ('disease', *ANIMAL_MODEL_KEYS):
            self._load_model(model_key)
        self._update_public_status()

    def _load_model(self, model_key: str) -> None:
        model_path = self.model_paths[model_key]
        mapping_path = self.mapping_paths[model_key]
        metadata_path = self.metadata_paths[model_key]
        if not model_path.is_file():
            self.component_status[model_key] = 'missing'
            self.component_errors[model_key] = f'Model artifact file is missing: {model_path.name}.'
            return

        if not mapping_path.is_file():
            self.component_status[model_key] = 'unavailable'
            self.component_errors[model_key] = (
                f'Required class names file is missing: {mapping_path.name}.'
            )
            return

        try:
            class_names = self._read_class_names(mapping_path)
            metadata = self._read_metadata(metadata_path, class_names, model_key)
            if self._tensorflow is None:
                import tensorflow as tf

                self._tensorflow = tf
            model = self._tensorflow.keras.models.load_model(model_path, compile=False)
            metadata = self._complete_metadata(model, metadata)
            self._validate_model_shape(model, metadata, class_names)
        except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError, ImportError) as exc:
            self.component_status[model_key] = 'unavailable'
            self.component_errors[model_key] = f'Unable to load {model_key} model: {exc}'
            return
        except Exception as exc:  # TensorFlow raises backend-specific errors for bad artifacts.
            self.component_status[model_key] = 'unavailable'
            self.component_errors[model_key] = f'Unable to load {model_key} model: {exc}'
            return

        self.models[model_key] = model
        self.class_names[model_key] = class_names
        self.metadata[model_key] = metadata
        self.component_status[model_key] = 'ready'
        self.component_errors.pop(model_key, None)

    @staticmethod
    def _read_class_names(path: Path) -> list[str]:
        with path.open('r', encoding='utf-8') as file:
            mapping = json.load(file)

        if isinstance(mapping, list):
            class_names = mapping
        elif isinstance(mapping, dict) and isinstance(mapping.get('class_names'), list):
            class_names = mapping['class_names']
        elif isinstance(mapping, dict) and isinstance(mapping.get('classes'), list):
            class_names = mapping['classes']
        elif isinstance(mapping, dict):
            index_to_class = mapping.get('index_to_class')
            class_to_index = mapping.get('class_to_index')
            if not isinstance(index_to_class, dict) or not isinstance(class_to_index, dict):
                raise ValueError(
                    'Class names file must contain a class_names/classes list or indexed mappings.'
                )
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
            if class_to_index != {name: index for index, name in indexed_classes}:
                raise ValueError('class_to_index and index_to_class mappings disagree.')
        else:
            raise ValueError('Class names must be a JSON array or object.')

        if not class_names or not all(isinstance(name, str) and name for name in class_names):
            raise ValueError('Class names must be non-empty strings.')
        return class_names

    @staticmethod
    def _read_metadata(path: Path, class_names: list[str], model_key: str) -> dict:
        if not path.is_file():
            return {'image_size': None, 'input_range': [0, 255], 'classes': class_names}

        with path.open('r', encoding='utf-8') as file:
            metadata = json.load(file)

        if not isinstance(metadata, dict):
            raise ValueError('Model metadata must be a JSON object.')
        if metadata.get('model_type') is not None and metadata['model_type'] not in (
            model_key,
            'breed' if model_key.endswith('_breed') else model_key,
            'disease' if model_key == 'disease' else model_key,
        ):
            raise ValueError(f'Metadata model_type does not match {model_key}.')
        if metadata.get('classes') is not None and metadata['classes'] != class_names:
            raise ValueError('Metadata class order does not match the class names file.')
        input_range = metadata.get('input_range', [0, 255])
        if input_range not in ([0, 255], [0, 1], [0.0, 1.0]):
            raise ValueError('Model input_range must be [0, 255] or [0, 1].')
        image_size = metadata.get('image_size')
        if isinstance(image_size, int):
            image_size = [image_size, image_size]
        if image_size is not None and (
            not isinstance(image_size, (list, tuple))
            or len(image_size) != 2
            or not all(isinstance(size, int) and size > 0 for size in image_size)
        ):
            raise ValueError('Model image_size must be a positive integer or two-item list.')
        metadata['image_size'] = image_size
        metadata['input_range'] = input_range
        return metadata

    @staticmethod
    def _complete_metadata(model: Any, metadata: dict) -> dict:
        input_shape = model.input_shape
        if isinstance(input_shape, list) or len(input_shape) != 4:
            raise ValueError('Models must have one rank-four image input.')
        model_size = input_shape[1:3]
        if any(size is None for size in model_size):
            raise ValueError(f'Model input shape {input_shape} must have fixed image dimensions.')
        model_size = [int(size) for size in model_size]
        if metadata['image_size'] is None:
            metadata['image_size'] = model_size
        elif metadata['image_size'] != model_size:
            raise ValueError(
                f'Metadata image_size {metadata["image_size"]} does not match model input {model_size}.'
            )
        if input_shape[-1] != 3:
            raise ValueError(f'Model input shape {input_shape} must use RGB images.')
        return metadata

    @staticmethod
    def _validate_model_shape(model: Any, metadata: dict, class_names: list[str]) -> None:
        input_shape = model.input_shape
        output_shape = model.output_shape
        if isinstance(input_shape, list) or isinstance(output_shape, list):
            raise ValueError('Models must have one image input and one class-probability output.')
        expected_input_shape = (*metadata['image_size'], 3)
        if len(input_shape) != 4 or tuple(input_shape[1:]) != expected_input_shape:
            raise ValueError(f'Model input shape {input_shape} does not match metadata.')
        if len(output_shape) != 2 or output_shape[-1] != len(class_names):
            raise ValueError(
                f'Model output shape {output_shape} does not match the class mapping.'
            )

    def _update_public_status(self) -> None:
        self.model_status['disease'] = self.component_status.get('disease', 'missing')
        if self.model_status['disease'] != 'ready':
            self.model_errors['disease'] = self.component_errors.get(
                'disease', 'The disease model is not configured.'
            )
        else:
            self.model_errors.pop('disease', None)

        required_breed_models = ('animal_type', *ANIMAL_TYPE_TO_BREED_MODEL.values())
        unavailable = [
            (key, self.component_errors.get(key, f'{key} model is unavailable.'))
            for key in required_breed_models
            if self.component_status.get(key) != 'ready'
        ]
        self.model_status['breed'] = 'ready' if not unavailable else (
            'missing' if all(self.component_status.get(key) == 'missing' for key, _ in unavailable)
            else 'unavailable'
        )
        if unavailable:
            self.model_errors['breed'] = '; '.join(
                f'{key}: {error}' for key, error in unavailable
            )
        else:
            self.model_errors.pop('breed', None)

    def get_status(self) -> dict[str, str]:
        return self.model_status.copy()

    def get_errors(self) -> dict[str, str]:
        return self.model_errors.copy()

    def is_available(self, model_type: str) -> bool:
        return self.model_status.get(model_type) == 'ready'

    def get_supported_classes(self, model_type: str) -> list[str]:
        if model_type == 'disease':
            return self.class_names.get('disease', []).copy()
        if model_type == 'breed':
            return [
                class_name
                for model_key in ('cow_breed', 'cat_breed', 'dog_breed')
                for class_name in self.class_names.get(model_key, [])
            ]
        return self.class_names.get(model_type, []).copy()

    def _has_model(self, model_type: str) -> bool:
        return self.is_available(model_type)

    def _load_class_mapping(self, model_type: str) -> list[str]:
        return self.get_supported_classes(model_type)

    def _prepare_image(self, model_key: str, image_path: str) -> np.ndarray:
        image_size = self.metadata[model_key]['image_size']
        image = Image.open(image_path).convert('RGB')
        image_array = np.asarray(image, dtype=np.float32)
        resized = self._tensorflow.image.resize(image_array, image_size)
        if self.metadata[model_key]['input_range'] in ([0, 1], [0.0, 1.0]):
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
            if model_type == 'breed':
                result = self._predict_breed(image_path)
                if result.get('status') != 'ok':
                    return result
                return result
            return self._predict_single_model('disease', image_path)
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

    def _predict_single_model(self, model_key: str, image_path: str) -> dict:
        image_batch = self._prepare_image(model_key, image_path)
        prediction = np.asarray(
            self.models[model_key].predict(image_batch, verbose=0),
            dtype=np.float32,
        )
        class_names = self.class_names[model_key]
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
        is_disease = model_key == 'disease'
        class_name = class_names[top_index]
        info = CLASS_INFORMATION.get(model_key, {}).get(class_name)
        if info is None:
            if is_disease:
                description = (
                    'The model classified this image as this supported disease or health category.'
                )
            elif model_key == 'animal_type':
                description = 'The model classified this image as this supported animal type.'
            else:
                description = 'The model classified this image as this supported breed.'
            info = {
                'title': class_name.replace('_', ' ').replace('-', ' ').title(),
                'description': description,
                'details': [
                    'This model result is a preliminary classification and may be incorrect.',
                    'Consult a qualified veterinarian if the animal appears unwell.',
                ],
            }
        result = {
            'status': 'ok',
            'model_type': 'disease' if is_disease else model_key,
            'class_name': class_name,
            'confidence': round(float(probabilities[top_index]) * 100, 2),
            'information': info,
            'probabilities': {
                name: round(float(probability) * 100, 2)
                for name, probability in zip(class_names, probabilities)
            },
            'supported_classes': class_names,
        }
        if is_disease:
            result['message'] = (
                'Preliminary screening result only. This is not a confirmed diagnosis; '
                'consult a qualified veterinarian.'
            )
        return result

    def _predict_breed(self, image_path: str) -> dict:
        type_result = self._predict_single_model('animal_type', image_path)
        animal_type = type_result['class_name'].strip().lower()
        breed_model_key = ANIMAL_TYPE_TO_BREED_MODEL.get(animal_type)
        if breed_model_key is None:
            raise ValueError(f'Animal type model returned unsupported class: {animal_type}.')
        breed_result = self._predict_single_model(breed_model_key, image_path)
        breed_result['model_type'] = 'breed'
        breed_result['animal_type'] = animal_type
        breed_result['animal_type_confidence'] = type_result['confidence']
        breed_result['message'] = (
            'Breed classification is limited to the supported classes for the detected animal type.'
        )
        return breed_result
