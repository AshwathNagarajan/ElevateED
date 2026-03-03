import React, { useState, useEffect } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { Search, Filter, BookOpen, Clock, Users, Star, ChevronLeft, ChevronRight } from 'lucide-react'

const Courses = () => {
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

  useEffect(() => {
    fetchFilterOptions()
  }, [])

  useEffect(() => {
    fetchCourses()
  }, [currentPage, trackType, level])

  const fetchFilterOptions = async () => {
    try {
      // TODO: Replace with actual API call
      // const response = await fetch('/api/courses/filter-options')
      // const data = await response.json()
      
      setFilterOptions({
        track_types: ['Math', 'Science', 'Language', 'Technology', 'Arts'],
        levels: ['Beginner', 'Intermediate', 'Advanced', 'Expert']
      })
    } catch (err) {
      console.error('Failed to fetch filter options:', err)
    }
  }

  const fetchCourses = async () => {
    try {
      setLoading(true)
      setError(null)

      // TODO: Replace with actual API call
      // const skip = (currentPage - 1) * limit
      // const params = new URLSearchParams({ skip, limit })
      // if (trackType) params.append('track_type', trackType)
      // if (level) params.append('level', level)
      // const response = await fetch(`/api/courses?${params}`)
      // const data = await response.json()

      // Mock data
      const mockCourses = [
        { id: 1, title: 'Advanced Mathematics', description: 'Master calculus, linear algebra, and more.', track_type: 'Math', level: 'Advanced', duration_hours: 40, enrolled_count: 234, rating: 4.8 },
        { id: 2, title: 'Physics Fundamentals', description: 'Learn the basics of classical mechanics and thermodynamics.', track_type: 'Science', level: 'Beginner', duration_hours: 30, enrolled_count: 456, rating: 4.6 },
        { id: 3, title: 'English Literature', description: 'Explore classic and modern literature.', track_type: 'Language', level: 'Intermediate', duration_hours: 25, enrolled_count: 187, rating: 4.7 },
        { id: 4, title: 'Web Development', description: 'Build modern web applications with React and Node.js.', track_type: 'Technology', level: 'Intermediate', duration_hours: 50, enrolled_count: 892, rating: 4.9 },
        { id: 5, title: 'Data Science Basics', description: 'Introduction to data analysis and machine learning.', track_type: 'Technology', level: 'Beginner', duration_hours: 35, enrolled_count: 567, rating: 4.5 },
        { id: 6, title: 'Creative Writing', description: 'Develop your storytelling and writing skills.', track_type: 'Arts', level: 'Beginner', duration_hours: 20, enrolled_count: 321, rating: 4.4 },
      ]

      // Filter mock data
      let filtered = mockCourses
      if (trackType) {
        filtered = filtered.filter(c => c.track_type === trackType)
      }
      if (level) {
        filtered = filtered.filter(c => c.level === level)
      }
      if (searchQuery) {
        filtered = filtered.filter(c => 
          c.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
          c.description.toLowerCase().includes(searchQuery.toLowerCase())
        )
      }

      setCourses(filtered)
      setTotalCourses(filtered.length)
      setTotalPages(Math.ceil(filtered.length / limit))
      setLoading(false)
    } catch (err) {
      setError('Failed to load courses')
      setLoading(false)
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
        <h1 className="text-4xl font-bold text-gray-900 mb-2">Explore Courses</h1>
        <p className="text-gray-600">Discover courses to advance your learning journey</p>
      </div>

      {/* Search and Filters */}
      <div className="bg-white rounded-xl border border-gray-200 p-6 mb-8">
        <div className="flex flex-col md:flex-row gap-4">
          {/* Search */}
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
            <input
              type="text"
              placeholder="Search courses..."
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
