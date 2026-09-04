import React from 'react'
import { motion } from 'framer-motion'
import { useAuth } from '../contexts/AuthContext'
import { Button } from './ui/button'
import {
  CpuChipIcon,
  UserCircleIcon,
  CogIcon,
  ArrowRightOnRectangleIcon
} from '@heroicons/react/24/outline'

interface HeaderProps {
  onSettingsClick: () => void
}

export function Header({ onSettingsClick }: HeaderProps) {
  const { user, profile, signOut } = useAuth()

  return (
    <motion.header
      initial={{ y: -50, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      className="bg-ultron-dark/90 backdrop-blur-sm border-b border-ultron-red/30 px-6 py-4"
    >
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <motion.div
            whileHover={{ rotate: 360 }}
            transition={{ duration: 0.5 }}
            className="w-10 h-10 bg-gradient-ultron rounded-full flex items-center justify-center"
          >
            <CpuChipIcon className="w-6 h-6 text-white" />
          </motion.div>
          
          <div>
            <h1 className="text-xl font-orbitron font-bold bg-gradient-ultron bg-clip-text text-transparent">
              ULTRON AI
            </h1>
            <p className="text-xs text-gray-400">Advanced Neural Interface</p>
          </div>
        </div>

        <div className="flex items-center space-x-4">
          <div className="text-right">
            <p className="text-sm text-white font-medium">
              {profile?.full_name || user?.email}
            </p>
            <p className="text-xs text-gray-400 capitalize">
              {profile?.preferred_ai_provider || 'OpenAI'} Active
            </p>
          </div>
          
          <div className="flex items-center space-x-2">
            <Button
              variant="ghost"
              size="icon"
              onClick={onSettingsClick}
              className="text-gray-400 hover:text-ultron-blue"
            >
              <CogIcon className="w-5 h-5" />
            </Button>
            
            <Button
              variant="ghost"
              size="icon"
              onClick={signOut}
              className="text-gray-400 hover:text-ultron-red"
            >
              <ArrowRightOnRectangleIcon className="w-5 h-5" />
            </Button>
          </div>
          
          <div className="w-8 h-8 bg-gradient-ultron rounded-full flex items-center justify-center">
            <UserCircleIcon className="w-5 h-5 text-white" />
          </div>
        </div>
      </div>
    </motion.header>
  )
}