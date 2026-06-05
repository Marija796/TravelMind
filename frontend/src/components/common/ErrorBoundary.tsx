import { Component } from 'react'
import type { ErrorInfo, ReactNode } from 'react'
import { AlertTriangle } from 'lucide-react'
import Button from '@/components/ui/Button'

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
          <h2 className="text-xl font-semibold text-slate-900 dark:text-white">Something went wrong</h2>
          <p className="text-sm text-slate-500 max-w-md">{this.state.message}</p>
          <Button onClick={() => this.setState({ hasError: false, message: '' })}>Try Again</Button>
        </div>
      )
    }
    return this.props.children
  }
}
