import axios from 'axios'

// Central axios instance. Every service module funnels through here so
// auth headers, error normalization, and the base URL only live in one
// place.
const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Attach the authenticated account to each request.
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('reverie:token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Normalize error shape so callers can just read `error.message`.
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    const message =
      error.response?.data?.detail ||
      error.response?.data?.message ||
      error.response?.data?.error ||
      error.message ||
      'Something went wrong talking to the server.'
    return Promise.reject(new Error(message))
  }
)

export default apiClient
