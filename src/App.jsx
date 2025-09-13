import React, { useState } from 'react'
import { Toaster } from 'react-hot-toast'
import Header from './components/Header'
import UploadSection from './components/UploadSection'
import AnalysisSection from './components/AnalysisSection'
import VideoPreview from './components/VideoPreview'
import EmotionDisplay from './components/EmotionDisplay'
import Footer from './components/Footer'

function App() {
  const [referenceFiles, setReferenceFiles] = useState([])
  const [photoFiles, setPhotoFiles] = useState([])
  const [analysisResults, setAnalysisResults] = useState(null)
  const [videoData, setVideoData] = useState(null)
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [isGeneratingVideo, setIsGeneratingVideo] = useState(false)

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100">
      <Toaster 
        position="top-right"
        toastOptions={{
          duration: 4000,
          style: {
            background: '#363636',
            color: '#fff',
          },
        }}
      />
      
      <div className="container mx-auto px-4 py-8">
        <Header />
        
        <div className="space-y-8">
          <UploadSection 
            referenceFiles={referenceFiles}
            setReferenceFiles={setReferenceFiles}
            photoFiles={photoFiles}
            setPhotoFiles={setPhotoFiles}
          />
          
          <AnalysisSection 
            referenceFiles={referenceFiles}
            photoFiles={photoFiles}
            analysisResults={analysisResults}
            setAnalysisResults={setAnalysisResults}
            videoData={videoData}
            setVideoData={setVideoData}
            isAnalyzing={isAnalyzing}
            setIsAnalyzing={setIsAnalyzing}
            isGeneratingVideo={isGeneratingVideo}
            setIsGeneratingVideo={setIsGeneratingVideo}
          />
          
          {videoData && videoData.emotionAnalysis && (
            <EmotionDisplay emotionData={videoData.emotionAnalysis} />
          )}
          
          {videoData && (
            <VideoPreview 
              videoData={videoData}
              analysisResults={analysisResults}
            />
          )}
        </div>
        
        <Footer />
      </div>
    </div>
  )
}

export default App