import React from 'react'
import { Sparkles } from 'lucide-react'

const Footer = () => {
  return (
    <footer className="mt-16 py-8 border-t border-gray-200 animate-fade-in">
      <div className="text-center">
        <div className="flex items-center justify-center mb-4">
          <Sparkles className="w-5 h-5 text-primary-500 mr-2 animate-pulse" />
          <span className="text-gray-600 font-medium">Face Analysis Studio</span>
          <Sparkles className="w-5 h-5 text-secondary-500 ml-2 animate-pulse" />
        </div>
        
        <div className="flex items-center justify-center space-x-6 text-sm text-gray-500">
          <span>AI-Powered Analysis</span>
          <span>•</span>
          <span>Emotion Detection</span>
          <span>•</span>
          <span>HD Video Generation</span>
        </div>
        
        <div className="mt-4 text-xs text-gray-400">
          Advanced face detection • Real-time emotion analysis • Cinematic audio generation
        </div>
      </div>
    </footer>
  )
}

export default Footer