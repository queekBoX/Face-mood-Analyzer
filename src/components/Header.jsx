import React from 'react'
import { Brain, Sparkles } from 'lucide-react'

const Header = () => {
  return (
    <header className="text-center mb-12 animate-fade-in">
      <div className="flex items-center justify-center mb-6">
        <div className="relative">
          <Brain className="w-16 h-16 text-primary-600 mr-4" />
          <Sparkles className="w-6 h-6 text-secondary-500 absolute -top-2 -right-2 animate-pulse" />
        </div>
      </div>
      
      <h1 className="text-5xl font-bold gradient-text mb-4">
        Face Analysis Studio
      </h1>
      
      <p className="text-xl text-gray-600 max-w-2xl mx-auto leading-relaxed">
        Advanced AI-powered face detection and emotion analysis with beautiful video generation
      </p>
      
      <div className="flex items-center justify-center mt-6 space-x-6 text-sm text-gray-500">
        <div className="flex items-center">
          <div className="w-2 h-2 bg-green-500 rounded-full mr-2 animate-pulse"></div>
          AI-Powered Detection
        </div>
        <div className="flex items-center">
          <div className="w-2 h-2 bg-blue-500 rounded-full mr-2 animate-pulse"></div>
          Real-time Analysis
        </div>
        <div className="flex items-center">
          <div className="w-2 h-2 bg-purple-500 rounded-full mr-2 animate-pulse"></div>
          HD Video Generation
        </div>
      </div>
    </header>
  )
}

export default Header