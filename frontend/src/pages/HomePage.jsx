import {
  Activity,
  ArrowRight,
  ArrowUpRight,
  BookHeart,
  Check,
  CircleHelp,
  ShieldCheck,
  Stethoscope,
} from 'lucide-react';
import { Link } from 'react-router-dom';
import { useTranslation } from '../contexts/LanguageContext';

export default function HomePage() {
  const { t } = useTranslation();

  const cards = [
    {
      title: t.home.diseaseCard,
      description: t.home.diseaseDesc,
      link: '/disease',
      action: t.home.getStarted,
      icon: Stethoscope,
      tone: 'emerald',
    },
    {
      title: t.home.breedCard,
      description: t.home.breedDesc,
      link: '/breed',
      action: t.home.getStarted,
      icon: BookHeart,
      tone: 'amber',
    },
  ];
  return (
    <div className="space-y-9">
      <section className="relative isolate overflow-hidden rounded-[28px] bg-[#173b2b] text-white shadow-[0_24px_70px_-32px_rgba(17,57,39,0.6)]">
        <div className="absolute inset-0 -z-10 bg-[radial-gradient(ellipse_at_20%_0%,rgba(87,151,91,0.5),transparent_55%)]" />
        <div className="grid min-h-[390px] lg:grid-cols-[1.05fr_0.95fr]">
          <div className="relative z-10 flex flex-col items-start justify-center px-6 py-10 sm:px-10 sm:py-12 lg:px-12 lg:py-14">
            <span className="mb-5 inline-flex items-center gap-2 rounded-full border border-white/15 bg-white/10 px-3.5 py-1.5 text-[11px] font-semibold uppercase tracking-[0.17em] text-emerald-50">
              <span className="h-1.5 w-1.5 rounded-full bg-lime-300" />
              {t.home.smarterCare}
            </span>
            <h2 className="max-w-xl text-[2.5rem] font-semibold leading-[1.08] tracking-[-0.045em] sm:text-5xl">
              {t.home.title}
            </h2>
            <p className="mt-5 max-w-lg text-sm leading-7 text-emerald-50/80 sm:text-base">
              {t.home.subtitle}
            </p>
            <div className="mt-7 flex flex-wrap gap-3">
              <Link
                to="/disease"
                className="group inline-flex items-center gap-2 rounded-full bg-[#d9f27c] px-5 py-3 text-sm font-bold text-[#1d3821] transition hover:bg-white"
              >
                {t.home.screenAnimal}
                <ArrowRight className="h-4 w-4 transition group-hover:translate-x-0.5" />
              </Link>
              <Link
                to="/breed"
                className="inline-flex items-center gap-2 rounded-full border border-white/25 bg-white/5 px-5 py-3 text-sm font-semibold text-white transition hover:bg-white/10"
              >
                {t.home.exploreBreeds}
              </Link>
            </div>
            <div className="mt-8 flex items-center gap-2 text-xs text-emerald-50/75">
              <ShieldCheck className="h-4 w-4 text-lime-300" />
              {t.home.preliminaryInsights}
            </div>
          </div>

          <div className="relative min-h-[250px] overflow-hidden lg:min-h-full">
            <img
              src="/images/cattle-hero.jpg"
              alt="Holstein cow in a green pasture"
              className="absolute inset-0 h-full w-full object-cover object-center"
            />
            <div className="absolute inset-0 bg-gradient-to-t from-[#173b2b]/75 via-[#173b2b]/10 to-transparent lg:bg-gradient-to-r lg:from-[#173b2b] lg:via-[#173b2b]/20 lg:to-transparent" />
            <div className="absolute bottom-5 left-5 right-5 flex items-center justify-between rounded-2xl border border-white/20 bg-[#153629]/75 p-4 text-white shadow-xl backdrop-blur-md sm:bottom-7 sm:left-7 sm:right-7">
              <div>
                <p className="text-[10px] font-semibold uppercase tracking-[0.16em] text-emerald-100/75">
                  Thoughtful technology
                </p>
                <p className="mt-1 text-sm font-semibold">Made to support the people who care</p>
              </div>
              <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-lime-300 text-emerald-950">
                <Activity className="h-5 w-5" />
              </span>
            </div>
          </div>
        </div>
      </section>

      <section>
        <div className="mb-4 flex flex-wrap items-end justify-between gap-3">
          <div>
            <p className="text-[10px] font-bold uppercase tracking-[0.2em] text-emerald-700">{t.home.yourTools}</p>
            <h2 className="mt-1.5 text-2xl font-semibold tracking-tight text-slate-900">{t.home.howCanHelp}</h2>
          </div>
          <Link
            to="/history"
            className="inline-flex items-center gap-1.5 text-sm font-semibold text-slate-500 transition hover:text-emerald-800"
          >
            {t.home.viewHistory} <ArrowUpRight className="h-4 w-4" />
          </Link>
        </div>

        <div className="grid gap-4 md:grid-cols-2">
          {cards.map(({ title, description, link, action, icon: Icon, tone }) => {
            const isEmerald = tone === 'emerald';
            return (
              <Link
                key={title}
                to={link}
                className="group rounded-[22px] border border-[#e8eadf] bg-white p-5 shadow-[0_8px_28px_-22px_rgba(24,45,31,0.25)] transition duration-200 hover:-translate-y-1 hover:border-emerald-200 hover:shadow-[0_18px_42px_-26px_rgba(24,70,44,0.35)] sm:p-6"
              >
                <div className="flex items-start justify-between">
                  <span className={`flex h-12 w-12 items-center justify-center rounded-2xl ${isEmerald ? 'bg-emerald-50 text-emerald-800' : 'bg-amber-50 text-amber-800'}`}>
                    <Icon className="h-5 w-5" />
                  </span>
                  <span className="flex h-9 w-9 items-center justify-center rounded-full bg-slate-50 text-slate-400 transition group-hover:bg-emerald-700 group-hover:text-white">
                    <ArrowUpRight className="h-4 w-4" />
                  </span>
                </div>
                <h3 className="mt-5 text-lg font-semibold tracking-tight text-slate-900">{title}</h3>
                <p className="mt-2 max-w-md text-sm leading-6 text-slate-500">{description}</p>
                <span className="mt-5 inline-flex items-center gap-2 text-sm font-bold text-emerald-800">
                  {action} <ArrowRight className="h-4 w-4 transition group-hover:translate-x-1" />
                </span>
              </Link>
            );
          })}
        </div>
      </section>

      <section className="grid gap-4 md:grid-cols-[1.15fr_0.85fr]">
        <div className="rounded-[22px] border border-[#e8eadf] bg-white p-5 sm:p-6">
          <div className="flex items-center gap-3">
            <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-[#f0f5e6] text-emerald-800">
              <Check className="h-5 w-5" />
            </span>
            <div>
              <p className="text-sm font-semibold text-slate-900">{t.home.clearStep}</p>
              <p className="mt-0.5 text-xs text-slate-500">{t.home.transparent}</p>
            </div>
          </div>
          <div className="mt-5 grid gap-3 text-sm text-slate-600 sm:grid-cols-2">
            <p className="rounded-xl bg-[#f8f9f5] p-3 leading-6">
              {t.home.modelAvailability}
            </p>
            <p className="rounded-xl bg-[#f8f9f5] p-3 leading-6">
              {t.home.limitedPredictions}
            </p>
          </div>
        </div>

        <div className="flex gap-3 rounded-[22px] border border-amber-100 bg-[#fffaf0] p-5 sm:p-6">
          <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-amber-100 text-amber-800">
            <CircleHelp className="h-5 w-5" />
          </span>
          <div>
            <h3 className="text-sm font-semibold text-amber-950">{t.home.noteOnHealth}</h3>
            <p className="mt-2 text-sm leading-6 text-amber-900/75">
              {t.home.noteOnHealthDesc}
            </p>
          </div>
        </div>
      </section>
    </div>
  );
}
