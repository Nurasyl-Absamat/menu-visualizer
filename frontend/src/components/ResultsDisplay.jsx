import ProductCard from './ProductCard'

const ResultsDisplay = ({ results, onReset }) => {
  const { items = [], session_id } = results || {}
  const matchedCount = items.filter(item => item.matched).length
  const totalCount = items.length

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="card">
        <div className="flex justify-between items-center">
          <div>
            <h2 className="text-2xl font-semibold text-gray-900 mb-2">
              Processing Results
            </h2>
            <p className="text-gray-600">
              Found {matchedCount} of {totalCount} items in our catalog
            </p>
            <p className="text-sm text-gray-500 mt-1">
              Session ID: {session_id}
            </p>
          </div>
          <button
            onClick={onReset}
            className="btn-primary"
          >
            Upload New Image
          </button>
        </div>
      </div>

      {/* Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="card text-center">
          <div className="text-2xl font-bold text-primary-600 mb-1">
            {totalCount}
          </div>
          <div className="text-sm text-gray-600">Items Detected</div>
        </div>
        <div className="card text-center">
          <div className="text-2xl font-bold text-green-600 mb-1">
            {matchedCount}
          </div>
          <div className="text-sm text-gray-600">Matched Products</div>
        </div>
        <div className="card text-center">
          <div className="text-2xl font-bold text-gray-600 mb-1">
            {totalCount - matchedCount}
          </div>
          <div className="text-sm text-gray-600">Unmatched Items</div>
        </div>
      </div>

      {/* Results Grid */}
      <div>
        <h3 className="text-lg font-medium text-gray-900 mb-4">
          Detected Items
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {items.map((item, index) => (
            <ProductCard key={index} item={item} />
          ))}
        </div>
      </div>

      {/* No results message */}
      {items.length === 0 && (
        <div className="card text-center">
          <div className="text-gray-500">
            <svg className="w-16 h-16 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <p className="text-lg font-medium mb-2">No items detected</p>
            <p className="text-sm">Try uploading a clearer image of your menu</p>
          </div>
        </div>
      )}
    </div>
  )
}

export default ResultsDisplay 