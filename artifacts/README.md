# Model Artifacts

This directory stores trained model files. **Do not commit model files to Git** — they are large binary files.

## Structure

```
artifacts/
├── disease_model/
│   ├── PashuRakshak_Disease_Model.keras
│   └── PashuRakshak_Class_Names.json
└── breed_model/
    ├── PashuRakshak_AnimalType.keras
    ├── PashuRakshak_AnimalType_Classes.json
    ├── PashuRakshak_CowBreed_BalancedBatch.keras
    ├── PashuRakshak_CowBreed_BalancedBatch_Classes.json
    ├── PashuRakshak_CatBreed_10Class.keras
    ├── PashuRakshak_CatBreed_10Class_Classes.json
    ├── PashuRakshak_DogBreed_129_Best.keras
    └── PashuRakshak_DogBreed_129_Classes.json
```

Breed recognition first classifies the image as Cat, Cow, or Dog using
`PashuRakshak_AnimalType.keras`, then runs the matching cat, cow, or dog breed
model. Disease screening uses `PashuRakshak_Disease_Model.keras` directly.
Class names are read in their listed order from the accompanying JSON files.

## How to Obtain

### Option 1: Train the Models Yourself
Run `notebooks/train_models_colab.py` in Google Colab. Copy the project (including
the datasets and this script) to Google Drive under `MyDrive/animal-health-ai`.
Mount Drive in Colab, enable a GPU, and run:

```python
!python /content/drive/MyDrive/animal-health-ai/notebooks/train_models_colab.py \
  --task disease \
  --project-root /content/drive/MyDrive/animal-health-ai
```

Run the same command with `--task breed` to train the breed classifier.

The disease trainer uses the existing `datasets/disease_split/{train,val,test}`
folders. The breed trainer uses `datasets/breed_split/{train,val,test}` when
present; otherwise it creates a reproducible 70/15/15 split from
`datasets/breed/Cattle Breeds/`, keeping files with matching `_c` suffixes in
the same split.

Each run writes the model, class mapping, training configuration, and test
evaluation report to its matching artifact folder. It also updates the
corresponding `ml/<task>/class_mapping.json` file used by the backend.

### Option 2: Download Pre-trained Models
(Links will be provided after models are trained and evaluated.)

## File Descriptions

| File | Purpose |
|------|---------|
| `*.keras` | The trained TensorFlow/Keras model weights and architecture |
| `*_Classes.json`, `PashuRakshak_Class_Names.json` | Class labels in model output-index order |
| `training_config.json` | Records the exact training setup for reproducibility |
| `evaluation_report.json` | Test set accuracy, precision, recall, F1, confusion matrix |
