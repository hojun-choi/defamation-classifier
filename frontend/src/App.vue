<template>
  <div class="app">
    <nav class="nav">
      <a class="nav-link" @click.prevent="go('/')" href="/">명예훼손 AI</a>
      <a class="nav-link" @click.prevent="go('/cases')" href="/cases">최근 사례</a>
    </nav>

    <main class="main">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
const router = useRouter()
const go = (p) => router.push(p)
</script>

<style>
/* 추가 보강: 혹시 전역이 늦게 로드돼도 App가 잡도록 한 번 더 선언 */
html, body { margin: 0 !important; padding: 0 !important; border: 0 !important; }

/* 상단 네비 */
.nav {
  display: flex;
  gap: 16px;
  padding: 12px 16px;
  background: #0f172a;
  color: #e2e8f0;
}

/* 밑줄 제거 + 색상 */
.nav-link,
.nav-link:visited,
.nav-link:active,
.nav-link:hover,
.nav-link:focus {
  color: #e2e8f0;
  text-decoration: none !important;
  -webkit-text-decoration: none !important;
  text-decoration-thickness: 0 !important;
  border-bottom: none !important;
  outline: none;
  display: inline-block;
  font-weight: 700;
}

/* 본문 래퍼: 좌우 2vw 여백, 중앙 정렬, 최댓값 없음 */
.main {
  width: min(96vw, 1600px);
  margin-inline: auto;
  padding-inline: 2vw;
  padding-block: 16px;
}

/* 공통 카드/컨트롤(다른 뷰에서 활용) */
.card { background:#111827; border:1px solid #1f2937; border-radius:12px; color:#e5e7eb; }
.input, .select, .btn { width:100%; padding:10px 12px; border-radius:8px; border:1px solid #334155; background:#0b1221; color:#e5e7eb; }
.btn { cursor:pointer; font-weight:700; }
.row { display:flex; gap:12px; }
</style>
