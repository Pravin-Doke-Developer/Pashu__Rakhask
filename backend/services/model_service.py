import json
import os
import shutil
import threading
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image

# Optimize TensorFlow memory usage before import
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # Suppress TensorFlow warnings
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'  # Disable oneDNN to reduce memory

# ImageNet animal class indices (subset of 1000 classes that are animals)
IMAGENET_ANIMAL_INDICES = {
    # Cats
    281, 282, 283, 284, 285, 286, 287, 288, 289, 290, 291, 292, 293, 294, 295, 296, 297, 298,
    # Dogs
    151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168,
    169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186,
    187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 203, 204,
    205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 221, 222,
    223, 224, 225, 226, 227, 228, 229, 230, 231, 232, 233, 234, 235, 236, 237, 238, 239, 240,
    241, 242, 243, 244, 245, 246, 247, 248, 249, 250, 251, 252, 253, 254, 255, 256, 257, 258,
    259, 260, 261, 262, 263, 264, 265, 266, 267, 268, 269, 270, 271, 272, 273, 274, 275, 276,
    277, 278, 279, 280,
    # Cows and other livestock
    326,  # ox
    344,  # water buffalo
    345,  # water buffalo
    # Other animals
    299, 300, 301, 302, 303, 304, 305, 306, 307, 308, 309, 310, 311, 312, 313, 314, 315, 316,
    317, 318, 319, 320, 321, 322, 323, 324, 325, 327, 328, 329, 330, 331, 332, 333, 334, 335,
    336, 337, 338, 339, 340, 341, 342, 343, 346, 347, 348, 349, 350, 351, 352, 353, 354, 355,
    356, 357, 358, 359, 360, 361, 362, 363, 364, 365, 366, 367, 368, 369, 370, 371, 372, 373,
    374, 375, 376, 377, 378, 379, 380, 381, 382, 383, 384, 385, 386, 387, 388, 389, 390, 391,
    392, 393, 394, 395, 396, 397, 398, 399, 400, 401, 402, 403, 404, 405, 406, 407, 408, 409,
    410, 411, 412, 413, 414, 415, 416, 417, 418, 419, 420, 421, 422, 423, 424, 425, 426, 427,
    428, 429, 430, 431, 432, 433, 434, 435, 436, 437, 438,
}


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
            'symptoms': [
                'High fever (up to 41°C)',
                'Blisters or sores in the mouth and on the feet',
                'Excessive drooling and foaming at the mouth',
                'Lameness and difficulty walking',
                'Reduced appetite and weight loss',
                'Decreased milk production in dairy animals',
            ],
            'home_care': [
                'Isolate the affected animal immediately to prevent spread',
                'Provide soft, easily digestible food and fresh water',
                'Keep the animal in a clean, comfortable environment',
                'Clean mouth and feet with mild antiseptic solution',
                'Apply soothing ointments to blisters if recommended by vet',
                'Monitor temperature and other vital signs regularly',
            ],
            'details': [
                'If suspected, contact a veterinarian or local animal-health authority promptly.',
                'Follow their advice about limiting animal movement.',
                'This is a reportable disease in many regions.',
            ],
        },
        'Lumpy_Skin_Disease': {
            'title': 'Lumpy skin disease',
            'description': (
                'A viral cattle disease that can cause skin nodules and may spread between '
                'animals, including through insect vectors.'
            ),
            'symptoms': [
                'High fever (up to 41°C)',
                'Firm, raised skin nodules (2-5 cm in diameter)',
                'Swollen lymph nodes',
                'Nasal and ocular discharge',
                'Reduced appetite and milk production',
                'Weight loss and emaciation',
            ],
            'home_care': [
                'Isolate affected animals to prevent spread',
                'Use insect repellents to control vectors (flies, mosquitoes)',
                'Clean and disinfect wounds with antiseptic solution',
                'Provide nutritious diet and plenty of fresh water',
                'Apply antibiotic ointment to secondary infections',
                'Keep the animal cool and comfortable',
                'Monitor for secondary bacterial infections',
            ],
            'details': [
                'Contact a veterinarian for assessment and advice on limiting spread.',
                'An image prediction alone cannot confirm the disease.',
                'Vaccination is available for prevention in endemic areas.',
            ],
        },
        'Mastitis_Disease': {
            'title': 'Mastitis',
            'description': (
                'An inflammatory condition of the mammary gland, commonly affecting dairy cows.'
            ),
            'symptoms': [
                'Swollen, hot, or painful udder',
                'Changes in milk appearance (watery, bloody, or containing pus)',
                'Clots or flakes in the milk',
                'Reduced milk production',
                'Fever and lethargy in severe cases',
                'Reluctance to let calf suckle',
            ],
            'home_care': [
                'Apply warm compresses to the affected udder',
                'Gently massage the udder to improve circulation',
                'Milk the affected quarter frequently to remove infected milk',
                'Ensure clean milking equipment and hygiene',
                'Provide clean, dry bedding',
                'Increase fluid intake',
                'Consider natural anti-inflammatory remedies like turmeric',
            ],
            'details': [
                'Consult a veterinarian for proper diagnosis and treatment.',
                'Antibiotics may be necessary for bacterial mastitis.',
                'Early treatment is crucial to prevent permanent damage.',
            ],
        },
        'demodicosis': {
            'title': 'Demodicosis (Mange)',
            'description': (
                'A skin condition caused by Demodex mites, affecting dogs and other animals.'
            ),
            'symptoms': [
                'Patchy hair loss (alopecia)',
                'Red, inflamed skin',
                'Scaling and crusting',
                'Itching (may be mild to severe)',
                'Thickening of the skin in chronic cases',
                'Secondary bacterial infections',
            ],
            'home_care': [
                'Bathe with medicated or benzoyl peroxide shampoo',
                'Apply aloe vera gel to soothe irritated skin',
                'Boost immune system with nutritious diet',
                'Keep the animal clean and dry',
                'Wash bedding regularly in hot water',
                'Avoid stress and maintain good overall health',
                'Supplement with omega-3 fatty acids for skin health',
            ],
            'details': [
                'Veterinary consultation recommended for appropriate treatment.',
                'May require prescription medications in severe cases.',
                'Some animals may have genetic predisposition.',
            ],
        },
        'dermatitis': {
            'title': 'Dermatitis',
            'description': (
                'Inflammation of the skin that can have various causes including allergies, infections, or irritants.'
            ),
            'symptoms': [
                'Red, inflamed skin',
                'Intense itching and scratching',
                'Skin lesions or rashes',
                'Dry, flaky, or oozing skin',
                'Hair loss in affected areas',
                'Bad odor from skin infections',
            ],
            'home_care': [
                'Identify and remove allergens if possible',
                'Bathe with gentle, hypoallergenic shampoo',
                'Apply cool compresses to reduce inflammation',
                'Use oatmeal baths to soothe itching',
                'Apply coconut oil or aloe vera to affected areas',
                'Keep the animal from scratching (use Elizabethan collar if needed)',
                'Ensure clean, dry living environment',
            ],
            'details': [
                'Consult a veterinarian to determine the underlying cause.',
                'Allergy testing may be recommended for chronic cases.',
                'May require antihistamines or other medications.',
            ],
        },
        'flea_allergy': {
            'title': 'Flea allergy dermatitis',
            'description': (
                'An allergic reaction to flea saliva, commonly affecting dogs and cats.'
            ),
            'symptoms': [
                'Intense itching, especially near tail base and hind legs',
                'Red, inflamed skin',
                'Hair loss and hot spots',
                'Skin infections from excessive scratching',
                'Visible fleas or flea dirt (black specks)',
                'Restlessness and discomfort',
            ],
            'home_care': [
                'Use flea comb to remove fleas and flea dirt',
                'Bathe with flea shampoo',
                'Apply natural flea repellents (cedar oil, neem)',
                'Wash all bedding in hot water',
                'Vacuum home thoroughly and frequently',
                'Use flea prevention treatments (collars, spot-on)',
                'Treat all pets in the household simultaneously',
                'Soothe irritated skin with cool compresses',
            ],
            'details': [
                'Flea control and veterinary treatment are typically necessary.',
                'Even one flea bite can trigger allergic reaction in sensitive animals.',
                'Prevention is key to managing this condition.',
            ],
        },
        'fungal_infections': {
            'title': 'Fungal skin infection',
            'description': (
                'Skin infections caused by various types of fungi, affecting multiple animal species.'
            ),
            'symptoms': [
                'Circular, ring-shaped patches of hair loss',
                'Red, scaly borders around patches',
                'Crusting and scaling of skin',
                'Itching (may vary by type of fungus)',
                'Broken or brittle hair',
                'Spreading lesions if untreated',
            ],
            'home_care': [
                'Clip hair around affected areas',
                'Clean with antifungal solution (diluted apple cider vinegar)',
                'Apply antifungal creams or ointments',
                'Use medicated shampoos as directed',
                'Keep the area clean and dry',
                'Disinfect grooming tools and bedding',
                'Isolate infected animals to prevent spread',
                'Boost immune system with proper nutrition',
            ],
            'details': [
                'Veterinary diagnosis and antifungal treatment are usually required.',
                'Some fungal infections can spread to humans (zoonotic).',
                'Treatment may take several weeks to months.',
            ],
        },
        'hot_spots_disease': {
            'title': 'Hot spots (Acute moist dermatitis)',
            'description': (
                'A common skin condition in dogs characterized by red, moist, and painful lesions.'
            ),
            'symptoms': [
                'Red, moist, and oozing skin lesions',
                'Intense itching and pain',
                'Hair loss around the lesion',
                'Bad odor from infected area',
                'Rapid spreading if not treated',
                'Animal may lick or chew the area excessively',
            ],
            'home_care': [
                'Clip hair around the hot spot to expose it to air',
                'Clean gently with antiseptic solution',
                'Apply cool compresses to reduce inflammation',
                'Use Elizabethan collar to prevent licking',
                'Apply hydrocortisone spray if approved by vet',
                'Keep the area clean and dry',
                'Identify and address underlying cause (fleas, allergies)',
            ],
            'details': [
                'Veterinary treatment is recommended to address the underlying cause.',
                'Often caused by self-trauma from scratching or licking.',
                'May require antibiotics if secondary infection develops.',
            ],
        },
        'ringworm_cat': {
            'title': 'Ringworm in cats',
            'description': (
                'A fungal infection of the skin, hair, or nails caused by dermatophytes.'
            ),
            'symptoms': [
                'Circular patches of hair loss',
                'Red, scaly borders around patches',
                'Crusty or flaky skin',
                'Broken or brittle hair',
                'Itching (may be mild)',
                'Multiple lesions in severe cases',
            ],
            'home_care': [
                'Isolate infected cat from other pets',
                'Clip hair around lesions',
                'Clean with antifungal solution',
                'Apply antifungal cream as directed',
                'Use medicated shampoo weekly',
                'Disinfect environment thoroughly',
                'Wash hands after handling infected cat',
                'Boost immune system with quality diet',
            ],
            'details': [
                'Contagious to other animals and humans; veterinary treatment is necessary.',
                'Can spread through direct contact or contaminated objects.',
                'Treatment may take several weeks.',
            ],
        },
        'ringworm_dog': {
            'title': 'Ringworm in dogs',
            'description': (
                'A fungal infection of the skin, hair, or nails caused by dermatophytes.'
            ),
            'symptoms': [
                'Circular patches of hair loss',
                'Red, scaly borders around patches',
                'Crusty or flaky skin',
                'Broken or brittle hair',
                'Itching (may be mild)',
                'Multiple lesions in severe cases',
            ],
            'home_care': [
                'Isolate infected dog from other pets',
                'Clip hair around lesions',
                'Clean with antifungal solution',
                'Apply antifungal cream as directed',
                'Use medicated shampoo weekly',
                'Disinfect environment thoroughly',
                'Wash hands after handling infected dog',
                'Boost immune system with quality diet',
            ],
            'details': [
                'Contagious to other animals and humans; veterinary treatment is necessary.',
                'Can spread through direct contact or contaminated objects.',
                'Treatment may take several weeks.',
            ],
        },
        'scabies': {
            'title': 'Sarcoptic mange (Scabies)',
            'description': (
                'A highly contagious skin condition caused by Sarcoptes mites, affecting dogs and other animals.'
            ),
            'symptoms': [
                'Intense itching and scratching',
                'Red, inflamed skin',
                'Hair loss and crusting',
                'Skin sores from excessive scratching',
                'Restlessness and irritability',
                'Weight loss in severe cases',
                'Secondary bacterial infections',
            ],
            'home_care': [
                'Isolate infected animal immediately',
                'Bathe with medicated anti-mange shampoo',
                'Apply soothing remedies to reduce itching (oatmeal baths)',
                'Use Elizabethan collar to prevent scratching',
                'Wash all bedding in hot water',
                'Vacuum and disinfect living area thoroughly',
                'Treat all animals in contact with infected one',
                'Provide nutritious diet to support recovery',
            ],
            'details': [
                'Immediate veterinary treatment is required to prevent spread and relieve discomfort.',
                'Highly contagious to other animals and can affect humans.',
                'Prescription medications are usually necessary.',
            ],
        },
        'healthy_cat': {
            'title': 'Healthy cat',
            'description': (
                'The model classified this cat as healthy with no apparent disease patterns.'
            ),
            'symptoms': [],
            'home_care': [
                'Provide balanced, age-appropriate diet',
                'Ensure access to fresh clean water',
                'Regular grooming and nail trimming',
                'Provide mental stimulation and exercise',
                'Keep vaccinations up to date',
                'Regular veterinary check-ups (annually or bi-annually)',
                'Maintain clean litter box',
                'Monitor weight and behavior changes',
            ],
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
            'symptoms': [],
            'home_care': [
                'Provide balanced diet with adequate roughage',
                'Ensure access to clean water at all times',
                'Maintain clean and comfortable shelter',
                'Regular hoof care and trimming',
                'Monitor body condition score',
                'Provide mineral supplements as needed',
                'Regular veterinary check-ups and vaccinations',
                'Proper milking hygiene for dairy cows',
            ],
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
            'symptoms': [],
            'home_care': [
                'Provide balanced, age-appropriate diet',
                'Ensure access to fresh clean water',
                'Regular exercise and mental stimulation',
                'Regular grooming and dental care',
                'Keep vaccinations up to date',
                'Regular veterinary check-ups (annually)',
                'Maintain healthy weight',
                'Provide flea and tick prevention',
            ],
            'details': [
                'This result does not confirm the dog is completely healthy or rule out other conditions.',
                'Regular veterinary check-ups are recommended for optimal health.',
            ],
        },
    },
    'breed': {
        'brahman': {
            'title': 'Brahman',
            'description': 'A hardy zebu cattle breed known for heat tolerance and disease resistance.',
            'market_demand': 'High - Popular in tropical and subtropical regions',
            'general_weight': 'Bulls: 700-900 kg, Cows: 450-600 kg',
            'market_price': '₹40,000 - ₹70,000 (varies by age and quality)',
            'details': [
                'Excellent for crossbreeding to improve heat tolerance.',
                'Good mothering ability and calving ease.',
                'Adaptable to harsh climates.',
            ],
        },
        'brahman cross': {
            'title': 'Brahman Cross',
            'description': 'Crossbred cattle with Brahman genetics, combining hardiness with improved productivity.',
            'market_demand': 'High - Sought after for hybrid vigor',
            'general_weight': 'Bulls: 650-850 kg, Cows: 400-550 kg',
            'market_price': '₹35,000 - ₹60,000 (varies by cross)',
            'details': [
                'Better growth rate than pure Brahman.',
                'Improved milk production in dairy crosses.',
                'Maintains heat tolerance and disease resistance.',
            ],
        },
        'cholistani': {
            'title': 'Cholistani',
            'description': 'A dual-purpose cattle breed from the Cholistan desert region of Pakistan.',
            'market_demand': 'Moderate - Regional preference',
            'general_weight': 'Bulls: 500-600 kg, Cows: 350-450 kg',
            'market_price': '₹30,000 - ₹50,000',
            'details': [
                'Well-adapted to desert conditions.',
                'Good for both milk and meat production.',
                'Hardy and requires minimal maintenance.',
            ],
        },
        'cholistani cross': {
            'title': 'Cholistani Cross',
            'description': 'Crossbred cattle with Cholistani genetics for improved productivity.',
            'market_demand': 'Moderate - Local market preference',
            'general_weight': 'Bulls: 550-650 kg, Cows: 380-480 kg',
            'market_price': '₹32,000 - ₹55,000',
            'details': [
                'Improved productivity while maintaining hardiness.',
                'Good for small-scale farmers.',
                'Adaptable to various conditions.',
            ],
        },
        'dhani': {
            'title': 'Dhani',
            'description': 'A local cattle breed known for its adaptability.',
            'market_demand': 'Moderate - Local demand',
            'general_weight': 'Bulls: 450-550 kg, Cows: 300-400 kg',
            'market_price': '₹25,000 - ₹45,000',
            'details': [
                'Well-suited for local farming conditions.',
                'Good for draught and milk production.',
                'Low maintenance requirements.',
            ],
        },
        'fresian': {
            'title': 'Friesian (Holstein)',
            'description': 'A high-yielding dairy breed known for excellent milk production.',
            'market_demand': 'Very High - Premier dairy breed',
            'general_weight': 'Bulls: 900-1200 kg, Cows: 500-700 kg',
            'market_price': '₹50,000 - ₹1,00,000 (high quality)',
            'details': [
                'Highest milk production among dairy breeds.',
                'Requires good management and nutrition.',
                'Popular in commercial dairy farming.',
            ],
        },
        'fresian cross': {
            'title': 'Friesian Cross',
            'description': 'Crossbred cattle with Friesian genetics for improved milk production.',
            'market_demand': 'High - Popular for dairy improvement',
            'general_weight': 'Bulls: 800-1000 kg, Cows: 450-600 kg',
            'market_price': '₹40,000 - ₹80,000',
            'details': [
                'Improved milk yield over local breeds.',
                'Better adaptability than pure Friesian.',
                'Suitable for small and medium farms.',
            ],
        },
        'kankarej': {
            'title': 'Kankrej',
            'description': 'A dual-purpose breed from Gujarat, known for drought tolerance and good milk yield.',
            'market_demand': 'High - Popular in western India',
            'general_weight': 'Bulls: 600-800 kg, Cows: 400-550 kg',
            'market_price': '₹35,000 - ₹65,000',
            'details': [
                'Excellent draught capability.',
                'Good milk production (6-8 liters/day).',
                'Well-adapted to semi-arid regions.',
            ],
        },
        'sahiwal': {
            'title': 'Sahiwal',
            'description': 'A premier dairy breed from Punjab, known for high milk yield and heat tolerance.',
            'market_demand': 'Very High - Top indigenous dairy breed',
            'general_weight': 'Bulls: 600-800 kg, Cows: 400-500 kg',
            'market_price': '₹45,000 - ₹80,000',
            'details': [
                'Excellent milk yield (8-10 liters/day).',
                'High fat content in milk.',
                'Heat and disease resistant.',
            ],
        },
        'sahiwal cross': {
            'title': 'Sahiwal Cross',
            'description': 'Crossbred cattle with Sahiwal genetics for improved dairy performance.',
            'market_demand': 'High - Sought for dairy improvement',
            'general_weight': 'Bulls: 550-750 kg, Cows: 380-480 kg',
            'market_price': '₹40,000 - ₹70,000',
            'details': [
                'Improved milk production while maintaining hardiness.',
                'Popular for crossbreeding programs.',
                'Good for tropical climates.',
            ],
        },
        'sibbi': {
            'title': 'Sibi',
            'description': 'A hardy cattle breed from the Sibi region of Balochistan.',
            'market_demand': 'Moderate - Regional preference',
            'general_weight': 'Bulls: 500-650 kg, Cows: 350-450 kg',
            'market_price': '₹28,000 - ₹48,000',
            'details': [
                'Well-adapted to harsh desert conditions.',
                'Good for both milk and meat.',
                'Excellent drought tolerance.',
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
        self._imagenet_model = None  # Pre-trained model for animal detection
        self._load_lock = threading.RLock()

        # Read lightweight class mappings locally at startup. This does not import
        # TensorFlow and does not perform network requests.
        self._mapping_errors: dict[str, str] = {}
        for model_key in ('disease', *ANIMAL_MODEL_KEYS):
            mapping_path = self.mapping_paths[model_key]
            if not mapping_path.is_file():
                self._mapping_errors[model_key] = (
                    f'Required class names file is missing: {mapping_path.name}.'
                )
                continue
            try:
                self.class_names[model_key] = self._read_class_names(mapping_path)
            except (OSError, ValueError, TypeError, json.JSONDecodeError) as exc:
                self._mapping_errors[model_key] = (
                    f'Unable to read class names for {model_key}: {exc}'
                )

        # Record local artifact state without downloading or loading any models.
        for model_key in ('disease', *ANIMAL_MODEL_KEYS):
            model_path = self.model_paths[model_key]
            if model_key in self._mapping_errors:
                self.component_status[model_key] = 'unavailable'
                self.component_errors[model_key] = self._mapping_errors[model_key]
            elif not model_path.is_file():
                self.component_status[model_key] = 'missing'
                self.component_errors[model_key] = (
                    f'Model artifact file is missing: {model_path.name}.'
                )
            else:
                # Artifacts and class labels exist; the TensorFlow model is not loaded yet.
                self.component_status[model_key] = 'not_loaded'

        self._update_public_status()

    def _ensure_artifact_available(self, local_path: Path) -> bool:
        """Download one missing artifact on demand, preserving existing local files."""
        if local_path.is_file():
            return True

        repo_id = os.getenv('HF_MODEL_REPO', 'PRAVIN9087/pashurakshak-model')
        token = os.getenv('HF_TOKEN')
        
        if not token:
            print(f'[ERROR] HF_TOKEN is not configured; cannot download {local_path.name}.')
            return False

        temp_path = local_path.with_name(f'.{local_path.name}.{os.getpid()}.tmp')
        try:
            from huggingface_hub import hf_hub_download

            relative_path = local_path.relative_to(self.project_root).as_posix()
            print(f'[INFO] Downloading missing model artifact on demand: {relative_path}')
            
            cached_path = Path(hf_hub_download(
                repo_id=repo_id,
                filename=relative_path,
                repo_type='model',
                token=token,
            ))
            
            if not cached_path.is_file() or cached_path.stat().st_size == 0:
                raise FileNotFoundError(
                    f'Hugging Face returned an empty or missing artifact: {relative_path}'
                )

            local_path.parent.mkdir(parents=True, exist_ok=True)
            
            shutil.copyfile(cached_path, temp_path)
            
            if temp_path.stat().st_size == 0:
                raise OSError(f'Downloaded artifact is empty: {relative_path}')
            
            # Atomic replacement prevents readers from seeing a partially copied file.
            os.replace(temp_path, local_path)
            print(f'[INFO] Successfully installed artifact: {local_path.name}')
            return True
        except Exception as exc:
            print(f'[ERROR] Unable to download model artifact {local_path.name}: {exc}')
            return False
        finally:
            try:
                if temp_path.exists():
                    temp_path.unlink()
            except OSError:
                pass

    def _ensure_model_loaded(self, model_key: str) -> bool:
        """Load one model on demand, avoiding simultaneous loads of the same model."""
        if model_key in self.models:
            return True
        if model_key not in self.model_paths:
            self.component_errors[model_key] = f'Unknown model key: {model_key}.'
            return False

        with self._load_lock:
            if model_key in self.models:
                return True
            print(f'[INFO] Loading model: {model_key}')
            self._load_model(model_key)
            self._update_public_status()
            loaded = model_key in self.models
            print(f'[INFO] Model {model_key} load result: {"success" if loaded else "failed"}')
            return loaded

    def _load_model(self, model_key: str) -> None:
        model_path = self.model_paths[model_key]
        mapping_path = self.mapping_paths[model_key]
        metadata_path = self.metadata_paths[model_key]

        # Retry downloads only when an artifact is missing, and only when this
        # particular model is requested. Existing files are never overwritten.
        if not mapping_path.is_file():
            if self._ensure_artifact_available(mapping_path):
                try:
                    self.class_names[model_key] = self._read_class_names(mapping_path)
                    self._mapping_errors.pop(model_key, None)
                except (OSError, ValueError, TypeError, json.JSONDecodeError) as exc:
                    self._mapping_errors[model_key] = (
                        f'Unable to read class names for {model_key}: {exc}'
                    )
            else:
                self._mapping_errors[model_key] = (
                    f'Required class names file is missing: {mapping_path.name}; '
                    'download was unavailable or failed.'
                )

        if model_key in self._mapping_errors or model_key not in self.class_names:
            self.component_status[model_key] = 'unavailable'
            self.component_errors[model_key] = self._mapping_errors.get(
                model_key, f'Class names for {model_key} are unavailable.'
            )
            return

        if not model_path.is_file() and not self._ensure_artifact_available(model_path):
            self.component_status[model_key] = 'missing'
            self.component_errors[model_key] = (
                f'Model artifact file is missing: {model_path.name}; '
                'download was unavailable or failed.'
            )
            return

        try:
            class_names = self.class_names[model_key]
            metadata = self._read_metadata(metadata_path, class_names, model_key)
            if self._tensorflow is None:
                import tensorflow as tf
                # Configure TensorFlow to use less memory
                gpus = tf.config.list_physical_devices('GPU')
                if gpus:
                    try:
                        for gpu in gpus:
                            tf.config.experimental.set_memory_growth(gpu, True)
                    except RuntimeError as e:
                        print(f'[WARNING] GPU memory configuration failed: {e}')
                self._tensorflow = tf
            model = self._tensorflow.keras.models.load_model(model_path, compile=False)
            metadata = self._complete_metadata(model, metadata)
            self._validate_model_shape(model, metadata, class_names)
        except Exception as exc:  # Includes TensorFlow backend-specific load errors.
            self.component_status[model_key] = 'unavailable'
            self.component_errors[model_key] = f'Unable to load {model_key} model: {exc}'
            return

        self.models[model_key] = model
        self.metadata[model_key] = metadata
        self.component_status[model_key] = 'ready'
        self.component_errors.pop(model_key, None)
        self._mapping_errors.pop(model_key, None)

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
        disease_component_status = self.component_status.get('disease', 'missing')
        self.model_status['disease'] = 'not_loaded' if disease_component_status == 'not_loaded' else disease_component_status
        if self.model_status['disease'] not in ('ready', 'not_loaded'):
            self.model_errors['disease'] = self.component_errors.get(
                'disease', 'The disease model is not configured.'
            )
        else:
            self.model_errors.pop('disease', None)

        required_breed_models = ('animal_type', *ANIMAL_TYPE_TO_BREED_MODEL.values())
        unavailable = [
            (key, self.component_errors.get(key, f'{key} model is unavailable.'))
            for key in required_breed_models
            if self.component_status.get(key) not in ('ready', 'not_loaded')
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
        # Report artifact readiness, not whether a model is currently resident in memory.
        # This keeps /status lightweight and prevents it from loading TensorFlow models.
        status = self.model_status.copy()
        for key, value in status.items():
            if value == 'not_loaded':
                status[key] = 'ready'
        return status

    def get_errors(self) -> dict[str, str]:
        return self.model_errors.copy()

    def get_component_status(self) -> dict[str, str]:
        """Return per-model lifecycle state without changing the public status API."""
        return self.component_status.copy()

    def is_available(self, model_type: str) -> bool:
        """Check if a model is available (artifacts exist locally)."""
        return self.model_status.get(model_type) in ('ready', 'not_loaded')

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

    def _get_imagenet_model(self):
        """Lazy load the pre-trained ImageNet model for animal detection."""
        if self._imagenet_model is None:
            if self._tensorflow is None:
                import tensorflow as tf
                self._tensorflow = tf
            # Load MobileNetV2 pre-trained on ImageNet
            self._imagenet_model = self._tensorflow.keras.applications.MobileNetV2(
                weights='imagenet',
                include_top=True,
                input_shape=(224, 224, 3)
            )
        return self._imagenet_model

    def _validate_animal_image(self, image_path: str) -> dict:
        """Validate that the image contains an animal using pre-trained ImageNet model."""
        try:
            # Load pre-trained model
            imagenet_model = self._get_imagenet_model()
            
            # Prepare image for ImageNet model
            image = Image.open(image_path).convert('RGB')
            image_array = np.asarray(image, dtype=np.float32)
            resized = self._tensorflow.image.resize(image_array, (224, 224))
            # MobileNetV2 expects preprocessing
            preprocessed = self._tensorflow.keras.applications.mobilenet_v2.preprocess_input(resized)
            image_batch = self._tensorflow.expand_dims(preprocessed, axis=0)
            
            # Get predictions
            predictions = imagenet_model.predict(image_batch, verbose=0)
            top_5_indices = np.argsort(predictions[0])[-5:][::-1]
            top_5_probs = predictions[0][top_5_indices]
            
            # Check if any of the top predictions are animal classes
            animal_prob_sum = 0.0
            for idx, prob in zip(top_5_indices, top_5_probs):
                if idx in IMAGENET_ANIMAL_INDICES:
                    animal_prob_sum += prob
            
            # If the total probability of animal classes in top 5 is less than 60%, reject
            if animal_prob_sum < 0.6:
                return {
                    'status': 'error',
                    'error': 'Invalid image. Please upload a valid animal image.',
                    'animal_probability': round(animal_prob_sum * 100, 2),
                }
            
            return {'status': 'ok'}
        except Exception as exc:
            # If validation fails, allow the prediction to proceed
            # This ensures we don't block valid predictions due to validation errors
            print(f"Animal validation error: {exc}")
            return {'status': 'ok'}

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

        # Load only the requested path. In particular, a missing breed model
        # should not prevent the disease endpoint from working, and vice versa.
        if model_type == 'disease':
            if not self._ensure_model_loaded('disease'):
                self._update_public_status()
                return {
                    'status': 'error',
                    'model_type': model_type,
                    'error': self.component_errors.get(
                        'disease', 'The disease model is not configured.'
                    ),
                    'supported_classes': self.get_supported_classes('disease'),
                }

        try:
            # Skip ImageNet validation for breed prediction to conserve memory on Render
            # The breed models themselves handle animal type classification
            # if model_type == 'breed':
            #     validation_result = self._validate_animal_image(image_path)
            #     if validation_result.get('status') != 'ok':
            #         return validation_result

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
        if not self._ensure_model_loaded(model_key):
            error = self.component_errors.get(model_key, f'The {model_key} model could not be loaded.')
            raise RuntimeError(error)
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
        confidence = float(probabilities[top_index])
        is_disease = model_key == 'disease'
        is_breed_model = model_key in ('cow_breed', 'cat_breed', 'dog_breed')
        class_name = class_names[top_index]
        
        # For disease prediction, require minimum confidence to ensure it's a valid disease image
        if is_disease and confidence < 0.5:
            return {
                'status': 'error',
                'error': 'Invalid image. Please upload a valid animal disease image.',
                'confidence': round(confidence * 100, 2),
                'detected_class': class_name,
            }
        
        # Use 'breed' as the key for CLASS_INFORMATION lookup for breed models
        info_key = 'breed' if is_breed_model else model_key
        info = CLASS_INFORMATION.get(info_key, {}).get(class_name)
        if info is None:
            if is_disease:
                description = (
                    'The model classified this image as this supported disease or health category.'
                )
                symptoms = [
                    'Please consult a veterinarian for accurate symptom identification.',
                    'Monitor the animal for any changes in behavior, appetite, or physical condition.',
                ]
                home_care = [
                    'Isolate the animal from others if symptoms are present.',
                    'Provide fresh water and appropriate nutrition.',
                    'Keep the animal in a clean, comfortable environment.',
                    'Contact a veterinarian for proper diagnosis and treatment.',
                ]
                market_demand = None
                general_weight = None
                market_price = None
            elif model_key == 'animal_type':
                description = 'The model classified this image as this supported animal type.'
                symptoms = []
                home_care = []
                market_demand = None
                general_weight = None
                market_price = None
            elif is_breed_model:
                description = 'The model classified this image as this supported breed.'
                symptoms = []
                home_care = []
                market_demand = 'Information not available'
                general_weight = 'Information not available'
                market_price = 'Information not available'
            else:
                description = 'The model classified this image as this supported breed.'
                symptoms = []
                home_care = []
                market_demand = 'Information not available'
                general_weight = 'Information not available'
                market_price = 'Information not available'
            info = {
                'title': class_name.replace('_', ' ').replace('-', ' ').title(),
                'description': description,
                'symptoms': symptoms,
                'home_care': home_care,
                'market_demand': market_demand,
                'general_weight': general_weight,
                'market_price': market_price,
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
