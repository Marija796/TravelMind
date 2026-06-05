import { useTranslation } from 'react-i18next'

export default function LanguageSwitcher() {
  const { i18n } = useTranslation()
  const current = i18n.language?.startsWith('mk') ? 'mk' : 'en'

  return (
    <div className="flex items-center gap-0.5 bg-slate-100 dark:bg-slate-800 rounded-lg p-0.5">
      {(['en', 'mk'] as const).map((lang) => (
        <button
          key={lang}
          onClick={() => i18n.changeLanguage(lang)}
          className={`px-2 py-1 rounded-md text-xs font-semibold transition-all ${
            current === lang
              ? 'bg-white dark:bg-slate-700 text-slate-900 dark:text-white shadow-sm'
              : 'text-slate-500 dark:text-slate-400 hover:text-slate-700 dark:hover:text-slate-200'
          }`}
        >
          {lang === 'en' ? 'EN' : 'МК'}
        </button>
      ))}
    </div>
  )
}
