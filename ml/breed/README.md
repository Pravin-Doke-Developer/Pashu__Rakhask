# Breed recognition model training

This directory stores the breed model workflow and class metadata.

## Current dataset status
- Source dataset: `datasets/breed/Cattle Breeds/`
- Verified breeds: Ayrshire cattle, Brown Swiss cattle, Holstein Friesian cattle, Jersey cattle, Red Dane cattle

## Artifacts
- Exported model files belong in `artifacts/breed_model/`
- Class mapping file: `class_mapping.json`

## Colab workflow
1. Open `notebooks/breed_training_colab.ipynb` in Google Colab.
2. Mount the dataset or upload it to the Colab runtime.
3. Train with MobileNetV2 or EfficientNetB0 and record validation metrics.
4. Export the model and class mapping file.
5. Download the artifact bundle to `artifacts/breed_model/`.
