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

  useEffect(() => {
    fetchCourseData()
  }, [id])

  const fetchCourseData = async () => {
    try {
      setLoading(true)
      setError(null)

      // TODO: Replace with actual API call
       const response = await fetch(`/api/courses/${id}`, {
       headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      })
      const data = await response.json()

      // Mock course data
      const mockCourse = {
        id: parseInt(id),
        title: 'Advanced Mathematics',
        description: 'Master advanced mathematical concepts including calculus, linear algebra, and differential equations. This comprehensive course covers everything from limits to multivariable calculus.',
        track_type: 'Math',
        level: 'Advanced',
        duration_hours: 40,
        enrolled_count: 234,
        rating: 4.8,
        instructor: 'Dr. Sarah Johnson',
        progress_percentage: 45,
        modules: [
          {
            id: 1,
            title: 'Calculus Fundamentals',
            order_number: 1,
            lessons: [
              { id: 1, title: 'Introduction to Limits', content: 'Learn about the concept of limits and their importance in calculus.', video_url: null, duration_minutes: 12, completed: true, has_quiz: true, quiz_id: 1 },
              { id: 2, title: 'Derivatives Explained', content: 'Understanding derivatives and their applications.', video_url: null, duration_minutes: 18, completed: true, has_quiz: true, quiz_id: 2 },
              { id: 3, title: 'Power Rule and Chain Rule', content: 'Master the power rule and chain rule for derivatives.', video_url: null, duration_minutes: 15, completed: false, has_quiz: true, quiz_id: 3 }
            ]
          },
          {
            id: 2,
            title: 'Integration and Applications',
            order_number: 2,
            lessons: [
              { id: 4, title: 'Introduction to Integration', content: 'Learn the basics of integration and antiderivatives.', video_url: null, duration_minutes: 20, completed: false, has_quiz: true, quiz_id: 4 },
              { id: 5, title: 'Integration Techniques', content: 'Advanced integration techniques including substitution and parts.', video_url: null, duration_minutes: 22, completed: false, has_quiz: true, quiz_id: 5 }
            ]
          },
          {
            id: 3,
            title: 'Applications of Calculus',
            order_number: 3,
            lessons: [
              { id: 6, title: 'Area Under Curves', content: 'Calculate areas using definite integrals.', video_url: null, duration_minutes: 16, completed: false, has_quiz: true, quiz_id: 6 },
              { id: 7, title: 'Volume of Solids', content: 'Learn to calculate volumes of revolution.', video_url: null, duration_minutes: 25, completed: false, has_quiz: false, quiz_id: null }
            ]
          }
        ]
      }

      setCourse(mockCourse)
      setIsEnrolled(true) // Mock enrolled status
      
      // Set completed lessons from course data
      const completed = new Set()
      mockCourse.modules.forEach(module => {
        module.lessons.forEach(lesson => {
          if (lesson.completed) completed.add(lesson.id)
        })
      })
      setCompletedLessons(completed)

      // Auto-expand first module
      if (mockCourse.modules.length > 0) {
        setExpandedModuleId(mockCourse.modules[0].id)
      }

      setLoading(false)
    } catch (err) {
      setError('Failed to load course')
      setLoading(false)
    }
  }

  const handleMarkComplete = async (lessonId) => {
    try {
      setMarkingComplete(lessonId)

      // TODO: Replace with actual API call
      // await fetch(`/api/lessons/${lessonId}/complete`, {
      //   method: 'POST',
      //   headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      // })

      await new Promise(resolve => setTimeout(resolve, 500))

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
      setError('Failed to mark lesson as complete')
      setMarkingComplete(null)
    }
  }

  const handleEnroll = async () => {
    try {
      // TODO: Replace with actual API call
      // await fetch('/api/enrollments/', {
      //   method: 'POST',
      //   headers: {
      //     'Authorization': `Bearer ${localStorage.getItem('token')}`,
      //     'Content-Type': 'application/json'
      //   },
      //   body: JSON.stringify({ course_id: id })
      // })

      setIsEnrolled(true)
    } catch (err) {
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
