/**
 * Centralized API client for ElevateED frontend
 * Handles:
 * - Base URL configuration via VITE_API_URL environment variable
 * - Automatic Authorization Bearer token attachment
 * - Consistent JSON headers
 * - Centralized error handling
 * - Token expiration (401 Unauthorized)
 * 
 * ✅ SECURITY:
 * - Detects 401 responses and triggers auth cleanup
 * - Prevents stale tokens from being used
 * - Redirects to login on token expiration
 */

import { handleUnauthorizedResponse } from './interceptor'

const getBaseUrl = () => {
  return import.meta.env.VITE_API_URL || 'http://localhost:8000/api'
}

const getAuthHeaders = (includeContentType = true) => {
  const token = localStorage.getItem('token')
  const headers = {}
  
  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }
  
  if (includeContentType) {
    headers['Content-Type'] = 'application/json'
  }
  
  return headers
}

const handleResponse = async (response) => {
  // ⚠️  SECURITY: Handle 401 Unauthorized (token expired or invalid)
  if (response.status === 401) {
    // Clear auth state in AuthContext
    handleUnauthorizedResponse()
    // Still throw error for the calling code to handle
    const error = new Error('Unauthorized - please login again')
    error.status = 401
    throw error
  }

  if (!response.ok) {
    let errorMessage = 'API request failed'
    try {
      const errorData = await response.json()
      errorMessage = errorData.detail || errorData.message || errorMessage
    } catch {
      // If response is not JSON, use status text
      errorMessage = response.statusText || errorMessage
    }
    
    const error = new Error(errorMessage)
    error.status = response.status
    throw error
  }
  
  // Handle empty responses (e.g., 204 No Content)
  if (response.status === 204) {
    return null
  }
  
  return response.json().catch(() => null)
}

/**
 * Make a GET request
 * @param {string} endpoint - API endpoint (without base URL)
 * @param {object} options - Additional fetch options
 * @returns {Promise} Response data
 */
export const apiGet = async (endpoint, options = {}) => {
  const url = `${getBaseUrl()}${endpoint}`
  const response = await fetch(url, {
    method: 'GET',
    headers: getAuthHeaders(true),
    ...options
  })
  return handleResponse(response)
}

/**
 * Make a POST request
 * @param {string} endpoint - API endpoint (without base URL)
 * @param {object} data - Request body data
 * @param {object} options - Additional fetch options
 * @returns {Promise} Response data
 */
export const apiPost = async (endpoint, data = null, options = {}) => {
  const url = `${getBaseUrl()}${endpoint}`
  const body = data ? JSON.stringify(data) : null
  const response = await fetch(url, {
    method: 'POST',
    headers: getAuthHeaders(true),
    body,
    ...options
  })
  return handleResponse(response)
}

/**
 * Make a PUT request
 * @param {string} endpoint - API endpoint (without base URL)
 * @param {object} data - Request body data
 * @param {object} options - Additional fetch options
 * @returns {Promise} Response data
 */
export const apiPut = async (endpoint, data = null, options = {}) => {
  const url = `${getBaseUrl()}${endpoint}`
  const body = data ? JSON.stringify(data) : null
  const response = await fetch(url, {
    method: 'PUT',
    headers: getAuthHeaders(true),
    body,
    ...options
  })
  return handleResponse(response)
}

/**
 * Make a DELETE request
 * @param {string} endpoint - API endpoint (without base URL)
 * @param {object} options - Additional fetch options
 * @returns {Promise} Response data
 */
export const apiDelete = async (endpoint, options = {}) => {
  const url = `${getBaseUrl()}${endpoint}`
  const response = await fetch(url, {
    method: 'DELETE',
    headers: getAuthHeaders(true),
    ...options
  })
  return handleResponse(response)
}

/**
 * Generic fetch wrapper for custom requests
 * @param {string} endpoint - API endpoint (without base URL)
 * @param {object} options - Full fetch options
 * @returns {Promise} Response data
 */
export const apiFetch = async (endpoint, options = {}) => {
  const url = `${getBaseUrl()}${endpoint}`
  const headers = {
    ...getAuthHeaders(true),
    ...options.headers
  }
  
  const response = await fetch(url, {
    ...options,
    headers
  })
  return handleResponse(response)
}

/**
 * Export base URL for use in other contexts (e.g., image loading)
 */
export const API_BASE_URL = getBaseUrl()
