import { useEffect, useState } from 'react';
import { BookHeart, CheckCircle2, ScanSearch } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import UploadPanel from '../components/UploadPanel';
import StatusBadge from '../components/StatusBadge';
import { getModelsStatus, predictBreed } from '../services/api';

const statusLabel = (status) =>
  status === 'ready' ? 'Configured' : status === 'unavailable' ? 'Unavailable' : 'Not configured';

export default function BreedPage() {
  const navigate = useNavigate();
  const [file, setFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [status, setStatus] = useState({ disease: 'missing', breed: 'missing' });

  useEffect(() => {
    let isMounted = true;
    getModelsStatus()
      .then(({ data }) => {
        if (isMounted) {
          setStatus(data?.models || { disease: 'unavailable', breed: 'unavailable' });
        }
      })
      .catch(() => {
        if (isMounted) setStatus({ disease: 'unavailable', breed: 'unavailable' });
      });
    return () => {
      isMounted = false;
    };
  }, []);

  const handleSelect = (selectedFile) => {
    if (!selectedFile) return;
    if (!selectedFile.type.startsWith('image/')) {
      setError('Please select a valid image file.');
      return;
    }
    if (selectedFile.size > 10 * 1024 * 1024) {
      setError('Image must be less than 10 MB.');
      return;
    }

    if (previewUrl) URL.revokeObjectURL(previewUrl);
    setFile(selectedFile);
    setPreviewUrl(URL.createObjectURL(selectedFile));
    setError('');
  };

  const handleSubmit = async () => {
    if (!file) {
      setError('Please choose an image first.');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const formData = new FormData();
      formData.append('image', file);
      const { data } = await predictBreed(formData);
      navigate('/results', { state: { ...data, source: 'breed' } });
    } catch (err) {
      setError(err?.response?.data?.error || 'The breed model is unavailable right now.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <div className="rounded-xl bg-violet-100 p-3 text-violet-700">
          <BookHeart className="h-5 w-5" />
        </div>
        <div>
          <h1 className="text-3xl font-bold text-slate-900">Breed recognition</h1>
          <p className="text-slate-600">Predict the most likely breed supported by the trained model.</p>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-[1.1fr_0.9fr]">
        <UploadPanel
          title="Upload cattle image"
          description="Use a frontal, visible cattle photo for more consistent breed classification."
          accept="image/*"
          file={file}
          previewUrl={previewUrl}
          loading={loading}
          error={error}
          onFileSelect={handleSelect}
          onClear={() => {
            if (previewUrl) URL.revokeObjectURL(previewUrl);
            setFile(null);
            setPreviewUrl('');
            setError('');
          }}
        />

        <div className="card space-y-4">
          <h2 className="text-lg font-semibold text-slate-900">Model readiness</h2>
          <div className="space-y-3 text-sm">
            <div className="flex items-center justify-between rounded-xl bg-slate-50 px-3 py-2">
              <span className="text-slate-600">Disease model</span>
              <StatusBadge status={status.disease} label={statusLabel(status.disease)} />
            </div>
            <div className="flex items-center justify-between rounded-xl bg-slate-50 px-3 py-2">
              <span className="text-slate-600">Breed model</span>
              <StatusBadge status={status.breed} label={statusLabel(status.breed)} />
            </div>
          </div>

          <div className="rounded-xl border border-violet-200 bg-violet-50 p-3 text-sm text-violet-800">
            <div className="flex items-start gap-2">
              <ScanSearch className="mt-0.5 h-4 w-4" />
              <p>Breed prediction is only valid for supported classes in the trained dataset. Unsupported animals may not be recognized reliably.</p>
            </div>
          </div>

          <button
            type="button"
            onClick={handleSubmit}
            disabled={!file || loading}
            className="inline-flex w-full items-center justify-center gap-2 rounded-xl bg-violet-600 px-4 py-3 font-semibold text-white transition hover:bg-violet-700 disabled:cursor-not-allowed disabled:bg-slate-300"
          >
            {loading ? 'Processing...' : 'Identify breed'}
            {!loading && <CheckCircle2 className="h-4 w-4" />}
          </button>
        </div>
      </div>
    </div>
  );
}
