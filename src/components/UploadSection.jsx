import React from 'react'
import { Upload, User, Image, X } from 'lucide-react'
import { useDropzone } from 'react-dropzone'
import toast from 'react-hot-toast'
import axios from 'axios'

const UploadSection = ({ 
  referenceFiles, 
  setReferenceFiles, 
  photoFiles, 
  setPhotoFiles 
}) => {
  const uploadReferenceFiles = async (files) => {
    try {
      for (let i = 0; i < files.length; i++) {
        const formData = new FormData()
        formData.append('file', files[i])
        
        await axios.post(`/api/upload_reference?is_first=${i === 0}`, formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        })
      }
      
      setReferenceFiles(files)
      toast.success(`${files.length} reference photo(s) uploaded successfully!`)
    } catch (error) {
      toast.error('Failed to upload reference photos')
      console.error('Upload error:', error)
    }
  }

  const uploadPhotoFiles = async (files) => {
    try {
      const formData = new FormData()
      files.forEach(file => {
        formData.append('files[]', file)
      })
      
      await axios.post('/api/upload_photos', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      
      setPhotoFiles(files)
      toast.success(`${files.length} photo(s) uploaded successfully!`)
    } catch (error) {
      toast.error('Failed to upload photos')
      console.error('Upload error:', error)
    }
  }

  const referenceDropzone = useDropzone({
    accept: {
      'image/*': ['.jpeg', '.jpg', '.png', '.bmp']
    },
    onDrop: uploadReferenceFiles,
    multiple: true
  })

  const photoDropzone = useDropzone({
    accept: {
      'image/*': ['.jpeg', '.jpg', '.png', '.bmp']
    },
    onDrop: uploadPhotoFiles,
    multiple: true
  })

  const removeReferenceFile = (index) => {
    const newFiles = referenceFiles.filter((_, i) => i !== index)
    setReferenceFiles(newFiles)
  }

  const removePhotoFile = (index) => {
    const newFiles = photoFiles.filter((_, i) => i !== index)
    setPhotoFiles(newFiles)
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 animate-slide-up">
      {/* Reference Photos Upload */}
      <div className="card">
        <div className="flex items-center mb-6">
          <User className="w-6 h-6 text-secondary-600 mr-3" />
          <h2 className="text-2xl font-bold text-gray-800">Reference Photos</h2>
        </div>
        
        <div 
          {...referenceDropzone.getRootProps()} 
          className={`upload-zone ${referenceDropzone.isDragActive ? 'active' : ''}`}
        >
          <input {...referenceDropzone.getInputProps()} />
          <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-600 mb-2 font-medium">
            Upload clear photos of the person to track
          </p>
          <p className="text-sm text-gray-500">
            Drag & drop or click to browse
          </p>
        </div>

        {referenceFiles.length > 0 && (
          <div className="mt-6">
            <h3 className="text-sm font-semibold text-gray-700 mb-3">
              Uploaded Reference Photos ({referenceFiles.length})
            </h3>
            <div className="grid grid-cols-4 gap-3">
              {referenceFiles.map((file, index) => (
                <div key={index} className="relative group">
                  <img
                    src={URL.createObjectURL(file)}
                    alt={`Reference ${index + 1}`}
                    className="w-full h-20 object-cover rounded-lg border-2 border-gray-200"
                  />
                  <button
                    onClick={() => removeReferenceFile(index)}
                    className="absolute -top-2 -right-2 bg-red-500 text-white rounded-full p-1 opacity-0 group-hover:opacity-100 transition-opacity"
                  >
                    <X className="w-3 h-3" />
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Photos to Analyze Upload */}
      <div className="card">
        <div className="flex items-center mb-6">
          <Image className="w-6 h-6 text-primary-600 mr-3" />
          <h2 className="text-2xl font-bold text-gray-800">Photos to Analyze</h2>
        </div>
        
        <div 
          {...photoDropzone.getRootProps()} 
          className={`upload-zone ${photoDropzone.isDragActive ? 'active' : ''}`}
        >
          <input {...photoDropzone.getInputProps()} />
          <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-600 mb-2 font-medium">
            Upload photos for face detection & emotion analysis
          </p>
          <p className="text-sm text-gray-500">
            Drag & drop or click to browse
          </p>
        </div>

        {photoFiles.length > 0 && (
          <div className="mt-6">
            <h3 className="text-sm font-semibold text-gray-700 mb-3">
              Uploaded Photos ({photoFiles.length})
            </h3>
            <div className="grid grid-cols-4 gap-3 max-h-40 overflow-y-auto">
              {photoFiles.slice(0, 8).map((file, index) => (
                <div key={index} className="relative group">
                  <img
                    src={URL.createObjectURL(file)}
                    alt={`Photo ${index + 1}`}
                    className="w-full h-20 object-cover rounded-lg border-2 border-gray-200"
                  />
                  <button
                    onClick={() => removePhotoFile(index)}
                    className="absolute -top-2 -right-2 bg-red-500 text-white rounded-full p-1 opacity-0 group-hover:opacity-100 transition-opacity"
                  >
                    <X className="w-3 h-3" />
                  </button>
                </div>
              ))}
              {photoFiles.length > 8 && (
                <div className="w-full h-20 bg-gray-100 rounded-lg border-2 border-dashed border-gray-300 flex items-center justify-center">
                  <span className="text-sm text-gray-500">+{photoFiles.length - 8} more</span>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default UploadSection