import React from 'react'

type Props = { children: React.ReactNode }
type State = { hasError: boolean; error?: any }

export class ErrorBoundary extends React.Component<Props, State> {
  constructor(props: Props) {
    super(props)
    this.state = { hasError: false }
  }

  static getDerivedStateFromError(error: any) {
    return { hasError: true, error }
  }

  componentDidCatch(error: any) {
    console.error('Frontend runtime error:', error)
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{ padding: 24, color: '#b00020', fontFamily: 'system-ui, sans-serif' }}>
          <h2>Une erreur est survenue dans l'interface React</h2>
          <pre style={{ whiteSpace: 'pre-wrap' }}>{String(this.state.error)}</pre>
        </div>
      )
    }
    return this.props.children
  }
}


