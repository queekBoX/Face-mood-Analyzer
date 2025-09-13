import React, { useState, useRef, useEffect } from 'react'
import { Play, Pause, Download, Volume2, VolumeX, Maximize2 } from 'lucide-react'
import toast from 'react-hot-toast'
import axios from 'axios'

const VideoPreview = ({ videoData, analysisResults }) => {
  const [isPlaying, setIsPlaying] = useState(false)
  const [isMuted, setIsMuted] = useState(false)
  const [currentTime, setCurrentTime] = useState(0)
  const [duration, setDuration] = useState(0)
  const [isFullscreen, setIsFullscreen] = useState(false)
  const videoRef = useRef(null)
  const containerRef = useRef(null)

  useEffect(() => {
    const video = videoRef.current
    if (!video) return

    const handleTimeUpdate = () => setCurrentTime(video.currentTime)
    const handleDurationChange = () => setDuration(video.duration)
    const handlePlay = () => setIsPlaying(true)
    const handlePause = () => setIsPlaying(false)
    const handleEnded = () => setIsPlaying(false)

    video.addEventListener('timeupdate', handleTimeUpdate)
    video.addEventListener('durationchange', handleDurationChange)
    video.addEventListener('play', handlePlay)
    video.addEventListener('pause', handlePause)
    video.addEventListener('ended', handleEnded)

    return () => {
      video.removeEventListener('timeupdate', handleTimeUpdate)
      video.removeEventListener('durationchange', handleDurationChange)
      video.removeEventListener('play', handlePlay)
      video.removeEventListener('pause', handlePause)
      video.removeEventListener('ended', handleEnded)
    }
  }, [])

  const togglePlay = () => {
    const video = videoRef.current
    if (!video) return

    if (isPlaying) {
      video.pause()
    } else {
      video.play()
    }
  }

  const toggleMute = () => {
    const video = videoRef.current
    if (!video) return

    video.muted = !video.muted
    setIsMuted(video.muted)
  }

  const handleSeek = (e) => {
    const video = videoRef.current
    if (!video) return

    const rect = e.currentTarget.getBoundingClientRect()
    const pos = (e.clientX - rect.left) / rect.width
    video.currentTime = pos * duration
  }

  const toggleFullscreen = () => {
    const container = containerRef.current
    if (!container) return

    if (!document.fullscreenElement) {
      container.requestFullscreen()
      setIsFullscreen(true)
    } else {
      document.exitFullscreen()
      setIsFullscreen(false)
    }
  }

  const handleDownload = async () => {
    if (!videoData?.video_path) return

    try {
      toast.loading('Preparing download...')
      
      const response = await axios.get(`/api/download/${videoData.video_path}`, {
        responseType: 'blob'
      })
      
      const url = window.URL.createObjectURL(response.data)
      const link = document.createElement('a')
      link.href = url
      link.download = 'face_analysis_video.mp4'
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)
      
      toast.dismiss()
      toast.success('Video downloaded successfully!')
    } catch (error) {
      toast.dismiss()
      toast.error('Download failed: ' + error.message)
      console.error('Download error:', error)
    }
  }

  const formatTime = (time) => {
    const minutes = Math.floor(time / 60)
    const seconds = Math.floor(time % 60)
    return `${minutes}:${seconds.toString().padStart(2, '0')}`
  }

  if (!videoData) return null

  return (
    <div className="card animate-fade-in">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-gray-800">Video Preview</h2>
        <div className="flex items-center space-x-2 text-sm text-gray-600">
          <div className="flex items-center">
            <div className="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
            With Audio
          </div>
          <div className="flex items-center">
            <div className="w-2 h-2 bg-blue-500 rounded-full mr-2"></div>
            HD Quality
          </div>
        </div>
      </div>

      <div 
        ref={containerRef}
        className="relative bg-black rounded-xl overflow-hidden shadow-2xl group"
      >
        <video
          ref={videoRef}
          className="w-full h-auto max-h-96 object-contain"
          src={`/api/preview_video/${videoData.video_path}`}
          preload="metadata"
          onError={(e) => {
            console.error('Video error:', e)
            toast.error('Error loading video preview')
          }}
        />

        {/* Video Controls Overlay */}
        <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300">
          {/* Play/Pause Button */}
          <div className="absolute inset-0 flex items-center justify-center">
            <button
              onClick={togglePlay}
              className="bg-white/20 backdrop-blur-sm rounded-full p-4 hover:bg-white/30 transition-all duration-200 transform hover:scale-110"
            >
              {isPlaying ? (
                <Pause className="w-8 h-8 text-white" />
              ) : (
                <Play className="w-8 h-8 text-white ml-1" />
              )}
            </button>
          </div>

          {/* Bottom Controls */}
          <div className="absolute bottom-0 left-0 right-0 p-4">
            {/* Progress Bar */}
            <div 
              className="w-full h-2 bg-white/20 rounded-full cursor-pointer mb-3"
              onClick={handleSeek}
            >
              <div 
                className="h-full bg-primary-500 rounded-full transition-all duration-100"
                style={{ width: `${duration ? (currentTime / duration) * 100 : 0}%` }}
              />
            </div>

            {/* Control Buttons */}
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <button
                  onClick={togglePlay}
                  className="text-white hover:text-primary-300 transition-colors"
                >
                  {isPlaying ? <Pause className="w-5 h-5" /> : <Play className="w-5 h-5" />}
                </button>
                
                <button
                  onClick={toggleMute}
                  className="text-white hover:text-primary-300 transition-colors"
                >
                  {isMuted ? <VolumeX className="w-5 h-5" /> : <Volume2 className="w-5 h-5" />}
                </button>
                
                <span className="text-white text-sm">
                  {formatTime(currentTime)} / {formatTime(duration)}
                </span>
              </div>

              <button
                onClick={toggleFullscreen}
                className="text-white hover:text-primary-300 transition-colors"
              >
                <Maximize2 className="w-5 h-5" />
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Video Info */}
      <div className="mt-6 p-4 bg-gray-50 rounded-xl">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 text-sm">
          <div className="text-center">
            <div className="font-semibold text-gray-800">Photos Processed</div>
            <div className="text-primary-600 text-lg font-bold">
              {analysisResults?.marked_photos?.length || 0}
            </div>
          </div>
          <div className="text-center">
            <div className="font-semibold text-gray-800">Video Duration</div>
            <div className="text-secondary-600 text-lg font-bold">
              {formatTime(duration)}
            </div>
          </div>
          <div className="text-center">
            <div className="font-semibold text-gray-800">Audio Theme</div>
            <div className="text-purple-600 text-lg font-bold">
              {videoData.emotionAnalysis ? (
                <span className="flex items-center justify-center">
                  {videoData.emotionAnalysis.theme_info.icon}
                  <span className="ml-1 capitalize">{videoData.emotionAnalysis.dominant_emotion}</span>
                </span>
              ) : 'Cinematic'}
            </div>
          </div>
          <div className="text-center">
            <div className="font-semibold text-gray-800">Quality</div>
            <div className="text-green-600 text-lg font-bold">HD</div>
          </div>
        </div>
        
        {videoData.emotionAnalysis && (
          <div className="mt-4 pt-4 border-t border-gray-200">
            <div className="text-center">
              <h4 className="font-semibold text-gray-800 mb-2">🎵 Generated Soundtrack</h4>
              <p className="text-sm text-gray-600 mb-2">
                <strong>{videoData.emotionAnalysis.theme_info.name}</strong>
              </p>
              <p className="text-xs text-gray-500">
                {videoData.emotionAnalysis.theme_info.description}
              </p>
            </div>
          </div>
        )}
      </div>

      {/* Download Button */}
      <div className="mt-6 text-center">
        <button
          onClick={handleDownload}
          className="button-primary flex items-center mx-auto"
        >
          <Download className="w-5 h-5 mr-2" />
          Download Video
        </button>
        <p className="text-sm text-gray-500 mt-2">
          High-quality MP4 with audio included
        </p>
      </div>
    </div>
  )
}

export default VideoPreview