<template>
  <div class="page">
    <!-- 로딩 오버레이 -->
    <transition name="fade">
      <div v-if="showOverlay" class="overlay">
        <video class="overlay-video" src="/law.mp4" autoplay loop muted playsinline></video>
      </div>
    </transition>

    <div class="grid">
      <!-- 1행 1열: 입력 -->
      <section class="card">
        <header class="card-hd">
          <h3>명예훼손 AI</h3>
          <div class="muted">{{ text.length }} 자</div>
        </header>

        <div class="card-bd">
          <div class="field">
            <label class="label">Model</label>
            <select v-model="modelVersion" class="control">
              <option v-for="m in models" :key="m" :value="m">{{ m }}</option>
            </select>
          </div>

          <div class="field" style="margin-top:12px;">
            <label class="label">Text</label>
            <textarea
              v-model="text"
              class="control"
              rows="9"
              placeholder="예) 그는 학력과 경력을 모두 속였다는 글을 봤는데 사실인가요?"></textarea>
          </div>

          <div class="row" style="margin-top:14px;">
            <button class="btn" :disabled="loading" @click="onClassify">
              {{ loading ? 'Predicting…' : 'Classify' }}
            </button>
            <button class="btn secondary" :disabled="loading" @click="onClear">Clear</button>
          </div>
        </div>
      </section>

      <!-- 1행 2열: 결과 -->
      <section class="card">
        <header class="card-hd"><h3>예상 판결</h3></header>
        <div class="card-bd">
          <div v-if="result" class="verdict">
            <div class="pill" :class="verdictView.cls">{{ verdictView.text }}</div>
            <pre class="json">{{ prettyResult }}</pre>
          </div>
          <div v-else class="muted">아직 결과가 없습니다. 왼쪽에서 텍스트를 입력해 분류해보세요.</div>
        </div>
      </section>

      <!-- 2행 전체: 관련 실제 판례 -->
      <section class="card span-2">
        <header class="card-hd">
          <h3>관련 실제 판례</h3>
          <div class="row" style="gap:8px; align-items:center;">
            <label class="muted">Show</label>
            <select v-model.number="court.limit" class="control small" @change="loadCourt">
              <option :value="5">5</option>
              <option :value="10">10</option>
              <option :value="20">20</option>
              <option :value="50">50</option>
            </select>
            <span class="muted">cases</span>
          </div>
        </header>

        <div class="card-bd">
          <table class="table">
            <thead>
              <tr>
                <th style="width:60%">상황</th>
                <th style="width:20%">판결</th>
                <th style="width:20%">형량</th>
              </tr>
            </thead>

            <tbody v-if="courtItems.length">
              <tr v-for="it in courtItems" :key="it.id">
                <td>{{ it.sentence ?? it.context ?? '—' }}</td>
                <td>{{ it.label ?? it.verdict ?? '—' }}</td>
                <td>{{ it.sentencing ?? '—' }}</td>
              </tr>
            </tbody>

            <tbody v-else>
              <tr>
                <td colspan="3" class="empty">데이터가 없습니다.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { fetchRecentCases } from '@/api/defamation'

const models = ref(['mT5-Base', 'mT5-Large', 'Qwen2.5', 'KoGPT2'])
const modelVersion = ref(models.value[0])

const text = ref('')
const loading = ref(false)
const result = ref(null)
const showOverlay = ref(false)

const prettyResult = computed(() =>
  result.value ? JSON.stringify(result.value, null, 2) : ''
)

const verdictView = computed(() => {
  const raw = (result.value?.result?.label || '').toString().toUpperCase().trim()
  if (raw === 'DEFAMATION') return { text: '유죄', cls: 'pill--bad' }
  if (raw === 'NON_DEFAMATION' || raw === 'NOT_DEFAMATION' || raw === 'NON-DEFAMATION') {
    return { text: '무죄', cls: 'pill--good' }
  }
  return { text: '분류 불가', cls: 'pill--unknown' }
})

async function onClassify () {
  if (!text.value.trim() || !modelVersion.value) return
  loading.value = true
  showOverlay.value = true
  result.value = null
  try {
    await new Promise(res => setTimeout(res, 3000))
    result.value = {
      id: 'req_2025-09-27T14:12:03Z_9a12',
      model_version: modelVersion.value,
      result: { label: 'NON_DEFAMATION' }
    }
  } finally {
    loading.value = false
    showOverlay.value = false
  }
}
function onClear () { text.value = ''; result.value = null }

