import React, { useState, useEffect } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { Search, Filter, BookOpen, Clock, Users, Star, ChevronLeft, ChevronRight } from 'lucide-react'
import { useTranslation } from 'react-i18next'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const Courses = () => {
  const { t } = useTranslation()
  const [searchParams, setSearchParams] = useSearchParams()
  const [courses, setCourses] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [filterOptions, setFilterOptions] = useState({ track_types: [], levels: [] })
  
  // Pagination state
  const [currentPage, setCurrentPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)
  const [totalCourses, setTotalCourses] = useState(0)
  const limit = 12

  // Filter state
  const [trackType, setTrackType] = useState(searchParams.get('track_type') || '')
  const [level, setLevel] = useState(searchParams.get('level') || '')
  const [searchQuery, setSearchQuery] = useState('')

  const getAuthHeaders = () => {
    const token = localStorage.getItem('token')
    return {
      'Content-Type': 'application/json',
      'Authorization': token ? `Bearer ${token}` : ''
    }
  }

  useEffect(() => {
    fetchFilterOptions()
  }, [])

  useEffect(() => {
    fetchCourses()
  }, [currentPage, trackType, level])

  const fetchFilterOptions = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/courses/filter-options`, {
        headers: getAuthHeaders()
      })
      
      if (response.ok) {
        const data = await response.json()
        setFilterOptions({
          track_types: data.track_types || [],
          levels: data.levels || []
        })
      }
    } catch (err) {
      console.error('Failed to fetch filter options:', err)
      // Fallback to default options
      setFilterOptions({
        track_types: ['Engineering', 'Data Science', 'Design', 'Product Management', 'Business Analytics'],
        levels: ['beginner', 'intermediate', 'advanced']
      })
    }
  }

  const fetchCourses = async () => {
    try {
      setLoading(true)
      setError(null)

      const skip = (currentPage - 1) * limit
      const params = new URLSearchParams({ skip: skip.toString(), limit: limit.toString() })
      if (trackType) params.append('track_type', trackType)
      if (level) params.append('level', level)
      
      const response = await fetch(`${API_BASE_URL}/courses?${params}`, {
        headers: getAuthHeaders()
      })

      if (!response.ok) {
        throw new Error('Failed to fetch courses')
      }

      const data = await response.json()
      
      // Filter by search query client-side if needed
      let filteredCourses = data.items || []
      if (searchQuery) {
        filteredCourses = filteredCourses.filter(c => 
          c.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
          c.description.toLowerCase().includes(searchQuery.toLowerCase())
        )
      }

      setCourses(filteredCourses)
      setTotalCourses(data.total || filteredCourses.length)
      setTotalPages(data.pages || Math.ceil(filteredCourses.length / limit))
      setLoading(false)
    } catch (err) {
      setError('Failed to load courses. Please try again.')
      setLoading(false)
      console.error('Courses fetch error:', err)
    }
  }

  const handleFilterChange = (type, value) => {
    if (type === 'track_type') {
      setTrackType(value)
      setSearchParams(value ? { track_type: value, ...(level && { level }) } : { ...(level && { level }) })
    } else if (type === 'level') {
      setLevel(value)
      setSearchParams(trackType ? { track_type: trackType, ...(value && { level: value }) } : { ...(value && { level: value }) })
    }
    setCurrentPage(1)
  }

  const clearFilters = () => {
    setTrackType('')
    setLevel('')
    setSearchQuery('')
    setSearchParams({})
    setCurrentPage(1)
  }

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
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-gray-900 mb-2">{t('dashboard.exploreCourses')}</h1>
        <p className="text-gray-600">{t('dashboard.exploreCoursesDesc')}</p>
      </div>

      {/* Search and Filters */}
      <div className="bg-white rounded-xl border border-gray-200 p-6 mb-8">
        <div className="flex flex-col md:flex-row gap-4">
          {/* Search */}
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
            <input
              type="text"
              placeholder={t('common.search') + '...'}
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && fetchCourses()}
              className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            />
          </div>

          {/* Track Type Filter */}
          <select
            value={trackType}
            onChange={(e) => handleFilterChange('track_type', e.target.value)}
            className="px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
          >
            <option value="">All Tracks</option>
            {filterOptions.track_types.map(track => (
              <option key={track} value={track}>{track}</option>
            ))}
          </select>

          {/* Level Filter */}
          <select
            value={level}
            onChange={(e) => handleFilterChange('level', e.target.value)}
            className="px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
          >
            <option value="">All Levels</option>
            {filterOptions.levels.map(lvl => (
              <option key={lvl} value={lvl}>{lvl}</option>
            ))}
          </select>

          {/* Clear Filters */}
          {(trackType || level || searchQuery) && (
            <button
              onClick={clearFilters}
              className="px-4 py-3 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
            >
              Clear
            </button>
          )}
        </div>

        {/* Active Filters */}
        {(trackType || level) && (
          <div className="mt-4 flex items-center gap-2">
            <Filter size={16} className="text-gray-400" />
            <span className="text-sm text-gray-500">Active filters:</span>
            {trackType && (
              <span className="px-2 py-1 bg-primary-100 text-primary-700 text-sm rounded-full">
                {trackType}
              </span>
            )}
            {level && (
              <span className="px-2 py-1 bg-secondary-100 text-secondary-700 text-sm rounded-full">
                {level}
              </span>
            )}
          </div>
        )}
      </div>

      {/* Results Count */}
      <div className="mb-4 text-sm text-gray-600">
        Showing {courses.length} of {totalCourses} courses
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
            onClick={fetchCourses}
            className="mt-4 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
          >
            Retry
          </button>
        </div>
      )}

      {/* Courses Grid */}
      {!loading && !error && (
        <>
          {courses.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
              {courses.map(course => (
                <Link
                  key={course.id}
                  to={`/course/${course.id}`}
                  className="group bg-white rounded-xl border border-gray-200 overflow-hidden hover:shadow-lg hover:border-primary-300 transition-all"
                >
                  {/* Course Image Placeholder */}
                  <div className="h-40 bg-gradient-to-br from-primary-100 to-secondary-100 flex items-center justify-center">
                    <BookOpen className="text-primary-400" size={48} />
                  </div>

                  <div className="p-5">
                    {/* Tags */}
                    <div className="flex items-center gap-2 mb-3">
                      <span className="px-2 py-1 bg-gray-100 text-gray-600 text-xs font-medium rounded">
                        {course.track_type}
                      </span>
                      <span className={`px-2 py-1 text-xs font-medium rounded ${getLevelColor(course.level)}`}>
                        {course.level}
                      </span>
                    </div>

                    {/* Title & Description */}
                    <h3 className="text-lg font-bold text-gray-900 mb-2 group-hover:text-primary-600 transition-colors">
                      {course.title}
                    </h3>
                    <p className="text-sm text-gray-600 mb-4 line-clamp-2">
                      {course.description}
                    </p>

                    {/* Meta Info */}
                    <div className="flex items-center justify-between text-sm text-gray-500">
                      <div className="flex items-center gap-1">
                        <Clock size={14} />
                        <span>{course.duration_hours}h</span>
                      </div>
                      <div className="flex items-center gap-1">
                        <Users size={14} />
                        <span>{course.enrolled_count}</span>
                      </div>
                      <div className="flex items-center gap-1">
                        <Star size={14} className="text-yellow-500" />
                        <span>{course.rating}</span>
                      </div>
                    </div>
                  </div>
                </Link>
              ))}
            </div>
          ) : (
            <div className="bg-gray-50 rounded-xl p-12 text-center">
              <BookOpen className="mx-auto text-gray-300 mb-4" size={48} />
              <h3 className="text-lg font-semibold text-gray-700 mb-2">No courses found</h3>
              <p className="text-gray-500 mb-4">Try adjusting your filters or search terms.</p>
              <button
                onClick={clearFilters}
                className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
              >
                Clear Filters
              </button>
            </div>
          )}

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex items-center justify-center gap-2">
              <button
                onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                disabled={currentPage === 1}
                className="p-2 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <ChevronLeft size={20} />
              </button>

              {Array.from({ length: totalPages }, (_, i) => i + 1).map(page => (
                <button
                  key={page}
                  onClick={() => setCurrentPage(page)}
                  className={`w-10 h-10 rounded-lg font-medium transition-colors ${
                    currentPage === page
                      ? 'bg-primary-600 text-white'
                      : 'border border-gray-300 hover:bg-gray-50'
                  }`}
                >
                  {page}
                </button>
              ))}

              <button
                onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                disabled={currentPage === totalPages}
                className="p-2 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <ChevronRight size={20} />
              </button>
            </div>
          )}
        </>
      )}
    </div>
  )
}

export default Courses
