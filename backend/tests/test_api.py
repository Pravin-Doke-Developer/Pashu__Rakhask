import io
import sys
import tempfile
import unittest
from pathlib import Path
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app import app
from services.history_service import HistoryService


class TestAnimalHealthAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = app
        cls.model_service = cls.app.extensions['model_service']

    def setUp(self):
        self.app.config['TESTING'] = True
        self.app.config['MAX_IMAGE_SIZE_MB'] = 10
        self.history_directory = tempfile.TemporaryDirectory()
        self.app.extensions['history_service'] = HistoryService(
            str(Path(self.history_directory.name) / 'history.json')
        )
        self.addCleanup(self.history_directory.cleanup)
        self.client = self.app.test_client()

    def test_health_check(self):
        response = self.client.get('/health')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['status'], 'ok')

    def test_history_returns_saved_predictions(self):
        saved_prediction = {
            'timestamp': '2026-10-16T07:33:51+00:00',
            'model_type': 'disease',
            'filename': 'cattle.jpg',
            'class_name': 'healthy',
            'confidence': 92.43,
            'source': 'api_inference',
        }
        self.app.extensions['history_service'].add_entry(saved_prediction)

        response = self.client.get('/history')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['status'], 'ok')
        self.assertEqual(response.json['history'], [saved_prediction])

    def test_status_reports_model_load_state(self):
        response = self.client.get('/status')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(set(response.json['models']), {'disease', 'breed'})
        self.assertIn(response.json['models']['disease'], {'ready', 'missing', 'unavailable'})
        self.assertIn(response.json['models']['breed'], {'ready', 'missing', 'unavailable'})
        self.assertIn('errors', response.json)
        expected_root = Path(__file__).resolve().parents[2] / 'artifacts'
        self.assertEqual(
            self.model_service.model_paths['disease'],
            expected_root / 'disease_model' / 'disease_model.keras',
        )
        self.assertEqual(
            self.model_service.get_supported_classes('disease'),
            ['foot-and-mouth', 'healthy', 'lumpy'],
        )
        self.assertEqual(
            self.model_service.get_supported_classes('breed'),
            [
                'Ayrshire cattle',
                'Brown Swiss cattle',
                'Holstein Friesian cattle',
                'Jersey cattle',
                'Red Dane cattle',
            ],
        )

    def test_empty_upload_rejected(self):
        response = self.client.post('/predict/disease', data={})
        self.assertEqual(response.status_code, 400)
        self.assertIn('No image file was uploaded', response.json['error'])

    def test_invalid_file_type_rejected(self):
        response = self.client.post('/predict/disease', data={'image': (io.BytesIO(b'not-an-image'), 'test.txt')})
        self.assertEqual(response.status_code, 400)
        self.assertIn('Unsupported file type', response.json['error'])

    def test_oversized_upload_rejected(self):
        self.app.config['MAX_IMAGE_SIZE_MB'] = 0
        payload = io.BytesIO(b'a' * 100)
        response = self.client.post('/predict/disease', data={'image': (payload, 'large.jpg')})
        self.assertEqual(response.status_code, 400)

    def test_corrupt_image_rejected(self):
        response = self.client.post('/predict/disease', data={'image': (io.BytesIO(b'abcdef'), 'corrupt.jpg')})
        self.assertEqual(response.status_code, 400)
        self.assertIn('corrupt or unreadable', response.json['error'])

    def test_unavailable_model_returns_service_unavailable(self):
        unavailable_type = next(
            (
                model_type
                for model_type in ('disease', 'breed')
                if not self.model_service.is_available(model_type)
            ),
            None,
        )
        if unavailable_type is None:
            self.skipTest('Both TensorFlow models loaded successfully.')

        img = io.BytesIO()
        Image.new('RGB', (224, 224), color=(100, 120, 140)).save(img, format='PNG')
        img.seek(0)
        response = self.client.post(
            f'/predict/{unavailable_type}',
            data={'image': (img, 'animal.png')},
        )

        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json['status'], 'error')
        self.assertIn('model_type', response.json)

    def test_disease_prediction_uses_loaded_model(self):
        img = io.BytesIO()
        image = Image.new('RGB', (224, 224), color=(255, 0, 0))
        image.save(img, format='JPEG')
        img.seek(0)

        response = self.client.post('/predict/disease', data={'image': (img, 'healthy.jpg')})
        if not self.model_service.is_available('disease'):
            self.skipTest(self.model_service.get_errors().get('disease', 'Disease model unavailable.'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['status'], 'ok')
        self.assertIn(
            response.json['class_name'],
            self.model_service.get_supported_classes('disease'),
        )
        self.assertGreaterEqual(response.json['confidence'], 0)
        self.assertLessEqual(response.json['confidence'], 100)
        self.assertEqual(response.json['model_type'], 'disease')
        self.assertIn('not a confirmed diagnosis', response.json['message'])
        self.assertIn('title', response.json['information'])
        self.assertTrue(response.json['information']['description'])
        self.assertTrue(response.json['information']['details'])

    def test_breed_prediction_uses_loaded_model(self):
        img = io.BytesIO()
        image = Image.new('RGB', (224, 224), color=(128, 180, 90))
        image.save(img, format='JPEG')
        img.seek(0)

        response = self.client.post('/predict/breed', data={'image': (img, 'cattle.jpg')})
        if not self.model_service.is_available('breed'):
            self.skipTest(self.model_service.get_errors().get('breed', 'Breed model unavailable.'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['status'], 'ok')
        self.assertIn(
            response.json['class_name'],
            self.model_service.get_supported_classes('breed'),
        )
        self.assertGreaterEqual(response.json['confidence'], 0)
        self.assertLessEqual(response.json['confidence'], 100)
        self.assertEqual(response.json['model_type'], 'breed')
        self.assertIn('title', response.json['information'])
        self.assertTrue(response.json['information']['description'])
        self.assertTrue(response.json['information']['details'])


if __name__ == '__main__':
    unittest.main()
