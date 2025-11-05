import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '@/views/Dashboard.vue'

const routes = [
  { path: '/', component: Dashboard },
  { path: '/cases', component: () => import('@/views/RecentCases.vue') },
]

export default createRouter({
  history: createWebHistory(),
  routes,
})
