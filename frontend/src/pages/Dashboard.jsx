import React from 'react'
import { Link } from 'react-router-dom'
import { BookOpen, GraduationCap, Lightbulb, ArrowRight } from 'lucide-react'
import StudentDashboard from '../components/StudentDashboard'

const Dashboard = () => {
  // For admin role, we could render AdminDashboard instead
  // For now, we'll show the student dashboard with navigation cards

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      {/* Quick Navigation Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        {/* Explore Courses */}
        <Link
          to="/courses"
          className="group p-6 bg-gradient-to-br from-blue-50 to-blue-100 border-2 border-blue-200 rounded-xl hover:border-blue-400 hover:shadow-lg transition-all"
        >
          <div className="flex items-center justify-between mb-4">
            <div className="w-12 h-12 bg-blue-500 rounded-lg flex items-center justify-center">
              <BookOpen className="text-white" size={24} />
            </div>
            <ArrowRight className="text-blue-400 group-hover:text-blue-600 group-hover:translate-x-1 transition-all" size={20} />
          </div>
          <h3 className="text-lg font-bold text-gray-900 mb-2">Explore Courses</h3>
          <p className="text-sm text-gray-600">Browse all available courses and find your next learning adventure.</p>
        </Link>

        {/* My Courses */}
        <Link
          to="/my-courses"
          className="group p-6 bg-gradient-to-br from-green-50 to-green-100 border-2 border-green-200 rounded-xl hover:border-green-400 hover:shadow-lg transition-all"
        >
          <div className="flex items-center justify-between mb-4">
            <div className="w-12 h-12 bg-green-500 rounded-lg flex items-center justify-center">
              <GraduationCap className="text-white" size={24} />
            </div>
            <ArrowRight className="text-green-400 group-hover:text-green-600 group-hover:translate-x-1 transition-all" size={20} />
          </div>
          <h3 className="text-lg font-bold text-gray-900 mb-2">My Courses</h3>
          <p className="text-sm text-gray-600">Continue your enrolled courses and track your progress.</p>
        </Link>

        {/* Recommendations */}
        <Link
          to="/recommendations"
          className="group p-6 bg-gradient-to-br from-purple-50 to-purple-100 border-2 border-purple-200 rounded-xl hover:border-purple-400 hover:shadow-lg transition-all"
        >
          <div className="flex items-center justify-between mb-4">
            <div className="w-12 h-12 bg-purple-500 rounded-lg flex items-center justify-center">
              <Lightbulb className="text-white" size={24} />
            </div>
            <ArrowRight className="text-purple-400 group-hover:text-purple-600 group-hover:translate-x-1 transition-all" size={20} />
          </div>
          <h3 className="text-lg font-bold text-gray-900 mb-2">Recommendations</h3>
          <p className="text-sm text-gray-600">Get personalized course suggestions based on your learning.</p>
        </Link>
      </div>

      {/* Student Dashboard Content */}
      <StudentDashboard />
    </div>
  )
}

export default Dashboard
