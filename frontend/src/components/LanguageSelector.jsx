import { Globe } from 'lucide-react';
import { useTranslation } from '../contexts/LanguageContext';

export default function LanguageSelector() {
  const { language, changeLanguage, t } = useTranslation();

  return (
    <div className="flex items-center gap-2">
      <Globe className="h-4 w-4 text-slate-600" />
      <select
        value={language}
        onChange={(e) => changeLanguage(e.target.value)}
        className="rounded-lg border border-slate-200 bg-white px-2 py-1.5 text-sm font-medium text-slate-700 hover:border-slate-300 focus:border-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-500/20"
      >
        <option value="en">{t.language.english}</option>
        <option value="hi">{t.language.hindi}</option>
        <option value="mr">{t.language.marathi}</option>
      </select>
    </div>
  );
}
