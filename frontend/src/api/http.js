import axios from 'axios'
const http = axios.create({
  baseURL: import.meta.env.VITE_API_BASE || '/api',
  timeout: 15000,
})
http.interceptors.response.use(r=>r, e=>{
  console.error('[API ERROR]', e?.response?.data || e.message)
  return Promise.reject(e)
})
export default http
