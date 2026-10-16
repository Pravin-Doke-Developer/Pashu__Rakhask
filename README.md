# 🐄 Animal Health AI

AI-powered cattle disease screening and breed recognition system for farmers and agricultural teams.

## Overview

This project builds a full-stack application for:
- disease screening from uploaded cattle images
- supported breed recognition from uploaded cattle images
- a farmer-friendly dashboard with safety-oriented guidance
- model status and prediction history support

## Important limitation
This system is intended for educational and research use only. It does not replace professional veterinary diagnosis.

## Current workspace status
The project currently includes:
- validated dataset folders under `datasets/disease/` and `datasets/breed/`
- ML utilities under `ml/common/`
- a Flask backend under `backend/` that loads the root-level disease and breed model artifacts once at startup
- a Vite + React frontend under `frontend/` connected to the prediction API
- training notebooks under `notebooks/`

Model availability is reported by `GET /status`. Missing or invalid artifacts and TensorFlow load errors are reported as unavailable; the app does not substitute mock predictions.

## Directory structure

```text
animal-health-ai/
├── backend/
│   ├── app.py
│   ├── requirements.txt
│   ├── .env.example
│   ├── routes/
│   ├── services/
│   ├── utils/
│   └── tests/
├── frontend/
│   ├── src/
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   └── .env.example
├── ml/
│   ├── common/
│   ├── disease/
│   └── breed/
├── datasets/
│   ├── disease/
│   └── breed/
├── artifacts/
│   ├── disease_model/
│   └── breed_model/
├── docs/
├── notebooks/
├── tests/
├── .gitignore
├── .env.example
├── README.md
└── datasets/README.md
```

## Local setup

### Windows PowerShell

```powershell
cd c:\DYPIT\CEP\animal-health-ai
# TensorFlow 2.17.1 supports Python 3.9–3.12; Python 3.11 is recommended.
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r backend\requirements.txt
```

### Frontend

```powershell
cd c:\DYPIT\CEP\animal-health-ai\frontend
npm.cmd install
Copy-Item .env.example .env
npm.cmd run dev
```

### Backend

```powershell
cd c:\DYPIT\CEP\animal-health-ai\backend
Copy-Item .env.example .env
python app.py
```

The frontend typically runs on http://localhost:5173 and the backend on http://127.0.0.1:5000.

### Verify model status

With the backend running, open http://127.0.0.1:5000/status. Both `models.disease`
and `models.breed` should report `ready`. If either does not, the response's
`errors` object explains why.

## Dataset locations
- Disease dataset: `datasets/disease/`
- Breed dataset: `datasets/breed/Cattle Breeds/`

## Model artifact directories
- Disease model directory: `artifacts/disease_model/`
- Breed model directory: `artifacts/breed_model/`

Each directory contains its `.keras` file, `class_mapping.json`, and `metadata.json`.
The backend resolves both directories from the project root, reads the model
input and class-order metadata, and loads each model once when the Flask app is
created. The model metadata specifies 224×224 RGB inputs in the 0–255 range;
resize uses TensorFlow's bilinear image resize, and the models perform their
own pixel normalization.

Disease predictions are screening results only and are not confirmed diagnoses.

## Training workflow
- Use the Google Colab notebooks under `notebooks/`.
- Export model files as `.keras` and keep class mapping JSON files beside them.
- Download them to `artifacts/<model>_model/`.

## Testing

### Backend tests

```powershell
cd c:\DYPIT\CEP\animal-health-ai
python -m unittest discover -s backend/tests -q
```

### Frontend build check

```powershell
cd c:\DYPIT\CEP\animal-health-ai\frontend
npm.cmd run build
```

## Important notes
- Do not train models locally in VS Code.
- Do not commit large datasets or model artifacts.
- Do not claim a diagnosis from a model result alone.
