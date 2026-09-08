import React from 'react'

interface UltronLogoProps {
  size?: 'sm' | 'md' | 'lg' | 'xl'
  className?: string
  animated?: boolean
}

export const UltronLogo: React.FC<UltronLogoProps> = ({ 
  size = 'md', 
  className = '',
  animated = true 
}) => {
  const sizeClasses = {
    sm: 'w-8 h-8',
    md: 'w-12 h-12',
    lg: 'w-16 h-16',
    xl: 'w-24 h-24'
  }

  return (
    <div className={`relative ${sizeClasses[size]} ${className}`}>
      {/* Outer glow ring */}
      <div className={`absolute inset-0 rounded-full border-2 border-red-500 opacity-30 ${
        animated ? 'animate-ping' : ''
      }`} />
      
      {/* Main logo container */}
      <div className="relative w-full h-full flex items-center justify-center bg-gradient-to-br from-red-600 to-red-800 rounded-full shadow-lg glow-red">
        {/* Inner circuit pattern */}
        <div className="absolute inset-1 rounded-full bg-black opacity-20" />
        
        {/* The "U" letter */}
        <div className="relative z-10 font-orbitron font-black text-white text-glow-red" style={{
          fontSize: size === 'sm' ? '16px' : size === 'md' ? '20px' : size === 'lg' ? '24px' : '32px'
        }}>
          U
        </div>
        
        {/* Circuit lines */}
        <div className="absolute inset-0 rounded-full">
          <div className="absolute top-1 left-1/2 w-0.5 h-2 bg-red-400 transform -translate-x-1/2" />
          <div className="absolute bottom-1 left-1/2 w-0.5 h-2 bg-red-400 transform -translate-x-1/2" />
          <div className="absolute left-1 top-1/2 h-0.5 w-2 bg-red-400 transform -translate-y-1/2" />
          <div className="absolute right-1 top-1/2 h-0.5 w-2 bg-red-400 transform -translate-y-1/2" />
        </div>
      </div>
      
      {/* Scanning line effect */}
      {animated && (
        <div className="absolute inset-0 rounded-full overflow-hidden">
          <div className="scan-line w-full h-full" />
        </div>
      )}
    </div>
  )
}