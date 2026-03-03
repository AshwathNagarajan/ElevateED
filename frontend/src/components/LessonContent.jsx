import React, { useState, useEffect, Suspense, lazy } from 'react'
import { Loader, CheckCircle2, Circle, HelpCircle, BookOpen, AlertCircle } from 'lucide-react'
import { useIntersectionObserver } from '../hooks/useIntersectionObserver'
import LazyImage from './LazyImage'

/**
 * LessonContent component with lazy loading
 * Fetches detailed lesson content on demand instead of loading all lessons upfront
 * Lazy loads media content and uses Suspense for smooth loading states
 */
const LessonContent = ({ 
  lesson, 
  isCompleted, 
  onMarkComplete, 
  isMarking 
}) => {
  const [ref, isVisible] = useIntersectionObserver({ threshold: 0.1, rootMargin: '100px' })
  const [detailedLesson, setDetailedLesson] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  // Lazy load full lesson details when visible
  useEffect(() => {
    if (!isVisible || !lesson) return

    // Only fetch if we don't have the full details yet
    if (detailedLesson?.id === lesson.id) return

    const fetchLessonDetails = async () => {
      try {
        setLoading(true)
        setError(null)

        // Simulate API call - replace with actual endpoint
        // const response = await fetch(`/api/lessons/${lesson.id}`, {
        //   headers: {
        //     'Authorization': `Bearer ${localStorage.getItem('token')}`
        //   }
        // })
        // const data = await response.json()

        // Simulate network delay and add more detailed content
        await new Promise(resolve => setTimeout(resolve, 300))
        
        setDetailedLesson({
          ...lesson,
          fullContent: `<h3>Learning Objectives</h3>
<ul>
  <li>Understand the fundamental concepts</li>
  <li>Apply knowledge to real-world scenarios</li>
  <li>Practice problem-solving</li>
</ul>

<h3>Key Concepts</h3>
<p>${lesson.content}</p>

<h3>Summary</h3>
<p>This comprehensive lesson covers all essential aspects of the topic, providing both theoretical foundation and practical applications.</p>`,
          resources: [
            { type: 'pdf', name: 'Lesson Notes', url: '#' },
            { type: 'link', name: 'External Reading', url: '#' },
            { type: 'code', name: 'Code Examples', url: '#' }
          ],
          prerequisites: ['Previous Lesson 1', 'Previous Lesson 2']
        })

        setLoading(false)
      } catch (err) {
        setError('Failed to load lesson details')
        setLoading(false)
      }
    }

    fetchLessonDetails()
  }, [isVisible, lesson, detailedLesson])

  if (!lesson) {
    return null
  }

  return (
    <div ref={ref} className="space-y-6">
      {/* Lesson Card */}
      <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
        {/* Video/Image Section - Lazy loaded */}
        <div className="bg-gray-900 aspect-video flex items-center justify-center relative overflow-hidden">
          {isVisible ? (
            <LazyImage
              src={lesson.video_url || 'https://via.placeholder.com/1280x720?text=Lesson+Video'}
              alt={lesson.title}
              className="w-full h-full"
              placeholderColor="bg-gray-900"
            />
          ) : (
            <div className="w-full h-full bg-gradient-to-br from-gray-800 to-gray-900 flex items-center justify-center">
              <div className="text-center">
                <div className="w-20 h-20 bg-white/10 rounded-full flex items-center justify-center mx-auto mb-4">
                  <BookOpen className="text-white" size={40} />
                </div>
                <p className="text-white text-lg font-semibold">{lesson.title}</p>
                <p className="text-gray-400 text-sm mt-2">{lesson.duration_minutes} minutes</p>
              </div>
            </div>
          )}
        </div>

        {/* Lesson Info */}
        <div className="p-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">{lesson.title}</h2>
          
          {/* Loading State */}
          {loading && (
            <div className="flex items-center justify-center py-8">
              <Loader className="animate-spin text-primary-600 mr-2" size={20} />
              <span className="text-gray-600">Loading lesson content...</span>
            </div>
          )}

          {/* Error State */}
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6 flex items-start gap-3">
              <AlertCircle className="text-red-600 flex-shrink-0 mt-0.5" size={20} />
              <div>
                <p className="text-red-800 font-semibold">Error Loading Lesson</p>
                <p className="text-red-700 text-sm mt-1">{error}</p>
              </div>
            </div>
          )}

          {/* Content - Only render when loaded */}
          {!loading && !error && detailedLesson && (
            <>
              <div className="prose prose-sm max-w-none mb-6">
                <p className="text-gray-600">{lesson.content}</p>
              </div>

              {/* Learning Objectives and Key Concepts */}
              {detailedLesson.fullContent && (
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
                  <h3 className="font-semibold text-blue-900 mb-3">Lesson Overview</h3>
                  <div className="text-blue-800 text-sm space-y-2">
                    <p><strong>Duration:</strong> {lesson.duration_minutes} minutes</p>
                    {detailedLesson.prerequisites && detailedLesson.prerequisites.length > 0 && (
                      <div>
                        <strong>Prerequisites:</strong>
                        <ul className="list-disc list-inside mt-1">
                          {detailedLesson.prerequisites.map((prereq, idx) => (
                            <li key={idx}>{prereq}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Resources Section */}
              {detailedLesson.resources && detailedLesson.resources.length > 0 && (
                <div className="border-t border-gray-200 pt-6">
                  <h3 className="font-semibold text-gray-900 mb-4">Lesson Resources</h3>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    {detailedLesson.resources.map((resource, idx) => (
                      <a
                        key={idx}
                        href={resource.url}
                        className="p-3 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors flex items-center gap-2"
                      >
                        <span className="text-sm font-medium text-gray-700">{resource.name}</span>
                        <span className="text-xs bg-gray-100 px-2 py-1 rounded text-gray-600">
                          {resource.type}
                        </span>
                      </a>
                    ))}
                  </div>
                </div>
              )}

              {/* Action Buttons */}
              <div className="border-t border-gray-200 pt-6 mt-6">
                <div className="flex flex-col sm:flex-row gap-4">
                  {/* Mark Complete Button */}
                  <button
                    onClick={() => onMarkComplete(lesson.id)}
                    disabled={isCompleted || isMarking}
                    className={`flex-1 py-3 px-6 rounded-lg font-semibold transition-colors flex items-center justify-center gap-2 ${
                      isCompleted
                        ? 'bg-green-50 text-green-700 border border-green-200 cursor-default'
                        : 'bg-primary-600 text-white hover:bg-primary-700'
                    }`}
                  >
                    {isMarking ? (
                      <>
                        <Loader size={18} className="animate-spin" />
                        Marking...
                      </>
                    ) : isCompleted ? (
                      <>
                        <CheckCircle2 size={18} />
                        Completed
                      </>
                    ) : (
                      'Mark as Complete'
                    )}
                  </button>

                  {/* Quiz Button */}
                  {lesson.has_quiz && (
                    <button className="flex-1 py-3 px-6 rounded-lg font-semibold bg-secondary-100 text-secondary-700 hover:bg-secondary-200 transition-colors flex items-center justify-center gap-2 border border-secondary-300">
                      <HelpCircle size={18} />
                      Take Quiz
                    </button>
                  )}
                </div>
              </div>
            </>
          )}

          {/* Initial Loading Placeholder */}
          {!loading && !detailedLesson && !error && (
            <div className="animate-pulse space-y-4">
              <div className="h-4 bg-gray-200 rounded w-full"></div>
              <div className="h-4 bg-gray-200 rounded w-5/6"></div>
              <div className="h-4 bg-gray-200 rounded w-4/6"></div>
            </div>
          )}
        </div>
      </div>

      {/* Metadata Cards */}
      {!loading && detailedLesson && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="bg-blue-50 rounded-lg border border-blue-200 p-4">
            <h4 className="font-semibold text-blue-900 mb-2">Lesson Duration</h4>
            <p className="text-blue-700">{lesson.duration_minutes} minutes</p>
          </div>
          <div className="bg-purple-50 rounded-lg border border-purple-200 p-4">
            <h4 className="font-semibold text-purple-900 mb-2">Status</h4>
            <p className="text-purple-700 flex items-center gap-2">
              {isCompleted ? (
                <>
                  <CheckCircle2 size={18} className="text-green-600" />
                  <span>Completed</span>
                </>
              ) : (
                <>
                  <Circle size={18} className="text-yellow-600" />
                  <span>In Progress</span>
                </>
              )}
            </p>
          </div>
        </div>
      )}
    </div>
  )
}

export default LessonContent
