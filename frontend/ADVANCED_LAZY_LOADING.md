# Advanced Lazy Loading Patterns

## Pattern 1: Code Splitting with React.lazy

Split large components into separate chunks loaded on demand.

### Basic Code Splitting
```javascript
// src/components/CourseView.jsx
import { lazy, Suspense } from 'react'

// These components will be in separate bundles
const LessonContent = lazy(() => import('./LessonContent'))
const AdminPanel = lazy(() => import('./AdminPanel'))

function CourseView() {
  return (
    <Suspense fallback={<LoadingSpinner />}>
      <LessonContent lesson={lesson} />
    </Suspense>
  )
}
```

### Route-based Code Splitting
```javascript
// src/App.jsx
import { lazy, Suspense } from 'react'
import { BrowserRouter, Routes, Route } from 'react-router-dom'

const CourseView = lazy(() => import('./pages/CourseView'))
const AdminDashboard = lazy(() => import('./pages/AdminDashboard'))
const StudentDashboard = lazy(() => import('./pages/StudentDashboard'))

function App() {
  return (
    <BrowserRouter>
      <Suspense fallback={<PageLoader />}>
        <Routes>
          <Route path="/course/:id" element={<CourseView />} />
          <Route path="/admin" element={<AdminDashboard />} />
          <Route path="/student" element={<StudentDashboard />} />
        </Routes>
      </Suspense>
    </BrowserRouter>
  )
}
```

## Pattern 2: Progressive Image Loading

Load images progressively from low quality to high quality.

### Blur-up Technique
```javascript
// src/components/ProgressiveImage.jsx
import { useState } from 'react'
import { useIntersectionObserver } from '../hooks/useIntersectionObserver'

function ProgressiveImage({ src, placeholder, alt }) {
  const [ref, isVisible] = useIntersectionObserver()
  const [imageSrc, setImageSrc] = useState(placeholder)
  const [isLoading, setIsLoading] = useState(false)

  useState(() => {
    if (!isVisible) return

    setIsLoading(true)
    const img = new Image()
    img.src = src
    img.onload = () => {
      setImageSrc(src)
      setIsLoading(false)
    }
  }, [isVisible, src])

  return (
    <img
      ref={ref}
      src={imageSrc}
      alt={alt}
      className={`transition-all duration-500 ${
        isLoading ? 'blur-md' : 'blur-0'
      }`}
    />
  )
}
```

**Usage:**
```javascript
<ProgressiveImage
  placeholder="https://cdn.example.com/images/lesson-thumb-low.jpg"
  src="https://cdn.example.com/images/lesson-full.jpg"
  alt="Lesson content"
/>
```

### LQIP (Low Quality Image Placeholder)
```javascript
// More sophisticated version with proper placeholders
const ProgressiveImage = ({ src, lqip, alt }) => {
  const [ref, isVisible] = useIntersectionObserver()
  const [imageSrc, setImageSrc] = useState(lqip)
  const [isLoaded, setIsLoaded] = useState(false)

  useEffect(() => {
    if (!isVisible) return

    const img = new Image()
    img.src = src
    img.onload = () => {
      setImageSrc(src)
      setIsLoaded(true)
    }
  }, [isVisible])

  return (
    <div className="relative overflow-hidden">
      <img
        ref={ref}
        src={imageSrc}
        alt={alt}
        className={`transition-opacity duration-500 ${
          isLoaded ? 'opacity-100' : 'opacity-60'
        }`}
      />
      {!isLoaded && (
        <div className="absolute inset-0 bg-gray-200 animate-pulse" />
      )}
    </div>
  )
}
```

## Pattern 3: Virtual Scrolling for Large Lists

Render only visible items in scrollable lists.

### Using react-window
```bash
npm install react-window
```

```javascript
// src/components/VirtualLessonList.jsx
import { FixedSizeList as List } from 'react-window'
import LessonListItem from './LessonListItem'

function VirtualLessonList({ lessons, onSelectLesson }) {
  const Row = ({ index, style }) => (
    <div style={style}>
      <LessonListItem
        lesson={lessons[index]}
        onSelect={onSelectLesson}
      />
    </div>
  )

  return (
    <List
      height={600}
      itemCount={lessons.length}
      itemSize={64}
      width="100%"
    >
      {Row}
    </List>
  )
}
```

