import React, { useState } from 'react'
import { NavLink as Link } from 'react-router-dom'
import { Menu, X, LogOut, Home, BookOpen, GraduationCap, Lightbulb, Users, UserCog, User } from 'lucide-react'
import { useTranslation } from 'react-i18next'
import LanguageSwitcher from './LanguageSwitcher'

const Navbar = ({ userRole, onLogout }) => {
  const { t } = useTranslation()
  const [isOpen, setIsOpen] = useState(false)

  const toggleMenu = () => setIsOpen(!isOpen)

  // Student navigation links
  const studentLinks = [
    { to: '/', label: t('nav.dashboard'), icon: Home },
    { to: '/courses', label: t('nav.courses'), icon: BookOpen },
    { to: '/my-courses', label: t('nav.myCourses'), icon: GraduationCap },
    { to: '/recommendations', label: t('nav.recommendations'), icon: Lightbulb },
  ]

  // Admin navigation links
  const adminLinks = [
    { to: '/', label: t('nav.dashboard'), icon: Home },
    { to: '/courses', label: t('nav.manageCourses'), icon: BookOpen },
    { to: '/admin/students', label: 'Students', icon: Users },
    { to: '/admin/mentors', label: 'Mentors', icon: UserCog },
  ]

  const mentorLinks = [
    { to: '/', label: t('nav.dashboard'), icon: Home },
    { to: '/mentor/courses', label: t('nav.courses'), icon: BookOpen },
    { to: '/mentor/profile', label: 'Profile', icon: User },
  ]

  const navLinks = userRole === 'admin' ? adminLinks : userRole === 'mentor' ? mentorLinks : studentLinks

  const getLinkClassName = ({ isActive }) =>
    `flex items-center gap-2 px-3 py-2 rounded-lg transition-colors ${
      isActive
        ? 'bg-cyan-300 text-slate-950 font-bold shadow-sm'
        : 'text-slate-300 hover:bg-white/10 hover:text-white'
    }`

  return (
    <nav className="sticky top-0 z-50 border-b border-white/10 bg-[#08111f]/85 shadow-2xl shadow-black/20 backdrop-blur-xl">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          {/* Logo */}
          <div className="flex items-center">
            <Link to="/" className="text-2xl font-black text-white hover:text-cyan-200">
              ElevateED
            </Link>
          </div>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center gap-2">
            {navLinks.map(link => (
              <Link
                key={link.to}
                to={link.to}
                className={getLinkClassName}
                end={link.to === '/'}
              >
                <link.icon size={18} />
                <span className="text-sm">{link.label}</span>
              </Link>
            ))}
          </div>

          {/* Desktop User Menu */}
          <div className="hidden md:flex items-center gap-4">
            <LanguageSwitcher />
            <span className="text-xs font-bold text-amber-100 bg-amber-300/15 border border-amber-200/20 px-3 py-1 rounded-full">
              {userRole === 'admin' ? t('nav.admin') : userRole === 'mentor' ? 'Mentor' : t('nav.student')}
            </span>
            <button
              onClick={onLogout}
              className="flex items-center gap-2 px-4 py-2 text-rose-200 hover:bg-rose-400/10 rounded-lg transition-colors"
            >
              <LogOut size={18} />
              <span className="text-sm font-medium">{t('nav.logout')}</span>
            </button>
          </div>

          {/* Mobile Menu Button */}
          <div className="md:hidden flex items-center">
            <button
              onClick={toggleMenu}
              className="text-slate-200 hover:text-white p-2"
              aria-label="Toggle menu"
            >
              {isOpen ? <X size={24} /> : <Menu size={24} />}
            </button>
          </div>
        </div>

        {/* Mobile Menu */}
        {isOpen && (
          <div className="md:hidden pb-4 border-t border-white/10 pt-4">
            <div className="space-y-1">
              {navLinks.map(link => (
                <Link
                  key={link.to}
                  to={link.to}
                  className={getLinkClassName}
                  end={link.to === '/'}
                  onClick={() => setIsOpen(false)}
                >
                  <link.icon size={18} />
                  <span>{link.label}</span>
                </Link>
              ))}
            </div>
            <div className="mt-4 pt-4 border-t border-white/10">
              <div className="mb-3 px-3">
                <LanguageSwitcher />
              </div>
              <div className="text-xs font-bold text-amber-100 mb-3 px-3">
                {userRole === 'admin' ? t('nav.admin') : userRole === 'mentor' ? 'Mentor' : t('nav.student')}
              </div>
              <button
                onClick={() => {
                  setIsOpen(false)
                  onLogout()
                }}
                className="w-full flex items-center gap-2 px-3 py-2 text-rose-200 hover:bg-rose-400/10 rounded-lg transition-colors"
              >
                <LogOut size={18} />
                {t('nav.logout')}
              </button>
            </div>
          </div>
        )}
      </div>
    </nav>
  )
}

export default Navbar
