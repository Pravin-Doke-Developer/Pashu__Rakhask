import { ShieldAlert, Sparkles } from 'lucide-react';

export default function AboutPage() {
  return (
    <div className="space-y-6">
      <div className="card">
        <div className="flex items-center gap-3">
          <div className="rounded-xl bg-emerald-100 p-3 text-emerald-700">
            <Sparkles className="h-5 w-5" />
          </div>
          <h1 className="text-3xl font-bold text-slate-900">About this project</h1>
        </div>

        <div className="mt-6 space-y-4 text-sm leading-7 text-slate-600">
          <p>
            This project is an AI-powered animal health screening and breed recognition dashboard designed for use by farmers, livestock managers, and agricultural teams.
          </p>
          <p>
            It uses image-based machine learning models trained on real datasets contained in the project workspace. While the app is built to support inference once the artifacts are configured, it intentionally reports when model files are missing instead of showing fake predictions.
          </p>
          <p>
            The disease prediction should be treated as a preliminary screening result only and is not a substitute for a professional veterinary diagnosis.
          </p>
        </div>
      </div>

      <div className="card border-amber-200 bg-amber-50">
        <div className="flex items-center gap-3 text-amber-900">
          <ShieldAlert className="h-5 w-5" />
          <h2 className="text-lg font-semibold">Clinical safety notice</h2>
        </div>
        <ul className="mt-4 space-y-2 text-sm text-amber-800">
          <li>• Never diagnose animals based solely on an image classification model.</li>
          <li>• If an animal appears sick, consult a licensed veterinarian as soon as possible.</li>
          <li>• Do not prescribe medication or treatments based on the model’s output alone.</li>
        </ul>
      </div>
    </div>
  );
}
