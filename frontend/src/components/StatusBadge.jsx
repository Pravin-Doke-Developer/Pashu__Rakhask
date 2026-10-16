export default function StatusBadge({ status, label }) {
  const palette = {
    ready: 'bg-emerald-100 text-emerald-700 border-emerald-200',
    missing: 'bg-amber-100 text-amber-700 border-amber-200',
    unavailable: 'bg-red-100 text-red-700 border-red-200',
  };

  return (
    <span
      className={`inline-flex items-center rounded-full border px-2.5 py-1 text-xs font-semibold ${palette[status] || palette.unavailable}`}
    >
      {label}
    </span>
  );
}
