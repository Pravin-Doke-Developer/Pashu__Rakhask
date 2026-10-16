# API documentation

## Health endpoints
- `GET /health`
- `GET /status`
- `GET /history`

## Prediction endpoints
- `POST /predict/disease`
- `POST /predict/breed`

## Request format
Upload a multipart image field named `image`.

## Response model
The API returns JSON with a `status` field and a clear `error` message when unavailable.

### Model unavailable example
```json
{
  "status": "error",
  "error": "The disease model is not configured. Add the trained artifact before using this endpoint.",
  "model_type": "disease"
}
```

### Success example
```json
{
  "status": "ok",
  "model_type": "disease",
  "class_name": "healthy",
  "confidence": 96.0,
  "information": {
    "title": "No supported disease pattern detected",
    "description": "The model classified this image as healthy rather than one of the disease classes it was trained to recognize.",
    "details": [
      "This result does not confirm that the animal is healthy or rule out other conditions.",
      "Seek veterinary advice if the animal shows concerning signs or its condition changes."
    ]
  },
  "message": "Preliminary screening result only. Confirm diagnosis with a veterinarian."
}
```

Successful predictions include `information` for the predicted supported class.
It provides general educational context and is not a diagnosis; disease screening
results should be confirmed by a qualified veterinarian.

### Prediction history
`GET /history` returns saved successful predictions in a `history` array. Each
entry includes its timestamp, model type, uploaded filename, predicted class,
confidence, and source.

```json
{
  "status": "ok",
  "history": [
    {
      "timestamp": "2026-10-16T07:33:51+00:00",
      "model_type": "disease",
      "filename": "cattle.jpg",
      "class_name": "healthy",
      "confidence": 92.43,
      "source": "api_inference"
    }
  ]
}
```
