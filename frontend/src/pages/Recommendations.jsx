import React, { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { 
  Lightbulb, 
  BookOpen, 
  TrendingUp, 
  AlertTriangle,
  Star,
  Clock,
  ArrowRight,
  RefreshCw,
  Target
} from 'lucide-react'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const Recommendations = () => {
  const { t } = useTranslation()
  const [recommendations, setRecommendations] = useState([])
  const [courseRecommendations, setCourseRecommendations] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const getAuthHeaders = () => {
    const token = localStorage.getItem('token')
    return {
      'Content-Type': 'application/json',
      'Authorization': token ? `Bearer ${token}` : ''
    }
  }

  useEffect(() => {
    fetchRecommendations()
  }, [])

  const fetchRecommendations = async () => {
    try {
      setLoading(true)
      setError(null)

      // Fetch skill-based recommendations
      let skillRecommendations = []
      try {
        const skillResponse = await fetch(`${API_BASE_URL}/recommendations/my-recommendations`, {
          headers: getAuthHeaders()
        })
        if (skillResponse.ok) {
          skillRecommendations = await skillResponse.json()
        }
      } catch (e) {
        console.warn('Skill recommendations endpoint not available')
      }

      // Fetch course recommendations (not enrolled courses for the user)
      let courseRecs = []
      try {
        // Fetch user's enrollments to exclude already enrolled courses
        const enrollmentsResponse = await fetch(`${API_BASE_URL}/enrollments/my-enrollments`, {
          headers: getAuthHeaders()
        })
        const enrolledCourseIds = new Set()
        if (enrollmentsResponse.ok) {
          const enrollments = await enrollmentsResponse.json()
          enrollments.forEach(e => enrolledCourseIds.add(e.course_id))
        }

        const courseResponse = await fetch(`${API_BASE_URL}/courses?limit=10`, {
          headers: getAuthHeaders()
        })
        if (courseResponse.ok) {
          const data = await courseResponse.json()
          // Filter out already enrolled courses and limit to 6
          courseRecs = (data.items || [])
            .filter(course => !enrolledCourseIds.has(course.id))
            .slice(0, 6)
            .map((course) => ({
              id: course.id,
              course_id: course.id,
              title: course.title,
              description: course.description,
              track_type: course.track_type,
              level: course.level,
              duration_hours: course.duration_hours || 0,
              rating: course.rating || null,
              reason: 'Explore new topics'
            }))
        }
      } catch (e) {
        console.warn('Course recommendations fetch failed')
      }

      // No fake defaults - let the UI show empty state for new users

      setRecommendations(skillRecommendations)
      setCourseRecommendations(courseRecs)
      setLoading(false)
    } catch (err) {
      console.error('Recommendations fetch error:', err)
      setError('Failed to load recommendations')
      setLoading(false)
    }
  }

  const getTypeIcon = (type) => {
    switch (type) {
      case 'revision': return <BookOpen className="text-blue-600" size={24} />
      case 'next_level': return <TrendingUp className="text-green-600" size={24} />
      case 'foundational_review': return <AlertTriangle className="text-yellow-600" size={24} />
      case 'practice': return <Target className="text-purple-600" size={24} />
      default: return <Lightbulb size={24} />
    }
  }

  const getTypeLabel = (type) => {
    switch (type) {
      case 'revision': return t('recommendations.reviewNeeded')
      case 'next_level': return t('recommendations.readyToAdvance')
      case 'foundational_review': return t('recommendations.strengthenBasics')
      case 'practice': return t('recommendations.recommendation')
      default: return t('recommendations.recommendation')
    }
  }

  const getTypeColor = (type) => {
    switch (type) {
      case 'revision': return 'border-blue-400 bg-blue-50'
      case 'next_level': return 'border-green-400 bg-green-50'
      case 'foundational_review': return 'border-yellow-400 bg-yellow-50'
      case 'practice': return 'border-purple-400 bg-purple-50'
      default: return 'border-gray-400 bg-gray-50'
    }
  }

  const getPriorityBadge = (priority) => {
    switch (priority) {
      case 'high': return 'bg-red-100 text-red-700'
      case 'medium': return 'bg-yellow-100 text-yellow-700'
      case 'low': return 'bg-green-100 text-green-700'
      default: return 'bg-gray-100 text-gray-700'
    }
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      {/* Header */}
      <div className="flex items-start justify-between mb-8">
        <div>
          <h1 className="text-4xl font-bold text-gray-900 mb-2">{t('recommendations.title')}</h1>
          <p className="text-gray-600">{t('recommendations.basedOnProgress')}</p>
        </div>
        <button
          onClick={fetchRecommendations}
          className="flex items-center gap-2 px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
        >
          <RefreshCw size={18} />
          {t('common.retry')}
        </button>
      </div>

      {/* Loading State */}
      {loading && (
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
        </div>
      )}

      {/* Error State */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
          <p className="text-red-700">{error}</p>
          <button
            onClick={fetchRecommendations}
            className="mt-4 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
          >
            Retry
          </button>
        </div>
      )}

      {!loading && !error && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Skill-Based Recommendations */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-xl border border-gray-200 p-6 mb-8">
              <div className="flex items-center gap-2 mb-6">
                <Lightbulb className="text-primary-600" size={24} />
                <h2 className="text-xl font-bold text-gray-900">Learning Insights</h2>
              </div>

              {recommendations.length > 0 ? (
                <div className="space-y-4">
                  {recommendations.map(rec => (
                    <div
                      key={rec.id}
                      className={`p-5 rounded-lg border-l-4 ${getTypeColor(rec.type)}`}
                    >
                      <div className="flex items-start gap-4">
                        <div className="flex-shrink-0 mt-1">
                          {getTypeIcon(rec.type)}
                        </div>
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-2">
                            <span className="text-xs font-bold text-primary-600 uppercase">
                              {getTypeLabel(rec.type)}
                            </span>
                            <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${getPriorityBadge(rec.priority)}`}>
                              {rec.priority} priority
                            </span>
                          </div>
                          <h3 className="font-semibold text-gray-900 mb-1">{rec.module_name}</h3>
                          <p className="text-sm text-gray-600 mb-3">{rec.message}</p>
                          <div className="flex items-center justify-between">
                            <div className="flex items-center gap-2">
                              <span className="text-xs text-gray-500">Current Score:</span>
                              <span className={`text-sm font-bold ${
                                rec.score >= 70 ? 'text-green-600' : 
                                rec.score >= 50 ? 'text-yellow-600' : 'text-red-600'
                              }`}>
                                {rec.score}%
                              </span>
                            </div>
                            <button className="flex items-center gap-1 text-sm text-primary-600 hover:text-primary-700 font-medium">
                              Start Learning
                              <ArrowRight size={14} />
                            </button>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8">
                  <Lightbulb className="mx-auto text-gray-300 mb-4" size={48} />
                  <p className="text-gray-500">Complete more lessons and quizzes to get personalized insights!</p>
                </div>
              )}
            </div>
          </div>

          {/* Course Recommendations Sidebar */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-xl border border-gray-200 p-6 sticky top-4">
              <div className="flex items-center gap-2 mb-6">
                <Star className="text-yellow-500" size={24} />
                <h2 className="text-xl font-bold text-gray-900">Courses to Explore</h2>
              </div>

              {courseRecommendations.length > 0 ? (
                <div className="space-y-4">
                  {courseRecommendations.map(course => (
                    <Link
                      key={course.id}
                      to={`/course/${course.course_id}`}
                      className="block p-4 border border-gray-200 rounded-lg hover:border-primary-300 hover:shadow-md transition-all"
                    >
                      <div className="flex items-center gap-2 mb-2">
                        <span className="px-2 py-0.5 bg-gray-100 text-gray-600 text-xs font-medium rounded">
                          {course.track_type}
                        </span>
                        <span className="px-2 py-0.5 bg-purple-100 text-purple-700 text-xs font-medium rounded">
                          {course.level}
                        </span>
                      </div>

                      <h3 className="font-semibold text-gray-900 mb-1">{course.title}</h3>
                      <p className="text-xs text-gray-500 mb-3 line-clamp-2">{course.description}</p>

                      <div className="flex items-center justify-between text-xs text-gray-500 mb-2">
                        <div className="flex items-center gap-1">
                          <Clock size={12} />
                          <span>{course.duration_hours || 0}h</span>
                        </div>
                        {course.rating && (
                          <div className="flex items-center gap-1">
                            <Star size={12} className="text-yellow-500" />
                            <span>{course.rating}</span>
                          </div>
                        )}
                      </div>

                      <div className="flex items-center justify-between">
                        <span className="text-xs text-primary-600 font-medium">
                          View Course
                        </span>
                        <ArrowRight size={14} className="text-primary-600" />
                      </div>
                    </Link>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8">
                  <BookOpen className="mx-auto text-gray-300 mb-4" size={40} />
                  <p className="text-sm text-gray-500">No course recommendations available yet.</p>
                </div>
              )}

              <Link
                to="/courses"
                className="block mt-4 text-center text-sm text-primary-600 hover:text-primary-700 font-medium"
              >
                Browse All Courses →
              </Link>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default Recommendations
