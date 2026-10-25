import { ArrowLeft, AlertTriangle, CheckCircle2, Info, ShieldAlert, Syringe, HeartPulse, Home, TrendingUp, Scale, DollarSign } from 'lucide-react';
import { Link, useLocation } from 'react-router-dom';

export default function ResultsPage() {
  const { state } = useLocation();
  const result = state || {};

  const isModelConfigured = result?.status === 'ok';
  const isDiseaseScreening = result?.model_type === 'disease' || result?.source === 'disease';

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium uppercase tracking-[0.2em] text-slate-500">
            {isDiseaseScreening ? 'Disease screening result' : 'Breed recognition result'}
          </p>
          <h1 className="mt-1 text-3xl font-bold text-slate-900">
            {isDiseaseScreening ? 'Preliminary screening outcome' : 'Analysis outcome'}
          </h1>
        </div>
        <Link to="/" className="inline-flex items-center gap-2 rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm font-medium text-slate-700 hover:bg-slate-100">
          <ArrowLeft className="h-4 w-4" />
          Back home
        </Link>
      </div>

      {!isModelConfigured ? (
        <div className="card border-amber-200 bg-amber-50">
          <div className="flex items-start gap-3 text-amber-900">
            <AlertTriangle className="mt-0.5 h-5 w-5" />
            <div>
              <h2 className="text-xl font-semibold">Model not configured</h2>
              <p className="mt-2 text-sm text-amber-800">
                The backend is running, but the required trained model artifacts have not been added yet. The app is intentionally not showing a fake prediction.
              </p>
            </div>
          </div>
        </div>
      ) : (
        <div className="grid gap-6 lg:grid-cols-[0.9fr_1.1fr]">
          <div className="card">
            <div className="mb-4 flex items-center gap-3">
              <div className="rounded-xl bg-emerald-100 p-3 text-emerald-700">
                <CheckCircle2 className="h-5 w-5" />
              </div>
              <div>
                <p className="text-sm text-slate-500">
                  {isDiseaseScreening ? 'Screening result' : 'Predicted breed'}
                </p>
                <h2 className="text-2xl font-semibold text-slate-900">
                  {result.information?.title || result.class_name || 'Unknown'}
                </h2>
              </div>
            </div>

            <div className="rounded-xl bg-slate-50 p-4">
              <div className="flex items-center justify-between">
                <span className="text-sm text-slate-600">Confidence</span>
                <span className="text-lg font-bold text-slate-900">{result.confidence || 0}%</span>
              </div>
              <div className="mt-3 h-2.5 rounded-full bg-slate-200">
                <div className="h-2.5 rounded-full bg-emerald-500" style={{ width: `${Math.min(result.confidence || 0, 100)}%` }} />
              </div>
            </div>
          </div>

          {result.information && (
            <>
              <div className="card space-y-4">
                <div className="flex items-center gap-3">
                  <div className="rounded-xl bg-sky-100 p-3 text-sky-700">
                    <Info className="h-5 w-5" />
                  </div>
                  <h2 className="text-lg font-semibold text-slate-900">
                    About {result.information.title || result.class_name}
                  </h2>
                </div>
                <p className="text-sm leading-6 text-slate-600">
                  {result.information.description}
                </p>
                {Array.isArray(result.information.details) && result.information.details.length > 0 && (
                  <ul className="list-disc space-y-2 pl-5 text-sm leading-6 text-slate-600">
                    {result.information.details.map((detail) => (
                      <li key={detail}>{detail}</li>
                    ))}
                  </ul>
                )}
              </div>

              {!isDiseaseScreening && result.information && (
                <div className="card space-y-4">
                  <div className="flex items-center gap-3">
                    <div className="rounded-xl bg-purple-100 p-3 text-purple-700">
                      <TrendingUp className="h-5 w-5" />
                    </div>
                    <h2 className="text-lg font-semibold text-slate-900">Breed Information</h2>
                  </div>
                  <div className="grid gap-4 md:grid-cols-3">
                    {result.information.market_demand && (
                      <div className="rounded-lg bg-slate-50 p-4">
                        <div className="flex items-center gap-2 text-sm font-medium text-slate-600">
                          <TrendingUp className="h-4 w-4" />
                          Market Demand
                        </div>
                        <p className="mt-1 text-sm font-semibold text-slate-900">{result.information.market_demand}</p>
                      </div>
                    )}
                    {result.information.general_weight && (
                      <div className="rounded-lg bg-slate-50 p-4">
                        <div className="flex items-center gap-2 text-sm font-medium text-slate-600">
                          <Scale className="h-4 w-4" />
                          General Weight
                        </div>
                        <p className="mt-1 text-sm font-semibold text-slate-900">{result.information.general_weight}</p>
                      </div>
                    )}
                    {result.information.market_price && (
                      <div className="rounded-lg bg-slate-50 p-4">
                        <div className="flex items-center gap-2 text-sm font-medium text-slate-600">
                          <DollarSign className="h-4 w-4" />
                          Market Price
                        </div>
                        <p className="mt-1 text-sm font-semibold text-slate-900">{result.information.market_price}</p>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {isDiseaseScreening && Array.isArray(result.information.symptoms) && result.information.symptoms.length > 0 && (
                <div className="card space-y-4">
                  <div className="flex items-center gap-3">
                    <div className="rounded-xl bg-red-100 p-3 text-red-700">
                      <HeartPulse className="h-5 w-5" />
                    </div>
                    <div>
                      <h2 className="text-lg font-semibold text-slate-900">Symptoms</h2>
                      <p className="text-xs text-slate-500">Common signs to watch for</p>
                    </div>
                  </div>
                  <div className="space-y-2">
                    {result.information.symptoms.map((symptom, index) => (
                      <div key={index} className="flex items-start gap-3 rounded-lg bg-slate-50 p-3">
                        <div className="mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-red-100 text-xs font-semibold text-red-700">
                          {index + 1}
                        </div>
                        <p className="text-sm leading-6 text-slate-700">{symptom}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {isDiseaseScreening && Array.isArray(result.information.home_care) && result.information.home_care.length > 0 && (
                <div className="card space-y-4">
                  <div className="flex items-center gap-3">
                    <div className="rounded-xl bg-green-100 p-3 text-green-700">
                      <Home className="h-5 w-5" />
                    </div>
                    <div>
                      <h2 className="text-lg font-semibold text-slate-900">Home Care Solutions</h2>
                      <p className="text-xs text-slate-500">Immediate care you can provide</p>
                    </div>
                  </div>
                  <div className="space-y-2">
                    {result.information.home_care.map((care, index) => (
                      <div key={index} className="flex items-start gap-3 rounded-lg bg-slate-50 p-3">
                        <div className="mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-green-100 text-xs font-semibold text-green-700">
                          {index + 1}
                        </div>
                        <p className="text-sm leading-6 text-slate-700">{care}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </>
          )}

          <div className="card space-y-4">
            <div className="flex items-center gap-3">
              <div className="rounded-xl bg-amber-100 p-3 text-amber-700">
                <ShieldAlert className="h-5 w-5" />
              </div>
              <h2 className="text-lg font-semibold text-slate-900">Important guidance</h2>
            </div>
            {isDiseaseScreening && (
              <p className="rounded-xl border border-amber-200 bg-amber-50 px-3 py-2 text-sm font-semibold text-amber-900">
                Screening only — this is not a confirmed veterinary diagnosis.
              </p>
            )}
            <p className="text-sm leading-6 text-slate-600">
              {result?.message || 'This result is a preliminary model-based screening output and should be confirmed by a qualified veterinarian.'}
            </p>
            <ul className="space-y-2 text-sm text-slate-600">
              <li>• A supported class prediction is not a confirmed medical diagnosis.</li>
              <li>• If the animal appears unwell, isolate it and consult a veterinarian promptly.</li>
              <li>• Always combine model output with visual inspection and professional expertise.</li>
            </ul>
          </div>
        </div>
      )}
    </div>
  );
}
