import React from 'react'
import { Link } from 'react-router-dom'
import { BookOpen, GraduationCap, Lightbulb, ArrowRight } from 'lucide-react'
import { useTranslation } from 'react-i18next'
import StudentDashboard from '../components/StudentDashboard'

const Dashboard = () => {
  const { t } = useTranslation()
  // For admin role, we could render AdminDashboard instead
  // For now, we'll show the student dashboard with navigation cards

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      {/* Quick Navigation Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        {/* Explore Courses */}
        <Link
          to="/courses"
          className="group overflow-hidden rounded-lg border border-white/12 bg-white/10 p-6 shadow-2xl shadow-black/20 backdrop-blur transition-all hover:-translate-y-1 hover:border-cyan-300/50 hover:bg-white/15"
        >
          <div className="flex items-center justify-between mb-4">
            <div className="w-12 h-12 bg-cyan-300 rounded-lg flex items-center justify-center shadow-lg shadow-cyan-950/20">
              <BookOpen className="text-slate-950" size={24} />
            </div>
            <ArrowRight className="text-cyan-200 group-hover:text-white group-hover:translate-x-1 transition-all" size={20} />
          </div>
          <h3 className="text-lg font-black text-white mb-2">{t('dashboard.exploreCourses')}</h3>
          <p className="text-sm text-slate-300">{t('dashboard.exploreCoursesDesc')}</p>
        </Link>

        {/* My Courses */}
        <Link
          to="/my-courses"
          className="group overflow-hidden rounded-lg border border-white/12 bg-white/10 p-6 shadow-2xl shadow-black/20 backdrop-blur transition-all hover:-translate-y-1 hover:border-emerald-300/50 hover:bg-white/15"
        >
          <div className="flex items-center justify-between mb-4">
            <div className="w-12 h-12 bg-emerald-300 rounded-lg flex items-center justify-center shadow-lg shadow-emerald-950/20">
              <GraduationCap className="text-slate-950" size={24} />
            </div>
            <ArrowRight className="text-emerald-200 group-hover:text-white group-hover:translate-x-1 transition-all" size={20} />
          </div>
          <h3 className="text-lg font-black text-white mb-2">{t('dashboard.myCoursesTitle')}</h3>
          <p className="text-sm text-slate-300">{t('dashboard.myCoursesDesc')}</p>
        </Link>

        {/* Recommendations */}
        <Link
          to="/recommendations"
          className="group overflow-hidden rounded-lg border border-white/12 bg-white/10 p-6 shadow-2xl shadow-black/20 backdrop-blur transition-all hover:-translate-y-1 hover:border-amber-300/50 hover:bg-white/15"
        >
          <div className="flex items-center justify-between mb-4">
            <div className="w-12 h-12 bg-amber-300 rounded-lg flex items-center justify-center shadow-lg shadow-amber-950/20">
              <Lightbulb className="text-slate-950" size={24} />
            </div>
            <ArrowRight className="text-amber-200 group-hover:text-white group-hover:translate-x-1 transition-all" size={20} />
          </div>
          <h3 className="text-lg font-black text-white mb-2">{t('dashboard.recommendationsTitle')}</h3>
          <p className="text-sm text-slate-300">{t('dashboard.recommendationsDesc')}</p>
        </Link>
      </div>

      {/* Student Dashboard Content */}
      <StudentDashboard />
    </div>
  )
}

export default Dashboard
