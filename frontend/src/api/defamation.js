import http from './http'

// 모델 목록 (기존 백엔드 경로 유지)
export const fetchModels = () =>
  http.get('/api/v1/defamation/models').then(r => r.data)

// 분류 요청 (기존 백엔드 경로 유지)
export const classifyText = (payload) =>
  http.post('/api/v1/defamation/predict', payload).then(r => r.data)

// ===== 최근 사례 조회용 (새 백엔드) =====
// 백엔드는 page/size/q 형태로 받으니, 프론트 limit을 size로 매핑
const pageParams = (limit = 10, q = '') => ({ page: 0, size: limit, q })

// 실제 판례 목록
export const fetchRecentCases = (limit=10, q='') =>
  http.get('/cases', { params: pageParams(limit, q) }).then(r => r.data)

// 최근 모델 분류 목록
export const fetchRecentModelCases = (limit=10, q='') =>
  http.get('/classification-requests', { params: pageParams(limit, q) }).then(r => r.data)

// (옵션) 채팅
export const chatOnce = (payload) =>
  http.post('/api/v1/chat/completions', payload).then(r => r.data)
