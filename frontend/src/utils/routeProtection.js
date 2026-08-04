import React from 'react'
import ProtectedRoute from '../components/ProtectedRoute'

/**
 * Route Protection Helpers - Centralized role-based access control
 * 
 * These helpers provide a clean way to define routes with role requirements
 * instead of repeating ProtectedRoute components throughout the app.
 * 
 * ✅ SECURITY:
 * - Consistent role checking across all routes
 * - Clear separation of student/mentor/admin pages
 * - Easy to audit which pages require which roles
 */

/**
 * adminOnly - Restrict route to admin users only
 */
export const adminOnly = (component) => (
  <ProtectedRoute allowedRoles={['admin']}>
    {component}
  </ProtectedRoute>
)

/**
 * mentorOnly - Restrict route to mentor users only
 */
export const mentorOnly = (component) => (
  <ProtectedRoute allowedRoles={['mentor']}>
    {component}
  </ProtectedRoute>
)

/**
 * studentOnly - Restrict route to student users only
 */
export const studentOnly = (component) => (
  <ProtectedRoute allowedRoles={['student']}>
    {component}
  </ProtectedRoute>
)

/**
 * adminOrMentor - Restrict route to admin or mentor users
 */
export const adminOrMentor = (component) => (
  <ProtectedRoute allowedRoles={['admin', 'mentor']}>
    {component}
  </ProtectedRoute>
)

/**
 * authenticated - Require authentication but no specific role restriction
 */
export const authenticated = (component) => (
  <ProtectedRoute allowedRoles={['student', 'mentor', 'admin']}>
    {component}
  </ProtectedRoute>
)

export default {
  adminOnly,
  mentorOnly,
  studentOnly,
  adminOrMentor,
  authenticated
}
