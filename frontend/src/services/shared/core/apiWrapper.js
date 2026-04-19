/**
 * API Request Wrapper
 * Unified error handling and response extraction for all service methods
 */
import api from './api'

/**
 * Wrap API calls with consistent error handling
 * @param {Function} requestFn - Async function that returns axios response
 * @param {string} errorContext - Context for error logging
 * @returns {Promise<any>} - Response data
 */
export const handleRequest = async (requestFn, errorContext = 'API request') => {
    try {
        const response = await requestFn()
        return response.data
    } catch (error) {
        console.error(`Error in ${errorContext}:`, error.response?.data || error.message)
        throw error
    }
}

/**
 * Create a service method with automatic error handling
 * @param {string} method - HTTP method (get, post, put, patch, delete)
 * @param {string} url - API endpoint
 * @param {Object} options - Request options (data, params, config)
 * @param {string} errorContext - Context for error logging
 */
export const createRequest = (method, url, options = {}, errorContext) => {
    const { data, params, config } = options
    // console.log("request" , url)

    const requestMap = {
        get: () => api.get(url, { params, ...config }),
        post: () => api.post(url, data, config),
        put: () => api.put(url, data, config),
        patch: () => api.patch(url, data, config),
        delete: () => api.delete(url, config)
    }

    return handleRequest(requestMap[method], errorContext || `${method.toUpperCase()} ${url}`)
}

/**
 * Shorthand methods for common operations
 */
export const apiGet = (url, params, errorContext) =>
    createRequest('get', url, { params }, errorContext)

export const apiPost = (url, data, errorContext, config) =>
    createRequest('post', url, { data, config }, errorContext)

export const apiPut = (url, data, errorContext) =>
    createRequest('put', url, { data }, errorContext)

export const apiPatch = (url, data, errorContext) =>
    createRequest('patch', url, { data }, errorContext)

export const apiDelete = (url, errorContext) =>
    createRequest('delete', url, {}, errorContext)

export default { handleRequest, createRequest, apiGet, apiPost, apiPut, apiPatch, apiDelete }

