# Disease screening model training

This folder is reserved for the disease model training workflow and exported artifacts.

## Current dataset status
- Source dataset: `datasets/disease/`
- Verified class folders: `healthy`, `lumpy`, `foot-and-mouth`
- Training should be performed in Google Colab, not locally in VS Code.

## Artifacts
- Exported model files belong in `artifacts/disease_model/`
- Class mapping file: `class_mapping.json`

## Colab workflow
1. Open the notebook under `notebooks/disease_training_colab.ipynb` in Google Colab.
2. Mount Google Drive or upload the dataset folder.
3. Train on GPU when available.
4. Export the final model as `.keras` and save the `class_mapping.json` alongside it.
5. Download the exported artifact bundle and place it under `artifacts/disease_model/`.
