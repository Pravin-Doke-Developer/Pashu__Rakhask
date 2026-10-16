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


class FakeModel:
    input_shape = (None, 224, 224, 3)

    def __init__(self, number_of_classes):
        self.output_shape = (None, number_of_classes)
        self.last_batch = None

    def predict(self, batch, verbose=0):
        self.last_batch = np.asarray(batch)
        probabilities = np.zeros((1, self.output_shape[-1]), dtype=np.float32)
        probabilities[0, 1] = 0.9
        probabilities[0, 0] = 0.1
        return probabilities


class TestModelService(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.project_root = Path(self.temp_dir.name)
        self.classes = {
            'disease': ['foot-and-mouth', 'healthy', 'lumpy'],
            'breed': [
                'Ayrshire cattle',
                'Brown Swiss cattle',
                'Holstein Friesian cattle',
                'Jersey cattle',
                'Red Dane cattle',
            ],
        }
        self.models = {}
        for model_type, class_names in self.classes.items():
            artifact_dir = self.project_root / 'artifacts' / f'{model_type}_model'
            artifact_dir.mkdir(parents=True)
            (artifact_dir / f'{model_type}_model.keras').write_bytes(b'fake model placeholder')
            (artifact_dir / 'class_mapping.json').write_text(
                json.dumps(
                    {
                        'class_to_index': {
                            name: index for index, name in enumerate(class_names)
                        },
                        'index_to_class': {
                            str(index): name for index, name in enumerate(class_names)
                        },
                    }
                ),
                encoding='utf-8',
            )
            (artifact_dir / 'metadata.json').write_text(
                json.dumps(
                    {
                        'model_type': model_type,
                        'image_size': [224, 224],
                        'input_format': 'RGB',
                        'input_range': [0, 255],
                        'preprocessing': 'rescale RGB pixels to [-1, 1] inside model',
                        'classes': class_names,
                    }
                ),
                encoding='utf-8',
            )
            self.models[model_type] = FakeModel(len(class_names))

        self.load_model = Mock(
            side_effect=lambda path, compile=False: self.models[Path(path).parent.name.replace('_model', '')]
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

    def test_loads_each_model_once_and_uses_metadata_preprocessing(self):
        self.assertEqual(self.service.get_status(), {'disease': 'ready', 'breed': 'ready'})
        self.assertEqual(self.load_model.call_count, 2)

        image_path = self.project_root / 'input.png'
        Image.new('RGB', (224, 224), (100, 120, 140)).save(image_path, format='PNG')
        result = self.service.predict('disease', str(image_path))

        self.assertEqual(result['status'], 'ok')
        self.assertEqual(result['class_name'], 'healthy')
        self.assertEqual(result['confidence'], 90.0)
        self.assertEqual(
            result['information']['title'],
            'No supported disease pattern detected',
        )
        self.assertTrue(result['information']['description'])
        self.assertTrue(result['information']['details'])
        self.assertEqual(result['probabilities']['foot-and-mouth'], 10.0)
        np.testing.assert_array_equal(
            self.models['disease'].last_batch[0, 0, 0],
            np.array([100, 120, 140], dtype=np.float32),
        )
        self.assertEqual(self.load_model.call_count, 2)

    def test_every_supported_class_includes_information(self):
        image_path = self.project_root / 'input.png'
        Image.new('RGB', (224, 224), (100, 120, 140)).save(image_path, format='PNG')

        for model_type, class_names in self.classes.items():
            for class_index, class_name in enumerate(class_names):
                probabilities = np.zeros((1, len(class_names)), dtype=np.float32)
                probabilities[0, class_index] = 1.0
                self.models[model_type].predict = Mock(return_value=probabilities)

                result = self.service.predict(model_type, str(image_path))

                self.assertEqual(result['class_name'], class_name)
                self.assertIsNotNone(result['information'], f'{model_type}: {class_name}')
                self.assertTrue(result['information']['title'])
                self.assertTrue(result['information']['description'])
                self.assertTrue(result['information']['details'])

    def test_metadata_class_order_mismatch_marks_model_unavailable(self):
        metadata_path = (
            self.project_root / 'artifacts' / 'disease_model' / 'metadata.json'
        )
        metadata = json.loads(metadata_path.read_text(encoding='utf-8'))
        metadata['classes'] = list(reversed(metadata['classes']))
        metadata_path.write_text(json.dumps(metadata), encoding='utf-8')

        service = ModelService(self.project_root)

        self.assertEqual(service.get_status()['disease'], 'unavailable')
        self.assertIn('class order', service.get_errors()['disease'])
        self.assertEqual(service.get_status()['breed'], 'ready')

    def test_missing_artifacts_are_reported_without_loading_tensorflow(self):
        service = ModelService(self.project_root / 'missing-project')

        self.assertEqual(service.get_status(), {'disease': 'missing', 'breed': 'missing'})
        self.assertIn('missing', service.get_errors()['disease'])

    def test_inference_errors_return_an_error_result(self):
        self.models['disease'].predict = Mock(side_effect=RuntimeError('device failure'))
        image_path = self.project_root / 'input.png'
        Image.new('RGB', (224, 224), (20, 30, 40)).save(image_path, format='PNG')

        result = self.service.predict('disease', str(image_path))

        self.assertEqual(result['status'], 'error')
        self.assertIn('device failure', result['error'])


if __name__ == '__main__':
    unittest.main()
