import { useState } from 'react'
import axios from 'axios'
import ImageUploader from './components/ImageUploader'
import ResultsDisplay from './components/ResultsDisplay'
import LoadingSpinner from './components/LoadingSpinner'

function App() {
  const [isProcessing, setIsProcessing] = useState(false)
  const [results, setResults] = useState(null)
  const [error, setError] = useState(null)

  const handleImageUpload = async (imageFile) => {
    setIsProcessing(true)
    setError(null)
    setResults(null)

    try {
      console.log('Processing image:', imageFile.name)
      
      // Create FormData for file upload
      const formData = new FormData()
      formData.append('file', imageFile)
      
      // Call real backend API
      const response = await axios.post('http://localhost:8000/parse-image', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        timeout: 60000, // 60 second timeout
      })
      
      console.log('Backend response:', response.data)
      
      // Transform backend response to match frontend expectations
      const backendData = response.data
      setResults({
        session_id: backendData.session_id,
        total_items: backendData.total_items,
        matched_items: backendData.matched_items,
        ocr_error: backendData.ocr_error,
        items: backendData.items.map(item => ({
          name: item.name,
          nameEnglish: item.nameEnglish,
          matched: item.matched,
          image_url: item.image_url,
          images: item.images || [], // Add the new images array
          confidence: item.confidence,
          price: item.price,
          description: item.description,
          parsingError: item.parsingError,
          product_id: item.product_id
        }))
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

          {isProcessing && (
            <LoadingSpinner message="Processing your menu image..." />
          )}

          {error && (
            <div className="card bg-red-50 border-red-200 text-red-700 text-center">
              <p>{error}</p>
              <button 
                onClick={() => {
                  setError(null)
                  setResults(null)
                }}
                className="mt-4 btn-primary bg-red-500 hover:bg-red-600"
              >
                Try Again
              </button>
            </div>
          )}

          {results && (
            <ResultsDisplay 
              results={results} 
              onReset={() => {
                setResults(null)
                setError(null)
              }}
            />
          )}
        </main>
      </div>
    </div>
  )
}

export default App 