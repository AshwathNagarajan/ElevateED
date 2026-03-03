import React, { useState, useEffect, Suspense } from 'react'
import { ChevronDown, ChevronUp, BookOpen, AlertCircle, Loader } from 'lucide-react'
import LessonListItem from './LessonListItem'
import LessonContent from './LessonContent'

const CourseView = () => {
  const [courseId] = useState(1) // In real app, get from URL params
  const [course, setCourse] = useState(null)
  const [expandedModuleId, setExpandedModuleId] = useState(null)
  const [completedLessons, setCompletedLessons] = useState(new Set())
  const [selectedLesson, setSelectedLesson] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [markingComplete, setMarkingComplete] = useState(null)

  useEffect(() => {
    fetchCourseData()
  }, [courseId])

  const fetchCourseData = async () => {
    try {
      setLoading(true)
      setError(null)

      // Mock course data
      const mockCourse = {
        id: 1,
        title: 'Advanced Mathematics',
        description: 'Master advanced mathematical concepts including calculus, linear algebra, and differential equations.',
        track_type: 'Math',
        level: 'Advanced',
        progress_percentage: 45,
        modules: [
          {
            id: 1,
            title: 'Calculus Fundamentals',
            order_number: 1,
            lessons: [
              {
                id: 1,
                title: 'Introduction to Limits',
                content: 'Learn about the concept of limits and their importance in calculus.',
                video_url: 'https://example.com/video1.mp4',
                duration_minutes: 12,
                completed: true,
                has_quiz: true,
                quiz_id: 1
              },
              {
                id: 2,
                title: 'Derivatives Explained',
                content: 'Understanding derivatives and their applications.',
                video_url: 'https://example.com/video2.mp4',
                duration_minutes: 18,
                completed: true,
                has_quiz: true,
                quiz_id: 2
              },
              {
                id: 3,
                title: 'Power Rule and Chain Rule',
                content: 'Master the power rule and chain rule for derivatives.',
                video_url: 'https://example.com/video3.mp4',
                duration_minutes: 15,
                completed: false,
                has_quiz: true,
                quiz_id: 3
              }
            ]
          },
          {
            id: 2,
            title: 'Integration and Applications',
            order_number: 2,
            lessons: [
              {
                id: 4,
                title: 'Introduction to Integration',
                content: 'Learn the basics of integration and antiderivatives.',
                video_url: 'https://example.com/video4.mp4',
                duration_minutes: 20,
                completed: false,
                has_quiz: true,
                quiz_id: 4
              },
              {
                id: 5,
                title: 'Integration Techniques',
                content: 'Advanced integration techniques including substitution and parts.',
                video_url: 'https://example.com/video5.mp4',
                duration_minutes: 22,
                completed: false,
                has_quiz: true,
                quiz_id: 5
              }
            ]
          },
          {
            id: 3,
            title: 'Applications of Calculus',
            order_number: 3,
            lessons: [
              {
                id: 6,
                title: 'Optimization Problems',
                content: 'Solve real-world optimization problems using calculus.',
                video_url: 'https://example.com/video6.mp4',
                duration_minutes: 25,
                completed: false,
                has_quiz: true,
                quiz_id: 6
              }
            ]
          }
        ]
      }

      // TODO: Replace with actual API call
      // const response = await fetch(`/courses/${courseId}`, {
      //   headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      // })
      // const data = await response.json()
      // setCourse(data)

      // Initialize completed lessons from mock data
      const completed = new Set()
      mockCourse.modules.forEach(module => {
        module.lessons.forEach(lesson => {
          if (lesson.completed) {
            completed.add(lesson.id)
          }
        })
      })
      setCompletedLessons(completed)
      
      setCourse(mockCourse)
      setExpandedModuleId(mockCourse.modules[0].id)
      setSelectedLesson(mockCourse.modules[0].lessons[0])
      setLoading(false)
    } catch (err) {
      setError(err.message)
      setLoading(false)
    }
  }

  const handleMarkComplete = async (lessonId) => {
    try {
      setMarkingComplete(lessonId)

      // TODO: Replace with actual API call
      // const response = await fetch(`/lessons/${lessonId}/complete`, {
      //   method: 'POST',
      //   headers: {
      //     'Authorization': `Bearer ${localStorage.getItem('token')}`,
      //     'Content-Type': 'application/json'
      //   }
      // })
      // const data = await response.json()

      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 500))

      const newCompleted = new Set(completedLessons)
      newCompleted.add(lessonId)
      setCompletedLessons(newCompleted)

      // Update progress percentage
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
            <button
              onClick={fetchCourseData}
              className="btn-primary mt-4"
            >
              Try Again
            </button>
          </div>
        </div>
      </div>
    )
  }

  if (!course) {
    return <p className="text-center py-8 text-gray-500">Course not found</p>
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      {/* Header with Progress */}
      <div className="mb-8">
        <div className="flex items-start justify-between mb-4">
          <div>
            <h1 className="text-4xl font-bold text-gray-900 mb-2">{course.title}</h1>
            <p className="text-gray-600 max-w-2xl">{course.description}</p>
          </div>
          <div className="text-right">
            <span className="inline-block px-4 py-2 bg-primary-100 text-primary-700 rounded-full text-sm font-semibold mb-2">
              {course.level}
            </span>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-3">
            <h3 className="font-semibold text-gray-900">Course Progress</h3>
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
      </div>

      {/* Main Content */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Modules Sidebar */}
        <div className="lg:col-span-1">
          <div className="bg-white rounded-lg border border-gray-200 sticky top-4">
            <div className="p-4 border-b border-gray-200">
              <h2 className="font-semibold text-gray-900">Course Content</h2>
              <p className="text-xs text-gray-500 mt-1">{course.modules.length} modules</p>
            </div>
            
            <div className="divide-y divide-gray-200 max-h-96 overflow-y-auto">
              {course.modules.map((module) => (
                <div key={module.id}>
                  <button
                    onClick={() => toggleModule(module.id)}
                    className="w-full px-4 py-3 flex items-center justify-between hover:bg-gray-50 transition-colors text-left"
                  >
                    <span className="font-semibold text-sm text-gray-900">{module.title}</span>
                    {expandedModuleId === module.id ? (
                      <ChevronUp size={18} className="text-gray-400" />
                    ) : (
                      <ChevronDown size={18} className="text-gray-400" />
                    )}
                  </button>

                  {expandedModuleId === module.id && (
                    <div className="bg-gray-50 divide-y divide-gray-200">
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

        {/* Lesson Content with Lazy Loading */}
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
              <BookOpen className="text-gray-300 mx-auto mb-4" size={48} />
              <p className="text-gray-500 text-lg">Select a lesson to view content</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default CourseView
