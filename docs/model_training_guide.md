# Model training guide

## Training requirement
The application must not be trained locally in VS Code. Training is done in Google Colab.

## Colab notebooks
- Disease notebook: `notebooks/disease_training_colab.ipynb`
- Breed notebook: `notebooks/breed_training_colab.ipynb`

## Download and export workflow
1. Mount the dataset from Google Drive or upload it to Colab.
2. Run the notebook cells in order.
3. Validate the class distribution and save the final model artifact.
4. Export the trained model as `.keras`.
5. Save the class mapping JSON in the same folder.
6. Download the artifact bundle.
7. Copy the files into `artifacts/disease_model/` or `artifacts/breed_model/`.

## Required model format
The backend is designed to load Keras model files such as `.keras` or `.h5` when present.
