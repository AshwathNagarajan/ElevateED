import React, { useState, useEffect } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { 
  RefreshCw, 
  AlertCircle, 
  BookOpen, 
  CheckCircle2, 
  TrendingUp,
  Lightbulb,
  Play,
  ArrowRight,
  Compass,
  HeartHandshake,
  Target,
  Sparkles,
  Star,
  Clock3,
  Award
} from 'lucide-react'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'

const StudentDashboard = () => {
  const navigate = useNavigate()
  const { t } = useTranslation()
  const [enrollments, setEnrollments] = useState([])
  const [recommendations, setRecommendations] = useState([])
  const [quizResults, setQuizResults] = useState([])
  const [performance, setPerformance] = useState(null)
  const [guidancePlan, setGuidancePlan] = useState(null)
  const [achievements, setAchievements] = useState(null)
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
    fetchDashboardData()
  }, [])

  const fetchDashboardData = async () => {
    try {
      setLoading(true)
      setError(null)

      // Fetch enrollments
      let enrollmentsData = []
      try {
        const enrollResponse = await fetch(`${API_BASE_URL}/enrollments/my-courses`, {
          headers: getAuthHeaders()
        })
        if (enrollResponse.ok) {
          enrollmentsData = await enrollResponse.json()
        }
      } catch (e) {
        console.warn('Failed to fetch enrollments:', e)
      }

      // Fetch recommendations (if endpoint exists)
      let recommendationsData = []
      try {
        const recommendResponse = await fetch(`${API_BASE_URL}/recommendations/my-recommendations`, {
          headers: getAuthHeaders()
        })
        if (recommendResponse.ok) {
          recommendationsData = await recommendResponse.json()
        }
      } catch (e) {
        console.warn('Recommendations endpoint not available')
        // Provide helpful mock recommendations based on enrollment data
        recommendationsData = [
          { 
            type: 'next_level', 
            module_name: 'Continue Learning', 
            message: 'Keep up the great work! Explore more courses to advance your skills.',
            score: 85,
            reason: 'Active learner'
          }
        ]
      }

      // Fetch quiz submissions (if endpoint exists)
      let quizData = []
      try {
        const quizResponse = await fetch(`${API_BASE_URL}/quizzes/student/my-submissions`, {
          headers: getAuthHeaders()
        })
        if (quizResponse.ok) {
          quizData = await quizResponse.json()
        }
      } catch (e) {
        console.warn('Quiz submissions endpoint not available')
      }

      // Fetch performance data (if endpoint exists)
      let perfData = null
      try {
        const perfResponse = await fetch(`${API_BASE_URL}/recommendations/performance`, {
          headers: getAuthHeaders()
        })
        if (perfResponse.ok) {
          perfData = await perfResponse.json()
        }
      } catch (e) {
        console.warn('Performance endpoint not available')
        // Calculate from enrollments if available
        perfData = {
          total_quizzes: enrollmentsData.length * 5,
          passed: Math.floor(enrollmentsData.length * 4),
          failed: enrollmentsData.length,
          success_percentage: 80,
          average_score: 80,
          module_stats: []
        }
      }

      let guidanceData = null
      try {
        const guidanceResponse = await fetch(`${API_BASE_URL}/recommendations/guidance-plan`, {
          headers: getAuthHeaders()
        })
        if (guidanceResponse.ok) {
          guidanceData = await guidanceResponse.json()
        }
      } catch (e) {
        console.warn('Guidance plan endpoint not available')
      }

      let achievementsData = null
      try {
        const achievementsResponse = await fetch(`${API_BASE_URL}/badges/my-achievements`, {
          headers: getAuthHeaders()
        })
        if (achievementsResponse.ok) {
          achievementsData = await achievementsResponse.json()
        }
      } catch (e) {
        console.warn('Achievements endpoint not available')
      }

      setEnrollments(enrollmentsData)
      setRecommendations(recommendationsData)
      setQuizResults(quizData)
      setPerformance(perfData)
      setGuidancePlan(guidanceData)
      setAchievements(achievementsData)
      setLoading(false)
    } catch (err) {
      console.error('Dashboard fetch error:', err)
      setError(err.message)
      setLoading(false)
    }
  }

  const getProgressColor = (percentage) => {
    if (percentage >= 80) return 'bg-green-500'
    if (percentage >= 60) return 'bg-blue-500'
    if (percentage >= 40) return 'bg-yellow-500'
    return 'bg-red-500'
  }

  const getRecommendationIcon = (type) => {
    switch (type) {
      case 'revision':
        return <BookOpen className="text-blue-600" size={20} />
      case 'next_level':
        return <TrendingUp className="text-green-600" size={20} />
      case 'foundational_review':
        return <Lightbulb className="text-yellow-600" size={20} />
      default:
        return <AlertCircle size={20} />
    }
  }

  const getRecommendationLabel = (type) => {
    switch (type) {
      case 'revision':
        return t('recommendations.reviewNeeded')
      case 'next_level':
        return t('recommendations.readyToAdvance')
      case 'foundational_review':
        return t('recommendations.strengthenBasics')
      default:
        return t('recommendations.recommendation')
    }
  }

  const getSupportTone = (level) => {
    switch (level) {
      case 'high':
        return 'bg-rose-50 text-rose-700 border-rose-200'
      case 'medium':
        return 'bg-amber-50 text-amber-700 border-amber-200'
      default:
        return 'bg-emerald-50 text-emerald-700 border-emerald-200'
    }
  }

  if (loading) {
    return (
      <div className="flex justify-center items-center h-96">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
          <p className="text-gray-600 text-lg">{t('dashboard.loadingDashboard')}</p>
        </div>
      </div>
    )
  }

  const continueLearning = enrollments.length > 0 ? enrollments[0] : null
  const topGuidedCourse = guidancePlan?.recommended_courses?.[0]
  const mainNextStep = guidancePlan?.next_steps?.[0]
  const learningPattern = guidancePlan?.learning_pattern || {}
  const metrics = guidancePlan?.metrics || {}
  const modelInfo = guidancePlan?.model || {}

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <div className="mb-8">
        <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-primary-50 text-primary-700 border border-primary-100 text-sm font-semibold mb-4">
          <Sparkles size={16} />
          Your learning guide is ready
        </div>
        <h1 className="text-4xl font-bold text-gray-900 mb-2">{t('dashboard.welcomeBack')}</h1>
        <p className="text-gray-600 max-w-3xl">
          Choose one focused step, learn at your pace, and let ElevateED adjust the path as your pattern grows.
        </p>
      </div>

      {error && (
        <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4 flex items-start gap-3">
          <AlertCircle className="text-red-600 mt-0.5" size={20} />
          <div>
            <h3 className="font-semibold text-red-800">{t('dashboard.errorLoading')}</h3>
            <p className="text-red-700">{error}</p>
          </div>
        </div>
      )}

      {guidancePlan && (
        <div className="mb-8 overflow-hidden rounded-2xl border border-sky-100 bg-gradient-to-br from-sky-50 via-white to-emerald-50 shadow-sm">
          <div className="grid grid-cols-1 xl:grid-cols-[1.2fr_0.8fr]">
            <div className="p-6 sm:p-8">
              <div className="flex flex-wrap items-center gap-3 mb-5">
                <div className="w-12 h-12 rounded-2xl bg-sky-600 flex items-center justify-center shrink-0 shadow-sm">
                  <Compass className="text-white" size={24} />
                </div>
                <span className="px-3 py-1 rounded-full bg-white border border-sky-100 text-xs font-bold uppercase text-sky-700">
                  Personal guidance plan
                </span>
                <span className={`inline-flex items-center gap-2 px-3 py-1 rounded-full border text-xs font-bold capitalize ${getSupportTone(guidancePlan.support_level)}`}>
                  <HeartHandshake size={14} />
                  {guidancePlan.support_level} support
                </span>
              </div>

              <h2 className="text-3xl font-bold text-gray-950 mb-3">
                {guidancePlan.suggested_track?.track || 'Learning path'}
              </h2>
              <p className="text-gray-700 max-w-3xl leading-relaxed">{guidancePlan.guidance_summary}</p>

              <div className="mt-6 grid grid-cols-1 sm:grid-cols-3 gap-3">
                <div className="rounded-xl bg-white/80 border border-white p-4">
                  <p className="text-xs font-semibold text-gray-500 uppercase mb-1">Pace</p>
                  <p className="text-lg font-bold text-gray-950 capitalize">{learningPattern.pace || 'Growing'}</p>
                </div>
                <div className="rounded-xl bg-white/80 border border-white p-4">
                  <p className="text-xs font-semibold text-gray-500 uppercase mb-1">Quiz confidence</p>
                  <p className="text-lg font-bold text-gray-950">{Math.round(metrics.quiz_success_rate || 0)}%</p>
                </div>
                <div className="rounded-xl bg-white/80 border border-white p-4">
                  <p className="text-xs font-semibold text-gray-500 uppercase mb-1">Attendance</p>
                  <p className="text-lg font-bold text-gray-950">{Math.round(metrics.attendance_rate || 0)}%</p>
                </div>
              </div>

              <div className="mt-4 rounded-xl bg-white/70 border border-white p-4">
                <p className="text-xs font-semibold text-gray-500 uppercase mb-1">Model signal</p>
                <p className="text-sm font-semibold text-gray-900">
                  {modelInfo.readiness === 'ready'
                    ? `Ready with ${modelInfo.evidence_count || 0} learning signals`
                    : `Still learning your pattern from ${modelInfo.evidence_count || 0} signals`}
                </p>
              </div>

              <div className="mt-6 flex flex-col sm:flex-row gap-3">
                <button
                  onClick={() => topGuidedCourse ? navigate(`/course/${topGuidedCourse.course_id}`) : navigate('/courses')}
                  className="btn-primary inline-flex items-center justify-center gap-2"
                >
                  <Target size={18} />
                  Start guided course
                </button>
                <Link to="/recommendations" className="btn-secondary inline-flex items-center justify-center gap-2">
                  <Sparkles size={18} />
                  View guidance
                </Link>
              </div>
            </div>

            <div className="p-6 sm:p-8 bg-white/70 border-t xl:border-t-0 xl:border-l border-white">
              <div className="rounded-xl bg-white border border-gray-100 p-5 mb-5 shadow-sm">
                <div className="flex items-center gap-2 mb-3">
                  <Target size={18} className="text-sky-600" />
                  <p className="text-sm font-bold text-gray-950">Today&apos;s focused step</p>
                </div>
                <p className="text-lg font-bold text-gray-950 mb-2">{mainNextStep?.title || 'Pick one lesson and finish it'}</p>
                <p className="text-sm text-gray-600">{mainNextStep?.description || 'A small completed step matters more than a long unfinished plan.'}</p>
              </div>

              <div className="space-y-3">
                {(guidancePlan.recommended_courses || []).slice(0, 3).map((course) => (
                  <button
                    key={course.course_id}
                    onClick={() => navigate(`/course/${course.course_id}`)}
                    className="w-full rounded-xl bg-white border border-gray-100 p-4 text-left hover:border-sky-300 hover:shadow-md transition-all"
                  >
                    <div className="flex items-start justify-between gap-3">
                      <div>
                        <p className="text-sm font-bold text-gray-950">{course.title}</p>
                        <p className="text-xs text-gray-500 mt-1">{course.track_type} - {course.level}</p>
                      </div>
                      <ArrowRight size={16} className="text-sky-600 shrink-0 mt-1" />
                    </div>
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        {/* Continue Learning Card */}
        {continueLearning && (
          <div className="lg:col-span-2 card-lg bg-gradient-to-br from-primary-50 to-secondary-50 border-2 border-primary-200">
            <div className="flex items-start justify-between mb-6">
              <div>
                <h2 className="text-2xl font-bold text-gray-900 mb-1">{t('dashboard.continueLearning').split(' ')[0]}</h2>
                <p className="text-gray-600">{continueLearning.course?.title || 'Continue your course'}</p>
              </div>
              <Play className="text-primary-600" size={32} />
            </div>
            <div className="space-y-4">
              <div>
                <div className="flex justify-between items-center mb-2">
                  <span className="text-sm font-semibold text-gray-700">{t('dashboard.progress')}</span>
                  <span className="text-sm font-bold text-primary-600">{continueLearning.progress_percentage}%</span>
                </div>
                <div className="w-full bg-gray-300 rounded-full h-3 overflow-hidden">
                  <div
                    className={`${getProgressColor(continueLearning.progress_percentage)} h-full transition-all duration-300`}
                    style={{ width: `${continueLearning.progress_percentage}%` }}
                  ></div>
                </div>
              </div>
              <button 
                onClick={() => navigate(`/course/${continueLearning.course_id}`)}
                className="w-full btn-primary flex items-center justify-center gap-2"
              >
                <Play size={18} />
                {t('lesson.continue') || 'Continue'}
              </button>
            </div>
          </div>
        )}

        {/* Quick Stats */}
        {performance && (
          <div className="card-lg">
            <h3 className="section-title mb-6">{t('performance.title')}</h3>
            <div className="space-y-4">
              <div className="p-4 bg-green-50 rounded-lg border border-green-200">
                <p className="text-green-600 text-sm font-semibold mb-1 flex items-center gap-2"><Star size={16} />{t('performance.successRate')}</p>
                <p className="text-3xl font-bold text-green-700">{performance.success_percentage.toFixed(1)}%</p>
              </div>
              <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
                <p className="text-blue-600 text-sm font-semibold mb-1 flex items-center gap-2"><Clock3 size={16} />{t('performance.totalQuizzes')}</p>
                <p className="text-3xl font-bold text-blue-700">{performance.total_quizzes}</p>
              </div>
              <div className="p-4 bg-purple-50 rounded-lg border border-purple-200">
                <p className="text-purple-600 text-sm font-semibold mb-1">{t('performance.passedQuizzes')}</p>
                <p className="text-3xl font-bold text-purple-700">{performance.passed}</p>
              </div>
            </div>
          </div>
        )}
      </div>

      {achievements && achievements.total_badges > 0 && (
        <div className="card-lg mb-8">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 mb-6">
            <div>
              <h2 className="section-title mb-1 flex items-center gap-2">
                <Award className="text-amber-500" size={24} />
                Achievement shelf
              </h2>
              <p className="text-sm text-gray-500">{achievements.total_points} points earned from steady learning.</p>
            </div>
            <span className="inline-flex items-center justify-center px-3 py-1 rounded-full bg-amber-50 text-amber-700 border border-amber-100 text-sm font-bold">
              {achievements.total_badges} badges
            </span>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {achievements.badges.slice(0, 4).map((badge) => (
              <div key={badge.id} className="rounded-xl border border-gray-100 bg-gradient-to-br from-white to-amber-50 p-4">
                <div className="w-10 h-10 rounded-xl bg-amber-100 text-amber-700 flex items-center justify-center mb-3">
                  <Award size={20} />
                </div>
                <p className="font-bold text-gray-900">{badge.name}</p>
                <p className="text-xs text-gray-500 mt-1 line-clamp-2">{badge.description}</p>
                <p className="text-xs font-bold text-amber-700 mt-3">+{badge.points} points</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Enrolled Courses */}
      <div className="card-lg mb-8">
        <h2 className="section-title mb-6">{t('courses.enrolledCourses')}</h2>
        {enrollments.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {enrollments.map((enrollment) => (
              <div
                key={enrollment.id}
                className="p-5 border border-gray-200 rounded-lg hover:border-primary-400 hover:shadow-lg transition-all"
              >
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <h3 className="font-semibold text-gray-900">{enrollment.course?.title || 'Course'}</h3>
                    <p className="text-sm text-gray-500 mt-1">{enrollment.course?.track_type || ''}</p>
                  </div>
                  {enrollment.completed && <CheckCircle2 className="text-green-600" size={24} />}
                </div>
                <div className="space-y-3">
                  <div>
                    <div className="flex justify-between items-center mb-1">
                      <span className="text-xs font-semibold text-gray-600">{t('dashboard.progress')}</span>
                      <span className="text-xs font-bold text-primary-600">{enrollment.progress_percentage}%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
                      <div
                        className={`${getProgressColor(enrollment.progress_percentage)} h-full transition-all duration-300`}
                        style={{ width: `${enrollment.progress_percentage}%` }}
                      ></div>
                    </div>
                  </div>
                  <button 
                    onClick={() => navigate(`/course/${enrollment.course_id}`)}
                    className="w-full text-sm btn-secondary flex items-center justify-center gap-1"
                  >
                    {t('courses.viewDetails')}
                    <ArrowRight size={14} />
                  </button>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-gray-500 text-center py-8">{t('courses.noEnrolledCourses')}</p>
        )}
      </div>

      {/* Recommended Lessons */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
        {/* Recommendations */}
        <div className="card-lg">
          <h2 className="section-title mb-6">{t('recommendations.personalizedRecommendations')}</h2>
          {recommendations.length > 0 ? (
            <div className="space-y-4">
              {recommendations.map((rec, index) => (
                <div
                  key={index}
                  className="p-4 border-l-4 border-primary-600 bg-gray-50 rounded-r-lg hover:bg-gray-100 transition-colors"
                >
                  <div className="flex items-start gap-3 mb-2">
                    {getRecommendationIcon(rec.type)}
                    <div className="flex-1">
                      <p className="text-xs font-bold text-primary-600 uppercase">{getRecommendationLabel(rec.type)}</p>
                      <p className="font-semibold text-gray-900 text-sm">{rec.module_name}</p>
                    </div>
                  </div>
                  <p className="text-sm text-gray-600 mb-3">{rec.message}</p>
                  <div className="flex items-center justify-between">
                    <span className="text-xs text-gray-500">Success Rate: <span className="font-bold">{rec.score}%</span></span>
                    <Link to="/recommendations" className="text-xs btn-primary">Start</Link>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-500 text-center py-8">{t('recommendations.noRecommendations')}</p>
          )}
        </div>

        {/* Recent Quiz Results */}
        <div className="card-lg">
          <h2 className="section-title mb-6">{t('quiz.viewResults')}</h2>
          {quizResults.length > 0 ? (
            <div className="space-y-3 max-h-96 overflow-y-auto">
              {quizResults.slice(0, 5).map((result) => (
                <div
                  key={result.id}
                  className="p-4 bg-gray-50 rounded-lg border-b border-gray-200"
                >
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex-1">
                      <p className="text-sm font-semibold text-gray-900 mb-1">{result.question}</p>
                      <p className="text-xs text-gray-500">
                        {new Date(result.submitted_at).toLocaleDateString('en-US', {
                          month: 'short',
                          day: 'numeric',
                          hour: '2-digit',
                          minute: '2-digit'
                        })}
                      </p>
                    </div>
                    <div className={`flex items-center gap-1 ${result.is_correct ? 'text-green-600' : 'text-red-600'}`}>
                      <span className="text-sm font-bold">{result.score}</span>
                      {result.is_correct ? (
                        <CheckCircle2 size={20} />
                      ) : (
                        <AlertCircle size={20} />
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-500 text-center py-8">No quiz results yet</p>
          )}
        </div>
      </div>

      {/* Refresh Button */}
      <div className="flex justify-center">
        <button
          onClick={fetchDashboardData}
          className="btn-primary flex items-center gap-2"
        >
          <RefreshCw size={18} />
          Refresh Dashboard
        </button>
      </div>
    </div>
  )
}

export default StudentDashboard
