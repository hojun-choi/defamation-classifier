import http from './http'

// ✅ baseURL이 '/api'이므로 여기서는 '/api'를 빼고 호출해야 함

// 모델 목록
export const fetchModels = () =>
  http.get('/v1/defamation/models').then(r => r.data)

// 분류 요청
export const classifyText = (payload) =>
  http.post('/v1/defamation/predict', payload).then(r => r.data)

// ===== 최근 사례 조회용 =====
const pageParams = (limit = 10, q = '') => ({ page: 0, size: limit, q })

export const fetchRecentCases = (limit=10, q='') =>
  http.get('/cases', { params: pageParams(limit, q) }).then(r => r.data)

export const fetchRecentModelCases = (limit=10, q='') =>
  http.get('/classification-requests', { params: pageParams(limit, q) }).then(r => r.data)
