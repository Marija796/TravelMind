import { Link } from 'react-router-dom'
import { Compass } from 'lucide-react'
import { useTranslation } from 'react-i18next'
import Button from '@/components/ui/Button'

export default function NotFound() {
  const { t } = useTranslation()
  return (
    <div className="min-h-[80vh] flex flex-col items-center justify-center text-center px-4 gap-6">
      <div className="w-20 h-20 bg-gradient-to-br from-primary-100 to-accent-100 dark:from-primary-900/40 dark:to-accent-900/40 rounded-3xl flex items-center justify-center">
        <Compass className="w-10 h-10 text-primary-600 dark:text-primary-400" />
      </div>
      <div>
        <h1 className="text-8xl font-bold gradient-text mb-2">404</h1>
        <h2 className="text-2xl font-semibold text-slate-900 dark:text-white mb-3">{t('notFound.title')}</h2>
        <p className="text-slate-500 dark:text-slate-400 max-w-sm">{t('notFound.subtitle')}</p>
      </div>
      <div className="flex gap-3">
        <Link to="/"><Button>{t('notFound.goHome')}</Button></Link>
        <Link to="/explore"><Button variant="secondary">{t('notFound.explore')}</Button></Link>
      </div>
    </div>
  )
}
