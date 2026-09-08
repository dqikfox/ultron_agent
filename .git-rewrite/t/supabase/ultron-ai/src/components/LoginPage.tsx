import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { Button } from './ui/button'
import { Input } from './ui/input'
import { Card, CardContent, CardHeader, CardTitle } from './ui/card'
import { useAuth } from '../contexts/AuthContext'
import { ShieldCheckIcon, CpuChipIcon } from '@heroicons/react/24/outline'
import toast from 'react-hot-toast'

export function LoginPage() {
  const [isLogin, setIsLogin] = useState(true)
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [fullName, setFullName] = useState('')
  const [loading, setLoading] = useState(false)
  const { signIn, signUp } = useAuth()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!email || !password) {
      toast.error('Please fill in all fields')
      return
    }

    if (!isLogin && !fullName) {
      toast.error('Please enter your full name')
      return
    }

    setLoading(true)
    try {
      if (isLogin) {
        await signIn(email, password)
      } else {
        await signUp(email, password, fullName)
      }
    } catch (error) {
      // Error is handled in AuthContext
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-gradient-to-br from-ultron-dark via-ultron-darker to-black"></div>
      <div className="absolute inset-0 opacity-20">
        <div className="circuit-animation w-full h-full"></div>
      </div>
      
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="relative z-10"
      >
        <Card className="w-full max-w-md glass-morphism border-ultron-red/30">
          <CardHeader className="text-center space-y-4">
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.2, type: "spring" }}
              className="mx-auto w-16 h-16 bg-gradient-ultron rounded-full flex items-center justify-center"
            >
              <CpuChipIcon className="w-8 h-8 text-white" />
            </motion.div>
            
            <CardTitle className="text-2xl font-orbitron text-white">
              <span className="bg-gradient-ultron bg-clip-text text-transparent">
                ULTRON AI
              </span>
            </CardTitle>
            
            <p className="text-gray-400 text-sm">
              Advanced AI Interface System
            </p>
          </CardHeader>
          
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              {!isLogin && (
                <motion.div
                  initial={{ height: 0, opacity: 0 }}
                  animate={{ height: 'auto', opacity: 1 }}
                  exit={{ height: 0, opacity: 0 }}
                >
                  <Input
                    type="text"
                    placeholder="Full Name"
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                    className="bg-ultron-dark/50 border-ultron-blue/30 text-white placeholder:text-gray-400"
                  />
                </motion.div>
              )}
              
              <Input
                type="email"
                placeholder="Email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="bg-ultron-dark/50 border-ultron-blue/30 text-white placeholder:text-gray-400"
              />
              
              <Input
                type="password"
                placeholder="Password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="bg-ultron-dark/50 border-ultron-blue/30 text-white placeholder:text-gray-400"
              />
              
              <Button
                type="submit"
                variant="ultron"
                className="w-full font-orbitron"
                disabled={loading}
              >
                {loading ? (
                  <div className="flex items-center space-x-2">
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                    <span>{isLogin ? 'Signing In...' : 'Creating Account...'}</span>
                  </div>
                ) : (
                  <div className="flex items-center space-x-2">
                    <ShieldCheckIcon className="w-4 h-4" />
                    <span>{isLogin ? 'SIGN IN' : 'CREATE ACCOUNT'}</span>
                  </div>
                )}
              </Button>
            </form>
            
            <div className="mt-6 text-center">
              <button
                type="button"
                onClick={() => setIsLogin(!isLogin)}
                className="text-ultron-blue hover:text-ultron-red transition-colors text-sm"
              >
                {isLogin ? 'Need an account? Sign up' : 'Already have an account? Sign in'}
              </button>
            </div>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  )
}