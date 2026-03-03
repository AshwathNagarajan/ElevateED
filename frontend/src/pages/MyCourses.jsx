import React, { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { 
  BookOpen, 
  CheckCircle2, 
  Clock, 
  Play, 
  ArrowRight,
  Filter,
  GraduationCap
} from 'lucide-react'

const MyCourses = () => {
  const [enrollments, setEnrollments] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [filter, setFilter] = useState('all') // all, in_progress, completed

  useEffect(() => {
    fetchEnrollments()
  }, [])

  const fetchEnrollments = async () => {
    try {
      setLoading(true)
      setError(null)

      // TODO: Replace with actual API call
      // const response = await fetch('/api/enrollments/my-courses', {
      //   headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      // })
      // const data = await response.json()

      // Mock data
      const mockEnrollments = [
        { 
          id: 1, 
          course_id: 1, 
          course: { 
            id: 1,
            title: 'Advanced Mathematics', 
            track_type: 'Math',
            level: 'Advanced',
            duration_hours: 40,
            description: 'Master calculus, linear algebra, and differential equations.'
          }, 
          progress_percentage: 65, 
          status: 'in_progress',
          enrolled_at: '2024-02-15T10:00:00',
          last_accessed: '2024-03-03T14:30:00'
        },
        { 
          id: 2, 
          course_id: 2, 
          course: { 
            id: 2,
            title: 'Physics Fundamentals', 
            track_type: 'Science',
            level: 'Beginner',
            duration_hours: 30,
            description: 'Learn classical mechanics and thermodynamics.'
          }, 
          progress_percentage: 45, 
          status: 'in_progress',
          enrolled_at: '2024-02-20T09:00:00',
          last_accessed: '2024-03-02T11:15:00'
        },
        { 
          id: 3, 
          course_id: 3, 
          course: { 
            id: 3,
            title: 'English Literature', 
            track_type: 'Language',
            level: 'Intermediate',
            duration_hours: 25,
            description: 'Explore classic and modern literature.'
          }, 
          progress_percentage: 100, 
          status: 'completed',
          enrolled_at: '2024-01-10T08:00:00',
          completed_at: '2024-02-28T16:45:00'
        },
        { 
          id: 4, 
          course_id: 4, 
          course: { 
            id: 4,
            title: 'Introduction to Programming', 
            track_type: 'Technology',
            level: 'Beginner',
            duration_hours: 35,
            description: 'Learn programming fundamentals with Python.'
          }, 
          progress_percentage: 100, 
          status: 'completed',
          enrolled_at: '2024-01-05T10:00:00',
          completed_at: '2024-02-10T14:20:00'
        },
      ]

      setEnrollments(mockEnrollments)
      setLoading(false)
    } catch (err) {
      setError('Failed to load your courses')
      setLoading(false)
    }
  }

  const getProgressColor = (percentage) => {
    if (percentage >= 80) return 'bg-green-500'
    if (percentage >= 60) return 'bg-blue-500'
    if (percentage >= 40) return 'bg-yellow-500'
    return 'bg-red-500'
  }

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    })
  }

  const filteredEnrollments = enrollments.filter(enrollment => {
    if (filter === 'all') return true
    if (filter === 'in_progress') return enrollment.status === 'in_progress'
    if (filter === 'completed') return enrollment.status === 'completed'
    return true
  })

  const stats = {
    total: enrollments.length,
    inProgress: enrollments.filter(e => e.status === 'in_progress').length,
    completed: enrollments.filter(e => e.status === 'completed').length
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-gray-900 mb-2">My Courses</h1>
        <p className="text-gray-600">Track your learning progress and continue where you left off</p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
              <BookOpen className="text-blue-600" size={24} />
            </div>
            <div>
              <p className="text-sm text-gray-500">Total Enrolled</p>
              <p className="text-2xl font-bold text-gray-900">{stats.total}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 bg-yellow-100 rounded-lg flex items-center justify-center">
              <Clock className="text-yellow-600" size={24} />
            </div>
            <div>
              <p className="text-sm text-gray-500">In Progress</p>
              <p className="text-2xl font-bold text-gray-900">{stats.inProgress}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
              <CheckCircle2 className="text-green-600" size={24} />
            </div>
            <div>
              <p className="text-sm text-gray-500">Completed</p>
              <p className="text-2xl font-bold text-gray-900">{stats.completed}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Filter Tabs */}
      <div className="flex items-center gap-4 mb-6">
        <Filter size={20} className="text-gray-400" />
        <div className="flex gap-2">
          {[
            { key: 'all', label: 'All Courses' },
            { key: 'in_progress', label: 'In Progress' },
            { key: 'completed', label: 'Completed' }
          ].map(tab => (
            <button
              key={tab.key}
              onClick={() => setFilter(tab.key)}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                filter === tab.key
                  ? 'bg-primary-600 text-white'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>
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
            onClick={fetchEnrollments}
            className="mt-4 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
          >
            Retry
          </button>
        </div>
      )}

      {/* Courses List */}
      {!loading && !error && (
        <>
          {filteredEnrollments.length > 0 ? (
            <div className="space-y-4">
              {filteredEnrollments.map(enrollment => (
                <div
                  key={enrollment.id}
                  className="bg-white rounded-xl border border-gray-200 p-6 hover:shadow-lg transition-shadow"
                >
                  <div className="flex flex-col lg:flex-row lg:items-center gap-6">
                    {/* Course Image */}
                    <div className="w-full lg:w-48 h-32 bg-gradient-to-br from-primary-100 to-secondary-100 rounded-lg flex items-center justify-center flex-shrink-0">
                      <GraduationCap className="text-primary-400" size={40} />
                    </div>

                    {/* Course Info */}
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <span className="px-2 py-1 bg-gray-100 text-gray-600 text-xs font-medium rounded">
                          {enrollment.course.track_type}
                        </span>
                        <span className="px-2 py-1 bg-purple-100 text-purple-700 text-xs font-medium rounded">
                          {enrollment.course.level}
                        </span>
                        {enrollment.status === 'completed' && (
                          <span className="px-2 py-1 bg-green-100 text-green-700 text-xs font-medium rounded flex items-center gap-1">
                            <CheckCircle2 size={12} />
                            Completed
                          </span>
                        )}
                      </div>

                      <h3 className="text-xl font-bold text-gray-900 mb-2">
                        {enrollment.course.title}
                      </h3>
                      <p className="text-sm text-gray-600 mb-4">
                        {enrollment.course.description}
                      </p>

                      {/* Progress */}
                      <div className="mb-4">
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-sm font-medium text-gray-600">Progress</span>
                          <span className="text-sm font-bold text-primary-600">
                            {enrollment.progress_percentage}%
                          </span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
                          <div
                            className={`${getProgressColor(enrollment.progress_percentage)} h-full transition-all duration-300`}
                            style={{ width: `${enrollment.progress_percentage}%` }}
                          />
                        </div>
                      </div>

                      {/* Meta */}
                      <div className="flex flex-wrap items-center gap-4 text-xs text-gray-500">
                        <span>Enrolled: {formatDate(enrollment.enrolled_at)}</span>
                        {enrollment.status === 'completed' ? (
                          <span>Completed: {formatDate(enrollment.completed_at)}</span>
                        ) : (
                          <span>Last accessed: {formatDate(enrollment.last_accessed)}</span>
                        )}
                        <span>{enrollment.course.duration_hours} hours</span>
                      </div>
                    </div>

                    {/* Action Button */}
                    <div className="flex-shrink-0">
                      <Link
                        to={`/course/${enrollment.course.id}`}
                        className={`flex items-center gap-2 px-6 py-3 rounded-lg font-semibold transition-colors ${
                          enrollment.status === 'completed'
                            ? 'bg-green-100 text-green-700 hover:bg-green-200'
                            : 'bg-primary-600 text-white hover:bg-primary-700'
                        }`}
                      >
                        {enrollment.status === 'completed' ? (
                          <>
                            Review
                            <ArrowRight size={18} />
                          </>
                        ) : (
                          <>
                            <Play size={18} />
                            Continue
                          </>
                        )}
                      </Link>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="bg-gray-50 rounded-xl p-12 text-center">
              <GraduationCap className="mx-auto text-gray-300 mb-4" size={64} />
              <h3 className="text-xl font-semibold text-gray-700 mb-2">
                {filter === 'all' 
                  ? "You haven't enrolled in any courses yet"
                  : filter === 'in_progress'
                    ? "No courses in progress"
                    : "No completed courses"
                }
              </h3>
              <p className="text-gray-500 mb-6">
                {filter === 'all' 
                  ? "Start your learning journey by exploring our courses."
                  : "Check out our courses to continue learning."
                }
              </p>
              <Link
                to="/courses"
                className="inline-flex items-center gap-2 px-6 py-3 bg-primary-600 text-white rounded-lg font-semibold hover:bg-primary-700"
              >
                <BookOpen size={20} />
                Explore Courses
              </Link>
            </div>
          )}
        </>
      )}
    </div>
  )
}

export default MyCourses
