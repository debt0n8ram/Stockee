import React, { Component, ReactNode } from 'react';

interface Props {
    children: ReactNode;
    fallback?: ReactNode;
}

interface State {
    hasError: boolean;
    error?: Error;
    errorInfo?: any;
}

export class ErrorBoundary extends Component<Props, State> {
    constructor(props: Props) {
        super(props);
        this.state = { hasError: false };
    }

    static getDerivedStateFromError(error: Error): State {
        return { hasError: true, error };
    }

  componentDidCatch(error: Error, errorInfo: any) {
    console.error('ErrorBoundary caught an error:', error, errorInfo);
    
    // Log the exact error details
    if (error.message.includes('Objects are not valid as a React child')) {
      console.error('🚨 OBJECT RENDERING ERROR CAUGHT:', {
        error: error.message,
        stack: error.stack,
        componentStack: errorInfo.componentStack,
        timestamp: new Date().toISOString()
      });
      
      // Try to extract more details about the problematic object
      const stackLines = error.stack?.split('\n') || [];
      console.error('🚨 ERROR STACK TRACE:', stackLines);
      
      // Log component stack for debugging
      if (errorInfo.componentStack) {
        console.error('🚨 COMPONENT STACK:', errorInfo.componentStack);
      }
    }
    
    this.setState({ error, errorInfo });
  }

    render() {
        if (this.state.hasError) {
            return this.props.fallback || (
                <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
                    <h2 className="text-lg font-semibold text-red-800 mb-2">
                        Something went wrong
                    </h2>
                    <details className="text-sm text-red-700">
                        <summary className="cursor-pointer mb-2">Error Details</summary>
                        <pre className="whitespace-pre-wrap bg-red-100 p-2 rounded">
                            {this.state.error?.message}
                        </pre>
                        {this.state.errorInfo?.componentStack && (
                            <pre className="whitespace-pre-wrap bg-red-100 p-2 rounded mt-2">
                                Component Stack:
                                {this.state.errorInfo.componentStack}
                            </pre>
                        )}
                    </details>
                    <button
                        onClick={() => this.setState({ hasError: false })}
                        className="mt-2 px-3 py-1 bg-red-600 text-white rounded hover:bg-red-700"
                    >
                        Try Again
                    </button>
                </div>
            );
        }

        return this.props.children;
    }
}
