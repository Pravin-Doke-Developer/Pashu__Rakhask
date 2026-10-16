import { useMemo, useState } from 'react';
import {
  ArrowUpRight,
  Check,
  ExternalLink,
  Landmark,
  Search,
  ShieldCheck,
} from 'lucide-react';
import {
  governmentSchemeCategories,
  governmentSchemes,
} from '../data/governmentSchemes';

export default function GovernmentSchemesPage() {
  const [activeCategory, setActiveCategory] = useState('all');
  const [search, setSearch] = useState('');
  const categoryCount = new Set(governmentSchemes.map(({ category }) => category)).size;
  const query = search.trim().toLocaleLowerCase();

  const filteredSchemes = useMemo(
    () =>
      governmentSchemes.filter((scheme) => {
        const matchesCategory =
          activeCategory === 'all' || scheme.category === activeCategory;
        const searchableContent = [
          scheme.name,
          scheme.description,
          scheme.category,
          scheme.department,
          scheme.beneficiaries,
          scheme.supportType,
          ...scheme.keywords,
        ]
          .join(' ')
          .toLocaleLowerCase();
        return matchesCategory && (!query || searchableContent.includes(query));
      }),
    [activeCategory, query],
  );

  const hasActiveFilters = activeCategory !== 'all' || search.length > 0;

  const resetFilters = () => {
    setActiveCategory('all');
    setSearch('');
  };

  return (
    <div className="space-y-7">
      <section className="relative isolate overflow-hidden rounded-[28px] bg-[#173b2b] text-white shadow-[0_24px_70px_-32px_rgba(17,57,39,0.6)]">
        <img
          src="/images/cattle-hero.jpg"
          alt=""
          aria-hidden="true"
          className="absolute inset-0 -z-20 h-full w-full object-cover object-center opacity-35"
        />
        <div className="absolute inset-0 -z-10 bg-gradient-to-r from-[#173b2b] via-[#173b2b]/95 to-[#173b2b]/55" />
        <div className="max-w-3xl px-6 py-10 sm:px-10 sm:py-12 lg:px-12 lg:py-14">
          <span className="inline-flex items-center gap-2 rounded-full border border-white/15 bg-white/10 px-3.5 py-1.5 text-[11px] font-semibold uppercase tracking-[0.17em] text-emerald-50">
            <Landmark className="h-4 w-4" />
            Official schemes directory
          </span>
          <h2 className="mt-5 text-3xl font-semibold leading-tight tracking-tight sm:text-4xl">
            Government Schemes for Farmers
          </h2>
          <p className="mt-3 max-w-2xl text-sm leading-7 text-emerald-50/85 sm:text-base">
            Discover official government support for livestock, dairy farming, and animal
            healthcare.
          </p>
          <div className="mt-7 flex flex-wrap gap-3">
            <div className="min-w-36 rounded-2xl border border-white/15 bg-white/10 px-4 py-3 backdrop-blur">
              <p className="text-2xl font-semibold">{governmentSchemes.length}</p>
              <p className="mt-1 text-xs text-emerald-50/75">Listed schemes and catalogues</p>
            </div>
            <div className="min-w-36 rounded-2xl border border-white/15 bg-white/10 px-4 py-3 backdrop-blur">
              <p className="text-2xl font-semibold">{categoryCount}</p>
              <p className="mt-1 text-xs text-emerald-50/75">Support categories</p>
            </div>
          </div>
        </div>
      </section>

      <div className="flex items-start gap-3 rounded-2xl border border-emerald-100 bg-emerald-50 px-4 py-3 text-sm leading-6 text-emerald-950">
        <ShieldCheck className="mt-1 h-5 w-5 shrink-0 text-emerald-700" />
        <p>
          This directory shares general information and links to official government websites.
          Check each official source for current guidelines, eligibility, and application
          availability. Herdwell is not a government portal and does not process applications.
        </p>
      </div>

      <section className="space-y-5" aria-label="Browse government schemes">
        <div className="flex flex-col gap-4">
          <div className="relative max-w-xl">
            <Search className="pointer-events-none absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
            <input
              type="search"
              value={search}
              onChange={(event) => setSearch(event.target.value)}
              placeholder="Search schemes, support, or keywords"
              aria-label="Search schemes"
              className="w-full rounded-xl border border-slate-200 bg-white py-3 pl-10 pr-4 text-sm text-slate-800 shadow-sm outline-none transition placeholder:text-slate-400 focus:border-emerald-500 focus:ring-4 focus:ring-emerald-100"
            />
          </div>

          <div className="flex flex-wrap items-center gap-2" role="group" aria-label="Filter by category">
            {governmentSchemeCategories.map(({ id, label }) => (
              <button
                key={id}
                type="button"
                onClick={() => setActiveCategory(id)}
                aria-pressed={activeCategory === id}
                className={`rounded-full px-4 py-2 text-sm font-semibold transition ${
                  activeCategory === id
                    ? 'bg-emerald-800 text-white shadow-sm'
                    : 'border border-slate-200 bg-white text-slate-600 hover:border-emerald-200 hover:text-emerald-800'
                }`}
              >
                {label}
              </button>
            ))}
            {hasActiveFilters && (
              <button
                type="button"
                onClick={resetFilters}
                className="inline-flex items-center gap-1.5 rounded-full px-3 py-2 text-sm font-semibold text-slate-500 hover:text-slate-900"
              >
                <Check className="h-4 w-4" />
                Reset
              </button>
            )}
          </div>
        </div>

        <p className="text-sm text-slate-500" aria-live="polite">
          Showing {filteredSchemes.length} of {governmentSchemes.length} listings
        </p>

        {filteredSchemes.length === 0 ? (
          <div className="rounded-2xl border border-dashed border-slate-300 bg-white px-5 py-12 text-center">
            <Search className="mx-auto h-7 w-7 text-slate-400" />
            <h3 className="mt-3 text-lg font-semibold text-slate-900">No schemes found</h3>
            <p className="mt-1 text-sm text-slate-500">
              Try a different search or reset the filters to see all listings.
            </p>
            <button
              type="button"
              onClick={resetFilters}
              className="mt-4 rounded-full bg-emerald-800 px-4 py-2 text-sm font-semibold text-white hover:bg-emerald-900"
            >
              Reset filters
            </button>
          </div>
        ) : (
          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
            {filteredSchemes.map((scheme) => {
              const categoryLabel =
                governmentSchemeCategories.find(({ id }) => id === scheme.category)?.label;
              return (
                <article
                  key={scheme.id}
                  className="flex h-full flex-col rounded-2xl border border-[#e8eadf] bg-white p-5 shadow-[0_8px_28px_-22px_rgba(24,45,31,0.3)] transition hover:-translate-y-0.5 hover:shadow-soft"
                >
                  <div className="flex flex-wrap gap-2">
                    <span className="rounded-full bg-emerald-50 px-3 py-1 text-xs font-semibold text-emerald-800">
                      {categoryLabel}
                    </span>
                    <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-600">
                      {scheme.governmentLevel}
                    </span>
                  </div>

                  <h3 className="mt-4 text-lg font-semibold leading-6 text-slate-900">
                    {scheme.name}
                  </h3>
                  <p className="mt-2 text-sm leading-6 text-slate-600">
                    {scheme.description}
                  </p>

                  <dl className="mt-4 space-y-3 border-t border-slate-100 pt-4 text-sm">
                    <div>
                      <dt className="font-semibold text-slate-800">Department</dt>
                      <dd className="mt-0.5 leading-5 text-slate-500">{scheme.department}</dd>
                    </div>
                    <div>
                      <dt className="font-semibold text-slate-800">Who it may benefit</dt>
                      <dd className="mt-0.5 leading-5 text-slate-500">{scheme.beneficiaries}</dd>
                    </div>
                    <div>
                      <dt className="font-semibold text-slate-800">Type of support</dt>
                      <dd className="mt-0.5 leading-5 text-slate-500">{scheme.supportType}</dd>
                    </div>
                  </dl>

                  <p className="mt-4 rounded-xl bg-amber-50 px-3 py-2 text-xs leading-5 text-amber-900">
                    {scheme.eligibilityNote}
                  </p>

                  <div className="mt-auto pt-4">
                    <p className="mb-3 text-xs text-slate-500">
                      Official source: {scheme.department}
                    </p>
                    <a
                      href={scheme.officialUrl}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex w-full items-center justify-center gap-2 rounded-xl bg-emerald-800 px-4 py-3 text-sm font-semibold text-white transition hover:bg-emerald-900 focus:outline-none focus:ring-4 focus:ring-emerald-200"
                    >
                      View Official Scheme
                      <ExternalLink className="h-4 w-4" />
                      <span className="sr-only">(opens in a new tab)</span>
                    </a>
                    <a
                      href={scheme.sourceUrl}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="mt-2 inline-flex items-center gap-1 text-xs font-medium text-slate-500 hover:text-emerald-800"
                    >
                      Source details <ArrowUpRight className="h-3.5 w-3.5" />
                    </a>
                  </div>
                </article>
              );
            })}
          </div>
        )}
      </section>
    </div>
  );
}
