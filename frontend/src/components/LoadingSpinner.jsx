const LoadingSpinner = ({ message = "Processing..." }) => {
  return (
    <div className="card text-center">
      <div className="flex flex-col items-center space-y-4">
        <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-primary-500"></div>
        <div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            {message}
          </h3>
          <p className="text-sm text-gray-600">
            This may take a few moments...
          </p>
        </div>
      </div>
    </div>
  )
}

export default LoadingSpinner 