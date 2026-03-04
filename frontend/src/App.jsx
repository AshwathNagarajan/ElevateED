import React, { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import Navbar from './components/Navbar'
import AdminDashboard from './components/AdminDashboard'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import Courses from './pages/Courses'
import CourseView from './pages/CourseView'
import MyCourses from './pages/MyCourses'
import Recommendations from './pages/Recommendations'
import AdminCourses from './pages/AdminCourses'
import './App.css'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [userRole, setUserRole] = useState(null)
  const [isLoading, setIsLoading] = useState(true)

  // Check for existing authentication on app load
  useEffect(() => {
    const validateToken = async () => {
      const token = localStorage.getItem('token')
      
      if (!token) {
        setIsLoading(false)
        return
      }

      try {
        const response = await fetch(`${API_BASE_URL}/auth/me`, {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        })

        if (response.ok) {
          const user = await response.json()
          // Use the role from the server response
          const role = user.role?.toLowerCase() || 'student'
          setUserRole(role)
          setIsAuthenticated(true)
          localStorage.setItem('userRole', role)
        } else {
          // Token is invalid or expired - clear storage
          localStorage.removeItem('token')
          localStorage.removeItem('userEmail')
          localStorage.removeItem('userRole')
        }
      } catch (err) {
        console.error('Token validation failed:', err)
        // Keep existing localStorage values for offline support
        const savedRole = localStorage.getItem('userRole')
        if (savedRole) {
          setUserRole(savedRole)
          setIsAuthenticated(true)
        }
      }
      
      setIsLoading(false)
    }

    validateToken()
  }, [])

  const handleLogin = (role) => {
    setIsAuthenticated(true)
    setUserRole(role)
  }

  const handleLogout = () => {
    localStorage.removeItem('token')
    localStorage.removeItem('userEmail')
    localStorage.removeItem('userRole')
    setIsAuthenticated(false)
    setUserRole(null)
  }

  // Show loading spinner while checking authentication
  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  if (!isAuthenticated) {
    return <Login onLogin={handleLogin} />
  }

  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <Navbar userRole={userRole} onLogout={handleLogout} />
        <main>
          <Routes>
            {/* Dashboard Route */}
            <Route
              path="/"
              element={
                userRole === 'admin' ? (
                  <AdminDashboard />
                ) : (
                  <Dashboard userRole={userRole} />
                )
              }
            />
            
            {/* Course Routes */}
            <Route path="/courses" element={userRole === 'admin' ? <AdminCourses /> : <Courses />} />
            <Route path="/course/:id" element={<CourseView />} />
            
            {/* Student Routes */}
            <Route path="/my-courses" element={<MyCourses />} />
            <Route path="/recommendations" element={<Recommendations />} />
            
            {/* Admin Routes */}
            <Route path="/admin/courses" element={<AdminCourses />} />
            
            {/* Legacy redirect */}
            <Route path="/dashboard" element={<Navigate to="/" replace />} />
          </Routes>
        </main>
      </div>
    </Router>
  )
}

export default App
