# Dataset inspection report

## Project summary
- Disease dataset root: `datasets/disease/`
- Breed dataset root: `datasets/breed/`
- Current workspace has no trained model artifacts yet, so the app should report `model not configured` until model export is completed.

## Disease dataset
- Verified classes: `healthy`, `lumpy`, `foot-and-mouth`
- Counts: `healthy=1290`, `lumpy=1205`, `foot-and-mouth=745`
- Directory layout is already class-based and suitable for transfer learning.
- No evidence of a second nested folder layer beyond the class directories.

## Breed dataset
- Verified class folders under `datasets/breed/Cattle Breeds/`
- Classes and counts:
  - Ayrshire cattle: 260
  - Brown Swiss cattle: 238
  - Holstein Friesian cattle: 254
  - Jersey cattle: 252
  - Red Dane cattle: 204
- This dataset is species-compatible with cattle breed recognition.

## Data quality notes
- The app intentionally does not assume a model is ready before artifacts are exported.
- Duplicate detection and split validation utilities are present in `ml/common/` and should be run before model training.
- The disease dataset and breed dataset are both cattle-focused, which makes the application coherent and avoids cross-species misuse.
