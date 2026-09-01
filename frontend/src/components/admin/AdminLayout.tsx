import { Link, useLocation, useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { LayoutDashboard, Users, MapPin, Tags, Sparkles, ShieldCheck, LogOut } from 'lucide-react'
import { useAuth } from '@/hooks/useAuth'

// The Administrator interface's own layout - deliberately distinct from
// the public site's Navbar/Footer (which App.tsx suppresses entirely on
// /admin/* routes) rather than being the public chrome plus an extra tab
// strip, so the admin area reads as a dedicated application, not
// "user pages + a few admin buttons."
export default function AdminLayout({ children }: { children: React.ReactNode }) {
  const { t } = useTranslation()
  const location = useLocation()
  const navigate = useNavigate()
  const { user, logout } = useAuth()

  const links = [
    { to: '/admin', label: t('admin.nav.dashboard'), icon: <LayoutDashboard className="w-4 h-4" /> },
    { to: '/admin/users', label: t('admin.nav.users'), icon: <Users className="w-4 h-4" /> },
    { to: '/admin/destinations', label: t('admin.nav.destinations'), icon: <MapPin className="w-4 h-4" /> },
    { to: '/admin/taxonomy', label: t('admin.nav.taxonomy'), icon: <Tags className="w-4 h-4" /> },
    { to: '/admin/similar-users', label: t('admin.nav.similarUsers'), icon: <Sparkles className="w-4 h-4" /> },
  ]

  const handleLogout = () => {
    logout()
    navigate('/login', { state: { adminIntent: true } })
  }

  return (
    <div className="min-h-screen bg-slate-100 dark:bg-slate-950">
      <header className="sticky top-0 z-40 bg-slate-900 border-b border-slate-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <Link to="/admin" className="flex items-center gap-2.5">
              <div className="w-8 h-8 bg-primary-600/20 border border-primary-500/30 rounded-xl flex items-center justify-center">
                <ShieldCheck className="w-4.5 h-4.5 text-primary-400" />
              </div>
              <span className="text-base font-bold text-white tracking-tight">
                TravelMind <span className="text-primary-400">Admin</span>
              </span>
            </Link>

            <nav className="hidden md:flex items-center gap-1">
              {links.map((link) => (
                <Link
                  key={link.to}
                  to={link.to}
                  className={`flex items-center gap-1.5 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                    location.pathname === link.to
                      ? 'bg-slate-800 text-white'
                      : 'text-slate-400 hover:text-white hover:bg-slate-800/60'
                  }`}
                >
                  {link.icon}
                  {link.label}
                </Link>
              ))}
            </nav>

            <div className="flex items-center gap-3">
              <span className="hidden sm:inline text-sm text-slate-400">{user?.username}</span>
              <button
                onClick={handleLogout}
                className="flex items-center gap-1.5 px-3 py-2 rounded-lg text-sm font-medium text-slate-300 hover:text-white hover:bg-slate-800 transition-colors"
              >
                <LogOut className="w-4 h-4" />
                <span className="hidden sm:inline">{t('auth.signOut')}</span>
              </button>
            </div>
          </div>

          {/* Mobile nav strip */}
          <nav className="flex md:hidden items-center gap-1 pb-3 overflow-x-auto">
            {links.map((link) => (
              <Link
                key={link.to}
                to={link.to}
                className={`shrink-0 flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
                  location.pathname === link.to
                    ? 'bg-slate-800 text-white'
                    : 'text-slate-400 hover:text-white hover:bg-slate-800/60'
                }`}
              >
                {link.icon}
                {link.label}
              </Link>
            ))}
          </nav>
        </div>
      </header>

      <main>{children}</main>
    </div>
  )
}
