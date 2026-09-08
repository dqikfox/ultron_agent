import React from 'react'
import { AnimatePresence } from 'framer-motion'
import { Toaster } from 'react-hot-toast'
import { AuthProvider, useAuth } from './contexts/AuthContext'
import { LoginPage } from './components/LoginPage'
import { Dashboard } from './components/Dashboard'
import './index.css'

function AppContent() {
  const { user, loading } = useAuth()

  if (loading) {
    return (
      <div className="min-h-screen bg-ultron-darker flex items-center justify-center">
        <div className="text-center space-y-4">
          <div className="w-16 h-16 bg-gradient-ultron rounded-full flex items-center justify-center mx-auto animate-pulse">
            <span className="text-white text-xl font-orbitron">AI</span>
          </div>
          <div className="text-white font-orbitron">Initializing Ultron AI...</div>
          <div className="w-32 h-1 bg-ultron-dark rounded-full overflow-hidden mx-auto">
            <div className="w-full h-full bg-gradient-to-r from-ultron-red via-ultron-blue to-ultron-purple animate-pulse" />
          </div>
        </div>
      </div>
    )
  }

  return (
    <AnimatePresence mode="wait">
      {user ? (
        <Dashboard key="dashboard" />
      ) : (
        <LoginPage key="login" />
      )}
    </AnimatePresence>
  )
}

function App() {
  return (
    <AuthProvider>
      <AppContent />
      <Toaster
        position="top-right"
        toastOptions={{
          style: {
            background: '#1A1A2E',
            color: '#fff',
            border: '1px solid rgba(255, 0, 64, 0.3)',
          },
          success: {
            iconTheme: {
              primary: '#00BFFF',
              secondary: '#fff',
            },
          },
          error: {
            iconTheme: {
              primary: '#FF0040',
              secondary: '#fff',
            },
          },
        }}
      />
    </AuthProvider>
  )
}

export default App