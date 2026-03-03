import { useEffect, useRef, useState } from 'react'

/**
 * Custom hook for Intersection Observer API
 * Detects when an element enters or leaves the viewport
 * Useful for lazy loading images, videos, and lesson content
 */
export const useIntersectionObserver = (options = {}) => {
  const ref = useRef(null)
  const [isVisible, setIsVisible] = useState(false)

  useEffect(() => {
    const observer = new IntersectionObserver(([entry]) => {
      if (entry.isIntersecting) {
        setIsVisible(true)
        // Once visible, stop observing (for one-time loading)
        observer.unobserve(entry.target)
      }
    }, {
      threshold: 0.1,
      rootMargin: '50px', // Start loading 50px before element enters viewport
      ...options
    })

    if (ref.current) {
      observer.observe(ref.current)
    }

    return () => {
      if (ref.current) {
        observer.unobserve(ref.current)
      }
    }
  }, [options])

  return [ref, isVisible]
}

/**
 * Hook for continuous visibility tracking (doesn't stop observing)
 * Useful for virtual scrolling and performance monitoring
 */
export const useIntersectionObserverContinuous = (options = {}) => {
  const ref = useRef(null)
  const [isVisible, setIsVisible] = useState(false)

  useEffect(() => {
    const observer = new IntersectionObserver(([entry]) => {
      setIsVisible(entry.isIntersecting)
    }, {
      threshold: 0.1,
      rootMargin: '50px',
      ...options
    })

    if (ref.current) {
      observer.observe(ref.current)
    }

    return () => {
      if (ref.current) {
        observer.unobserve(ref.current)
      }
    }
  }, [options])

  return [ref, isVisible]
}
