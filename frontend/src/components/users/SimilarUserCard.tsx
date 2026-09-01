import { useTranslation } from 'react-i18next'
import type { SimilarUser } from '@/types/user'

interface Props {
  user: SimilarUser
  subtitle?: string
}

export default function SimilarUserCard({ user, subtitle }: Props) {
  const { t } = useTranslation()
  const initials = user.username.slice(0, 2).toUpperCase()

  return (
    <div className="relative rounded-2xl overflow-hidden bg-white dark:bg-slate-800 border border-slate-100 dark:border-slate-700/50 shadow-sm card-hover p-5">
      <div className="absolute top-3 right-3 bg-primary-600 text-white text-xs font-bold px-2.5 py-1 rounded-full z-10">
        {t('similarUsers.match', { value: user.similarity })}
      </div>
      <div className="flex flex-col items-center text-center gap-3">
        {user.profile_image ? (
          <img src={user.profile_image} alt={user.username} className="w-16 h-16 rounded-full object-cover" />
        ) : (
          <div className="w-16 h-16 rounded-full bg-gradient-to-br from-primary-400 to-accent-400 flex items-center justify-center text-white text-xl font-bold">
            {initials}
          </div>
        )}
        <div>
          <h3 className="font-semibold text-slate-900 dark:text-white">{user.username}</h3>
          {user.gender && (
            <p className="text-xs text-slate-400 dark:text-slate-500 mt-0.5">
              {t(`gender.${user.gender}`)}
            </p>
          )}
        </div>
        {user.short_summary && (
          <p className="text-sm text-slate-500 dark:text-slate-400 line-clamp-2">{user.short_summary}</p>
        )}
        {subtitle && (
          <p className="text-xs font-medium text-primary-600 dark:text-primary-400">{subtitle}</p>
        )}
      </div>
    </div>
  )
}
