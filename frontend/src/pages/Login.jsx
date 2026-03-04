import React, { useState } from 'react'
import { Mail, Lock, User, Phone, Calendar, BookOpen } from 'lucide-react'
import { useTranslation } from 'react-i18next'
import LanguageSwitcher from '../components/LanguageSwitcher'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const Login = ({ onLogin }) => {
  const { t } = useTranslation()
  const [isLoginMode, setIsLoginMode] = useState(true)
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')
  
  // Signup fields
  const [fullName, setFullName] = useState('')
  const [age, setAge] = useState('')
  const [guardianContact, setGuardianContact] = useState('')
  const [interestTrack, setInterestTrack] = useState('Engineering')

  const tracks = ['Engineering', 'Data Science', 'Design', 'Product Management', 'Business Analytics']

  const handleLogin = async (e) => {
    e.preventDefault()
    setError('')
    setIsLoading(true)

    try {
      if (!email || !password) {
        setError('Please fill in all fields')
        setIsLoading(false)
        return
      }

      const response = await fetch(`${API_BASE_URL}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      })

      const data = await response.json()

      if (!response.ok) {
        setError(data.detail || 'Invalid email or password')
        setIsLoading(false)
        return
      }

      // Store token in localStorage
      localStorage.setItem('token', data.access_token)
      localStorage.setItem('userEmail', email)
      
      // Fetch the actual user role from the server
      try {
        const meResponse = await fetch(`${API_BASE_URL}/auth/me`, {
          headers: {
            'Authorization': `Bearer ${data.access_token}`,
            'Content-Type': 'application/json'
          }
        })
        
        if (meResponse.ok) {
          const user = await meResponse.json()
          const userRole = user.role?.toLowerCase() || 'student'
          localStorage.setItem('userRole', userRole)
          onLogin(userRole)
        } else {
          // Fallback to email-based role detection if /me fails
          const userRole = email.includes('admin') ? 'admin' : 
                           email.includes('mentor') ? 'mentor' : 'student'
          localStorage.setItem('userRole', userRole)
          onLogin(userRole)
        }
      } catch (fetchErr) {
        // Fallback to email-based role detection if network fails
        const userRole = email.includes('admin') ? 'admin' : 
                         email.includes('mentor') ? 'mentor' : 'student'
        localStorage.setItem('userRole', userRole)
        onLogin(userRole)
      }
      
      setIsLoading(false)
    } catch (err) {
      setError('Login failed. Please check your connection and try again.')
      setIsLoading(false)
    }
  }

  const handleSignup = async (e) => {
    e.preventDefault()
    setError('')
    setIsLoading(true)

    try {
      if (!email || !password || !fullName || !age || !guardianContact) {
        setError('Please fill in all required fields')
        setIsLoading(false)
        return
      }

      // First, create user account
      const userResponse = await fetch(`${API_BASE_URL}/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email,
          password,
          full_name: fullName,
          role: 'student'
        })
      })

      const userData = await userResponse.json()

      if (!userResponse.ok) {
        setError(userData.detail || 'Registration failed')
        setIsLoading(false)
        return
      }

      // Then create student record
      const studentResponse = await fetch(`${API_BASE_URL}/students/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: fullName,
          age: parseInt(age),
          guardian_contact: guardianContact,
          interest_track: interestTrack
        })
      })

      if (!studentResponse.ok) {
        console.warn('Student record creation warning - user created but student profile may need setup')
      }

      // Auto-login after successful registration
      const loginResponse = await fetch(`${API_BASE_URL}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      })

      const loginData = await loginResponse.json()

      if (loginResponse.ok) {
        localStorage.setItem('token', loginData.access_token)
        localStorage.setItem('userEmail', email)
        localStorage.setItem('userRole', 'student')
        onLogin('student')
      } else {
        // Registration succeeded but auto-login failed, switch to login mode
        setIsLoginMode(true)
        setError('Registration successful! Please log in.')
      }

      setIsLoading(false)
    } catch (err) {
      setError('Registration failed. Please try again.')
      setIsLoading(false)
    }
  }

  const handleSubmit = isLoginMode ? handleLogin : handleSignup

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-600 to-secondary-600 flex items-center justify-center px-4 py-8">
      <div className="w-full max-w-md">
        {/* Language Switcher */}
        <div className="flex justify-end mb-4">
          <div className="bg-white/10 backdrop-blur-sm rounded-lg">
            <LanguageSwitcher />
          </div>
        </div>
        
        {/* Header */}
        <div className="text-center mb-8">
          <div className="text-5xl font-bold text-white mb-2">
            ElevateED
          </div>
          <p className="text-primary-100 text-lg">
            {t('login.title')}
          </p>
        </div>

        {/* Login/Signup Card */}
        <div className="card shadow-card-lg">
          <form onSubmit={handleSubmit} className="space-y-5">
            <h2 className="text-2xl font-bold text-gray-900 text-center">
              {isLoginMode ? t('login.welcomeBack') : t('login.createAccount')}
            </h2>

            {/* Error Message */}
            {error && (
              <div className={`px-4 py-3 rounded-lg text-sm ${
                error.includes('successful') 
                  ? 'bg-green-50 border border-green-200 text-green-700'
                  : 'bg-red-50 border border-red-200 text-red-700'
              }`}>
                {error}
              </div>
            )}

            {/* Signup: Full Name Field */}
            {!isLoginMode && (
              <div>
                <label htmlFor="fullName" className="block text-sm font-medium text-gray-700 mb-2">
                  {t('login.fullName')} *
                </label>
                <div className="relative">
                  <User size={18} className="absolute left-3 top-3 text-gray-400" />
                  <input
                    id="fullName"
                    type="text"
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                    placeholder="John Doe"
                    className="input-field pl-10"
                    disabled={isLoading}
                  />
                </div>
              </div>
            )}

            {/* Email Field */}
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
                {t('login.email')} *
              </label>
              <div className="relative">
                <Mail size={18} className="absolute left-3 top-3 text-gray-400" />
                <input
                  id="email"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="you@example.com"
                  className="input-field pl-10"
                  disabled={isLoading}
                />
              </div>
            </div>

            {/* Password Field */}
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-2">
                {t('login.password')} *
              </label>
              <div className="relative">
                <Lock size={18} className="absolute left-3 top-3 text-gray-400" />
                <input
                  id="password"
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  className="input-field pl-10"
                  disabled={isLoading}
                />
              </div>
            </div>

            {/* Signup: Additional Fields */}
            {!isLoginMode && (
              <>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label htmlFor="age" className="block text-sm font-medium text-gray-700 mb-2">
                      {t('login.age')} *
                    </label>
                    <div className="relative">
                      <Calendar size={18} className="absolute left-3 top-3 text-gray-400" />
                      <input
                        id="age"
                        type="number"
                        min="16"
                        max="60"
                        value={age}
                        onChange={(e) => setAge(e.target.value)}
                        placeholder="20"
                        className="input-field pl-10"
                        disabled={isLoading}
                      />
                    </div>
                  </div>
                  <div>
                    <label htmlFor="guardianContact" className="block text-sm font-medium text-gray-700 mb-2">
                      {t('login.contact')} *
                    </label>
                    <div className="relative">
                      <Phone size={18} className="absolute left-3 top-3 text-gray-400" />
                      <input
                        id="guardianContact"
                        type="tel"
                        value={guardianContact}
                        onChange={(e) => setGuardianContact(e.target.value)}
                        placeholder="9876543210"
                        className="input-field pl-10"
                        disabled={isLoading}
                      />
                    </div>
                  </div>
                </div>

                <div>
                  <label htmlFor="interestTrack" className="block text-sm font-medium text-gray-700 mb-2">
                    {t('login.interestTrack')}
                  </label>
                  <div className="relative">
                    <BookOpen size={18} className="absolute left-3 top-3 text-gray-400" />
                    <select
                      id="interestTrack"
                      value={interestTrack}
                      onChange={(e) => setInterestTrack(e.target.value)}
                      className="input-field pl-10"
                      disabled={isLoading}
                    >
                      {tracks.map(track => (
                        <option key={track} value={track}>{track}</option>
                      ))}
                    </select>
                  </div>
                </div>
              </>
            )}

            {/* Submit Button */}
            <button
              type="submit"
              disabled={isLoading}
              className="w-full py-3 bg-primary-600 text-white rounded-lg font-medium hover:bg-primary-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading 
                ? (isLoginMode ? t('login.loggingIn') : t('login.creatingAccount')) 
                : (isLoginMode ? t('login.loginButton') : t('login.createAccountButton'))
              }
            </button>

            {/* Toggle Login/Signup */}
            <div className="text-center">
              <button
                type="button"
                onClick={() => {
                  setIsLoginMode(!isLoginMode)
                  setError('')
                }}
                className="text-primary-600 hover:text-primary-700 text-sm font-medium"
              >
                {isLoginMode 
                  ? t('login.noAccount')
                  : t('login.hasAccount')
                }
              </button>
            </div>

            {/* Demo Credentials */}
            {isLoginMode && (
              <div className="pt-4 border-t border-gray-200">
                <p className="text-xs text-gray-600 text-center mb-3">
                  {t('login.demoCredentials')}
                </p>
                <div className="bg-gray-50 rounded-lg p-3 space-y-2 text-xs">
                  <p className="text-gray-700">
                    <strong>Admin:</strong> admin@elevated.com / dharsini@3137
                  </p>
                  <p className="text-gray-700">
                    <strong>Student:</strong> aarav.patel@student.elevated.com / student123
                  </p>
                </div>
              </div>
            )}
          </form>
        </div>

        {/* Footer */}
        <div className="text-center mt-8 text-primary-100">
          <p className="text-sm">
            {t('login.copyright')}
          </p>
        </div>
      </div>
    </div>
  )
}

export default Login
