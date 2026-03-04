import React, { useState } from 'react'
import { NavLink as Link } from 'react-router-dom'
import { Menu, X, LogOut, Home, BookOpen, GraduationCap, Lightbulb } from 'lucide-react'
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
  ]

  const navLinks = userRole === 'admin' ? adminLinks : studentLinks

  const getLinkClassName = ({ isActive }) =>
    `flex items-center gap-2 px-3 py-2 rounded-lg transition-colors ${
      isActive
        ? 'bg-primary-100 text-primary-700 font-semibold'
        : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
    }`

  return (
    <nav className="bg-white shadow-md sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          {/* Logo */}
          <div className="flex items-center">
            <Link to="/" className="text-2xl font-bold text-primary-600 hover:text-primary-700">
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
            <span className="text-xs font-medium text-gray-500 bg-gray-100 px-3 py-1 rounded-full">
              {userRole === 'admin' ? t('nav.admin') : t('nav.student')}
            </span>
            <button
              onClick={onLogout}
              className="flex items-center gap-2 px-4 py-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
            >
              <LogOut size={18} />
              <span className="text-sm font-medium">{t('nav.logout')}</span>
            </button>
          </div>

          {/* Mobile Menu Button */}
          <div className="md:hidden flex items-center">
            <button
              onClick={toggleMenu}
              className="text-gray-600 hover:text-gray-900 p-2"
              aria-label="Toggle menu"
            >
              {isOpen ? <X size={24} /> : <Menu size={24} />}
            </button>
          </div>
        </div>

        {/* Mobile Menu */}
        {isOpen && (
          <div className="md:hidden pb-4 border-t border-gray-100 pt-4">
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
            <div className="mt-4 pt-4 border-t border-gray-100">
              <div className="mb-3 px-3">
                <LanguageSwitcher />
              </div>
              <div className="text-xs font-medium text-gray-500 mb-3 px-3">
                {userRole === 'admin' ? t('nav.admin') : t('nav.student')}
              </div>
              <button
                onClick={() => {
                  setIsOpen(false)
                  onLogout()
                }}
                className="w-full flex items-center gap-2 px-3 py-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
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
