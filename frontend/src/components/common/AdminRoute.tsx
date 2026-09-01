import { useEffect } from 'react'
import { Navigate, useLocation } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import toast from 'react-hot-toast'
import { useAuth } from '@/hooks/useAuth'

interface Props {
  children: React.ReactNode
}

export default function AdminRoute({ children }: Props) {
  const { isAuthenticated, isLoading, user } = useAuth()
  const location = useLocation()
  const { t } = useTranslation()

  const denied = !isLoading && isAuthenticated && user?.role !== 'admin'

  // toast() triggers a state update in react-hot-toast's own Toaster
  // component - calling it directly in the render body (rather than an
  // effect) updates that component while this one is still rendering,
  // which React flags with "Cannot update a component while rendering a
  // different component" and can fire repeatedly on re-renders.
  useEffect(() => {
    if (denied) toast.error(t('admin.accessDenied'))
  }, [denied, t])

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="w-8 h-8 border-4 border-primary-500 border-t-transparent rounded-full animate-spin" />
      </div>
    )
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location, adminIntent: true }} replace />
  }

  if (denied) {
    return <Navigate to="/" replace />
  }

  return <>{children}</>
}
