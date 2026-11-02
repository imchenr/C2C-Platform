import axios from 'axios'
import { ElMessage } from 'element-plus'

const api = axios.create({
  baseURL: '/api',
  timeout: 12000,
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('campus_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

api.interceptors.response.use(
  (response) => response.data,
  (error) => {
    const message = error.response?.data?.detail || error.message || '请求失败，请稍后再试'
    if (error.response?.status === 401) {
      localStorage.removeItem('campus_token')
      localStorage.removeItem('campus_user')
    }
    ElMessage.error(message)
    return Promise.reject(error)
  },
)

export default api