const court = ref({ limit: 10 })
const courtItems = ref([])
async function loadCourt () {
  const { items: list } = await fetchRecentCases(court.value.limit, '')
  courtItems.value = list || []
}
onMounted(loadCourt)
</script>

<style scoped>
/* =========================================================
   핵심: 컴포넌트 범위 내에서 가로 넘침을 원천 차단
   ========================================================= */
.page {
  --fs-base: clamp(12px, 1vw + 0.5rem, 16px);
  --sp-1: clamp(10px, 0.7vw + 6px, 14px);
  --sp-2: clamp(12px, 0.9vw + 6px, 16px);
  --ctl-pad-v: clamp(8px, 0.7vw + 4px, 12px);
  font-size: var(--fs-base);
  width: 100%;
  overflow-x: clip;                 /* 페이지 레벨 차단 */
}
.page * { min-width: 0; }           /* 그리드 자식들의 폭 주장 금지 */

/* Grid */
.grid{
  display: grid;
  grid-template-columns: minmax(0,1fr) minmax(0,1fr);
  grid-template-rows: auto auto;
  gap: 22px;
  width: 100%;
  min-width: 0;
  overflow-x: clip;                 /* 추가 방지 */
}
@media (max-width: 1024px){
  .grid{ grid-template-columns: 1fr; }
}

/* Card */
.card{
  background:#111827; border:1px solid #1f2937; border-radius:12px; color:#e5e7eb;
  min-width:0; overflow-x: clip;   /* 카드 단위에서도 넘침 차단 */
}
.card-hd{
  display:flex; justify-content:space-between; align-items:center;
  padding: var(--sp-2);
  border-bottom:1px solid #1f2937;
}
.card-bd{ padding: var(--sp-2); min-width:0; overflow-x: clip; }
.span-2{ grid-column: 1 / -1; }
.muted{ color:#94a3b8; font-size: .78rem; }
.row{ display:flex; gap:12px; align-items:center; }

/* Inputs */
.field{ width:100%; }
.label{ display:block; margin-bottom:6px; color:#cbd5e1; font-size:.9rem; }
.control{
  width:100%; box-sizing:border-box; background:#0b1221; border:1px solid #334155; color:#e5e7eb;
  border-radius:10px; padding: var(--ctl-pad-v) 12px; font-size:1rem;
}
.control.small{ width:auto; padding: calc(var(--ctl-pad-v) - 2px) 10px; font-size:.95rem; }
textarea.control{ min-height: 9rem; resize:vertical; }

/* Buttons */
.btn{
  background:#2563eb; color:#fff; border:none; border-radius:10px;
  padding: var(--ctl-pad-v) 14px; font-weight:700; cursor:pointer; font-size:1rem;
}
.btn:disabled{ opacity:.6; cursor:not-allowed; }
.btn.secondary{ background:#18243c; border:1px solid #334155; }

/* Verdict */
.verdict{ display:grid; gap:10px; }
.pill{ display:inline-block; padding:6px 10px; border-radius:999px; font-weight:800; width:fit-content; background:#64748b22; color:#cbd5e1; border:1px solid #334155; }
.pill--bad{ background:#ef444422; color:#fecaca; border:1px solid #7f1d1d; }
.pill--good{ background:#16a34a22; color:#86efac; border:1px solid #14532d; }
.pill--unknown{ background:#64748b22; color:#cbd5e1; border:1px solid #334155; }
.json{
  margin:0; padding:10px 12px; border-radius:10px; background:#0b1221; border:1px solid #334155;
  font-family: ui-mono, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", monospace;
  font-size:.85rem; color:#cbd5e1; white-space: pre-wrap; word-break: break-word;
  overflow-wrap: anywhere; max-width: 100%;
}

/* Table */
.table{
  width:100%; border-collapse:collapse; table-layout: fixed; /* 셀 너비 고정 */
}
.table th,.table td{
  border-top:1px solid #1f2937; padding:10px 12px; text-align:left; font-size:.95rem;
  word-break: break-word; overflow-wrap:anywhere; /* 긴 텍스트 줄바꿈 */
}
.table .empty{ text-align:center; padding:24px 12px; color:#94a3b8; }

/* Overlay */
.fade-enter-active, .fade-leave-active { transition: opacity .25s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
.overlay{ position:fixed; inset:0; display:grid; place-items:center; background:rgba(2,6,23,.35); backdrop-filter:blur(1px); z-index:1000; }
.overlay-video{ width:min(40vw,520px); max-height:60vh; opacity:.75; border-radius:16px; outline:1px solid rgba(148,163,184,.25); }
</style>
