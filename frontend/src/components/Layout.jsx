import { Link, NavLink, useLocation } from 'react-router-dom';
import {
  Activity,
  BookHeart,
  HeartPulse,
  Home,
  History,
  Landmark,
  ShieldAlert,
  Stethoscope,
} from 'lucide-react';

const navItems = [
  { to: '/', label: 'Overview', icon: Home, end: true },
  { to: '/disease', label: 'Disease screening', icon: Stethoscope },
  { to: '/breed', label: 'Breed recognition', icon: BookHeart },
  { to: '/history', label: 'History', icon: History },
  { to: '/schemes', label: 'Government schemes', icon: Landmark },
  { to: '/about', label: 'About', icon: ShieldAlert },
];

function Navigation({ mobile = false }) {
  return (
    <nav
      aria-label="Main navigation"
      className={
        mobile
          ? 'grid grid-cols-6 gap-1'
          : 'flex flex-col gap-1'
      }
    >
      {navItems.map(({ to, label, icon: Icon, end }) => (
        <NavLink
          key={to}
          to={to}
          end={end}
          className={({ isActive }) =>
            mobile
              ? `flex min-w-0 flex-col items-center gap-1 rounded-xl px-1 py-2 text-[10px] font-semibold transition ${
                  isActive ? 'text-emerald-700' : 'text-slate-500'
                }`
              : `flex items-center gap-3 rounded-xl px-3 py-3 text-sm font-medium transition ${
                  isActive
                    ? 'bg-emerald-50 text-emerald-800 shadow-sm'
                    : 'text-slate-500 hover:bg-slate-50 hover:text-slate-900'
                }`
          }
        >
          <Icon className={mobile ? 'h-5 w-5' : 'h-[18px] w-[18px]'} />
          <span className={mobile ? 'truncate' : ''}>{label}</span>
        </NavLink>
      ))}
    </nav>
  );
}

export default function Layout({ children }) {
  const { pathname } = useLocation();
  const currentPage = navItems.find(({ to }) => to === pathname)?.label || 'Analysis results';

  return (
    <div className="min-h-screen bg-[#f6f7f2] text-slate-800 lg:flex">
      <aside className="hidden w-[260px] shrink-0 flex-col border-r border-[#e8eadf] bg-white px-5 py-7 lg:flex">
        <Link to="/" className="mb-10 flex items-center gap-3 px-2">
          <span className="flex h-11 w-11 items-center justify-center rounded-2xl bg-emerald-700 text-white shadow-lg shadow-emerald-900/15">
            <Activity className="h-5 w-5" />
          </span>
          <span>
            <span className="block text-[15px] font-bold tracking-tight text-slate-900">PashuRakshak</span>
            <span className="mt-0.5 block text-[10px] font-semibold uppercase tracking-[0.18em] text-slate-400">
              Animal health AI
            </span>
          </span>
        </Link>

        <p className="mb-3 px-3 text-[10px] font-bold uppercase tracking-[0.2em] text-slate-400">
          Workspace
        </p>
        <Navigation />

        <div className="mt-auto overflow-hidden rounded-2xl bg-[#f1f5e9]">
          <img
            src="/images/cattle-hero.jpg"
            alt="Holstein cow standing in a green pasture"
            className="h-28 w-full object-cover object-center"
          />
          <div className="p-4">
            <div className="flex items-center gap-2 text-xs font-semibold text-emerald-900">
              <HeartPulse className="h-4 w-4" />
              Healthier herds, together
            </div>
            <p className="mt-2 text-xs leading-5 text-slate-500">
              Simple tools to support everyday livestock care.
            </p>
          </div>
        </div>
      </aside>

      <div className="min-w-0 flex-1">
        <header className="sticky top-0 z-20 border-b border-[#e8eadf] bg-white/90 px-4 py-3 backdrop-blur-xl sm:px-7 lg:px-10 lg:py-5">
          <div className="mx-auto flex max-w-[1440px] items-center justify-between">
            <Link to="/" className="flex items-center gap-2.5 lg:hidden">
              <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-emerald-700 text-white">
                <Activity className="h-[18px] w-[18px]" />
              </span>
              <span className="text-sm font-bold tracking-tight text-slate-900">Herdwell</span>
            </Link>
            <div className="hidden lg:block">
              <p className="text-[10px] font-bold uppercase tracking-[0.2em] text-emerald-700">
                Herd health workspace
              </p>
              <h1 className="mt-1 text-lg font-semibold tracking-tight text-slate-900">{currentPage}</h1>
            </div>
            <div className="ml-auto flex items-center gap-2 rounded-full border border-emerald-100 bg-emerald-50 px-3 py-1.5 text-xs font-semibold text-emerald-800">
              <span className="h-2 w-2 rounded-full bg-emerald-500" />
              AI screening tools
            </div>
          </div>
        </header>

        <main className="mx-auto max-w-[1440px] px-4 pb-28 pt-6 sm:px-7 sm:pt-8 lg:px-10 lg:pb-10 lg:pt-9">
          {children}
        </main>
      </div>

      <div className="fixed inset-x-0 bottom-0 z-30 border-t border-[#e8eadf] bg-white/95 px-2 pb-[env(safe-area-inset-bottom)] pt-1 backdrop-blur-xl lg:hidden">
        <Navigation mobile />
      </div>
    </div>
  );
}
