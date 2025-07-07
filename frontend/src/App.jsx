import { useState, useEffect } from 'react'
import axios from 'axios'
import ImageUploader from './components/ImageUploader'
import ResultsDisplay from './components/ResultsDisplay'
import LoadingSpinner from './components/LoadingSpinner'

function App() {
  const [isProcessing, setIsProcessing] = useState(false)
  const [results, setResults] = useState(null)
  const [error, setError] = useState(null)
  const [imageProcessingStatus, setImageProcessingStatus] = useState(null)
  const [sessionId, setSessionId] = useState(null)

  // Poll for image processing updates
  useEffect(() => {
    if (sessionId && imageProcessingStatus?.status !== 'completed' && imageProcessingStatus?.status !== 'error') {
      const pollInterval = setInterval(async () => {
        try {
          const response = await axios.get(`http://localhost:8000/session/${sessionId}/status`)
          const statusData = response.data
          
          setImageProcessingStatus(statusData.processing_status)
          
          // Update results with new image data
          if (statusData.items) {
            setResults(prev => ({
              ...prev,
              items: statusData.items
            }))
          }
          
          // Stop polling when completed or error
          if (statusData.processing_status.status === 'completed' || statusData.processing_status.status === 'error') {
            clearInterval(pollInterval)
          }
          
        } catch (err) {
          console.error('Error polling session status:', err)
          // Don't clear interval on error, keep trying
        }
      }, 2000) // Poll every 2 seconds
      
      return () => clearInterval(pollInterval)
    }
  }, [sessionId, imageProcessingStatus?.status])

  const handleImageUpload = async (imageFile) => {
    setIsProcessing(true)
    setError(null)
    setResults(null)
    setImageProcessingStatus(null)
    setSessionId(null)

    try {
      console.log('Processing image:', imageFile.name)
      
      // Create FormData for file upload
      const formData = new FormData()
      formData.append('file', imageFile)
      
      // Call backend API - now returns immediately with OCR results
      const response = await axios.post('http://localhost:8000/parse-image', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        timeout: 30000, // Reduced timeout since we get immediate response
      })
      
      console.log('Backend response:', response.data)
      
      // Transform backend response to match frontend expectations
      const backendData = response.data
      const newSessionId = backendData.session_id
      
      setSessionId(newSessionId)
      setResults({
        session_id: newSessionId,
        total_items: backendData.total_items,
        matched_items: backendData.matched_items,
        ocr_error: backendData.ocr_error,
        items: backendData.items.map(item => ({
          name: item.name,
          nameEnglish: item.nameEnglish,
          matched: item.matched,
          image_url: item.image_url,
          images: item.images || [],
          confidence: item.confidence,
          price: item.price,
          description: item.description,
          parsingError: item.parsingError,
          product_id: item.product_id
        }))
      })
      
      // Set initial image processing status
      setImageProcessingStatus({
        status: 'processing_images',
        progress: 0,
        total: backendData.total_items,
        completed: 0,
        error: null
      })
      
    } catch (err) {
      console.error('Error processing image:', err)
      
      // Handle different error types
      if (err.code === 'ECONNABORTED') {
        setError('Request timed out. Please try with a smaller image.')
      } else if (err.response?.status === 400) {
        setError(err.response.data.detail || 'Invalid file. Please upload an image.')
      } else if (err.response?.status === 500) {
        setError('Server error. This might be due to missing API keys.')
      } else if (err.request) {
        setError('Cannot connect to server. Please check if the backend is running.')
      } else {
        setError('Failed to process image. Please try again.')
      }
    } finally {
      setIsProcessing(false)
    }
  }

  const getLoadingMessage = () => {
    if (isProcessing) {
      return "Processing your menu image..."
    }
    
    if (imageProcessingStatus) {
      switch (imageProcessingStatus.status) {
        case 'processing_images':
          return `Loading images... ${imageProcessingStatus.completed}/${imageProcessingStatus.total} (${Math.round(imageProcessingStatus.progress)}%)`
        case 'completed':
          return null
        case 'error':
          return `Image loading error: ${imageProcessingStatus.error}`
        default:
          return "Processing images..."
      }
    }
    
    return null
  }

  const shouldShowLoader = isProcessing || (imageProcessingStatus && imageProcessingStatus.status === 'processing_images')

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        <header className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            Menu Visualizer
          </h1>
          <p className="text-lg text-gray-600">
            AI-Powered OCR + Product Matcher
          </p>
        </header>

        <main className="max-w-4xl mx-auto">
          {!results && !isProcessing && (
            <ImageUploader onImageUpload={handleImageUpload} />
          )}

          {shouldShowLoader && (
            <LoadingSpinner message={getLoadingMessage()} />
          )}

          {error && (
            <div className="card bg-red-50 border-red-200 text-red-700 text-center">
              <p>{error}</p>
              <button 
                onClick={() => {
                  setError(null)
                  setResults(null)
                  setImageProcessingStatus(null)
                  setSessionId(null)
                }}
                className="mt-4 btn-primary bg-red-500 hover:bg-red-600"
              >
                Try Again
              </button>
            </div>
          )}

          {results && (
            <div>
              {/* Show image processing status */}
              {imageProcessingStatus && imageProcessingStatus.status === 'processing_images' && (
                <div className="mb-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                  <div className="flex items-center justify-between">
                    <span className="text-blue-800">
                      Loading product images... {imageProcessingStatus.completed}/{imageProcessingStatus.total}
                    </span>
                    <span className="text-blue-600 font-medium">
                      {Math.round(imageProcessingStatus.progress)}%
                    </span>
                  </div>
                  <div className="mt-2 w-full bg-blue-200 rounded-full h-2">
                    <div 
                      className="bg-blue-600 h-2 rounded-full transition-all duration-300" 
                      style={{ width: `${imageProcessingStatus.progress}%` }}
                    ></div>
                  </div>
                </div>
              )}
              
              {imageProcessingStatus && imageProcessingStatus.status === 'completed' && (
                <div className="mb-4 p-4 bg-green-50 border border-green-200 rounded-lg">
                  <span className="text-green-800">
                    ✅ All images loaded successfully!
                  </span>
                </div>
              )}
              
              {imageProcessingStatus && imageProcessingStatus.status === 'error' && (
                <div className="mb-4 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                  <span className="text-yellow-800">
                    ⚠️ Some images couldn't be loaded, using placeholders
                  </span>
                </div>
              )}
              
              <ResultsDisplay 
                results={results} 
                onReset={() => {
                  setResults(null)
                  setError(null)
                  setImageProcessingStatus(null)
                  setSessionId(null)
                }}
              />
            </div>
          )}
        </main>
      </div>
    </div>
  )
}

export default App 