## Pattern 4: Request Deduplication

Prevent duplicate API requests for the same resource.

```javascript
// src/utils/requestCache.js
class RequestCache {
  constructor() {
    this.cache = new Map()
    this.pending = new Map()
  }

  async get(key, fetcher) {
    // Return cached result if available
    if (this.cache.has(key)) {
      return this.cache.get(key)
    }

    // Return pending request if already in flight
    if (this.pending.has(key)) {
      return this.pending.get(key)
    }

    // Create new request
    const promise = fetcher()
      .then(result => {
        this.cache.set(key, result)
        this.pending.delete(key)
        return result
      })
      .catch(error => {
        this.pending.delete(key)
        throw error
      })

    this.pending.set(key, promise)
    return promise
  }

  invalidate(key) {
    this.cache.delete(key)
    this.pending.delete(key)
  }

  clear() {
    this.cache.clear()
    this.pending.clear()
  }
}

export const lessonCache = new RequestCache()
```

**Usage:**
```javascript
import { lessonCache } from '../utils/requestCache'

function LessonContent({ lesson }) {
  const [details, setDetails] = useState(null)

  useEffect(() => {
    lessonCache
      .get(`lesson-${lesson.id}`, () => 
        fetch(`/api/lessons/${lesson.id}`).then(r => r.json())
      )
      .then(setDetails)
  }, [lesson.id])

  return <div>{details?.title}</div>
}
```

## Pattern 5: Adaptive Loading Based on Network

Adjust lazy loading strategy based on connection quality.

```javascript
// src/hooks/useNetworkStatus.js
import { useState, useEffect } from 'react'

export const useNetworkStatus = () => {
  const [isSlowNetwork, setIsSlowNetwork] = useState(false)
  const [effectiveType, setEffectiveType] = useState('4g')

  useEffect(() => {
    const connection = navigator.connection || navigator.mozConnection
    
    if (!connection) {
      setIsSlowNetwork(false)
      return
    }

    const checkConnection = () => {
      const type = connection.effectiveType
      setEffectiveType(type)
      setIsSlowNetwork(type === 'slow-2g' || type === '2g')
    }

    checkConnection()
    connection.addEventListener('change', checkConnection)

    return () => {
      connection.removeEventListener('change', checkConnection)
    }
  }, [])

  return { isSlowNetwork, effectiveType }
}

// Usage
function LessonContent({ lesson }) {
  const { isSlowNetwork } = useNetworkStatus()
  const rootMargin = isSlowNetwork ? '200px' : '50px'
  
  const [ref, isVisible] = useIntersectionObserver({ rootMargin })

  // Load with larger margin on slow networks for better UX
  return <div ref={ref}>{isVisible && <Content lesson={lesson} />}</div>
}
```

## Pattern 6: Prefetching Strategy

Intelligently prefetch content the user might need next.

```javascript
// src/hooks/usePrefetch.js
import { useEffect } from 'react'
import { lessonCache } from '../utils/requestCache'

export const usePrefetch = (items, getCurrentIndex) => {
  useEffect(() => {
    const currentIndex = getCurrentIndex()
    const nextIndex = currentIndex + 1
    const nextNextIndex = currentIndex + 2

    // Prefetch next lesson
    if (nextIndex < items.length) {
      const nextLesson = items[nextIndex]
      lessonCache
        .get(`lesson-${nextLesson.id}`, () =>
          fetch(`/api/lessons/${nextLesson.id}`).then(r => r.json())
        )
        .catch(() => {}) // Silent fail for prefetch
    }

    // Prefetch lesson after next with lower priority
    if (nextNextIndex < items.length) {
      setTimeout(() => {
        const nextNextLesson = items[nextNextIndex]
        lessonCache
          .get(`lesson-${nextNextLesson.id}`, () =>
            fetch(`/api/lessons/${nextNextLesson.id}`).then(r => r.json())
          )
          .catch(() => {})
      }, 2000) // Delay to avoid blocking
    }
  }, [items, getCurrentIndex])
}

// Usage
function CourseView({ modules, selectedLessonId }) {
  const allLessons = modules.flatMap(m => m.lessons)
  const currentIndex = allLessons.findIndex(l => l.id === selectedLessonId)

  usePrefetch(allLessons, () => currentIndex)

  return <div>{/* ... */}</div>
}
```

