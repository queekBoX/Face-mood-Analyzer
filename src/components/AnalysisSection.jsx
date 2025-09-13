import React from 'react'
import { Play, Download, Video, Loader2, CheckCircle, AlertCircle } from 'lucide-react'
import toast from 'react-hot-toast'
import axios from 'axios'

const AnalysisSection = ({ 
  referenceFiles, 
  photoFiles, 
  analysisResults, 
  setAnalysisResults,
  videoData,
  setVideoData,
  isAnalyzing,
  setIsAnalyzing,
  isGeneratingVideo,
  setIsGeneratingVideo
}) => {
  const canAnalyze = referenceFiles.length > 0 && photoFiles.length > 0 && !isAnalyzing
  const canGenerateVideo = analysisResults && analysisResults.marked_photos.length > 0 && !isGeneratingVideo

  const handleAnalyze = async () => {
    if (!canAnalyze) return

    setIsAnalyzing(true)
    try {
      const response = await axios.post('/api/analyze')
      setAnalysisResults(response.data)
      
      if (response.data.marked_photos.length > 0) {
        toast.success(`Analysis completed! Found faces in ${response.data.marked_photos.length} photos`)
      } else {
        toast.error('No matching faces found in the uploaded photos')
      }
    } catch (error) {
      toast.error('Analysis failed: ' + (error.response?.data?.error || error.message))
      console.error('Analysis error:', error)
    } finally {
      setIsAnalyzing(false)
    }
  }

  const handleGenerateVideo = async () => {
    if (!canGenerateVideo) return

    setIsGeneratingVideo(true)
    try {
      const response = await axios.post('/api/generate_video')
      
      // Get emotion analysis data
      const emotionResponse = await axios.get('/api/get_emotion_analysis')
      
      setVideoData({
        ...response.data,
        emotionAnalysis: emotionResponse.data
      })
      
      toast.success(`Video generated with ${emotionResponse.data.theme_info.name} soundtrack!`)
    } catch (error) {
      toast.error('Video generation failed: ' + (error.response?.data?.error || error.message))
      console.error('Video generation error:', error)
    } finally {
      setIsGeneratingVideo(false)
    }
  }

  const handleDownloadMarkedPhotos = async () => {
    if (!analysisResults || analysisResults.marked_photos.length === 0) return

    try {
      toast.loading('Preparing download...')
      
      // Create a zip file containing all marked photos
      const JSZip = (await import('jszip')).default
      const zip = new JSZip()
      
      // Download each marked photo and add to zip
      for (const photo of analysisResults.marked_photos) {
        try {
          const response = await axios.get(`/api/download/${photo}`, {
            responseType: 'blob'
          })
          zip.file(photo, response.data)
        } catch (photoError) {
          console.warn(`Failed to download ${photo}:`, photoError)
        }
      }
      
      // Generate and download the zip file
      const content = await zip.generateAsync({ type: 'blob' })
      const url = window.URL.createObjectURL(content)
      const link = document.createElement('a')
      link.href = url
      link.download = 'marked_photos.zip'
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)
      
      toast.dismiss()
      toast.success('Photos downloaded successfully!')
    } catch (error) {
      toast.dismiss()
      toast.error('Download failed: ' + error.message)
      console.error('Download error:', error)
    }
  }

  return (
    <div className="card animate-slide-up">
      <h2 className="text-2xl font-bold text-gray-800 mb-6 text-center">
        Analysis & Video Generation
      </h2>

      {/* Status Display */}
      <div className="mb-8 p-4 rounded-xl bg-gray-50 border border-gray-200">
        {isAnalyzing && (
          <div className="flex items-center justify-center text-primary-600">
            <Loader2 className="w-6 h-6 animate-spin mr-3" />
            <span className="font-medium">Analyzing photos with AI...</span>
          </div>
        )}
        
        {isGeneratingVideo && (
          <div className="flex items-center justify-center text-secondary-600">
            <Loader2 className="w-6 h-6 animate-spin mr-3" />
            <span className="font-medium">Generating video with audio...</span>
          </div>
        )}
        
        {!isAnalyzing && !isGeneratingVideo && !analysisResults && (
          <div className="text-center text-gray-600">
            <AlertCircle className="w-8 h-8 mx-auto mb-2 text-gray-400" />
            <p>Upload reference photos and photos to analyze, then click "Start Analysis"</p>
          </div>
        )}
        
        {!isAnalyzing && !isGeneratingVideo && analysisResults && (
          <div className="text-center text-green-600">
            <CheckCircle className="w-8 h-8 mx-auto mb-2" />
            <p className="font-medium">
              Analysis completed! Found faces in {analysisResults.marked_photos.length} photos
            </p>
          </div>
        )}
        
        {videoData && videoData.emotionAnalysis && (
          <div className="mt-4 p-4 bg-gradient-to-r from-purple-50 to-blue-50 rounded-xl border border-purple-200">
            <div className="text-center">
              <div className="flex items-center justify-center mb-2">
                <span className="text-2xl mr-2">{videoData.emotionAnalysis.theme_info.icon}</span>
                <h3 className="text-lg font-bold" style={{ color: videoData.emotionAnalysis.theme_info.color }}>
                  {videoData.emotionAnalysis.theme_info.name}
                </h3>
              </div>
              <p className="text-sm text-gray-600 mb-3">
                {videoData.emotionAnalysis.theme_info.description}
              </p>
              <div className="flex items-center justify-center space-x-4 text-xs text-gray-500">
                <span>Dominant Emotion: <strong className="capitalize">{videoData.emotionAnalysis.dominant_emotion}</strong></span>
                <span>•</span>
                <span>Cinematic Score Generated</span>
              </div>
            </div>
          </div>
        )}
        
        {videoData && !isGeneratingVideo && (
          <div className="text-center text-purple-600 mt-4">
            <CheckCircle className="w-8 h-8 mx-auto mb-2" />
            <p className="font-medium">Video generated successfully with audio!</p>
          </div>
        )}
      </div>

      {/* Action Buttons */}
      <div className="flex flex-col items-center space-y-4">
        {/* Primary Action - Analyze */}
        <button
          onClick={handleAnalyze}
          disabled={!canAnalyze}
          className={`button-primary w-64 flex items-center justify-center ${
            !canAnalyze ? 'opacity-50 cursor-not-allowed transform-none' : ''
          }`}
        >
          {isAnalyzing ? (
            <Loader2 className="w-5 h-5 animate-spin mr-2" />
          ) : (
            <Play className="w-5 h-5 mr-2" />
          )}
          {isAnalyzing ? 'Analyzing...' : 'Start Analysis'}
        </button>

        {/* Secondary Actions */}
        {analysisResults && analysisResults.marked_photos.length > 0 && (
          <div className="flex flex-wrap justify-center gap-4">
            <button
              onClick={handleDownloadMarkedPhotos}
              className="button-secondary flex items-center"
            >
              <Download className="w-5 h-5 mr-2" />
              Download Marked Photos
            </button>

            <button
              onClick={handleGenerateVideo}
              disabled={!canGenerateVideo}
              className={`button-primary flex items-center ${
                !canGenerateVideo ? 'opacity-50 cursor-not-allowed transform-none' : ''
              }`}
            >
              {isGeneratingVideo ? (
                <Loader2 className="w-5 h-5 animate-spin mr-2" />
              ) : (
                <Video className="w-5 h-5 mr-2" />
              )}
              {isGeneratingVideo ? 'Generating...' : 'Generate Video'}
            </button>
          </div>
        )}
      </div>

      {/* Progress Indicators */}
      <div className="mt-8 flex justify-center space-x-8 text-sm">
        <div className={`flex items-center ${referenceFiles.length > 0 ? 'text-green-600' : 'text-gray-400'}`}>
          <div className={`w-3 h-3 rounded-full mr-2 ${referenceFiles.length > 0 ? 'bg-green-500' : 'bg-gray-300'}`}></div>
          Reference Photos ({referenceFiles.length})
        </div>
        <div className={`flex items-center ${photoFiles.length > 0 ? 'text-green-600' : 'text-gray-400'}`}>
          <div className={`w-3 h-3 rounded-full mr-2 ${photoFiles.length > 0 ? 'bg-green-500' : 'bg-gray-300'}`}></div>
          Photos to Analyze ({photoFiles.length})
        </div>
        <div className={`flex items-center ${analysisResults ? 'text-green-600' : 'text-gray-400'}`}>
          <div className={`w-3 h-3 rounded-full mr-2 ${analysisResults ? 'bg-green-500' : 'bg-gray-300'}`}></div>
          Analysis {analysisResults ? 'Complete' : 'Pending'}
        </div>
        <div className={`flex items-center ${videoData ? 'text-green-600' : 'text-gray-400'}`}>
          <div className={`w-3 h-3 rounded-full mr-2 ${videoData ? 'bg-green-500' : 'bg-gray-300'}`}></div>
          Video {videoData ? 'Ready' : 'Pending'}
        </div>
      </div>
    </div>
  )
}

export default AnalysisSection