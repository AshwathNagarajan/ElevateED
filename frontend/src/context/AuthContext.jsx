import React, { createContext, useContext, useEffect, useState, useCallback } from 'react'
import { apiGet } from '../api/client'
import { registerUnauthorizedHandler } from '../api/interceptor'

/**
 * AuthContext - Centralized authentication state
 * 
 * ✅ SECURITY:
 * - isAuthenticated: Only true after verified /auth/me response
 * - userRole: Always from server response (source of truth)
 * - isLoading: Prevents rendering before auth verification completes
 * - Logout clears ALL state and storage
 * - Handles 401 token expiration from API
 */

const AuthContext = createContext()

export const AuthProvider = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [userRole, setUserRole] = useState(null)
  const [user, setUser] = useState(null)
  const [isLoading, setIsLoading] = useState(true)

  // Verify token on mount - this is the ONLY source of truth for auth state
  const verifyAuth = useCallback(async () => {
    const token = localStorage.getItem('token')
    
    if (!token) {
      // No token stored - not authenticated
      setIsAuthenticated(false)
      setUserRole(null)
      setUser(null)
      setIsLoading(false)
      return
    }

    try {
      // Verify token by calling /auth/me - this is the security check
      const userData = await apiGet('/auth/me')
      
      // Server response is the source of truth
      const role = userData.role?.toLowerCase() || 'student'
      
      setUserRole(role)
      setUser(userData)
      setIsAuthenticated(true)
      
      // Update cached role (for fallback only)
      localStorage.setItem('userRole', role)
    } catch (err) {
      console.error('Auth verification failed:', err)
      
      // Token is invalid or expired - clear everything
      localStorage.removeItem('token')
      localStorage.removeItem('userEmail')
      localStorage.removeItem('userRole')
      
      setIsAuthenticated(false)
      setUserRole(null)
      setUser(null)
    }
    
    setIsLoading(false)
  }, [])

  // Verify auth on component mount
  useEffect(() => {
    verifyAuth()
  }, [verifyAuth])

  const login = useCallback((userData, role) => {
    // Store token from login response
    if (userData.access_token) {
      localStorage.setItem('token', userData.access_token)
    }
    if (userData.email) {
      localStorage.setItem('userEmail', userData.email)
    }
    
    // Use role from server response (source of truth)
    const normalizedRole = role?.toLowerCase() || 'student'
    
    setUserRole(normalizedRole)
    setUser(userData)
    setIsAuthenticated(true)
    
    // Cache role for offline fallback
    localStorage.setItem('userRole', normalizedRole)
  }, [])

  const logout = useCallback(() => {
    // Clear ALL auth state
    localStorage.removeItem('token')
    localStorage.removeItem('userEmail')
    localStorage.removeItem('userRole')
    
    setIsAuthenticated(false)
    setUserRole(null)
    setUser(null)
  }, [])

  // Register logout handler for API 401 responses
  useEffect(() => {
    registerUnauthorizedHandler(logout)
  }, [logout])

  // Handle token expiration (401 from API)
  const handleUnauthorized = useCallback(() => {
    logout()
  }, [logout])

  const value = {
    isAuthenticated,
    userRole,
    user,
    isLoading,
    login,
    logout,
    handleUnauthorized,
    verifyAuth // Expose for manual re-verify if needed
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

/**
 * Hook to use auth context
 * Use this in any component that needs auth state or functions
 */
export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider')
  }
  return context
}

export default AuthContext
