import React from 'react'
import { Music, Palette, Heart, Zap, Sparkles, AlertTriangle, Minus } from 'lucide-react'

const EmotionDisplay = ({ emotionData }) => {
  if (!emotionData) return null

  const getEmotionIcon = (emotion) => {
    const icons = {
      happy: <Heart className="w-5 h-5" />,
      sad: <Minus className="w-5 h-5" />,
      angry: <Zap className="w-5 h-5" />,
      fear: <AlertTriangle className="w-5 h-5" />,
      surprise: <Sparkles className="w-5 h-5" />,
      disgust: <AlertTriangle className="w-5 h-5" />,
      neutral: <Minus className="w-5 h-5" />
    }
    return icons[emotion] || <Minus className="w-5 h-5" />
  }

  const getEmotionColor = (emotion) => {
    const colors = {
      happy: 'text-green-600 bg-green-100',
      sad: 'text-blue-600 bg-blue-100',
      angry: 'text-red-600 bg-red-100',
      fear: 'text-purple-600 bg-purple-100',
      surprise: 'text-yellow-600 bg-yellow-100',
      disgust: 'text-orange-600 bg-orange-100',
      neutral: 'text-gray-600 bg-gray-100'
    }
    return colors[emotion] || 'text-gray-600 bg-gray-100'
  }

  const totalPhotos = Object.values(emotionData.emotion_counts).reduce((sum, count) => sum + count, 0)

  return (
    <div className="bg-white rounded-xl shadow-lg p-6 animate-fade-in">
      <div className="flex items-center mb-4">
        <Music className="w-6 h-6 text-primary-600 mr-3" />
        <h3 className="text-xl font-bold text-gray-800">Emotion Analysis & Soundtrack</h3>
      </div>

      {/* Dominant Emotion */}
      <div className="mb-6 p-4 rounded-xl" style={{ backgroundColor: emotionData.theme_info.color + '20' }}>
        <div className="flex items-center justify-center mb-3">
          <span className="text-3xl mr-3">{emotionData.theme_info.icon}</span>
          <div className="text-center">
            <h4 className="text-lg font-bold" style={{ color: emotionData.theme_info.color }}>
              {emotionData.theme_info.name}
            </h4>
            <p className="text-sm text-gray-600 capitalize">
              Dominant Emotion: {emotionData.dominant_emotion}
            </p>
          </div>
        </div>
        <p className="text-sm text-gray-700 text-center">
          {emotionData.theme_info.description}
        </p>
      </div>

      {/* Emotion Breakdown */}
      <div className="space-y-3">
        <h5 className="font-semibold text-gray-800 text-sm">Emotion Distribution:</h5>
        {Object.entries(emotionData.emotion_counts)
          .filter(([_, count]) => count > 0)
          .sort(([,a], [,b]) => b - a)
          .map(([emotion, count]) => {
            const percentage = totalPhotos > 0 ? Math.round((count / totalPhotos) * 100) : 0
            return (
              <div key={emotion} className="flex items-center justify-between">
                <div className="flex items-center">
                  <div className={`p-2 rounded-lg mr-3 ${getEmotionColor(emotion)}`}>
                    {getEmotionIcon(emotion)}
                  </div>
                  <span className="capitalize font-medium text-gray-700">{emotion}</span>
                </div>
                <div className="flex items-center">
                  <div className="w-20 bg-gray-200 rounded-full h-2 mr-3">
                    <div 
                      className="h-2 rounded-full transition-all duration-500"
                      style={{ 
                        width: `${percentage}%`,
                        backgroundColor: emotionData.theme_info.color 
                      }}
                    />
                  </div>
                  <span className="text-sm font-semibold text-gray-600 w-12 text-right">
                    {count} ({percentage}%)
                  </span>
                </div>
              </div>
            )
          })}
      </div>

      {/* Audio Info */}
      <div className="mt-6 pt-4 border-t border-gray-200">
        <div className="flex items-center justify-center space-x-4 text-sm text-gray-600">
          <div className="flex items-center">
            <Palette className="w-4 h-4 mr-1" />
            Cinematic Score
          </div>
          <span>•</span>
          <div className="flex items-center">
            <Music className="w-4 h-4 mr-1" />
            HD Audio
          </div>
          <span>•</span>
          <div>
            {totalPhotos} Photos Analyzed
          </div>
        </div>
      </div>
    </div>
  )
}

export default EmotionDisplay