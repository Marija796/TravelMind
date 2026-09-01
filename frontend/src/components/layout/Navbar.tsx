import { useState, useEffect } from 'react'
import { Link, useNavigate, useLocation } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { Compass, Menu, X, User, LogOut, Sparkles, Map, Bookmark, CheckSquare, MessageSquare, ShieldCheck, History } from 'lucide-react'
import { useTranslation } from 'react-i18next'
import { useAuth } from '@/hooks/useAuth'
import ThemeToggle from '@/components/common/ThemeToggle'
import LanguageSwitcher from '@/components/common/LanguageSwitcher'
import Button from '@/components/ui/Button'

export default function Navbar() {
  const { isAuthenticated, user, logout } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const { t } = useTranslation()
  const [scrolled, setScrolled] = useState(false)
  const [menuOpen, setMenuOpen] = useState(false)

  useEffect(() => {
    const handler = () => setScrolled(window.scrollY > 20)
    window.addEventListener('scroll', handler)
    return () => window.removeEventListener('scroll', handler)
  }, [])

  useEffect(() => setMenuOpen(false), [location.pathname])

  const handleLogout = () => {
    logout()
    navigate('/')
  }

  // Every one of these routes requires an account (there is no guest/
  // anonymous access anywhere in the app), so none of them are shown until
  // the user is logged in - clicking one pre-login would otherwise just
  // dead-end at a login redirect.
  const navLinks = isAuthenticated
    ? [
        { to: '/explore', label: t('nav.explore'), icon: <Map className="w-4 h-4" /> },
        { to: '/recommendations', label: t('nav.forYou'), icon: <Sparkles className="w-4 h-4" /> },
        { to: '/app-reviews', label: t('nav.appReviews'), icon: <MessageSquare className="w-4 h-4" /> },
        ...(user?.role === 'admin'
          ? [{ to: '/admin', label: t('nav.admin'), icon: <ShieldCheck className="w-4 h-4" /> }]
          : []),
        { to: '/wishlist', label: t('nav.wishlist'), icon: <Bookmark className="w-4 h-4" /> },
        { to: '/visited', label: t('nav.visited'), icon: <CheckSquare className="w-4 h-4" /> },
        { to: '/activity', label: t('nav.activity'), icon: <History className="w-4 h-4" /> },
        { to: '/profile', label: user?.username || t('nav.profile'), icon: <User className="w-4 h-4" /> },
      ]
    : []

  return (
    <header
      className={`fixed top-0 left-0 right-0 z-40 transition-all duration-300 ${
        scrolled
          ? 'glass shadow-lg shadow-black/5'
          : 'bg-transparent'
      }`}
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-2.5 group">
            <div className="w-8 h-8 bg-gradient-to-br from-primary-500 to-accent-500 rounded-xl flex items-center justify-center shadow-sm group-hover:shadow-primary-500/30 transition-shadow">
              <Compass className="w-4.5 h-4.5 text-white" />
            </div>
            <span className="text-lg font-bold tracking-tight text-slate-900 dark:text-white">
              Travel<span className="gradient-text">Mind</span>
            </span>
          </Link>

          {/* Desktop Nav */}
          <nav className="hidden md:flex items-center gap-1">
            {navLinks.map((link) => (
              <Link
                key={link.to}
                to={link.to}
                className={`flex items-center gap-1.5 px-3 py-2 rounded-xl text-sm font-medium transition-colors ${
                  location.pathname === link.to
                    ? 'bg-primary-50 text-primary-700 dark:bg-primary-900/30 dark:text-primary-300'
                    : 'text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800'
                }`}
              >
                {link.icon}
                {link.label}
              </Link>
            ))}
          </nav>

          {/* Desktop Actions */}
          <div className="hidden md:flex items-center gap-2">
            <LanguageSwitcher />
            <ThemeToggle />
            {isAuthenticated ? (
              <Button variant="ghost" size="sm" leftIcon={<LogOut className="w-4 h-4" />} onClick={handleLogout}>
                {t('auth.signOut')}
              </Button>
            ) : (
              <>
                <Button variant="ghost" size="sm" onClick={() => navigate('/login')}>{t('auth.signIn')}</Button>
                <Button size="sm" onClick={() => navigate('/register')}>{t('nav.getStarted')}</Button>
              </>
            )}
          </div>

          {/* Mobile menu button */}
          <div className="flex md:hidden items-center gap-2">
            <LanguageSwitcher />
            <ThemeToggle />
            <button
              onClick={() => setMenuOpen(!menuOpen)}
              className="p-2 rounded-xl hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
            >
              {menuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Menu */}
      <AnimatePresence>
        {menuOpen && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="md:hidden glass border-t border-white/20 dark:border-slate-700/50"
          >
            <div className="max-w-7xl mx-auto px-4 py-4 flex flex-col gap-1">
              {navLinks.map((link) => (
                <Link
                  key={link.to}
                  to={link.to}
                  className="flex items-center gap-2 px-3 py-2.5 rounded-xl text-sm font-medium text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
                >
                  {link.icon}
                  {link.label}
                </Link>
              ))}
              <div className="pt-2 border-t border-slate-200 dark:border-slate-700 mt-1 flex flex-col gap-1">
                {isAuthenticated ? (
                  <button
                    onClick={handleLogout}
                    className="flex items-center gap-2 px-3 py-2.5 rounded-xl text-sm font-medium text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors"
                  >
                    <LogOut className="w-4 h-4" /> {t('auth.signOut')}
                  </button>
                ) : (
                  <>
                    <Link to="/login" className="px-3 py-2.5 rounded-xl text-sm font-medium text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors">{t('auth.signIn')}</Link>
                    <Link to="/register" className="px-3 py-2.5 rounded-xl text-sm font-medium bg-primary-600 text-white text-center">{t('nav.getStarted')}</Link>
                  </>
                )}
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </header>
  )
}
