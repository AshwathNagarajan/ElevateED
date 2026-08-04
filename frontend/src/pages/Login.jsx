import React, { useState } from 'react'
import { Mail, Lock, User, Phone, Calendar, BookOpen, Sparkles, Target, TrendingUp, ShieldCheck, ArrowRight } from 'lucide-react'
import { useTranslation } from 'react-i18next'
import LanguageSwitcher from '../components/LanguageSwitcher'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'

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

  const tracks = ['Engineering', 'Computer Science', 'Data Science', 'Business Analytics', 'Design', 'Humanities', 'Life Science', 'Commerce']

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
        await fetch(`${API_BASE_URL}/students/profile/me`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${loginData.access_token}`
          },
          body: JSON.stringify({
            name: fullName,
            age: parseInt(age),
            guardian_contact: guardianContact,
            interest_track: interestTrack
          })
        })
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
    <div className="min-h-screen bg-[#08111f] text-white">
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute inset-0 bg-[linear-gradient(135deg,#08111f_0%,#12323c_45%,#0d1b2d_100%)]" />
        <div className="absolute inset-0 opacity-20 bg-[radial-gradient(circle_at_20%_20%,#22d3ee_0_1px,transparent_1px),radial-gradient(circle_at_80%_40%,#facc15_0_1px,transparent_1px)] bg-[size:34px_34px]" />
        <div className="absolute left-0 top-0 h-full w-1/2 bg-[linear-gradient(115deg,rgba(20,184,166,0.28),transparent_65%)]" />
        <div className="absolute bottom-0 right-0 h-40 w-full bg-[linear-gradient(0deg,rgba(250,204,21,0.16),transparent)]" />
      </div>

      <div className="relative mx-auto grid min-h-screen w-full max-w-7xl grid-cols-1 items-center gap-8 px-4 py-6 sm:px-6 lg:grid-cols-[1.05fr_0.95fr] lg:px-8">
        <section className="hidden lg:block">
          <div className="max-w-2xl">
            <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-white/15 bg-white/10 px-4 py-2 text-sm font-semibold text-cyan-100 shadow-lg backdrop-blur">
              <Sparkles size={16} />
              Adaptive guidance for every learning pace
            </div>
            <h1 className="text-6xl font-black leading-[1.02] tracking-normal">
              ElevateED
              <span className="mt-3 block text-3xl font-bold text-amber-200">
                Find the next right step, not the hardest one.
              </span>
            </h1>
            <p className="mt-6 max-w-xl text-lg leading-8 text-slate-200">
              A guided learning space that watches each student's pace, confidence, and interests, then suggests a path they can actually finish.
            </p>

            <div className="mt-10 grid max-w-2xl grid-cols-3 gap-3">
              <div className="rounded-lg border border-white/12 bg-white/10 p-4 backdrop-blur">
                <Target className="mb-3 text-amber-200" size={24} />
                <p className="text-2xl font-black">1:1</p>
                <p className="mt-1 text-xs font-medium text-slate-300">Guidance path</p>
              </div>
              <div className="rounded-lg border border-white/12 bg-white/10 p-4 backdrop-blur">
                <TrendingUp className="mb-3 text-cyan-200" size={24} />
                <p className="text-2xl font-black">ML</p>
                <p className="mt-1 text-xs font-medium text-slate-300">Learning signals</p>
              </div>
              <div className="rounded-lg border border-white/12 bg-white/10 p-4 backdrop-blur">
                <ShieldCheck className="mb-3 text-emerald-200" size={24} />
                <p className="text-2xl font-black">Safe</p>
                <p className="mt-1 text-xs font-medium text-slate-300">Student first</p>
              </div>
            </div>

            <div className="mt-10 rounded-lg border border-cyan-200/20 bg-slate-950/35 p-5 shadow-2xl backdrop-blur">
              <div className="mb-4 flex items-center justify-between">
                <p className="text-sm font-semibold text-cyan-100">Today's learner signal</p>
                <span className="rounded-full bg-emerald-300 px-3 py-1 text-xs font-black text-emerald-950">Active</span>
              </div>
              <div className="space-y-3">
                <div>
                  <div className="mb-1 flex justify-between text-xs text-slate-300">
                    <span>Interest match</span>
                    <span>82%</span>
                  </div>
                  <div className="h-2 rounded-full bg-white/10">
                    <div className="h-2 w-[82%] rounded-full bg-cyan-300" />
                  </div>
                </div>
                <div>
                  <div className="mb-1 flex justify-between text-xs text-slate-300">
                    <span>Confidence growth</span>
                    <span>68%</span>
                  </div>
                  <div className="h-2 rounded-full bg-white/10">
                    <div className="h-2 w-[68%] rounded-full bg-amber-300" />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        <section className="mx-auto w-full max-w-md">
          <div className="mb-5 flex items-center justify-between lg:hidden">
            <div>
              <p className="text-3xl font-black">ElevateED</p>
              <p className="text-sm font-medium text-cyan-100">{t('login.title')}</p>
            </div>
            <div className="rounded-lg border border-white/10 bg-white/10 backdrop-blur">
              <LanguageSwitcher />
            </div>
          </div>

          <div className="hidden justify-end lg:flex">
            <div className="mb-4 rounded-lg border border-white/10 bg-white/10 backdrop-blur">
              <LanguageSwitcher />
            </div>
          </div>

          <div className="rounded-lg border border-white/15 bg-white p-5 text-gray-900 shadow-2xl sm:p-6">
            <form onSubmit={handleSubmit} className="space-y-5">
              <div>
                <div className="mb-3 inline-flex rounded-lg bg-slate-100 p-1">
                  <button
                    type="button"
                    onClick={() => {
                      setIsLoginMode(true)
                      setError('')
                    }}
                    className={`rounded-md px-4 py-2 text-sm font-bold transition-colors ${
                      isLoginMode ? 'bg-white text-slate-950 shadow-sm' : 'text-slate-500 hover:text-slate-800'
                    }`}
                  >
                    Login
                  </button>
                  <button
                    type="button"
                    onClick={() => {
                      setIsLoginMode(false)
                      setError('')
                    }}
                    className={`rounded-md px-4 py-2 text-sm font-bold transition-colors ${
                      !isLoginMode ? 'bg-white text-slate-950 shadow-sm' : 'text-slate-500 hover:text-slate-800'
                    }`}
                  >
                    Sign up
                  </button>
                </div>
                <h2 className="text-3xl font-black tracking-normal text-slate-950">
                  {isLoginMode ? t('login.welcomeBack') : t('login.createAccount')}
                </h2>
                <p className="mt-2 text-sm leading-6 text-slate-600">
                  {isLoginMode
                    ? 'Continue your learning journey with a path shaped around your pace.'
                    : 'Create a student profile so ElevateED can start learning your interests.'}
                </p>
              </div>

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
              className="flex w-full items-center justify-center gap-2 rounded-lg bg-slate-950 px-4 py-3 font-bold text-white shadow-lg shadow-slate-300 transition-colors hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-50"
            >
              <span>{isLoading 
                ? (isLoginMode ? t('login.loggingIn') : t('login.creatingAccount')) 
                : (isLoginMode ? t('login.loginButton') : t('login.createAccountButton'))
              }</span>
              {!isLoading && <ArrowRight size={18} />}
            </button>

            {/* Toggle Login/Signup */}
            <div className="text-center">
              <button
                type="button"
                onClick={() => {
                  setIsLoginMode(!isLoginMode)
                  setError('')
                }}
                className="text-sm font-bold text-cyan-700 hover:text-cyan-800"
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
                <p className="mb-3 text-center text-xs font-bold uppercase tracking-wide text-slate-500">
                  {t('login.demoCredentials')}
                </p>
                <div className="grid gap-2 text-xs">
                  {[
                    ['Student', 'student.guide@elevated.com', 'Student@123', 'bg-cyan-50 text-cyan-800'],
                    ['Admin', 'admin.guide@elevated.com', 'Admin@123', 'bg-amber-50 text-amber-800'],
                    ['Teacher', 'teacher.guide@elevated.com', 'Teacher@123', 'bg-emerald-50 text-emerald-800']
                  ].map(([role, demoEmail, demoPassword, badgeClass]) => (
                    <div key={role} className="rounded-lg border border-slate-200 bg-slate-50 p-3">
                      <div className="mb-1 flex items-center justify-between gap-2">
                        <span className={`rounded-full px-2 py-1 font-black ${badgeClass}`}>{role}</span>
                        <span className="font-semibold text-slate-500">{demoPassword}</span>
                      </div>
                      <p className="break-words font-semibold text-slate-700">{demoEmail}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </form>
        </div>

        {/* Footer */}
        <div className="mt-6 text-center text-cyan-100">
          <p className="text-sm">
            {t('login.copyright')}
          </p>
        </div>
        </section>
      </div>
    </div>
  )
}

export default Login
