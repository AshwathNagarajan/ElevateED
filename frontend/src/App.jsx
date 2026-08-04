import React from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import Navbar from './components/Navbar'
import StudyPartner3D from './components/StudyPartner3D'
import AdminDashboard from './components/AdminDashboard'
import MentorDashboard from './components/MentorDashboard'
import ProtectedRoute from './components/ProtectedRoute'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import Courses from './pages/Courses'
import CourseView from './pages/CourseView'
import MyCourses from './pages/MyCourses'
import Recommendations from './pages/Recommendations'
import AdminCourses from './pages/AdminCourses'
import AdminStudents from './pages/AdminStudents'
import AdminMentors from './pages/AdminMentors'
import MentorCourses from './pages/MentorCourses'
import MentorProfile from './pages/MentorProfile'
import MentorSignup from './pages/MentorSignup'
import StudentProfile from './pages/StudentProfile'
import { useAuth } from './context/AuthContext'
import './App.css'

function App() {
  const { isAuthenticated, userRole, isLoading, login, logout } = useAuth()

  const handleLogin = (role) => {
    login({
      access_token: localStorage.getItem('token'),
      email: localStorage.getItem('userEmail')
    }, role)
  }

  // Show loading spinner while checking authentication
  if (isLoading) {
    return (
      <div className="min-h-screen bg-[#08111f] flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-cyan-300"></div>
      </div>
    )
  }

  return (
    <Router>
      <div className="app-shell min-h-screen">
        {isAuthenticated && <Navbar userRole={userRole} onLogout={logout} />}
        {isAuthenticated && <StudyPartner3D userRole={userRole} />}
        <main className="relative z-10">
          <Routes>
            <Route path="/login" element={isAuthenticated ? <Navigate to="/" replace /> : <Login onLogin={handleLogin} />} />
            <Route path="/mentor-signup" element={isAuthenticated ? <Navigate to="/" replace /> : <MentorSignup onLogin={handleLogin} />} />

            <Route
              path="/"
              element={
                <ProtectedRoute allowedRoles={['student', 'mentor', 'admin']}>
                  {userRole === 'admin' ? <AdminDashboard /> : userRole === 'mentor' ? <MentorDashboard /> : <Dashboard />}
                </ProtectedRoute>
              }
            />

            <Route path="/courses" element={<ProtectedRoute allowedRoles={['student', 'mentor', 'admin']}>{userRole === 'admin' ? <AdminCourses /> : <Courses />}</ProtectedRoute>} />
            <Route path="/course/:id" element={<ProtectedRoute allowedRoles={['student', 'mentor', 'admin']}><CourseView /></ProtectedRoute>} />
            <Route path="/my-courses" element={<ProtectedRoute allowedRoles={['student']}><MyCourses /></ProtectedRoute>} />
            <Route path="/recommendations" element={<ProtectedRoute allowedRoles={['student']}><Recommendations /></ProtectedRoute>} />
            <Route path="/profile" element={<ProtectedRoute allowedRoles={['student']}><StudentProfile /></ProtectedRoute>} />

            <Route path="/admin/courses" element={<ProtectedRoute allowedRoles={['admin']}><AdminCourses /></ProtectedRoute>} />
            <Route path="/admin/students" element={<ProtectedRoute allowedRoles={['admin']}><AdminStudents /></ProtectedRoute>} />
            <Route path="/admin/mentors" element={<ProtectedRoute allowedRoles={['admin']}><AdminMentors /></ProtectedRoute>} />

            <Route path="/mentor/courses" element={<ProtectedRoute allowedRoles={['mentor']}><MentorCourses /></ProtectedRoute>} />
            <Route path="/mentor/profile" element={<ProtectedRoute allowedRoles={['mentor']}><MentorProfile /></ProtectedRoute>} />

            <Route path="/dashboard" element={<Navigate to="/" replace />} />
            <Route path="*" element={<Navigate to={isAuthenticated ? "/" : "/login"} replace />} />
          </Routes>
        </main>
      </div>
    </Router>
  )
}

export default App
