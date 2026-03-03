import React, { useState } from 'react'
import { useIntersectionObserver } from '../hooks/useIntersectionObserver'
import { Loader } from 'lucide-react'

/**
 * LazyImage component for optimized image loading
 * Uses Intersection Observer to load images only when they enter viewport
 */
const LazyImage = ({ src, alt, className = '', placeholderColor = 'bg-gray-200' }) => {
  const [ref, isVisible] = useIntersectionObserver()
  const [loaded, setLoaded] = useState(false)
  const [error, setError] = useState(false)

  const handleLoad = () => setLoaded(true)
  const handleError = () => setError(true)

  return (
    <div ref={ref} className={`relative overflow-hidden ${className}`}>
      {/* Placeholder while loading */}
      {!loaded && !error && (
        <div className={`absolute inset-0 ${placeholderColor} flex items-center justify-center`}>
          <Loader size={24} className="text-gray-400 animate-spin" />
        </div>
      )}

      {/* Actual image - only load if visible */}
      {isVisible && (
        <img
          src={src}
          alt={alt}
          onLoad={handleLoad}
          onError={handleError}
          className={`w-full h-full object-cover transition-opacity duration-300 ${
            loaded ? 'opacity-100' : 'opacity-0'
          }`}
        />
      )}

      {/* Error state */}
      {error && (
        <div className="absolute inset-0 bg-gray-100 flex items-center justify-center">
          <p className="text-gray-500 text-sm">Failed to load image</p>
        </div>
      )}
    </div>
  )
}

export default LazyImage
