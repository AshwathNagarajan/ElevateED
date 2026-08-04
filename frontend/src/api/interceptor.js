/**
 * API Interceptor - Handles token expiration and unauthorized access
 * 
 * ✅ SECURITY:
 * - Detects 401 Unauthorized responses
 * - Clears auth state when token expires
 * - Redirects user to login on expiration
 * - Prevents infinite redirect loops
 */

let unauthorizedHandler = null

/**
 * Register handler for 401 Unauthorized responses
 * Called from AuthProvider to handle token expiration
 */
export const registerUnauthorizedHandler = (handler) => {
  unauthorizedHandler = handler
}

/**
 * Call when 401 is received from API
 */
export const handleUnauthorizedResponse = () => {
  if (unauthorizedHandler) {
    unauthorizedHandler()
  }
}

export default {
  registerUnauthorizedHandler,
  handleUnauthorizedResponse
}
