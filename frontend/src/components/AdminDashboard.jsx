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
import { RefreshCw, AlertCircle, Mail } from 'lucide-react'

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

const AdminDashboard = () => {
  const [trackDistribution, setTrackDistribution] = useState([])
  const [skillScores, setSkillScores] = useState([])
  const [dropoutRiskStudents, setDropoutRiskStudents] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchAdminData()
  }, [])

  const fetchAdminData = async () => {
    try {
      setLoading(true)
      setError(null)

      // Mock data
      const mockTrackDistribution = [
        { track: 'Math', count: 150 },
        { track: 'Science', count: 120 },
        { track: 'English', count: 100 },
        { track: 'Arts', count: 80 },
      ]

      const mockSkillScores = [
        { track: 'Math', averageScore: 78 },
        { track: 'Science', averageScore: 82 },
        { track: 'English', averageScore: 75 },
        { track: 'Arts', averageScore: 88 },
      ]

      const mockDropoutRisks = [
        { id: 1, name: 'John Doe', track: 'Math', attendance: 45, averageScore: 35, riskLevel: 'High' },
        { id: 2, name: 'Jane Smith', track: 'Science', attendance: 65, averageScore: 52, riskLevel: 'Medium' },
        { id: 3, name: 'Bob Wilson', track: 'English', attendance: 40, averageScore: 30, riskLevel: 'High' },
      ]

      setTrackDistribution(mockTrackDistribution)
      setSkillScores(mockSkillScores)
      setDropoutRiskStudents(mockDropoutRisks)
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
    labels: skillScores.map(item => item.track),
    datasets: [
      {
        label: 'Average Skill Score',
        data: skillScores.map(item => item.averageScore),
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
        text: 'Average Skill Scores by Track',
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        max: 100,
      },
    },
  }

  const getRiskColor = (level) => {
    switch (level) {
      case 'High':
        return 'bg-red-50 border-l-4 border-red-600'
      case 'Medium':
        return 'bg-yellow-50 border-l-4 border-yellow-600'
      case 'Low':
        return 'bg-green-50 border-l-4 border-green-600'
      default:
        return 'bg-gray-50'
    }
  }

  const getRiskBadgeColor = (level) => {
    switch (level) {
      case 'High':
        return 'bg-red-100 text-red-800'
      case 'Medium':
        return 'bg-yellow-100 text-yellow-800'
      case 'Low':
        return 'bg-green-100 text-green-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
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

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
        {/* Pie Chart - Track Distribution */}
        <div className="card-lg">
          <h2 className="section-title">Track Distribution</h2>
          {trackDistribution.length > 0 ? (
            <div className="relative h-96">
              <Pie data={pieChartData} options={pieChartOptions} />
            </div>
          ) : (
            <p className="text-gray-500">No track distribution data available</p>
          )}
        </div>

        {/* Bar Chart - Average Skill Scores */}
        <div className="card-lg">
          <h2 className="section-title">Average Skill Scores</h2>
          {skillScores.length > 0 ? (
            <div className="relative h-96">
              <Bar data={barChartData} options={barChartOptions} />
            </div>
          ) : (
            <p className="text-gray-500">No skill score data available</p>
          )}
        </div>
      </div>

      {/* Dropout Risk Students Table */}
      <div className="card-lg mb-8">
        <h2 className="section-title">Students at Risk of Dropout</h2>
        {dropoutRiskStudents.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="bg-gray-100 border-b border-gray-200">
                  <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">
                    Student ID
                  </th>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">
                    Name
                  </th>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">
                    Track
                  </th>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">
                    Attendance
                  </th>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">
                    Avg Score
                  </th>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">
                    Risk Level
                  </th>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">
                    Action
                  </th>
                </tr>
              </thead>
              <tbody>
                {dropoutRiskStudents.map((student) => (
                  <tr
                    key={student.id}
                    className={`border-b border-gray-200 hover:bg-gray-50 ${getRiskColor(student.riskLevel)}`}
                  >
                    <td className="px-6 py-4 text-sm text-gray-900">{student.id}</td>
                    <td className="px-6 py-4 text-sm text-gray-900">{student.name}</td>
                    <td className="px-6 py-4 text-sm text-gray-900">{student.track}</td>
                    <td className="px-6 py-4 text-sm text-gray-900">{student.attendance}%</td>
                    <td className="px-6 py-4 text-sm text-gray-900">{student.averageScore}</td>
                    <td className="px-6 py-4">
                      <span className={`px-3 py-1 rounded-full text-sm font-medium ${getRiskBadgeColor(student.riskLevel)}`}>
                        {student.riskLevel}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <button className="flex items-center gap-2 px-3 py-2 bg-primary-600 text-white rounded hover:bg-primary-700 transition-colors text-sm font-medium">
                        <Mail size={16} />
                        Contact
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p className="text-gray-500">No students at dropout risk</p>
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
