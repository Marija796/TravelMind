import { Link } from 'react-router-dom'
import { Compass, Heart } from 'lucide-react'
import { useTranslation } from 'react-i18next'

export default function Footer() {
  const { t } = useTranslation()

  const travelTypes = [
    { key: 'beach', label: t('travelType.beach') },
    { key: 'mountain', label: t('travelType.mountain') },
    { key: 'city', label: t('travelType.city') },
    { key: 'adventure', label: t('travelType.adventure') },
    { key: 'cultural', label: t('travelType.cultural') },
    { key: 'luxury', label: t('travelType.luxury') },
  ]

  return (
    <footer className="bg-white dark:bg-slate-900 border-t border-slate-100 dark:border-slate-800 mt-20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {/* Brand */}
          <div>
            <Link to="/" className="flex items-center gap-2.5 mb-3">
              <div className="w-8 h-8 bg-gradient-to-br from-primary-500 to-accent-500 rounded-xl flex items-center justify-center">
                <Compass className="w-4.5 h-4.5 text-white" />
              </div>
              <span className="text-lg font-bold text-slate-900 dark:text-white">
                Travel<span className="gradient-text">Mind</span>
              </span>
            </Link>
            <p className="text-sm text-slate-500 dark:text-slate-400 max-w-xs">
              {t('footer.tagline')}
            </p>
          </div>

          {/* Navigation */}
          <div>
            <h3 className="text-sm font-semibold text-slate-900 dark:text-white mb-3">{t('footer.exploreSection')}</h3>
            <ul className="space-y-2 text-sm text-slate-500 dark:text-slate-400">
              <li><Link to="/explore" className="hover:text-primary-600 transition-colors">{t('footer.allDestinations')}</Link></li>
              <li><Link to="/recommendations" className="hover:text-primary-600 transition-colors">{t('footer.personalizedPicks')}</Link></li>
              <li><Link to="/register" className="hover:text-primary-600 transition-colors">{t('footer.createAccount')}</Link></li>
            </ul>
          </div>

          {/* Travel Types */}
          <div>
            <h3 className="text-sm font-semibold text-slate-900 dark:text-white mb-3">{t('footer.travelTypesSection')}</h3>
            <ul className="space-y-2 text-sm text-slate-500 dark:text-slate-400">
              {travelTypes.map(({ key, label }) => (
                <li key={key}>
                  <Link to={`/explore?travel_type=${key}`} className="hover:text-primary-600 transition-colors">{label}</Link>
                </li>
              ))}
            </ul>
          </div>
        </div>

        <div className="mt-10 pt-6 border-t border-slate-100 dark:border-slate-800 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-slate-400">
          <p>© {new Date().getFullYear()} TravelMind. {t('footer.copyright')}</p>
          <p className="flex items-center gap-1">{t('footer.madeWith')} <Heart className="w-3 h-3 fill-rose-500 text-rose-500" /></p>
        </div>
      </div>
    </footer>
  )
}
