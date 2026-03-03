import React from 'react'
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

function App() {
  const [isAuthenticated, setIsAuthenticated] = React.useState(false)
  const [userRole, setUserRole] = React.useState(null)

  const handleLogin = (role) => {
    setIsAuthenticated(true)
    setUserRole(role)
  }

  const handleLogout = () => {
    setIsAuthenticated(false)
    setUserRole(null)
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
