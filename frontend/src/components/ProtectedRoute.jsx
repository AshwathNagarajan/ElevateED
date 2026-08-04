import React from 'react'
import { Navigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

/**
 * ProtectedRoute - Secure route wrapper with role-based access control
 * 
 * ✅ SECURITY:
 * - Verifies BOTH isAuthenticated AND role
 * - Prevents page flashing during auth verification
 * - Only renders children if all checks pass
 * - Shows loading state during verification
 * - Redirects to login if not authenticated
 * - Redirects to dashboard if role not allowed
 */

const ProtectedRoute = ({ children, allowedRoles }) => {
  const { isAuthenticated, userRole, isLoading } = useAuth()

  // 1. Still loading auth verification - show loading state
  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Verifying access...</p>
        </div>
      </div>
    )
  }

  // 2. Not authenticated - redirect to login
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  // 3. Authenticated but role not allowed - redirect to dashboard
  if (!allowedRoles.includes(userRole)) {
    return <Navigate to="/" replace />
  }

  // 4. All checks passed - render protected content
  return children
}

export default ProtectedRoute
