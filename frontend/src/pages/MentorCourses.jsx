import React, { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { BookOpen, Users, TrendingUp, Award, Eye } from 'lucide-react'
import { useTranslation } from 'react-i18next'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'

const MentorCourses = () => {
  const { t } = useTranslation()
  const [courses, setCourses] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [stats, setStats] = useState(null)

  const getAuthHeaders = () => {
    const token = localStorage.getItem('token')
    return {
      'Content-Type': 'application/json',
      'Authorization': token ? `Bearer ${token}` : ''
    }
  }

  useEffect(() => {
    fetchMentorData()
  }, [])

  const fetchMentorData = async () => {
    try {
      setLoading(true)
      setError(null)

      // Fetch mentor dashboard data (includes course stats)
      const dashboardRes = await fetch(`${API_BASE_URL}/analytics/mentor/dashboard`, {
        headers: getAuthHeaders()
      })

      if (dashboardRes.ok) {
        const dashboardData = await dashboardRes.json()
        setStats(dashboardData)
        setCourses(dashboardData.courses || [])
      } else {
        // Fallback to just courses
        const coursesRes = await fetch(`${API_BASE_URL}/mentors/my-courses`, {
          headers: getAuthHeaders()
        })
        if (coursesRes.ok) {
          const coursesData = await coursesRes.json()
          setCourses(coursesData)
        }
      }

      setLoading(false)
    } catch (err) {
      setError('Failed to load courses. Please try again.')
      setLoading(false)
      console.error('Error fetching mentor courses:', err)
    }
  }

  const getLevelColor = (level) => {
    switch (level?.toLowerCase()) {
      case 'beginner': return 'bg-green-100 text-green-700'
      case 'intermediate': return 'bg-blue-100 text-blue-700'
      case 'advanced': return 'bg-purple-100 text-purple-700'
      default: return 'bg-gray-100 text-gray-700'
    }
  }

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="flex items-center justify-center min-h-[400px]">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="text-center py-12">
          <p className="text-red-600">{error}</p>
          <button
            onClick={fetchMentorData}
            className="mt-4 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700"
          >
            Retry
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          {t('mentor.yourCourses', 'Your Courses')}
        </h1>
        <p className="text-gray-600">
          Manage and monitor the courses you are teaching
        </p>
      </div>

      {/* Stats Overview */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <div className="bg-white rounded-xl border border-gray-200 p-5">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
                <BookOpen className="w-5 h-5 text-purple-600" />
              </div>
              <div>
                <p className="text-2xl font-bold text-gray-900">{stats.total_courses}</p>
                <p className="text-sm text-gray-500">Total Courses</p>
              </div>
            </div>
          </div>
          <div className="bg-white rounded-xl border border-gray-200 p-5">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                <Users className="w-5 h-5 text-blue-600" />
              </div>
              <div>
                <p className="text-2xl font-bold text-gray-900">{stats.total_students}</p>
                <p className="text-sm text-gray-500">Total Students</p>
              </div>
            </div>
          </div>
          <div className="bg-white rounded-xl border border-gray-200 p-5">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
                <TrendingUp className="w-5 h-5 text-green-600" />
              </div>
              <div>
                <p className="text-2xl font-bold text-gray-900">{stats.overall_completion_rate}%</p>
                <p className="text-sm text-gray-500">Completion Rate</p>
              </div>
            </div>
          </div>
          <div className="bg-white rounded-xl border border-gray-200 p-5">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-orange-100 rounded-lg flex items-center justify-center">
                <Award className="w-5 h-5 text-orange-600" />
              </div>
              <div>
                <p className="text-2xl font-bold text-gray-900">{stats.overall_avg_quiz_score?.toFixed(1)}%</p>
                <p className="text-sm text-gray-500">Avg Quiz Score</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Courses Grid */}
      {courses.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {courses.map((course) => (
            <div
              key={course.course_id || course.id}
              className="bg-white rounded-xl border border-gray-200 overflow-hidden hover:shadow-lg transition-shadow"
            >
              {/* Course Header */}
              <div className="h-32 bg-gradient-to-br from-purple-500 to-purple-700 p-4 relative">
                <div className="absolute top-3 right-3">
                  <span className={`px-2 py-1 text-xs font-medium rounded-full ${getLevelColor(course.level)}`}>
                    {course.level}
                  </span>
                </div>
                <div className="absolute bottom-3 left-4 right-4">
                  <h3 className="text-lg font-semibold text-white line-clamp-2">
                    {course.course_title || course.title}
                  </h3>
                </div>
              </div>

              {/* Course Content */}
              <div className="p-4">
                {/* Track Type */}
                <div className="mb-4">
                  <span className="text-sm text-purple-600 font-medium">
                    {course.track_type}
                  </span>
                </div>

                {/* Stats */}
                <div className="grid grid-cols-2 gap-3 mb-4">
                  <div className="bg-gray-50 rounded-lg p-3">
                    <div className="flex items-center gap-2 text-gray-600">
                      <Users size={16} />
                      <span className="text-sm">Enrolled</span>
                    </div>
                    <p className="text-xl font-bold text-gray-900 mt-1">
                      {course.total_enrollments || 0}
                    </p>
                  </div>
                  <div className="bg-gray-50 rounded-lg p-3">
                    <div className="flex items-center gap-2 text-gray-600">
                      <TrendingUp size={16} />
                      <span className="text-sm">Completed</span>
                    </div>
                    <p className="text-xl font-bold text-green-600 mt-1">
                      {course.completed_count || 0}
                    </p>
                  </div>
                </div>

                {/* Progress Bar */}
                {course.completion_rate !== undefined && (
                  <div className="mb-4">
                    <div className="flex justify-between text-sm mb-1">
                      <span className="text-gray-600">Completion Rate</span>
                      <span className="font-medium text-gray-900">{course.completion_rate}%</span>
                    </div>
                    <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-purple-600 rounded-full transition-all"
                        style={{ width: `${Math.min(course.completion_rate, 100)}%` }}
                      />
                    </div>
                  </div>
                )}

                {/* Quiz Stats */}
                {course.avg_quiz_score !== undefined && (
                  <div className="flex items-center justify-between py-2 border-t border-gray-100">
                    <span className="text-sm text-gray-600">Avg Quiz Score</span>
                    <span className={`font-semibold ${
                      course.avg_quiz_score >= 70 ? 'text-green-600' :
                      course.avg_quiz_score >= 50 ? 'text-yellow-600' : 'text-red-600'
                    }`}>
                      {course.avg_quiz_score}%
                    </span>
                  </div>
                )}

                {/* Actions */}
                <div className="flex gap-2 mt-4">
                  <Link
                    to={`/course/${course.course_id || course.id}`}
                    className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
                  >
                    <Eye size={16} />
                    View Course
                  </Link>
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="bg-white rounded-xl border border-gray-200 p-12 text-center">
          <BookOpen className="w-16 h-16 text-gray-300 mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-gray-900 mb-2">No Courses Assigned</h3>
          <p className="text-gray-500">
            You do not have any courses assigned yet. Contact an administrator to get courses assigned to you.
          </p>
        </div>
      )}
    </div>
  )
}

export default MentorCourses
