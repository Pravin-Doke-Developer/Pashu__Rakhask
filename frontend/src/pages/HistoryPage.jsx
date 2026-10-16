import { useEffect, useState } from 'react';
import { AlertCircle, History as HistoryIcon, RefreshCw } from 'lucide-react';
import { Link } from 'react-router-dom';
import { getPredictionHistory } from '../services/api';

const formatTimestamp = (timestamp) => {
  const date = new Date(timestamp);
  if (Number.isNaN(date.getTime())) return 'Date unavailable';
  return new Intl.DateTimeFormat(undefined, {
    dateStyle: 'medium',
    timeStyle: 'short',
  }).format(date);
};

const formatConfidence = (confidence) => {
  const value = Number(confidence);
  const percentage = value > 0 && value <= 1 ? value * 100 : value;
  return `${percentage.toFixed(2)}%`;
};

export default function HistoryPage() {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [refreshKey, setRefreshKey] = useState(0);

  useEffect(() => {
    let isMounted = true;

    const loadHistory = async () => {
      setLoading(true);
      setError('');
      try {
        const { data } = await getPredictionHistory();
        if (data?.status !== 'ok' || !Array.isArray(data.history)) {
          throw new Error('The history service returned an invalid response.');
        }
        if (isMounted) {
          setHistory(
            [...data.history].sort(
              (first, second) => {
                const firstTimestamp = new Date(first.timestamp).getTime();
                const secondTimestamp = new Date(second.timestamp).getTime();
                return (
                  (Number.isFinite(secondTimestamp) ? secondTimestamp : 0) -
                  (Number.isFinite(firstTimestamp) ? firstTimestamp : 0)
                );
              },
            ),
          );
        }
      } catch (err) {
        if (isMounted) {
          setError(
            err?.response?.data?.error ||
              err?.message ||
              'Unable to load prediction history. Please try again.',
          );
        }
      } finally {
        if (isMounted) setLoading(false);
      }
    };

    loadHistory();
    return () => {
      isMounted = false;
    };
  }, [refreshKey]);

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="rounded-xl bg-sky-100 p-3 text-sky-700">
            <HistoryIcon className="h-5 w-5" />
          </div>
          <div>
            <h1 className="text-3xl font-bold text-slate-900">Prediction history</h1>
            <p className="text-slate-600">Review your saved breed and disease predictions.</p>
          </div>
        </div>
        <button
          type="button"
          onClick={() => setRefreshKey((key) => key + 1)}
          disabled={loading}
          className="inline-flex items-center gap-2 rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm font-semibold text-slate-700 transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-60"
        >
          <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
          Refresh
        </button>
      </div>

      <section className="card" aria-live="polite">
        {loading ? (
          <p className="py-8 text-center text-sm text-slate-500">
            Loading saved predictions...
          </p>
        ) : error ? (
          <div className="flex flex-col items-center gap-3 py-8 text-center">
            <AlertCircle className="h-7 w-7 text-rose-600" />
            <div>
              <h2 className="font-semibold text-slate-900">History could not be loaded</h2>
              <p className="mt-1 text-sm text-slate-600">{error}</p>
            </div>
            <button
              type="button"
              onClick={() => setRefreshKey((key) => key + 1)}
              className="rounded-xl bg-emerald-800 px-4 py-2 text-sm font-semibold text-white hover:bg-emerald-900"
            >
              Try again
            </button>
          </div>
        ) : history.length === 0 ? (
          <div className="py-8 text-center">
            <HistoryIcon className="mx-auto h-7 w-7 text-slate-400" />
            <h2 className="mt-3 font-semibold text-slate-900">No predictions saved yet</h2>
            <p className="mt-1 text-sm text-slate-500">
              Completed predictions will appear here.
            </p>
            <div className="mt-4 flex justify-center gap-3">
              <Link
                to="/disease"
                className="rounded-xl bg-emerald-800 px-4 py-2 text-sm font-semibold text-white hover:bg-emerald-900"
              >
                Screen an animal
              </Link>
              <Link
                to="/breed"
                className="rounded-xl border border-slate-200 px-4 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-50"
              >
                Identify a breed
              </Link>
            </div>
          </div>
        ) : (
          <div className="space-y-3">
            {history.map((entry, index) => {
              const isDisease = entry.model_type === 'disease';
              const predictionType = isDisease ? 'Disease screening' : 'Breed recognition';
              return (
                <article
                  key={`${entry.timestamp || 'prediction'}-${entry.model_type}-${index}`}
                  className="flex flex-col gap-3 rounded-xl border border-slate-200 p-4 sm:flex-row sm:items-center sm:justify-between"
                >
                  <div className="min-w-0">
                    <div className="flex flex-wrap items-center gap-2">
                      <p className="font-semibold text-slate-900">{predictionType}</p>
                      <span
                        className={`rounded-full px-2.5 py-1 text-xs font-semibold ${
                          isDisease
                            ? 'bg-amber-50 text-amber-800'
                            : 'bg-violet-50 text-violet-800'
                        }`}
                      >
                        {entry.class_name || 'Unknown'}
                      </span>
                    </div>
                    <p className="mt-1 break-all text-sm text-slate-500">
                      {entry.filename || 'Image filename unavailable'}
                    </p>
                    <time
                      className="mt-1 block text-xs text-slate-400"
                      dateTime={entry.timestamp || undefined}
                    >
                      {formatTimestamp(entry.timestamp)}
                    </time>
                  </div>
                  {Number.isFinite(Number(entry.confidence)) && (
                    <div className="shrink-0 rounded-xl bg-slate-50 px-3 py-2 text-sm">
                      <span className="text-slate-500">Confidence </span>
                      <span className="font-semibold text-slate-800">
                        {formatConfidence(entry.confidence)}
                      </span>
                    </div>
                  )}
                </article>
              );
            })}
          </div>
        )}
      </section>
    </div>
  );
}
