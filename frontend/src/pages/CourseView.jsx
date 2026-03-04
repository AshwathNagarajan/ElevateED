import React, { useState, useEffect, Suspense } from 'react'
import { useParams, Link, useNavigate } from 'react-router-dom'
import { 
  ChevronDown, 
  ChevronUp, 
  ChevronLeft,
  BookOpen, 
  AlertCircle, 
  Loader,
  Clock,
  Users,
  Star,
  CheckCircle2,
  Play
} from 'lucide-react'
import LessonListItem from '../components/LessonListItem'
import LessonContent from '../components/LessonContent'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const CourseView = () => {
  const { id } = useParams()
  const navigate = useNavigate()
  const [course, setCourse] = useState(null)
  const [expandedModuleId, setExpandedModuleId] = useState(null)
  const [completedLessons, setCompletedLessons] = useState(new Set())
  const [selectedLesson, setSelectedLesson] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [markingComplete, setMarkingComplete] = useState(null)
  const [isEnrolled, setIsEnrolled] = useState(false)

  const getAuthHeaders = () => {
    const token = localStorage.getItem('token')
    return {
      'Content-Type': 'application/json',
      'Authorization': token ? `Bearer ${token}` : ''
    }
  }

  useEffect(() => {
    fetchCourseData()
  }, [id])

  const fetchCourseData = async () => {
    try {
      setLoading(true)
      setError(null)

      const response = await fetch(`${API_BASE_URL}/courses/${id}`, {
        headers: getAuthHeaders()
      })
      
      if (!response.ok) {
        throw new Error('Failed to fetch course')
      }

      const data = await response.json()

      // Transform to expected format
      const transformedCourse = {
        id: data.id,
        title: data.title,
        description: data.description,
        track_type: data.track_type,
        level: data.level,
        duration_hours: data.modules?.reduce((sum, m) => 
          sum + (m.lessons?.reduce((s, l) => s + (l.duration_minutes || 0), 0) || 0), 0) / 60 || 0,
        enrolled_count: data.enrolled_count || 0,
        rating: data.rating || 4.5,
        instructor: data.instructor || 'ElevateED Instructor',
        progress_percentage: 0,
        modules: data.modules?.map(m => ({
          id: m.id,
          title: m.title,
          order_number: m.order_number,
          lessons: m.lessons?.map(l => ({
            id: l.id,
            title: l.title,
            content: l.content,
            video_url: l.video_url,
            duration_minutes: l.duration_minutes,
            completed: false,
            has_quiz: l.quizzes?.length > 0,
            quiz_id: l.quizzes?.[0]?.id || null
          })) || []
        })) || []
      }

      setCourse(transformedCourse)

      // Check enrollment status
      try {
        const enrollResponse = await fetch(`${API_BASE_URL}/enrollments/my-courses`, {
          headers: getAuthHeaders()
        })
        if (enrollResponse.ok) {
          const enrollments = await enrollResponse.json()
          const enrolled = enrollments.some(e => e.course_id === parseInt(id))
          setIsEnrolled(enrolled)
        }
      } catch (e) {
        console.error('Failed to check enrollment:', e)
      }

      // Auto-expand first module
      if (transformedCourse.modules.length > 0) {
        setExpandedModuleId(transformedCourse.modules[0].id)
      }

      setLoading(false)
    } catch (err) {
      console.error('Course fetch error:', err)
      setError('Failed to load course. Please try again.')
      setLoading(false)
    }
  }

  const handleMarkComplete = async (lessonId) => {
    try {
      setMarkingComplete(lessonId)

      const response = await fetch(`${API_BASE_URL}/lessons/${lessonId}/complete`, {
        method: 'POST',
        headers: getAuthHeaders()
      })

      if (!response.ok) {
        console.warn('Failed to mark lesson complete on server')
      }

      const newCompleted = new Set(completedLessons)
      newCompleted.add(lessonId)
      setCompletedLessons(newCompleted)

      // Update progress
      if (course) {
        const totalLessons = course.modules.reduce((sum, m) => sum + m.lessons.length, 0)
        const completedCount = newCompleted.size
        const newProgress = Math.round((completedCount / totalLessons) * 100)
        
        setCourse({
          ...course,
          progress_percentage: newProgress
        })
      }

      setMarkingComplete(null)
    } catch (err) {
      console.error('Mark complete error:', err)
      setError('Failed to mark lesson as complete')
      setMarkingComplete(null)
    }
  }

  const handleEnroll = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/enrollments/`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify({ course_id: parseInt(id) })
      })

      if (!response.ok) {
        throw new Error('Failed to enroll')
      }

      setIsEnrolled(true)
    } catch (err) {
      console.error('Enroll error:', err)
      setError('Failed to enroll in course')
    }
  }

  const toggleModule = (moduleId) => {
    setExpandedModuleId(expandedModuleId === moduleId ? null : moduleId)
  }

  const getTotalLessons = () => {
    return course?.modules.reduce((sum, m) => sum + m.lessons.length, 0) || 0
  }

  const getCompletedCount = () => {
    return completedLessons.size
  }

  if (loading) {
    return (
      <div className="flex justify-center items-center h-96">
        <div className="text-center">
          <Loader className="animate-spin h-12 w-12 text-primary-600 mx-auto mb-4" />
          <p className="text-gray-600 text-lg">Loading course...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="max-w-6xl mx-auto px-4 py-8">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6 flex items-start gap-4">
          <AlertCircle className="text-red-600 mt-0.5 flex-shrink-0" size={24} />
          <div>
            <h3 className="font-semibold text-red-800 text-lg">Error Loading Course</h3>
            <p className="text-red-700 mt-1">{error}</p>
            <button onClick={fetchCourseData} className="mt-4 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700">
              Try Again
            </button>
          </div>
        </div>
      </div>
    )
  }

  if (!course) {
    return (
      <div className="max-w-6xl mx-auto px-4 py-8 text-center">
        <BookOpen className="mx-auto text-gray-300 mb-4" size={64} />
        <h2 className="text-2xl font-bold text-gray-700 mb-2">Course not found</h2>
        <p className="text-gray-500 mb-4">The course you're looking for doesn't exist.</p>
        <Link to="/courses" className="text-primary-600 hover:underline">
          Browse all courses
        </Link>
      </div>
    )
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      {/* Back Button */}
      <button
        onClick={() => navigate(-1)}
        className="flex items-center gap-2 text-gray-600 hover:text-gray-900 mb-6"
      >
        <ChevronLeft size={20} />
        Back
      </button>

      {/* Course Header */}
      <div className="mb-8">
        <div className="flex flex-col lg:flex-row lg:items-start lg:justify-between gap-6 mb-6">
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-2">
              <span className="px-2 py-1 bg-gray-100 text-gray-600 text-sm font-medium rounded">
                {course.track_type}
              </span>
              <span className="px-2 py-1 bg-purple-100 text-purple-700 text-sm font-medium rounded">
                {course.level}
              </span>
            </div>
            <h1 className="text-4xl font-bold text-gray-900 mb-3">{course.title}</h1>
            <p className="text-gray-600 max-w-2xl mb-4">{course.description}</p>
            
            <div className="flex flex-wrap items-center gap-4 text-sm text-gray-500">
              <div className="flex items-center gap-1">
                <Clock size={16} />
                <span>{course.duration_hours} hours</span>
              </div>
              <div className="flex items-center gap-1">
                <Users size={16} />
                <span>{course.enrolled_count} enrolled</span>
              </div>
              <div className="flex items-center gap-1">
                <Star size={16} className="text-yellow-500" />
                <span>{course.rating}</span>
              </div>
              <span>by {course.instructor}</span>
            </div>
          </div>

          {/* Enroll Button */}
          {!isEnrolled && (
            <button
              onClick={handleEnroll}
              className="px-8 py-3 bg-primary-600 text-white font-semibold rounded-lg hover:bg-primary-700 transition-colors"
            >
              Enroll Now
            </button>
          )}
        </div>

        {/* Progress Bar (if enrolled) */}
        {isEnrolled && (
          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <div className="flex items-center justify-between mb-3">
              <h3 className="font-semibold text-gray-900">Your Progress</h3>
              <span className="text-sm font-bold text-primary-600">
                {getCompletedCount()} of {getTotalLessons()} lessons completed
              </span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-4 overflow-hidden">
              <div
                className="bg-gradient-to-r from-primary-500 to-primary-600 h-full transition-all duration-300 flex items-center justify-center"
                style={{ width: `${course.progress_percentage}%` }}
              >
                {course.progress_percentage > 10 && (
                  <span className="text-xs font-bold text-white">{course.progress_percentage}%</span>
                )}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Main Content */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Modules Sidebar */}
        <div className="lg:col-span-1">
          <div className="bg-white rounded-lg border border-gray-200 sticky top-4">
            <div className="p-4 border-b border-gray-200">
              <h2 className="font-semibold text-gray-900">Course Content</h2>
              <p className="text-xs text-gray-500 mt-1">{course.modules.length} modules • {getTotalLessons()} lessons</p>
            </div>
            
            <div className="divide-y divide-gray-200 max-h-[calc(100vh-200px)] overflow-y-auto">
              {course.modules.map((module) => (
                <div key={module.id}>
                  <button
                    onClick={() => toggleModule(module.id)}
                    className="w-full px-4 py-3 flex items-center justify-between hover:bg-gray-50 transition-colors text-left"
                  >
                    <div className="flex-1">
                      <span className="font-semibold text-sm text-gray-900">{module.title}</span>
                      <p className="text-xs text-gray-500 mt-0.5">{module.lessons.length} lessons</p>
                    </div>
                    {expandedModuleId === module.id ? (
                      <ChevronUp size={18} className="text-gray-400" />
                    ) : (
                      <ChevronDown size={18} className="text-gray-400" />
                    )}
                  </button>

                  {expandedModuleId === module.id && (
                    <div className="bg-gray-50">
                      {module.lessons.map((lesson) => (
                        <LessonListItem
                          key={lesson.id}
                          lesson={lesson}
                          isSelected={selectedLesson?.id === lesson.id}
                          isCompleted={completedLessons.has(lesson.id)}
                          onSelect={setSelectedLesson}
                        />
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Lesson Content */}
        <div className="lg:col-span-3">
          {selectedLesson ? (
            <Suspense fallback={
              <div className="bg-white rounded-lg border border-gray-200 p-12 flex items-center justify-center">
                <Loader className="animate-spin text-primary-600 mr-3" size={24} />
                <span className="text-gray-600 font-medium">Loading lesson...</span>
              </div>
            }>
              <LessonContent
                lesson={selectedLesson}
                isCompleted={completedLessons.has(selectedLesson.id)}
                onMarkComplete={handleMarkComplete}
                isMarking={markingComplete === selectedLesson.id}
              />
            </Suspense>
          ) : (
            <div className="bg-white rounded-lg border border-gray-200 p-12 text-center">
              <Play className="mx-auto text-gray-300 mb-4" size={64} />
              <h3 className="text-xl font-semibold text-gray-700 mb-2">Ready to learn?</h3>
              <p className="text-gray-500">Select a lesson from the sidebar to get started</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default CourseView
