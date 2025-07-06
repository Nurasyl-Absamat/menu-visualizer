import { useState } from 'react'

const ProductCard = ({ item }) => {
  const { name, matched, image_url, images, confidence, price, nameEnglish } = item
  const [currentImageIndex, setCurrentImageIndex] = useState(0)

  // Use images array if available, otherwise fallback to single image_url
  const displayImages = images && images.length > 0 ? images : (image_url ? [{ url: image_url, source: 'legacy', photographer: 'Unknown' }] : [])

  const nextImage = () => {
    if (displayImages.length > 1) {
      setCurrentImageIndex((prev) => (prev + 1) % displayImages.length)
    }
  }

  const prevImage = () => {
    if (displayImages.length > 1) {
      setCurrentImageIndex((prev) => (prev - 1 + displayImages.length) % displayImages.length)
    }
  }

  const goToImage = (index) => {
    setCurrentImageIndex(index)
  }

  return (
    <div className={`card transition-all ${matched ? 'border-green-200 bg-green-50' : 'border-gray-200'}`}>
      <div className="space-y-3">
        {/* Status Badge */}
        <div className="flex justify-between items-start">
          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
            matched 
              ? 'bg-green-100 text-green-800' 
              : 'bg-gray-100 text-gray-800'
          }`}>
            {matched ? (
              <>
                <svg className="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
                Matched
              </>
            ) : (
              <>
                <svg className="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
                Extracted
              </>
            )}
          </span>
          
          {confidence && (
            <span className="text-xs text-gray-500">
              {Math.round(confidence * 100)}%
            </span>
          )}
        </div>

        {/* Product Images Carousel */}
        {displayImages.length > 0 && (
          <div className="relative">
            <div className="aspect-w-16 aspect-h-9 rounded-lg overflow-hidden">
              <img
                src={displayImages[currentImageIndex].url}
                alt={name}
                className="w-full h-32 object-cover rounded-lg"
                onError={(e) => {
                  e.target.src = 'https://via.placeholder.com/300x200?text=No+Image'
                }}
              />
            </div>
            
            {/* Navigation arrows - only show if more than 1 image */}
            {displayImages.length > 1 && (
              <>
                <button
                  onClick={prevImage}
                  className="absolute left-1 top-1/2 transform -translate-y-1/2 bg-black bg-opacity-50 hover:bg-opacity-75 text-white rounded-full p-1 transition-all"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                  </svg>
                </button>
                <button
                  onClick={nextImage}
                  className="absolute right-1 top-1/2 transform -translate-y-1/2 bg-black bg-opacity-50 hover:bg-opacity-75 text-white rounded-full p-1 transition-all"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                </button>
              </>
            )}
            
            {/* Dots indicator - only show if more than 1 image */}
            {displayImages.length > 1 && (
              <div className="absolute bottom-2 left-1/2 transform -translate-x-1/2 flex space-x-1">
                {displayImages.map((_, index) => (
                  <button
                    key={index}
                    onClick={() => goToImage(index)}
                    className={`w-2 h-2 rounded-full transition-all ${
                      index === currentImageIndex 
                        ? 'bg-white' 
                        : 'bg-white bg-opacity-50'
                    }`}
                  />
                ))}
              </div>
            )}
            
            {/* Image source indicator */}
            {displayImages[currentImageIndex].source !== 'placeholder' && displayImages[currentImageIndex].source !== 'legacy' && (
              <div className="absolute top-2 right-2 bg-black bg-opacity-50 text-white text-xs px-2 py-1 rounded">
                {displayImages[currentImageIndex].source === 'pexels' ? 'Pexels' : 'Unsplash'}
              </div>
            )}
          </div>
        )}

        {/* Product Name */}
        <div>
          <h4 className="font-medium text-gray-900 text-sm">
            {name}
          </h4>
          {nameEnglish && nameEnglish !== name && (
            <p className="text-xs text-gray-600 mt-1">
              {nameEnglish}
            </p>
          )}
          {!matched && (
            <p className="text-xs text-gray-500 mt-1">
              Product not found in catalog
            </p>
          )}
        </div>

        {/* Price */}
        {price && (
          <div className="text-sm font-medium text-gray-900">
            {price}
          </div>
        )}

        {/* Image Info */}
        {displayImages.length > 0 && displayImages[currentImageIndex].photographer && displayImages[currentImageIndex].photographer !== 'Unknown' && (
          <div className="text-xs text-gray-500">
            Photo by {displayImages[currentImageIndex].photographer}
            {displayImages[currentImageIndex].photographer_url && (
              <a 
                href={displayImages[currentImageIndex].photographer_url} 
                target="_blank" 
                rel="noopener noreferrer"
                className="text-blue-500 hover:text-blue-700 ml-1"
              >
                ↗
              </a>
            )}
          </div>
        )}

        {/* Multiple Images Counter */}
        {displayImages.length > 1 && (
          <div className="text-xs text-gray-500 text-center">
            {currentImageIndex + 1} of {displayImages.length} images
          </div>
        )}

        {/* Action Button */}
        {matched && (
          <button className="w-full text-xs bg-primary-500 hover:bg-primary-600 text-white py-2 px-3 rounded-md transition-colors">
            View Details
          </button>
        )}
      </div>
    </div>
  )
}

export default ProductCard 