import React, { useState, useEffect } from 'react'
import { Loader, CheckCircle2, Circle, HelpCircle, BookOpen, AlertCircle, FileText, Lightbulb, PenLine } from 'lucide-react'
import { useIntersectionObserver } from '../hooks/useIntersectionObserver'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'

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
  const [quizzes, setQuizzes] = useState([])
  const [selectedAnswers, setSelectedAnswers] = useState({})
  const [quizFeedback, setQuizFeedback] = useState(null)
  const [loading, setLoading] = useState(false)
  const [quizLoading, setQuizLoading] = useState(false)
  const [submittingQuiz, setSubmittingQuiz] = useState(false)
  const [error, setError] = useState(null)

  const getAuthHeaders = () => {
    const token = localStorage.getItem('token')
    return {
      'Content-Type': 'application/json',
      'Authorization': token ? `Bearer ${token}` : ''
    }
  }

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
          fullContent: lesson.content,
          resources: [
            { type: 'notes', name: 'Concept Notes', url: '#' },
            { type: 'practice', name: 'Worked Practice', url: '#' },
            { type: 'quiz', name: 'Quick Check', url: '#' }
          ],
          prerequisites: ['Read the previous concept note', 'Try one solved example']
        })

        setLoading(false)
      } catch (err) {
        setError('Failed to load lesson details')
        setLoading(false)
      }
    }

    fetchLessonDetails()
  }, [isVisible, lesson, detailedLesson])

  useEffect(() => {
    if (!isVisible || !lesson?.id) return

    const startLesson = async () => {
      try {
        await fetch(`${API_BASE_URL}/lessons/${lesson.id}/start`, {
          method: 'POST',
          headers: getAuthHeaders()
        })
        window.dispatchEvent(new CustomEvent('learning-progress-updated'))
      } catch {
        // Already-started lessons return 400; that is still a valid tracked state.
      }
    }

    startLesson()
  }, [isVisible, lesson?.id])

  useEffect(() => {
    setQuizFeedback(null)
    setSelectedAnswers({})
    setQuizzes([])

    if (!isVisible || !lesson?.has_quiz) return

    const fetchQuizzes = async () => {
      try {
        setQuizLoading(true)
        const response = await fetch(`${API_BASE_URL}/quizzes/lessons/${lesson.id}`, {
          headers: getAuthHeaders()
        })
        if (response.ok) {
          setQuizzes(await response.json())
        }
      } catch (err) {
        console.warn('Failed to load lesson quizzes:', err)
      } finally {
        setQuizLoading(false)
      }
    }

    fetchQuizzes()
  }, [isVisible, lesson?.id, lesson?.has_quiz])

  const handleQuizSubmit = async (quiz) => {
    const selected = selectedAnswers[quiz.id]
    if (!selected) {
      setQuizFeedback({ type: 'warning', message: 'Choose an answer before submitting.' })
      return
    }

    try {
      setSubmittingQuiz(true)
      const response = await fetch(`${API_BASE_URL}/quizzes/${quiz.id}/submit`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify({ selected_answer: selected })
      })
      if (!response.ok) {
        throw new Error('Could not submit quiz answer')
      }
      const result = await response.json()
      setQuizFeedback({
        type: result.is_correct ? 'success' : 'retry',
        message: result.is_correct
          ? 'Nice work. Your answer was correct and your learning pattern was updated.'
          : 'Good attempt. Review the lesson once, then try the next question with a calmer pace.',
      })
      window.dispatchEvent(new CustomEvent('learning-progress-updated'))
    } catch (err) {
      setQuizFeedback({ type: 'error', message: err.message || 'Quiz submission failed.' })
    } finally {
      setSubmittingQuiz(false)
    }
  }

  if (!lesson) {
    return null
  }

  return (
    <div ref={ref} className="space-y-6">
      {/* Lesson Card */}
      <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
        <div className="border-b border-gray-200 bg-gradient-to-br from-cyan-300/15 via-white/10 to-amber-300/10 p-6">
          <div className="mb-4 flex items-center gap-3">
            <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-cyan-300 text-slate-950">
              <FileText size={24} />
            </div>
            <div>
              <p className="text-xs font-bold uppercase text-cyan-100">Notes lesson</p>
              <h2 className="text-2xl font-black text-white">{lesson.title}</h2>
            </div>
          </div>
          <p className="max-w-3xl text-sm leading-6 text-slate-300">
            Read the notes, follow the explanation, then answer the quick quiz. ElevateED uses these signals to tune the next recommendation.
          </p>
        </div>

        {/* Lesson Info */}
        <div className="p-6">
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
                <div className="rounded-lg border border-gray-200 bg-gray-50 p-5">
                  <div className="mb-3 flex items-center gap-2">
                    <BookOpen size={18} className="text-cyan-300" />
                    <h3 className="font-bold text-gray-900">Study Notes</h3>
                  </div>
                  <p className="whitespace-pre-line text-sm leading-7 text-gray-600">{lesson.content}</p>
                </div>
              </div>

              {/* Learning Objectives and Key Concepts */}
              {detailedLesson.fullContent && (
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
                  <h3 className="font-semibold text-blue-900 mb-3 flex items-center gap-2">
                    <Lightbulb size={18} />
                    Explanation Flow
                  </h3>
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
                  <h3 className="font-semibold text-gray-900 mb-4 flex items-center gap-2">
                    <PenLine size={18} className="text-amber-300" />
                    Notes Toolkit
                  </h3>
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

              {/* Practice Quiz */}
              {lesson.has_quiz && (
                <div className="border-t border-gray-200 pt-6 mt-6">
                  <h3 className="font-semibold text-gray-900 mb-2">Quick Check</h3>
                  <p className="text-sm text-gray-600 mb-4">
                    A short quiz helps ElevateED understand what support you need next.
                  </p>

                  {quizLoading && (
                    <div className="flex items-center gap-2 text-sm text-gray-500">
                      <Loader size={16} className="animate-spin" />
                      Loading quiz...
                    </div>
                  )}

                  {!quizLoading && quizzes.slice(0, 1).map((quiz) => (
                    <div key={quiz.id} className="rounded-xl border border-gray-200 bg-gray-50 p-4">
                      <p className="font-semibold text-gray-900 mb-4">{quiz.question}</p>
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                        {[
                          ['a', quiz.option_a],
                          ['b', quiz.option_b],
                          ['c', quiz.option_c],
                          ['d', quiz.option_d],
                        ].map(([value, label]) => (
                          <label
                            key={value}
                            className={`flex items-center gap-3 rounded-lg border p-3 text-sm cursor-pointer transition-colors ${
                              selectedAnswers[quiz.id] === value
                                ? 'border-sky-400 bg-sky-50 text-sky-900'
                                : 'border-gray-200 bg-white text-gray-700 hover:border-sky-200'
                            }`}
                          >
                            <input
                              type="radio"
                              name={`quiz-${quiz.id}`}
                              value={value}
                              checked={selectedAnswers[quiz.id] === value}
                              onChange={() => setSelectedAnswers({ ...selectedAnswers, [quiz.id]: value })}
                              className="text-sky-600"
                            />
                            <span>{label}</span>
                          </label>
                        ))}
                      </div>
                      <button
                        onClick={() => handleQuizSubmit(quiz)}
                        disabled={submittingQuiz}
                        className="mt-4 btn-primary inline-flex items-center justify-center gap-2"
                      >
                        {submittingQuiz && <Loader size={16} className="animate-spin" />}
                        Submit answer
                      </button>
                    </div>
                  ))}

                  {quizFeedback && (
                    <div className={`mt-4 rounded-lg border p-3 text-sm ${
                      quizFeedback.type === 'success'
                        ? 'bg-green-50 border-green-200 text-green-700'
                        : quizFeedback.type === 'warning'
                          ? 'bg-amber-50 border-amber-200 text-amber-700'
                          : 'bg-rose-50 border-rose-200 text-rose-700'
                    }`}>
                      {quizFeedback.message}
                    </div>
                  )}
                </div>
              )}

              {/* Action Buttons */}
              <div className="border-t border-gray-200 pt-6 mt-6">
                <div className="flex flex-col sm:flex-row gap-4">
                  {/* Mark Complete Button */}
                  <button
                    onClick={async () => {
                      await onMarkComplete(lesson.id)
                      window.dispatchEvent(new CustomEvent('learning-progress-updated'))
                    }}
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

                  {lesson.has_quiz && (
                    <div className="flex-1 py-3 px-6 rounded-lg font-semibold bg-secondary-50 text-secondary-700 border border-secondary-200 flex items-center justify-center gap-2">
                      <HelpCircle size={18} />
                      Quiz available above
                    </div>
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
