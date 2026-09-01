import { Component } from 'react'
import type { ErrorInfo, ReactNode } from 'react'
import { AlertTriangle } from 'lucide-react'
import Button from '@/components/ui/Button'
// Class components (required for React error boundaries - there is no hook
// equivalent) can't use useTranslation(), so this imports the i18next
// singleton directly and calls .t() on it - i18next keeps a module-level
// instance independent of React context, so this works without hooks.
import i18n from '@/i18n'

interface Props { children: ReactNode }
interface State { hasError: boolean; message: string }

export default class ErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false, message: '' }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, message: error.message }
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    console.error('ErrorBoundary caught:', error, info)
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-[60vh] flex flex-col items-center justify-center gap-4 text-center p-8">
          <AlertTriangle className="w-12 h-12 text-red-500" />
          <h2 className="text-xl font-semibold text-slate-900 dark:text-white">{i18n.t('common.somethingWentWrong')}</h2>
          <p className="text-sm text-slate-500 max-w-md">{this.state.message}</p>
          <Button onClick={() => this.setState({ hasError: false, message: '' })}>{i18n.t('common.tryAgain')}</Button>
        </div>
      )
    }
    return this.props.children
  }
}
