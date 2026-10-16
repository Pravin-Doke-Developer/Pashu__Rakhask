import { useEffect, useState } from 'react';
import { AlertTriangle, CheckCircle2, Stethoscope } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import UploadPanel from '../components/UploadPanel';
import StatusBadge from '../components/StatusBadge';
import { predictDisease, getModelsStatus } from '../services/api';

const statusLabel = (status) =>
  status === 'ready' ? 'Configured' : status === 'unavailable' ? 'Unavailable' : 'Not configured';

export default function DiseasePage() {
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
      setError('Please upload a valid image file.');
      return;
    }
    if (selectedFile.size > 10 * 1024 * 1024) {
      setError('Image must be smaller than 10 MB.');
      return;
    }

    if (previewUrl) URL.revokeObjectURL(previewUrl);
    setFile(selectedFile);
    setPreviewUrl(URL.createObjectURL(selectedFile));
    setError('');
  };

  const handleSubmit = async () => {
    if (!file) {
      setError('Please select an image before submitting.');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const formData = new FormData();
      formData.append('image', file);
      const { data } = await predictDisease(formData);
      navigate('/results', { state: { ...data, source: 'disease' } });
    } catch (err) {
      setError(err?.response?.data?.error || 'The disease model is unavailable right now.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <div className="rounded-xl bg-emerald-100 p-3 text-emerald-700">
          <Stethoscope className="h-5 w-5" />
        </div>
        <div>
          <h1 className="text-3xl font-bold text-slate-900">Disease screening</h1>
          <p className="text-slate-600">Upload a cattle photo for preliminary disease screening.</p>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-[1.1fr_0.9fr]">
        <UploadPanel
          title="Animal image upload"
          description="Use a clear, well-lit cattle photo for best results."
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
          <h2 className="text-lg font-semibold text-slate-900">Model status</h2>
          <div className="space-y-3 text-sm">
            <div className="flex items-center justify-between rounded-xl bg-slate-50 px-3 py-2">
              <span className="text-slate-600">Disease classifier</span>
              <StatusBadge status={status.disease} label={statusLabel(status.disease)} />
            </div>
            <div className="flex items-center justify-between rounded-xl bg-slate-50 px-3 py-2">
              <span className="text-slate-600">Breed classifier</span>
              <StatusBadge status={status.breed} label={statusLabel(status.breed)} />
            </div>
          </div>

          <div className="rounded-xl border border-amber-200 bg-amber-50 p-3 text-sm text-amber-800">
            <div className="flex items-start gap-2">
              <AlertTriangle className="mt-0.5 h-4 w-4" />
              <p>
                This tool provides a preliminary screening result and should not be treated as a confirmed diagnosis.
              </p>
            </div>
          </div>

          <button
            type="button"
            onClick={handleSubmit}
            disabled={!file || loading}
            className="inline-flex w-full items-center justify-center gap-2 rounded-xl bg-emerald-600 px-4 py-3 font-semibold text-white transition hover:bg-emerald-700 disabled:cursor-not-allowed disabled:bg-slate-300"
          >
            {loading ? 'Processing...' : 'Analyze image'}
            {!loading && <CheckCircle2 className="h-4 w-4" />}
          </button>
        </div>
      </div>
    </div>
  );
}
