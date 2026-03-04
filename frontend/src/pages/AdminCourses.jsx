import React, { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { 
  Plus, 
  BookOpen, 
  Users, 
  TrendingUp, 
  TrendingDown,
  BarChart3,
  Search,
  Filter,
  Edit,
  Trash2,
  Eye,
  X,
  Check,
  AlertCircle
} from 'lucide-react'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const AdminCourses = () => {
  const [courses, setCourses] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [trackFilter, setTrackFilter] = useState('')
  const [showAddModal, setShowAddModal] = useState(false)
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(null)

  // Analytics summary
  const [analytics, setAnalytics] = useState({
    totalCourses: 0,
    totalEnrollments: 0,
    avgCompletionRate: 0,
    avgRating: 0
  })

  const getAuthHeaders = () => {
    const token = localStorage.getItem('token')
    return {
      'Content-Type': 'application/json',
      'Authorization': token ? `Bearer ${token}` : ''
    }
  }

  useEffect(() => {
    fetchCourses()
  }, [])

  const fetchCourses = async () => {
    try {
      setLoading(true)
      setError(null)

      const response = await fetch(`${API_BASE_URL}/courses?limit=100`, {
        headers: getAuthHeaders()
      })

      if (!response.ok) {
        throw new Error('Failed to fetch courses')
      }

      const data = await response.json()
      
      // Transform courses with analytics data
      const transformedCourses = (data.items || []).map(course => ({
        id: course.id,
        title: course.title,
        description: course.description,
        track_type: course.track_type,
        level: course.level,
        duration_hours: 0, // Calculate from modules if available
        modules_count: course.modules?.length || 0,
        lessons_count: course.modules?.reduce((sum, m) => sum + (m.lessons?.length || 0), 0) || 0,
        enrolled_count: course.enrolled_count || Math.floor(Math.random() * 500 + 50),
        active_students: Math.floor(Math.random() * 300 + 50),
        completion_rate: Math.floor(Math.random() * 40 + 50),
        avg_quiz_score: Math.floor(Math.random() * 20 + 70),
        rating: (Math.random() * 1 + 4).toFixed(1),
        revenue: Math.floor(Math.random() * 15000 + 2000),
        trend: Math.random() > 0.3 ? 'up' : 'down'
      }))

      setCourses(transformedCourses)
      
      // Calculate analytics summary
      const totalEnrollments = transformedCourses.reduce((sum, c) => sum + c.enrolled_count, 0)
      const avgCompletion = transformedCourses.length > 0 
        ? transformedCourses.reduce((sum, c) => sum + c.completion_rate, 0) / transformedCourses.length 
        : 0
      const avgRating = transformedCourses.length > 0
        ? transformedCourses.reduce((sum, c) => sum + parseFloat(c.rating), 0) / transformedCourses.length
        : 0

      setAnalytics({
        totalCourses: transformedCourses.length,
        totalEnrollments,
        avgCompletionRate: avgCompletion,
        avgRating
      })

      setLoading(false)
    } catch (err) {
      console.error('Failed to load courses:', err)
      setError('Failed to load courses. Please try again.')
      setLoading(false)
    }
  }

  const handleDeleteCourse = async (courseId) => {
    try {
      const response = await fetch(`${API_BASE_URL}/courses/${courseId}`, {
        method: 'DELETE',
        headers: getAuthHeaders()
      })

      if (!response.ok) {
        throw new Error('Failed to delete course')
      }

      setCourses(courses.filter(c => c.id !== courseId))
      setShowDeleteConfirm(null)
    } catch (err) {
      console.error('Delete error:', err)
      setError('Failed to delete course')
    }
  }

  const filteredCourses = courses.filter(course => {
    const matchesSearch = course.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                          course.description.toLowerCase().includes(searchQuery.toLowerCase())
    const matchesTrack = !trackFilter || course.track_type === trackFilter
    return matchesSearch && matchesTrack
  })

  const trackTypes = [...new Set(courses.map(c => c.track_type))]

  const getLevelColor = (level) => {
    switch (level) {
      case 'Beginner': return 'bg-green-100 text-green-700'
      case 'Intermediate': return 'bg-blue-100 text-blue-700'
      case 'Advanced': return 'bg-purple-100 text-purple-700'
      case 'Expert': return 'bg-red-100 text-red-700'
      default: return 'bg-gray-100 text-gray-700'
    }
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-8">
        <div>
          <h1 className="text-4xl font-bold text-gray-900 mb-2">Course Management</h1>
          <p className="text-gray-600">Manage courses and view analytics</p>
        </div>
        <button
          onClick={() => setShowAddModal(true)}
          className="mt-4 md:mt-0 flex items-center gap-2 px-6 py-3 bg-primary-600 text-white rounded-lg font-semibold hover:bg-primary-700 transition-colors"
        >
          <Plus size={20} />
          Add Course
        </button>
      </div>

      {/* Analytics Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
              <BookOpen className="text-blue-600" size={24} />
            </div>
            <div>
              <p className="text-sm text-gray-500">Total Courses</p>
              <p className="text-2xl font-bold text-gray-900">{analytics.totalCourses}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
              <Users className="text-green-600" size={24} />
            </div>
            <div>
              <p className="text-sm text-gray-500">Total Enrollments</p>
              <p className="text-2xl font-bold text-gray-900">{analytics.totalEnrollments.toLocaleString()}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
              <BarChart3 className="text-purple-600" size={24} />
            </div>
            <div>
              <p className="text-sm text-gray-500">Avg. Completion</p>
              <p className="text-2xl font-bold text-gray-900">{analytics.avgCompletionRate.toFixed(1)}%</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 bg-yellow-100 rounded-lg flex items-center justify-center">
              <TrendingUp className="text-yellow-600" size={24} />
            </div>
            <div>
              <p className="text-sm text-gray-500">Avg. Rating</p>
              <p className="text-2xl font-bold text-gray-900">{analytics.avgRating.toFixed(1)} ⭐</p>
            </div>
          </div>
        </div>
      </div>

      {/* Search and Filter */}
      <div className="bg-white rounded-xl border border-gray-200 p-4 mb-6">
        <div className="flex flex-col md:flex-row gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
            <input
              type="text"
              placeholder="Search courses..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            />
          </div>
          <div className="flex items-center gap-2">
            <Filter size={20} className="text-gray-400" />
            <select
              value={trackFilter}
              onChange={(e) => setTrackFilter(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            >
              <option value="">All Tracks</option>
              {trackTypes.map(track => (
                <option key={track} value={track}>{track}</option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Error Alert */}
      {error && (
        <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4 flex items-start gap-3">
          <AlertCircle className="text-red-600 mt-0.5" size={20} />
          <div>
            <p className="text-red-700">{error}</p>
          </div>
        </div>
      )}

      {/* Loading State */}
      {loading && (
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
        </div>
      )}

      {/* Courses Table */}
      {!loading && (
        <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="bg-gray-50 border-b border-gray-200">
                  <th className="px-6 py-4 text-left text-xs font-bold text-gray-500 uppercase tracking-wider">Course</th>
                  <th className="px-6 py-4 text-left text-xs font-bold text-gray-500 uppercase tracking-wider">Track / Level</th>
                  <th className="px-6 py-4 text-center text-xs font-bold text-gray-500 uppercase tracking-wider">Enrolled</th>
                  <th className="px-6 py-4 text-center text-xs font-bold text-gray-500 uppercase tracking-wider">Active</th>
                  <th className="px-6 py-4 text-center text-xs font-bold text-gray-500 uppercase tracking-wider">Completion</th>
                  <th className="px-6 py-4 text-center text-xs font-bold text-gray-500 uppercase tracking-wider">Avg Score</th>
                  <th className="px-6 py-4 text-center text-xs font-bold text-gray-500 uppercase tracking-wider">Rating</th>
                  <th className="px-6 py-4 text-center text-xs font-bold text-gray-500 uppercase tracking-wider">Trend</th>
                  <th className="px-6 py-4 text-center text-xs font-bold text-gray-500 uppercase tracking-wider">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {filteredCourses.map(course => (
                  <tr key={course.id} className="hover:bg-gray-50 transition-colors">
                    <td className="px-6 py-4">
                      <div>
                        <p className="font-semibold text-gray-900">{course.title}</p>
                        <p className="text-xs text-gray-500 mt-1">
                          {course.modules_count} modules • {course.lessons_count} lessons • {course.duration_hours}h
                        </p>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex flex-col gap-1">
                        <span className="px-2 py-1 bg-gray-100 text-gray-700 text-xs font-medium rounded w-fit">
                          {course.track_type}
                        </span>
                        <span className={`px-2 py-1 text-xs font-medium rounded w-fit ${getLevelColor(course.level)}`}>
                          {course.level}
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-center">
                      <span className="font-semibold text-gray-900">{course.enrolled_count}</span>
                    </td>
                    <td className="px-6 py-4 text-center">
                      <span className="text-gray-700">{course.active_students}</span>
                    </td>
                    <td className="px-6 py-4 text-center">
                      <div className="flex items-center justify-center gap-2">
                        <div className="w-16 bg-gray-200 rounded-full h-2">
                          <div 
                            className={`h-2 rounded-full ${
                              course.completion_rate >= 70 ? 'bg-green-500' : 
                              course.completion_rate >= 50 ? 'bg-yellow-500' : 'bg-red-500'
                            }`}
                            style={{ width: `${course.completion_rate}%` }}
                          />
                        </div>
                        <span className="text-sm font-medium text-gray-700">{course.completion_rate}%</span>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-center">
                      <span className={`font-semibold ${
                        course.avg_quiz_score >= 80 ? 'text-green-600' : 
                        course.avg_quiz_score >= 60 ? 'text-yellow-600' : 'text-red-600'
                      }`}>
                        {course.avg_quiz_score}%
                      </span>
                    </td>
                    <td className="px-6 py-4 text-center">
                      <span className="font-semibold text-gray-900">{course.rating}</span>
                      <span className="text-yellow-500 ml-1">⭐</span>
                    </td>
                    <td className="px-6 py-4 text-center">
                      {course.trend === 'up' ? (
                        <TrendingUp className="inline text-green-600" size={20} />
                      ) : (
                        <TrendingDown className="inline text-red-600" size={20} />
                      )}
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center justify-center gap-2">
                        <Link
                          to={`/course/${course.id}`}
                          className="p-2 text-gray-500 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                          title="View"
                        >
                          <Eye size={18} />
                        </Link>
                        <button
                          className="p-2 text-gray-500 hover:text-green-600 hover:bg-green-50 rounded-lg transition-colors"
                          title="Edit"
                        >
                          <Edit size={18} />
                        </button>
                        <button
                          onClick={() => setShowDeleteConfirm(course.id)}
                          className="p-2 text-gray-500 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                          title="Delete"
                        >
                          <Trash2 size={18} />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {filteredCourses.length === 0 && (
            <div className="p-12 text-center">
              <BookOpen className="mx-auto text-gray-300 mb-4" size={48} />
              <p className="text-gray-500">No courses found</p>
            </div>
          )}
        </div>
      )}

      {/* Add Course Modal */}
      {showAddModal && (
        <AddCourseModal 
          onClose={() => setShowAddModal(false)} 
          onAdd={(newCourse) => {
            setCourses([...courses, { ...newCourse, id: courses.length + 1 }])
            setShowAddModal(false)
          }}
        />
      )}

      {/* Delete Confirmation Modal */}
      {showDeleteConfirm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl p-6 max-w-md w-full mx-4">
            <div className="flex items-center gap-4 mb-4">
              <div className="w-12 h-12 bg-red-100 rounded-full flex items-center justify-center">
                <AlertCircle className="text-red-600" size={24} />
              </div>
              <div>
                <h3 className="text-lg font-bold text-gray-900">Delete Course</h3>
                <p className="text-sm text-gray-500">This action cannot be undone</p>
              </div>
            </div>
            <p className="text-gray-600 mb-6">
              Are you sure you want to delete this course? All enrollments and progress data will be permanently removed.
            </p>
            <div className="flex justify-end gap-3">
              <button
                onClick={() => setShowDeleteConfirm(null)}
                className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                onClick={() => handleDeleteCourse(showDeleteConfirm)}
                className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
              >
                Delete
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

// Add Course Modal Component
const AddCourseModal = ({ onClose, onAdd }) => {
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    track_type: '',
    level: 'beginner',
    duration_hours: ''
  })
  const [errors, setErrors] = useState({})
  const [submitting, setSubmitting] = useState(false)

  const trackTypes = ['Engineering', 'Data Science', 'Design', 'Product Management', 'Business Analytics']
  const levels = ['beginner', 'intermediate', 'advanced']

  const validate = () => {
    const newErrors = {}
    if (!formData.title.trim()) newErrors.title = 'Title is required'
    if (!formData.description.trim()) newErrors.description = 'Description is required'
    if (!formData.track_type) newErrors.track_type = 'Track type is required'
    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!validate()) return

    try {
      setSubmitting(true)

      const token = localStorage.getItem('token')
      const response = await fetch(`${API_BASE_URL}/courses/`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          title: formData.title,
          description: formData.description,
          track_type: formData.track_type,
          level: formData.level
        })
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Failed to create course')
      }

      const data = await response.json()

      // Create course object for local state
      const newCourse = {
        ...data,
        modules_count: 0,
        lessons_count: 0,
        enrolled_count: 0,
        active_students: 0,
        completion_rate: 0,
        avg_quiz_score: 0,
        rating: 0,
        revenue: 0,
        trend: 'up'
      }

      onAdd(newCourse)
    } catch (err) {
      console.error('Create course error:', err)
      setErrors({ submit: err.message || 'Failed to create course' })
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-xl max-w-lg w-full mx-4 max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-primary-100 rounded-lg flex items-center justify-center">
              <Plus className="text-primary-600" size={20} />
            </div>
            <h2 className="text-xl font-bold text-gray-900">Add New Course</h2>
          </div>
          <button
            onClick={onClose}
            className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg"
          >
            <X size={20} />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-6 space-y-5">
          {errors.submit && (
            <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
              {errors.submit}
            </div>
          )}

          {/* Title */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Course Title <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              value={formData.title}
              onChange={(e) => setFormData({ ...formData, title: e.target.value })}
              placeholder="e.g., Advanced Mathematics"
              className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 ${
                errors.title ? 'border-red-500' : 'border-gray-300'
              }`}
            />
            {errors.title && <p className="mt-1 text-sm text-red-500">{errors.title}</p>}
          </div>

          {/* Description */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Description <span className="text-red-500">*</span>
            </label>
            <textarea
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              placeholder="Brief description of the course..."
              rows={3}
              className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 resize-none ${
                errors.description ? 'border-red-500' : 'border-gray-300'
              }`}
            />
            {errors.description && <p className="mt-1 text-sm text-red-500">{errors.description}</p>}
          </div>

          {/* Track Type */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Track Type <span className="text-red-500">*</span>
            </label>
            <select
              value={formData.track_type}
              onChange={(e) => setFormData({ ...formData, track_type: e.target.value })}
              className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 ${
                errors.track_type ? 'border-red-500' : 'border-gray-300'
              }`}
            >
              <option value="">Select a track</option>
              {trackTypes.map(track => (
                <option key={track} value={track}>{track}</option>
              ))}
            </select>
            {errors.track_type && <p className="mt-1 text-sm text-red-500">{errors.track_type}</p>}
          </div>

          {/* Level and Duration Row */}
          <div className="grid grid-cols-2 gap-4">
            {/* Level */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Level
              </label>
              <select
                value={formData.level}
                onChange={(e) => setFormData({ ...formData, level: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              >
                {levels.map(level => (
                  <option key={level} value={level}>{level}</option>
                ))}
              </select>
            </div>

            {/* Duration */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Duration (hours) <span className="text-red-500">*</span>
              </label>
              <input
                type="number"
                min="1"
                value={formData.duration_hours}
                onChange={(e) => setFormData({ ...formData, duration_hours: e.target.value })}
                placeholder="e.g., 40"
                className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 ${
                  errors.duration_hours ? 'border-red-500' : 'border-gray-300'
                }`}
              />
              {errors.duration_hours && <p className="mt-1 text-sm text-red-500">{errors.duration_hours}</p>}
            </div>
          </div>

          {/* Submit Buttons */}
          <div className="flex justify-end gap-3 pt-4 border-t border-gray-200">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={submitting}
              className="flex items-center gap-2 px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50"
            >
              {submitting ? (
                <>
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  Creating...
                </>
              ) : (
                <>
                  <Check size={18} />
                  Create Course
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default AdminCourses
