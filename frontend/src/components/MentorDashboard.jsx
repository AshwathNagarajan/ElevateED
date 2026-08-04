import React, { useState, useEffect } from 'react'
import { Bar, Doughnut } from 'react-chartjs-2'
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
import { RefreshCw, AlertCircle, Users, BookOpen, TrendingUp, Award, GraduationCap, X, BarChart2 } from 'lucide-react'
import { useTranslation } from 'react-i18next'
import { apiGet } from '../api/client'

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

const MentorDashboard = () => {
  const { t } = useTranslation()
  const [dashboardData, setDashboardData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [selectedCourse, setSelectedCourse] = useState(null)

  useEffect(() => {
    fetchMentorData()
  }, [])

  const fetchMentorData = async () => {
    try {
      setLoading(true)
      setError(null)

      // ✅ Using centralized apiGet for consistent error handling and auth
      const data = await apiGet('/analytics/mentor/dashboard')
      setDashboardData(data)
    } catch (e) {
      console.error('Error fetching mentor data:', e)
      setError(e.message || 'Failed to load dashboard data')
    } finally {
      setLoading(false)
    }
  }

  // Chart configurations
  const getEnrollmentChartData = () => {
    if (!dashboardData?.courses) return null

    return {
      labels: dashboardData.courses.map(c => c.course_title.length > 20 
        ? c.course_title.substring(0, 20) + '...' 
        : c.course_title),
      datasets: [
        {
          label: t('mentor.completed', 'Completed'),
          data: dashboardData.courses.map(c => c.completed_count),
          backgroundColor: 'rgba(34, 197, 94, 0.8)',
          borderRadius: 4,
        },
        {
          label: t('mentor.inProgress', 'In Progress'),
          data: dashboardData.courses.map(c => c.in_progress_count),
          backgroundColor: 'rgba(59, 130, 246, 0.8)',
          borderRadius: 4,
        },
        {
          label: t('mentor.notStarted', 'Not Started'),
          data: dashboardData.courses.map(c => c.not_started_count),
          backgroundColor: 'rgba(156, 163, 175, 0.8)',
          borderRadius: 4,
        },
      ],
    }
  }

  const getCompletionChartData = () => {
    if (!dashboardData?.courses) return null

    const colors = [
      'rgba(59, 130, 246, 0.8)',
      'rgba(34, 197, 94, 0.8)',
      'rgba(249, 115, 22, 0.8)',
      'rgba(168, 85, 247, 0.8)',
      'rgba(236, 72, 153, 0.8)',
      'rgba(20, 184, 166, 0.8)',
    ]

    return {
      labels: dashboardData.courses.map(c => c.course_title.length > 15 
        ? c.course_title.substring(0, 15) + '...' 
        : c.course_title),
      datasets: [
        {
          data: dashboardData.courses.map(c => c.completion_rate),
          backgroundColor: colors.slice(0, dashboardData.courses.length),
          borderWidth: 0,
        },
      ],
    }
  }

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'bottom',
      },
    },
    scales: {
      x: {
        stacked: true,
        grid: {
          display: false,
        },
      },
      y: {
        stacked: true,
        beginAtZero: true,
      },
    },
  }

  const doughnutOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'right',
      },
      tooltip: {
        callbacks: {
          label: (context) => `${context.label}: ${context.raw}%`
        }
      }
    },
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <RefreshCw className="w-8 h-8 text-primary-600 animate-spin" />
        <span className="ml-2 text-gray-600">{t('common.loading', 'Loading...')}</span>
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[400px] text-center">
        <AlertCircle className="w-12 h-12 text-red-500 mb-4" />
        <h3 className="text-lg font-semibold text-gray-900 mb-2">
          {t('common.error', 'Error Loading Data')}
        </h3>
        <p className="text-gray-600 mb-4">{error}</p>
        <button
          onClick={fetchMentorData}
          className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
        >
          {t('common.retry', 'Retry')}
        </button>
      </div>
    )
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          {t('mentor.dashboard', 'Mentor Dashboard')}
        </h1>
        <p className="text-gray-600">
          {t('mentor.welcomeMessage', 'Overview of your courses and student performance')}
        </p>
      </div>

      {/* Overview Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
              <BookOpen className="w-6 h-6 text-blue-600" />
            </div>
          </div>
          <h3 className="text-2xl font-bold text-gray-900">
            {dashboardData?.total_courses || 0}
          </h3>
          <p className="text-sm text-gray-500">{t('mentor.totalCourses', 'Total Courses')}</p>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
              <Users className="w-6 h-6 text-green-600" />
            </div>
          </div>
          <h3 className="text-2xl font-bold text-gray-900">
            {dashboardData?.total_students || 0}
          </h3>
          <p className="text-sm text-gray-500">{t('mentor.totalStudents', 'Total Students')}</p>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
              <TrendingUp className="w-6 h-6 text-purple-600" />
            </div>
          </div>
          <h3 className="text-2xl font-bold text-gray-900">
            {dashboardData?.overall_completion_rate || 0}%
          </h3>
          <p className="text-sm text-gray-500">{t('mentor.completionRate', 'Completion Rate')}</p>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center">
              <Award className="w-6 h-6 text-orange-600" />
            </div>
          </div>
          <h3 className="text-2xl font-bold text-gray-900">
            {dashboardData?.overall_avg_quiz_score?.toFixed(1) || 0}%
          </h3>
          <p className="text-sm text-gray-500">{t('mentor.avgQuizScore', 'Avg Quiz Score')}</p>
        </div>
      </div>

      {/* Charts Section */}
      {dashboardData?.courses?.length > 0 && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {/* Enrollment Distribution */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              {t('mentor.studentProgress', 'Student Progress by Course')}
            </h3>
            <div className="h-[300px]">
              <Bar data={getEnrollmentChartData()} options={chartOptions} />
            </div>
          </div>

          {/* Completion Rate Breakdown */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              {t('mentor.completionRates', 'Course Completion Rates')}
            </h3>
            <div className="h-[300px]">
              <Doughnut data={getCompletionChartData()} options={doughnutOptions} />
            </div>
          </div>
        </div>
      )}

      {/* Course Details Table */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-100">
          <h3 className="text-lg font-semibold text-gray-900">
            {t('mentor.yourCourses', 'Your Courses')}
          </h3>
        </div>
        
        {dashboardData?.courses?.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    {t('mentor.course', 'Course')}
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    {t('mentor.track', 'Track')}
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    {t('mentor.level', 'Level')}
                  </th>
                  <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                    {t('mentor.enrolled', 'Enrolled')}
                  </th>
                  <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                    {t('mentor.completed', 'Completed')}
                  </th>
                  <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                    {t('mentor.progress', 'Avg Progress')}
                  </th>
                  <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                    {t('mentor.quizScore', 'Quiz Score')}
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {dashboardData.courses.map((course) => (
                  <tr key={course.course_id} onClick={() => setSelectedCourse(course)} className="hover:bg-blue-50 cursor-pointer transition-colors">
                    <td className="px-6 py-4">
                      <div className="flex items-center">
                        <div className="w-10 h-10 bg-primary-100 rounded-lg flex items-center justify-center mr-3">
                          <GraduationCap className="w-5 h-5 text-primary-600" />
                        </div>
                        <div>
                          <p className="font-medium text-gray-900">{course.course_title}</p>
                          <p className="text-sm text-gray-500">{course.total_quizzes} quizzes</p>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                        {course.track_type}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                        course.level === 'Beginner' ? 'bg-green-100 text-green-800' :
                        course.level === 'Intermediate' ? 'bg-yellow-100 text-yellow-800' :
                        'bg-red-100 text-red-800'
                      }`}>
                        {course.level}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-center">
                      <span className="font-semibold text-gray-900">{course.total_enrollments}</span>
                    </td>
                    <td className="px-6 py-4 text-center">
                      <span className="font-semibold text-green-600">{course.completed_count}</span>
                      <span className="text-gray-400 text-sm ml-1">
                        ({course.completion_rate}%)
                      </span>
                    </td>
                    <td className="px-6 py-4 text-center">
                      <div className="flex items-center justify-center">
                        <div className="w-20 bg-gray-200 rounded-full h-2 mr-2">
                          <div 
                            className="bg-primary-600 h-2 rounded-full" 
                            style={{ width: `${Math.min(course.average_progress, 100)}%` }}
                          ></div>
                        </div>
                        <span className="text-sm text-gray-600">{course.average_progress}%</span>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-center">
                      <span className={`font-semibold ${
                        course.avg_quiz_score >= 70 ? 'text-green-600' :
                        course.avg_quiz_score >= 50 ? 'text-yellow-600' :
                        'text-red-600'
                      }`}>
                        {course.avg_quiz_score}%
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="px-6 py-12 text-center">
            <BookOpen className="w-12 h-12 text-gray-300 mx-auto mb-4" />
            <h4 className="text-lg font-medium text-gray-900 mb-2">
              {t('mentor.noCourses', 'No Courses Assigned')}
            </h4>
            <p className="text-gray-500">
              {t('mentor.noCoursesDesc', 'You don\'t have any courses assigned yet. Contact an administrator to get courses assigned to you.')}
            </p>
          </div>
        )}
      </div>

      {/* Course Analytics Popup */}
      {selectedCourse && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 backdrop-blur-sm" onClick={() => setSelectedCourse(null)}>
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-lg" onClick={e => e.stopPropagation()}>
            <div className="flex items-center justify-between px-6 py-5 border-b border-gray-100">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-primary-100 rounded-lg flex items-center justify-center">
                  <BarChart2 className="text-primary-600" size={20} />
                </div>
                <div>
                  <h2 className="text-lg font-bold text-gray-900 leading-tight">{selectedCourse.course_title}</h2>
                  <p className="text-xs text-gray-400">{selectedCourse.track_type} · {selectedCourse.level}</p>
                </div>
              </div>
              <button onClick={() => setSelectedCourse(null)} className="p-2 hover:bg-gray-100 rounded-lg"><X size={20} className="text-gray-500" /></button>
            </div>
            <div className="px-6 py-5 space-y-4">
              <div className="grid grid-cols-3 gap-3">
                <div className="bg-blue-50 rounded-xl p-4 text-center"><p className="text-2xl font-bold text-blue-700">{selectedCourse.total_enrollments ?? 0}</p><p className="text-xs text-blue-500 mt-0.5">Enrolled</p></div>
                <div className="bg-green-50 rounded-xl p-4 text-center"><p className="text-2xl font-bold text-green-700">{selectedCourse.completed_count ?? 0}</p><p className="text-xs text-green-500 mt-0.5">Completed</p></div>
                <div className="bg-yellow-50 rounded-xl p-4 text-center"><p className="text-2xl font-bold text-yellow-700">{selectedCourse.in_progress_count ?? 0}</p><p className="text-xs text-yellow-500 mt-0.5">In Progress</p></div>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div className="bg-gray-50 rounded-xl p-4">
                  <p className="text-xs text-gray-400 mb-2">Completion Rate</p>
                  <div className="flex items-center gap-2">
                    <div className="flex-1 bg-gray-200 rounded-full h-2">
                      <div className={`h-2 rounded-full ${selectedCourse.completion_rate >= 70 ? 'bg-green-500' : selectedCourse.completion_rate >= 40 ? 'bg-yellow-500' : 'bg-red-400'}`} style={{ width: `${Math.min(selectedCourse.completion_rate, 100)}%` }} />
                    </div>
                    <span className="text-sm font-bold text-gray-800">{selectedCourse.completion_rate}%</span>
                  </div>
                </div>
                <div className="bg-gray-50 rounded-xl p-4">
                  <p className="text-xs text-gray-400 mb-2">Avg Progress</p>
                  <div className="flex items-center gap-2">
                    <div className="flex-1 bg-gray-200 rounded-full h-2">
                      <div className="h-2 rounded-full bg-primary-500" style={{ width: `${Math.min(selectedCourse.average_progress, 100)}%` }} />
                    </div>
                    <span className="text-sm font-bold text-gray-800">{selectedCourse.average_progress}%</span>
                  </div>
                </div>
              </div>
              <div className="flex items-center justify-between bg-orange-50 rounded-xl p-4">
                <div>
                  <p className="text-xs text-gray-400 mb-0.5">Avg Quiz Score</p>
                  <p className="text-2xl font-bold text-orange-700">{selectedCourse.avg_quiz_score ?? 0}%</p>
                </div>
                <div className="text-right">
                  <p className="text-xs text-gray-400 mb-0.5">Not Started</p>
                  <p className="text-2xl font-bold text-gray-600">{selectedCourse.not_started_count ?? 0}</p>
                </div>
              </div>
              <p className="text-xs text-gray-400 text-center">{selectedCourse.total_quizzes ?? 0} quizzes in this course</p>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default MentorDashboard
