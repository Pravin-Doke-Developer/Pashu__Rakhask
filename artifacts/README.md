# Model Artifacts

This directory stores trained model files. **Do not commit model files to Git** — they are large binary files.

## Structure

```
artifacts/
├── disease_model/
│   ├── disease_model.keras      # Trained Keras model
│   ├── class_mapping.json       # Class label mapping
│   ├── training_config.json     # Training hyperparameters
│   └── evaluation_report.json   # Test set metrics
└── breed_model/
    ├── breed_model.keras
    ├── class_mapping.json
    ├── training_config.json
    └── evaluation_report.json
```

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
| `class_names.json` | Maps integer indices to human-readable class labels |
| `training_config.json` | Records the exact training setup for reproducibility |
| `evaluation_report.json` | Test set accuracy, precision, recall, F1, confusion matrix |
