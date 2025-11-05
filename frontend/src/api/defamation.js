import http from './http'

// 모델 목록
export const fetchModels = () =>
  http.get('/api/v1/defamation/models').then(r => r.data)

// 분류 요청
export const classifyText = (payload) =>
  http.post('/api/v1/defamation/predict', payload).then(r => r.data)

// 최근 케이스(검색/limit 지원)
export const fetchRecentCases = (limit=10, q='') =>
  http.get('/api/v1/defamation/cases', { params: { limit, q } }).then(r => r.data)

// (옵션) 채팅
export const chatOnce = (payload) =>
  http.post('/api/v1/chat/completions', payload).then(r => r.data)
