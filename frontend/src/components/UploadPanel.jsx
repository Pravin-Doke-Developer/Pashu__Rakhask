import { useEffect, useRef, useState } from 'react';
import {
  AlertTriangle,
  Camera,
  ImagePlus,
  Loader2,
  X,
  Trash2,
} from 'lucide-react';

export default function UploadPanel({
  title,
  description,
  accept,
  onFileSelect,
  file,
  previewUrl,
  loading,
  error,
  onClear,
}) {
  const imageInputRef = useRef(null);
  const videoRef = useRef(null);
  const cameraStreamRef = useRef(null);
  const [cameraActive, setCameraActive] = useState(false);
  const [cameraError, setCameraError] = useState('');

  useEffect(() => {
    if (!cameraActive || !videoRef.current || !cameraStreamRef.current) return;

    videoRef.current.srcObject = cameraStreamRef.current;
    videoRef.current.play().catch(() => {
      setCameraError('Unable to start the camera preview. Check your browser permissions and try again.');
    });
  }, [cameraActive]);

  useEffect(
    () => () => {
      cameraStreamRef.current?.getTracks().forEach((track) => track.stop());
    },
    [],
  );

  const handleChange = (event) => {
    const selectedFile = event.target.files?.[0];
    if (selectedFile) onFileSelect(selectedFile);
    event.target.value = '';
  };

  const stopCamera = () => {
    cameraStreamRef.current?.getTracks().forEach((track) => track.stop());
    cameraStreamRef.current = null;
    if (videoRef.current) videoRef.current.srcObject = null;
    setCameraActive(false);
  };

  const startCamera = async () => {
    setCameraError('');
    if (!navigator.mediaDevices?.getUserMedia) {
      setCameraError(
        'Live camera capture is unavailable. Open this app over HTTPS or localhost in a supported browser.',
      );
      return;
    }

    stopCamera();
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: false,
        video: {
          facingMode: { ideal: 'environment' },
          width: { ideal: 1280 },
          height: { ideal: 720 },
        },
      });
      cameraStreamRef.current = stream;
      setCameraActive(true);
    } catch (err) {
      if (err.name === 'NotAllowedError' || err.name === 'PermissionDeniedError') {
        setCameraError('Camera permission was denied. Allow camera access in your browser settings and try again.');
      } else if (err.name === 'NotFoundError' || err.name === 'DevicesNotFoundError') {
        setCameraError('No camera was found on this device.');
      } else if (err.name === 'NotReadableError' || err.name === 'TrackStartError') {
        setCameraError('The camera is already in use by another app. Close it and try again.');
      } else {
        setCameraError(err.message || 'Unable to access the camera. Check your camera connection and try again.');
      }
    }
  };

  const capturePhoto = async () => {
    const video = videoRef.current;
    if (!video || !video.videoWidth || !video.videoHeight) {
      setCameraError('The camera is not ready yet. Wait for the preview, then capture the photo.');
      return;
    }

    const canvas = document.createElement('canvas');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    canvas.getContext('2d').drawImage(video, 0, 0, canvas.width, canvas.height);

    try {
      const blob = await new Promise((resolve, reject) => {
        canvas.toBlob(
          (imageBlob) => {
            if (imageBlob) resolve(imageBlob);
            else reject(new Error('The camera image could not be captured. Please try again.'));
          },
          'image/jpeg',
          0.92,
        );
      });
      const photo = new File([blob], `camera-${Date.now()}.jpg`, { type: 'image/jpeg' });
      stopCamera();
      onFileSelect(photo);
      setCameraError('');
    } catch (err) {
      setCameraError(err.message || 'The camera image could not be captured. Please try again.');
    }
  };

  return (
    <div className="card space-y-4">
      <div>
        <h2 className="text-xl font-semibold text-slate-900">{title}</h2>
        <p className="mt-1 text-sm text-slate-600">{description}</p>
      </div>

      <div className="rounded-2xl border border-dashed border-slate-300 bg-slate-50 p-4">
        {cameraActive && (
          <div className="mb-4 space-y-3">
            <video
              ref={videoRef}
              autoPlay
              muted
              playsInline
              aria-label="Live camera preview"
              className="max-h-[28rem] w-full rounded-xl bg-slate-900 object-contain"
            />
            <div className="flex flex-wrap justify-center gap-2">
              <button
                type="button"
                onClick={capturePhoto}
                disabled={loading}
                className="inline-flex items-center gap-2 rounded-xl bg-emerald-800 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-emerald-900 disabled:cursor-not-allowed disabled:opacity-60"
              >
                <Camera className="h-4 w-4" />
                Capture photo
              </button>
              <button
                type="button"
                onClick={stopCamera}
                className="inline-flex items-center gap-2 rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm font-semibold text-slate-700 transition hover:bg-slate-50"
              >
                <X className="h-4 w-4" />
                Close camera
              </button>
            </div>
          </div>
        )}
        <input
          ref={imageInputRef}
          type="file"
          accept={accept}
          className="hidden"
          onChange={handleChange}
          disabled={loading}
        />
        {!cameraActive && previewUrl ? (
          <div className="space-y-3">
            <img src={previewUrl} alt="Upload preview" className="h-56 w-full rounded-xl object-cover" />
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div className="text-sm text-slate-700">
                <div className="font-medium">{file?.name}</div>
                <div>{file ? `${(file.size / 1024 / 1024).toFixed(2)} MB` : ''}</div>
              </div>
              <div className="flex flex-wrap gap-2">
                <button
                  type="button"
                  onClick={startCamera}
                  disabled={loading}
                  className="inline-flex items-center gap-2 rounded-lg border border-emerald-200 bg-white px-3 py-2 text-sm font-medium text-emerald-800 hover:bg-emerald-50 disabled:cursor-not-allowed disabled:opacity-60"
                >
                  <Camera className="h-4 w-4" />
                  Retake photo
                </button>
                <button
                  type="button"
                  onClick={onClear}
                  disabled={loading}
                  className="inline-flex items-center gap-2 rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm font-medium text-slate-700 hover:bg-slate-100 disabled:cursor-not-allowed disabled:opacity-60"
                >
                  <Trash2 className="h-4 w-4" />
                  Remove
                </button>
              </div>
            </div>
          </div>
        ) : !cameraActive ? (
          <div className="flex flex-col items-center gap-4 rounded-xl border border-slate-200 bg-white px-4 py-8 text-center">
            <ImagePlus className="h-10 w-10 text-emerald-600" />
            <div>
              <div className="font-semibold text-slate-800">Add a cattle image</div>
              <div className="text-sm text-slate-500">PNG, JPG, JPEG, WEBP up to 10MB</div>
            </div>
            <div className="flex flex-wrap justify-center gap-2">
              <button
                type="button"
                onClick={startCamera}
                disabled={loading}
                className="inline-flex items-center gap-2 rounded-xl bg-emerald-800 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-emerald-900 disabled:cursor-not-allowed disabled:opacity-60"
              >
                <Camera className="h-4 w-4" />
                Open camera
              </button>
              <button
                type="button"
                onClick={() => imageInputRef.current?.click()}
                disabled={loading}
                className="inline-flex items-center gap-2 rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm font-semibold text-slate-700 transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-60"
              >
                <ImagePlus className="h-4 w-4" />
                Choose from device
              </button>
            </div>
            <p className="text-xs text-slate-400">
              Camera capture is available on supported phones and devices.
            </p>
          </div>
        ) : null}
      </div>

      {cameraError && (
        <div className="flex items-start gap-2 rounded-xl border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
          <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0" />
          <span>{cameraError}</span>
        </div>
      )}

      {error && (
        <div className="flex items-start gap-2 rounded-xl border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
          <AlertTriangle className="mt-0.5 h-4 w-4" />
          <span>{error}</span>
        </div>
      )}

      {loading && (
        <div className="flex items-center justify-center gap-2 rounded-xl border border-emerald-200 bg-emerald-50 px-3 py-2 text-sm font-medium text-emerald-700">
          <Loader2 className="h-4 w-4 animate-spin" />
          Processing your image...
        </div>
      )}

    </div>
  );
}