## Pattern 7: Service Worker Caching

Cache lesson content for offline access and faster loads.

```javascript
// src/utils/serviceWorker-helper.js
export const registerServiceWorker = async () => {
  if ('serviceWorker' in navigator) {
    try {
      const registration = await navigator.serviceWorker.register('/sw.js')
      console.log('Service Worker registered:', registration)
    } catch (error) {
      console.error('Service Worker registration failed:', error)
    }
  }
}

// public/sw.js
const CACHE_NAME = 'elevateED-v1'
const LESSON_CACHE = 'lessons-v1'

const urlsToCache = [
  '/',
  '/index.html',
  '/manifest.json'
]

self.addEventListener('install', event => {
  event.waitUntil(
    caches
      .open(CACHE_NAME)
      .then(cache => cache.addAll(urlsToCache))
  )
})

self.addEventListener('fetch', event => {
  const { request } = event

  // Cache lesson API calls
  if (request.url.includes('/api/lessons/')) {
    event.respondWith(
      caches.match(request).then(response => {
        return (
          response ||
          fetch(request).then(response => {
            const responseClone = response.clone()
            caches.open(LESSON_CACHE).then(cache => {
              cache.put(request, responseClone)
            })
            return response
          })
        )
      })
    )
    return
  }

  // Standard caching for other requests
  event.respondWith(
    caches.match(request).then(response => {
      return response || fetch(request)
    })
  )
})
```

**Register in main.jsx:**
```javascript
import { registerServiceWorker } from './utils/serviceWorker-helper'

registerServiceWorker()
```

## Pattern 8: Skeleton Loading States

Better UX while content loads.

```javascript
// src/components/LessonSkeleton.jsx
function LessonSkeleton() {
  return (
    <div className="space-y-6 animate-pulse">
      <div className="bg-gray-200 aspect-video rounded-lg" />
      <div className="space-y-4">
        <div className="h-8 bg-gray-200 rounded w-3/4" />
        <div className="space-y-2">
          <div className="h-4 bg-gray-200 rounded w-full" />
          <div className="h-4 bg-gray-200 rounded w-5/6" />
          <div className="h-4 bg-gray-200 rounded w-4/6" />
        </div>
      </div>
    </div>
  )
}
```

**Usage:**
```javascript
<Suspense fallback={<LessonSkeleton />}>
  <LessonContent lesson={lesson} />
</Suspense>
```

## Combining All Patterns

Here's how to use multiple patterns together:

```javascript
// src/components/OptimizedCourseView.jsx
import { lazy, Suspense, useState } from 'react'
import { useNetworkStatus } from '../hooks/useNetworkStatus'
import { usePrefetch } from '../hooks/usePrefetch'
import { registerServiceWorker } from '../utils/serviceWorker-helper'

const LessonContent = lazy(() => import('./LessonContent'))
const LessonSkeleton = () => <div className="animate-pulse">Loading...</div>

export default function OptimizedCourseView() {
  const { isSlowNetwork } = useNetworkStatus()
  const [selectedLessonId, setSelectedLessonId] = useState(null)

  // Register service worker on mount
  useEffect(() => {
    registerServiceWorker()
  }, [])

  // Prefetch next lessons intelligently
  usePrefetch(allLessons, () => currentLessonIndex)

  return (
    <div>
      <VirtualLessonList 
        lessons={lessons}
        onSelectLesson={setSelectedLessonId}
      />
      
      {selectedLessonId && (
        <Suspense fallback={<LessonSkeleton />}>
          <LessonContent lesson={selectedLesson} />
        </Suspense>
      )}
    </div>
  )
}
```

This combines:
- ✅ Network-aware loading
- ✅ Service worker caching
- ✅ Code splitting with Suspense
- ✅ Virtual scrolling
- ✅ Prefetching
- ✅ Skeleton loading states
