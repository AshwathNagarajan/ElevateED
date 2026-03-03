import React, { useState, useEffect } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { 
  RefreshCw, 
  AlertCircle, 
  BookOpen, 
  CheckCircle2, 
  TrendingUp,
  Lightbulb,
  Play,
  ArrowRight
} from 'lucide-react'

const StudentDashboard = () => {
  const navigate = useNavigate()
  const [enrollments, setEnrollments] = useState([])
  const [recommendations, setRecommendations] = useState([])
  const [quizResults, setQuizResults] = useState([])
  const [performance, setPerformance] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchDashboardData()
  }, [])

  const fetchDashboardData = async () => {
    try {
      setLoading(true)
      setError(null)

      // Mock data for demonstration
      const mockEnrollments = [
        { id: 1, course_id: 1, course: { title: 'Advanced Mathematics', track_type: 'Math' }, progress_percentage: 65, completed: false },
        { id: 2, course_id: 2, course: { title: 'Physics Basics', track_type: 'Science' }, progress_percentage: 45, completed: false },
        { id: 3, course_id: 3, course: { title: 'English Literature', track_type: 'Language' }, progress_percentage: 80, completed: false },
      ]

      const mockRecommendations = [
        { 
          type: 'revision', 
          module_name: 'Calculus Fundamentals', 
          message: 'Consider reviewing Calculus Fundamentals. You had 3 quiz failures.',
          score: 40,
          reason: 'Multiple quiz failures detected'
        },
        { 
          type: 'next_level', 
          module_name: 'Algebra Advanced', 
          message: 'Great job in Algebra Advanced! You\'re ready for the next level.',
          score: 85,
          reason: 'High performance detected'
        },
        { 
          type: 'foundational_review', 
          module_name: 'Geometry Basics', 
          message: 'Let\'s strengthen your fundamentals in Geometry Basics.',
          score: 35,
          reason: 'Low performance detected'
        },
      ]

      const mockQuizResults = [
        { id: 1, quiz_id: 5, score: 100, is_correct: true, question: 'What is 2 + 2?', submitted_at: '2024-03-03T10:30:00' },
        { id: 2, quiz_id: 4, score: 100, is_correct: true, question: 'Define photosynthesis', submitted_at: '2024-03-02T14:15:00' },
        { id: 3, quiz_id: 3, score: 0, is_correct: false, question: 'Solve for x: 3x + 5 = 20', submitted_at: '2024-03-01T09:45:00' },
        { id: 4, quiz_id: 2, score: 100, is_correct: true, question: 'What is the capital of France?', submitted_at: '2024-02-28T11:20:00' },
        { id: 5, quiz_id: 1, score: 0, is_correct: false, question: 'Calculate the derivative', submitted_at: '2024-02-27T13:00:00' },
      ]

      const mockPerformance = {
        total_quizzes: 45,
        passed: 38,
        failed: 7,
        success_percentage: 84.44,
        average_score: 84.44,
        module_stats: [
          { module_name: 'Algebra', success_percentage: 90, total: 10 },
          { module_name: 'Geometry', success_percentage: 75, total: 8 },
          { module_name: 'Calculus', success_percentage: 65, total: 12 },
        ]
      }

      // TODO: Replace with actual API calls
      // const enrollResponse = await fetch('/enrollments/my-courses', {
      //   headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      // })
      // const enrollData = await enrollResponse.json()
      // setEnrollments(enrollData)

      // const recommendResponse = await fetch('/recommendations/my-recommendations', {
      //   headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      // })
      // const recommendData = await recommendResponse.json()
      // setRecommendations(recommendData)

      // const quizResponse = await fetch('/quizzes/student/my-submissions', {
      //   headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      // })
      // const quizData = await quizResponse.json()
      // setQuizResults(quizData)

      // const perfResponse = await fetch('/recommendations/performance', {
      //   headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      // })
      // const perfData = await perfResponse.json()
      // setPerformance(perfData)

      setEnrollments(mockEnrollments)
      setRecommendations(mockRecommendations)
      setQuizResults(mockQuizResults)
      setPerformance(mockPerformance)
      setLoading(false)
    } catch (err) {
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
        return 'Review Needed'
      case 'next_level':
        return 'Ready to Advance'
      case 'foundational_review':
        return 'Strengthen Basics'
      default:
        return 'Recommendation'
    }
  }

  if (loading) {
    return (
      <div className="flex justify-center items-center h-96">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
          <p className="text-gray-600 text-lg">Loading your dashboard...</p>
        </div>
      </div>
    )
  }

  const continueLearning = enrollments.length > 0 ? enrollments[0] : null

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-gray-900 mb-2">Welcome Back!</h1>
        <p className="text-gray-600">Continue your learning journey</p>
      </div>

      {error && (
        <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4 flex items-start gap-3">
          <AlertCircle className="text-red-600 mt-0.5" size={20} />
          <div>
            <h3 className="font-semibold text-red-800">Error Loading Dashboard</h3>
            <p className="text-red-700">{error}</p>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        {/* Continue Learning Card */}
        {continueLearning && (
          <div className="lg:col-span-2 card-lg bg-gradient-to-br from-primary-50 to-secondary-50 border-2 border-primary-200">
            <div className="flex items-start justify-between mb-6">
              <div>
                <h2 className="text-2xl font-bold text-gray-900 mb-1">Continue Learning</h2>
                <p className="text-gray-600">{continueLearning.course.title}</p>
              </div>
              <Play className="text-primary-600" size={32} />
            </div>
            <div className="space-y-4">
              <div>
                <div className="flex justify-between items-center mb-2">
                  <span className="text-sm font-semibold text-gray-700">Progress</span>
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
                Continue Lesson
              </button>
            </div>
          </div>
        )}

        {/* Quick Stats */}
        {performance && (
          <div className="card-lg">
            <h3 className="section-title mb-6">Your Statistics</h3>
            <div className="space-y-4">
              <div className="p-4 bg-green-50 rounded-lg border border-green-200">
                <p className="text-green-600 text-sm font-semibold mb-1">Success Rate</p>
                <p className="text-3xl font-bold text-green-700">{performance.success_percentage.toFixed(1)}%</p>
              </div>
              <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
                <p className="text-blue-600 text-sm font-semibold mb-1">Quizzes Taken</p>
                <p className="text-3xl font-bold text-blue-700">{performance.total_quizzes}</p>
              </div>
              <div className="p-4 bg-purple-50 rounded-lg border border-purple-200">
                <p className="text-purple-600 text-sm font-semibold mb-1">Passed</p>
                <p className="text-3xl font-bold text-purple-700">{performance.passed}</p>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Enrolled Courses */}
      <div className="card-lg mb-8">
        <h2 className="section-title mb-6">Enrolled Courses</h2>
        {enrollments.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {enrollments.map((enrollment) => (
              <div
                key={enrollment.id}
                className="p-5 border border-gray-200 rounded-lg hover:border-primary-400 hover:shadow-lg transition-all"
              >
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <h3 className="font-semibold text-gray-900">{enrollment.course.title}</h3>
                    <p className="text-sm text-gray-500 mt-1">{enrollment.course.track_type}</p>
                  </div>
                  {enrollment.completed && <CheckCircle2 className="text-green-600" size={24} />}
                </div>
                <div className="space-y-3">
                  <div>
                    <div className="flex justify-between items-center mb-1">
                      <span className="text-xs font-semibold text-gray-600">Progress</span>
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
                    Open Course
                    <ArrowRight size={14} />
                  </button>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-gray-500 text-center py-8">No enrolled courses yet. Start exploring!</p>
        )}
      </div>

      {/* Recommended Lessons */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
        {/* Recommendations */}
        <div className="card-lg">
          <h2 className="section-title mb-6">Personalized Recommendations</h2>
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
            <p className="text-gray-500 text-center py-8">No recommendations yet. Keep learning!</p>
          )}
        </div>

        {/* Recent Quiz Results */}
        <div className="card-lg">
          <h2 className="section-title mb-6">Recent Quiz Results</h2>
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
