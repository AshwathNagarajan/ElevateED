import React, { useState, useEffect } from 'react'
import { Pie, Bar } from 'react-chartjs-2'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js'
import { RefreshCw, AlertCircle, Users, BookOpen, TrendingUp, Award } from 'lucide-react'

// Register ChartJS components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
)

const API_BASE_URL = 'http://localhost:8000/api'

const getAuthHeaders = () => {
  const token = localStorage.getItem('token')
  return {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  }
}

const AdminDashboard = () => {
  const [trackDistribution, setTrackDistribution] = useState([])
  const [courseStats, setCourseStats] = useState([])
  const [overviewStats, setOverviewStats] = useState({
    totalCourses: 0,
    totalEnrollments: 0,
    overallCompletion: 0,
    avgQuizScore: 0
  })
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchAdminData()
  }, [])

  const fetchAdminData = async () => {
    try {
      setLoading(true)
      setError(null)

      // Fetch course completion stats
      let completionData = null
      try {
        const completionRes = await fetch(`${API_BASE_URL}/analytics/course-completion-rate`, {
          headers: getAuthHeaders()
        })
        if (completionRes.ok) {
          completionData = await completionRes.json()
        }
      } catch (e) {
        console.warn('Failed to fetch completion data:', e)
      }

      // Fetch quiz score stats
      try {
        const quizRes = await fetch(`${API_BASE_URL}/analytics/average-quiz-score`, {
          headers: getAuthHeaders()
        })
        if (quizRes.ok) {
          const quizData = await quizRes.json()
          setOverviewStats(prev => ({
            ...prev,
            avgQuizScore: quizData.overall_average_score || 0
          }))
        }
      } catch (e) {
        console.warn('Failed to fetch quiz data:', e)
      }

      // Fetch active learners (for future use)
      try {
        await fetch(`${API_BASE_URL}/analytics/active-learners`, {
          headers: getAuthHeaders()
        })
      } catch (e) {
        console.warn('Failed to fetch active learners:', e)
      }

      // Process course completion data for track distribution
      if (completionData && completionData.courses) {
        // Group courses by track_type
        const trackGroups = {}
        completionData.courses.forEach(course => {
          const track = course.course_title.split(' ')[0] // Simplified track extraction
          if (!trackGroups[track]) {
            trackGroups[track] = 0
          }
          trackGroups[track] += course.total_enrollments
        })
        
        const trackData = Object.entries(trackGroups).map(([track, count]) => ({
          track,
          count
        }))
        setTrackDistribution(trackData)
        setCourseStats(completionData.courses || [])
        
        setOverviewStats(prev => ({
          ...prev,
          totalCourses: completionData.total_courses || 0,
          totalEnrollments: completionData.total_enrollments || 0,
          overallCompletion: completionData.overall_completion_rate || 0
        }))
      }

      setLoading(false)
    } catch (err) {
      setError(err.message)
      setLoading(false)
    }
  }

  const pieChartData = {
    labels: trackDistribution.map(item => item.track),
    datasets: [
      {
        label: 'Students by Track',
        data: trackDistribution.map(item => item.count),
        backgroundColor: [
          '#9333ea',
          '#06b6d4',
          '#10b981',
          '#f59e0b',
          '#ef4444',
          '#ec4899',
        ],
        borderColor: '#fff',
        borderWidth: 2,
      },
    ],
  }

  const pieChartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'right',
      },
      title: {
        display: true,
        text: 'Track Distribution',
      },
    },
  }

  const barChartData = {
    labels: courseStats.slice(0, 8).map(item => item.course_title?.substring(0, 15) + '...' || 'Course'),
    datasets: [
      {
        label: 'Completion Rate (%)',
        data: courseStats.slice(0, 8).map(item => item.completion_rate || 0),
        backgroundColor: '#9333ea',
        borderColor: '#7c3aed',
        borderWidth: 1,
        borderRadius: 6,
      },
    ],
  }

  const barChartOptions = {
    indexAxis: 'x',
    responsive: true,
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: true,
        text: 'Course Completion Rates',
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        max: 100,
      },
    },
  }

  if (loading) {
    return (
      <div className="flex justify-center items-center h-96">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
          <p className="text-gray-600 text-lg">Loading admin dashboard...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <h1 className="section-header text-4xl mb-8">Admin Dashboard</h1>

      {error && (
        <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4 flex items-start gap-3">
          <AlertCircle className="text-red-600 mt-0.5" size={20} />
          <div>
            <h3 className="font-semibold text-red-800">Error</h3>
            <p className="text-red-700">{error}</p>
          </div>
        </div>
      )}

      {/* Overview Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div className="card-lg bg-gradient-to-br from-purple-50 to-purple-100 border border-purple-200">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-purple-600 rounded-lg">
              <BookOpen className="text-white" size={24} />
            </div>
            <div>
              <p className="text-sm text-purple-600 font-medium">Total Courses</p>
              <p className="text-2xl font-bold text-purple-900">{overviewStats.totalCourses}</p>
            </div>
          </div>
        </div>
        
        <div className="card-lg bg-gradient-to-br from-cyan-50 to-cyan-100 border border-cyan-200">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-cyan-600 rounded-lg">
              <Users className="text-white" size={24} />
            </div>
            <div>
              <p className="text-sm text-cyan-600 font-medium">Total Enrollments</p>
              <p className="text-2xl font-bold text-cyan-900">{overviewStats.totalEnrollments}</p>
            </div>
          </div>
        </div>
        
        <div className="card-lg bg-gradient-to-br from-green-50 to-green-100 border border-green-200">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-green-600 rounded-lg">
              <TrendingUp className="text-white" size={24} />
            </div>
            <div>
              <p className="text-sm text-green-600 font-medium">Completion Rate</p>
              <p className="text-2xl font-bold text-green-900">{overviewStats.overallCompletion}%</p>
            </div>
          </div>
        </div>
        
        <div className="card-lg bg-gradient-to-br from-orange-50 to-orange-100 border border-orange-200">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-orange-600 rounded-lg">
              <Award className="text-white" size={24} />
            </div>
            <div>
              <p className="text-sm text-orange-600 font-medium">Avg Quiz Score</p>
              <p className="text-2xl font-bold text-orange-900">{overviewStats.avgQuizScore.toFixed(1)}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
        {/* Pie Chart - Track Distribution */}
        <div className="card-lg">
          <h2 className="section-title">Enrollment Distribution</h2>
          {trackDistribution.length > 0 ? (
            <div className="relative h-96">
              <Pie data={pieChartData} options={pieChartOptions} />
            </div>
          ) : (
            <p className="text-gray-500">No enrollment data available</p>
          )}
        </div>

        {/* Bar Chart - Course Completion Rates */}
        <div className="card-lg">
          <h2 className="section-title">Course Completion Rates</h2>
          {courseStats.length > 0 ? (
            <div className="relative h-96">
              <Bar data={barChartData} options={barChartOptions} />
            </div>
          ) : (
            <p className="text-gray-500">No course data available</p>
          )}
        </div>
      </div>

      {/* Course Details Table */}
      <div className="card-lg mb-8">
        <h2 className="section-title">Course Performance</h2>
        {courseStats.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="bg-gray-100 border-b border-gray-200">
                  <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Course</th>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Enrollments</th>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Completed</th>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">In Progress</th>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Completion Rate</th>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Avg Progress</th>
                </tr>
              </thead>
              <tbody>
                {courseStats.map((course) => (
                  <tr key={course.course_id} className="border-b border-gray-200 hover:bg-gray-50">
                    <td className="px-6 py-4 text-sm text-gray-900 font-medium">{course.course_title}</td>
                    <td className="px-6 py-4 text-sm text-gray-900">{course.total_enrollments}</td>
                    <td className="px-6 py-4 text-sm text-green-600 font-medium">{course.completed_count}</td>
                    <td className="px-6 py-4 text-sm text-yellow-600 font-medium">{course.in_progress_count}</td>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-2">
                        <div className="w-24 bg-gray-200 rounded-full h-2">
                          <div 
                            className="bg-primary-600 h-2 rounded-full" 
                            style={{ width: `${course.completion_rate}%` }}
                          ></div>
                        </div>
                        <span className="text-sm text-gray-700">{course.completion_rate}%</span>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-900">{course.average_progress}%</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p className="text-gray-500">No course data available</p>
        )}
      </div>

      {/* Refresh Button */}
      <div className="flex justify-center">
        <button
          onClick={fetchAdminData}
          className="btn-primary flex items-center gap-2"
        >
          <RefreshCw size={18} />
          Refresh Dashboard
        </button>
      </div>
    </div>
  )
}

export default AdminDashboard
