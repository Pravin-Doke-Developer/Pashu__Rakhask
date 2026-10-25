import json
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from services.model_service import ModelService


CLASS_NAMES = {
    'disease': ['Foot_and_Mouth_Disease', 'healthy_cow', 'ringworm_dog'],
    'animal_type': ['Cat', 'Cow', 'Dog'],
    'cow_breed': ['sahiwal', 'brahman'],
    'cat_breed': ['siamese', 'bombay'],
    'dog_breed': ['Beagle', 'Poodle'],
}
ARTIFACTS = {
    'disease': (
        'disease_model',
        'PashuRakshak_Disease_Model.keras',
        'PashuRakshak_Class_Names.json',
    ),
    'animal_type': (
        'breed_model',
        'PashuRakshak_AnimalType.keras',
        'PashuRakshak_AnimalType_Classes.json',
    ),
    'cow_breed': (
        'breed_model',
        'PashuRakshak_CowBreed_BalancedBatch.keras',
        'PashuRakshak_CowBreed_BalancedBatch_Classes.json',
    ),
    'cat_breed': (
        'breed_model',
        'PashuRakshak_CatBreed_10Class.keras',
        'PashuRakshak_CatBreed_10Class_Classes.json',
    ),
    'dog_breed': (
        'breed_model',
        'PashuRakshak_DogBreed_129_Best.keras',
        'PashuRakshak_DogBreed_129_Classes.json',
    ),
}


class FakeModel:
    input_shape = (None, 224, 224, 3)

    def __init__(self, class_names, selected_index=1):
        self.output_shape = (None, len(class_names))
        self.selected_index = selected_index
        self.last_batch = None
        self.predict = Mock(side_effect=self._predict)

    def _predict(self, batch, verbose=0):
        self.last_batch = np.asarray(batch)
        probabilities = np.zeros((1, self.output_shape[-1]), dtype=np.float32)
        probabilities[0, self.selected_index] = 0.9
        if self.output_shape[-1] > 1:
            for index in range(self.output_shape[-1]):
                if index != self.selected_index:
                    probabilities[0, index] = 0.1 / (self.output_shape[-1] - 1)
        return probabilities


class TestModelService(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.project_root = Path(self.temp_dir.name)
        self.models = {}
        self.load_model = Mock(side_effect=self._load_fake_model)

        for model_key, (folder, model_name, mapping_name) in ARTIFACTS.items():
            artifact_dir = self.project_root / 'artifacts' / folder
            artifact_dir.mkdir(parents=True, exist_ok=True)
            (artifact_dir / model_name).write_bytes(b'fake model placeholder')
            (artifact_dir / mapping_name).write_text(
                json.dumps({'class_names': CLASS_NAMES[model_key]}),
                encoding='utf-8',
            )

        fake_tensorflow = types.SimpleNamespace(
            keras=types.SimpleNamespace(
                models=types.SimpleNamespace(load_model=self.load_model)
            ),
            image=types.SimpleNamespace(
                resize=lambda image, size: np.asarray(image, dtype=np.float32)
            ),
            expand_dims=np.expand_dims,
        )
        self.tensorflow_patch = patch.dict(sys.modules, {'tensorflow': fake_tensorflow})
        self.tensorflow_patch.start()
        self.addCleanup(self.tensorflow_patch.stop)
        self.addCleanup(self.temp_dir.cleanup)

        self.service = ModelService(self.project_root)

    def _load_fake_model(self, path, compile=False):
        path = Path(path)
        model_key = next(
            key for key, (folder, filename, _) in ARTIFACTS.items()
            if path.parent.name == folder and path.name == filename
        )
        if model_key not in self.models:
            selected_index = 1
            if model_key == 'animal_type':
                selected_index = 1
            self.models[model_key] = FakeModel(CLASS_NAMES[model_key], selected_index)
        return self.models[model_key]

    def test_loads_all_artifacts_and_predicts_breed_in_two_stages(self):
        self.assertEqual(self.service.get_status(), {'disease': 'ready', 'breed': 'ready'})
        self.assertEqual(self.load_model.call_count, 5)

        image_path = self.project_root / 'input.png'
        Image.new('RGB', (224, 224), (100, 120, 140)).save(image_path, format='PNG')
        result = self.service.predict('breed', str(image_path))

        self.assertEqual(result['status'], 'ok')
        self.assertEqual(result['class_name'], 'brahman')
        self.assertEqual(result['animal_type'], 'cow')
        self.assertEqual(result['confidence'], 90.0)
        self.assertEqual(result['animal_type_confidence'], 90.0)
        self.assertEqual(self.models['animal_type'].predict.call_count, 1)
        self.assertEqual(self.models['cow_breed'].predict.call_count, 1)
        self.assertEqual(self.models['cat_breed'].predict.call_count, 0)
        self.assertEqual(self.models['dog_breed'].predict.call_count, 0)

    def test_disease_prediction_uses_only_the_disease_model(self):
        image_path = self.project_root / 'input.png'
        Image.new('RGB', (224, 224), (100, 120, 140)).save(image_path, format='PNG')

        result = self.service.predict('disease', str(image_path))

        self.assertEqual(result['status'], 'ok')
        self.assertEqual(result['class_name'], 'healthy_cow')
        self.assertIn('not a confirmed diagnosis', result['message'])
        self.assertEqual(self.models['disease'].predict.call_count, 1)
        self.assertEqual(self.models['animal_type'].predict.call_count, 0)
        self.assertEqual(self.models['cow_breed'].predict.call_count, 0)

    def test_breed_uses_expert_for_predicted_animal_type(self):
        self.models['animal_type'].selected_index = 0
        self.models['cat_breed'].selected_index = 0
        image_path = self.project_root / 'input.png'
        Image.new('RGB', (224, 224), (100, 120, 140)).save(image_path, format='PNG')

        result = self.service.predict('breed', str(image_path))

        self.assertEqual(result['animal_type'], 'cat')
        self.assertEqual(result['class_name'], 'siamese')
        self.assertEqual(self.models['cat_breed'].predict.call_count, 1)
        self.assertEqual(self.models['cow_breed'].predict.call_count, 0)
        self.assertEqual(self.models['dog_breed'].predict.call_count, 0)

    def test_missing_artifacts_are_reported_without_loading_tensorflow(self):
        service = ModelService(self.project_root / 'missing-project')

        self.assertEqual(service.get_status(), {'disease': 'missing', 'breed': 'missing'})
        self.assertIn('missing', service.get_errors()['disease'])
        self.assertIn('missing', service.get_errors()['breed'])

    def test_inference_errors_return_an_error_result(self):
        self.models['disease'].predict.side_effect = RuntimeError('device failure')
        image_path = self.project_root / 'input.png'
        Image.new('RGB', (224, 224), (20, 30, 40)).save(image_path, format='PNG')

        result = self.service.predict('disease', str(image_path))

        self.assertEqual(result['status'], 'error')
        self.assertIn('device failure', result['error'])


if __name__ == '__main__':
    unittest.main()
