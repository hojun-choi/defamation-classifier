<template>
  <section class="page card">
    <header class="card-hd">
      <div class="left">
        <h3>{{ modeLabel }}</h3>
        <span class="muted helper">{{ helperText }}</span>
      </div>

      <div class="controls">
        <select v-model="mode" class="select small">
          <option value="court">실제 판례</option>
          <option value="model">최근 모델 분류</option>
        </select>

        <select v-model.number="limit" class="select small">
          <option :value="5">5</option>
          <option :value="10">10</option>
          <option :value="20">20</option>
          <option :value="50">50</option>
        </select>

        <input
          v-model="q"
          class="input"
          type="text"
          placeholder="검색어 입력"
          @keyup.enter="onSearch"
        />

        <button class="btn small" @click="onSearch">검색</button>
      </div>
    </header>

    <div class="card-bd">
      <table class="table">
        <thead>
          <tr>
            <!-- ✅ 순서: 판결 / 형량 / 상황 / 판결이유 -->
            <th style="width:10%">판결</th>
            <th style="width:18%">형량</th>
            <th style="width:42%">상황</th>
            <th style="width:30%">판결 이유</th>
          </tr>
        </thead>

        <tbody v-if="items.length">
          <tr v-for="it in items" :key="it.id">
            <!-- 판결 -->
            <td>{{ it.sentenceJudgment ?? '—' }}</td>

            <!-- 형량 -->
            <td>{{ formatSentence(it) || '—' }}</td>

            <!-- 상황 (2줄 + 클릭 모달) -->
            <td>
              <div class="cell-wrap">
                <div
                  class="clamp clickable"
                  @click="openModal('situation', it.problemSituation)"
                >
                  {{ it.problemSituation || '—' }}
                </div>
                <div class="hint muted">클릭하면 전체 보기 / 복사</div>
              </div>
            </td>

            <!-- 판결 이유 (2줄 + 클릭 모달) -->
            <td>
              <div class="cell-wrap">
                <div
                  class="clamp clickable"
                  @click="openModal('reason', it.sentenceReason)"
                >
                  {{ it.sentenceReason || '—' }}
                </div>
                <div class="hint muted">클릭하면 전체 보기 / 복사</div>
              </div>
            </td>
          </tr>
        </tbody>

        <tbody v-else>
          <tr>
            <td colspan="4" class="empty">
              {{ loading ? '로딩중...' : '데이터가 없습니다.' }}
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- =========================
         Full text modal (복사 가능)
         ========================= -->
    <transition name="fade">
      <div
        v-if="modal.show"
        class="modal-backdrop"
        @click.self="closeModal"
      >
        <div class="modal-card" role="dialog" aria-modal="true">
          <header class="modal-hd">
            <h4>{{ modalTitle }}</h4>
            <div class="modal-actions">
              <button class="btn ghost small modal-btn" @click="copyModalText">
                {{ copied ? '복사됨!' : '복사' }}
              </button>
              <button class="btn small modal-btn" @click="closeModal">
                닫기
              </button>
            </div>
          </header>

          <div class="modal-body">
            <pre class="modal-pre" ref="modalPre">{{ modal.text }}</pre>
          </div>
        </div>
      </div>
    </transition>
  </section>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { fetchRecentCases, fetchRecentModelCases } from '@/api/defamation'

const mode = ref('court')
const q = ref('')
const limit = ref(10)
const items = ref([])
const loading = ref(false)

const modal = ref({ show: false, text: '', type: 'situation' })
const copied = ref(false)
let copiedTimer = null
const modalPre = ref(null)

const modeLabel = computed(() =>
  mode.value === 'court' ? '실제 판례' : '최근 모델 분류'
)

const helperText = computed(() =>
  mode.value === 'court'
    ? '실제 판례를 검색/열람합니다. 키워드와 표시 개수를 설정하세요.'
    : '최근 모델이 예측한 결과를 조회합니다. 키워드와 표시 개수를 설정하세요.'
)

const modalTitle = computed(() => {
  return modal.value.type === 'reason'
    ? '판결 이유 전체 보기'
    : '상황 전체 보기'
})

function formatSentence (it) {
  const t = it.sentenceType ?? ''
  let v = it.sentenceValue ?? ''
  if (typeof v === 'number') v = v.toLocaleString() + '원'
  const sus = it.sentenceSuspension ? ` / 집유 ${it.sentenceSuspension}` : ''
  const base = `${t} ${v}`.trim()
  return (base + sus).trim()
}

async function onSearch() {
  loading.value = true
  try {
    const getter = mode.value === 'court' ? fetchRecentCases : fetchRecentModelCases
    const { items: list } = await getter(limit.value, q.value)
    items.value = list || []
  } finally {
    loading.value = false
  }
}

/* ===== modal handlers ===== */
async function openModal(type, text) {
  if (!text) return
  modal.value.type = type
  modal.value.text = text
  modal.value.show = true
  copied.value = false
  await nextTick()
  if (modalPre.value) modalPre.value.scrollTop = 0
}

function closeModal() {
  modal.value.show = false
  modal.value.text = ''
  copied.value = false
  if (copiedTimer) clearTimeout(copiedTimer)
  copiedTimer = null
}

async function copyModalText() {
  try {
    await navigator.clipboard.writeText(modal.value.text)
    copied.value = true
  } catch (e) {
    const el = modalPre.value
    if (el) {
      const range = document.createRange()
      range.selectNodeContents(el)
      const sel = window.getSelection()
      sel.removeAllRanges()
      sel.addRange(range)
      document.execCommand('copy')
      sel.removeAllRanges()
      copied.value = true
    }
  }
  if (copiedTimer) clearTimeout(copiedTimer)
  copiedTimer = setTimeout(() => (copied.value = false), 1200)
}

/* ESC로 닫기 */
function onKeydown(e) {
  if (e.key === 'Escape' && modal.value.show) closeModal()
}
window.addEventListener('keydown', onKeydown)
onBeforeUnmount(() => window.removeEventListener('keydown', onKeydown))

onMounted(onSearch)
</script>

<style scoped>
.page{
  --fs-base: clamp(13px, 0.65vw + 0.7rem, 18px);
  --pad-hd: clamp(12px, 0.9vw + 6px, 22px);
  --pad-bd: clamp(12px, 0.9vw + 6px, 22px);
  --ctl-pad-v: clamp(8px, 0.6vw + 4px, 14px);
  --radius: clamp(10px, 0.6vw, 14px);

  font-size: var(--fs-base);
  width: min(1400px, 96vw);
  margin: 0 auto;
  overflow-x: hidden;
  min-width: 0;
}

.card{
  background:#111827;
  border:1px solid #1f2937;
  border-radius: var(--radius);
  color:#e5e7eb;
  position: relative;
}
.card-hd{
  display:flex; justify-content:space-between; align-items:flex-start;
  padding: var(--pad-hd);
  gap:12px; flex-wrap: wrap;
}
.card-bd{ padding: var(--pad-bd); }

.left{ display:flex; flex-direction:column; min-width:0; }
.helper{ margin-top:4px; }

.controls{
  display:grid;
  gap:8px;
  width: 100%;
  grid-template-columns:
    clamp(120px, 10vw, 160px)
    clamp(90px, 7vw, 120px)
    minmax(0,1fr)
    clamp(90px, 7vw, 120px);
}
@media (max-width: 720px){
  .controls{ grid-template-columns: 1fr 1fr; }
  .controls .input{ grid-column: 1 / -1; }
}

.select, .input{
  background:#0b1221; border:1px solid #334155; color:#e5e7eb;
  border-radius: var(--radius);
  padding: var(--ctl-pad-v) 12px;
  font-size:1rem;
  width:100%;
  box-sizing: border-box;
}

.btn{
  background:#2563eb; color:#fff; border:none;
  border-radius: var(--radius);
  padding: var(--ctl-pad-v) 14px;
  font-weight:700;
  cursor:pointer;
  font-size:1rem;
  width:100%;
}
.btn.small{ font-size:.95rem; }
.btn.ghost{
  background: transparent;
  border:1px solid #334155;
  color:#e5e7eb;
}

.table{
  width:100%;
  border-collapse:collapse;
  table-layout: fixed;
}
.table th,.table td{
  border-top:1px solid #1f2937;
  padding: clamp(10px, 0.7vw + 6px, 16px)
           clamp(12px, 0.9vw + 6px, 18px);
  text-align:left;
  font-size:1rem;
  word-break: break-word;
  vertical-align: middle;
}

.table td.empty { text-align: center !important; color:#94a3b8; }
.empty{ text-align:center; padding:24px 12px; color:#94a3b8; }

/* ✅ 셀 내부 정렬 단위 */
.cell-wrap{
  display:flex;
  flex-direction:column;
  width:100%;
}

/* ✅ 공통 2줄 클램프 + 풀폭 */
.clamp{
  width: 100%;
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
  overflow: hidden;

  line-height: 1.5em;
  min-height: calc(1.5em * 2);
  max-height: calc(1.5em * 2);
  white-space: normal;
}

/* 클릭 텍스트 */
.clickable{
  cursor: pointer;
  transition: opacity .15s ease;
}
.clickable:hover{ opacity: .85; }

/* ✅ 힌트: 셀 오른쪽 끝에 “딱” 붙게 */
.hint{
  font-size: .85rem;
  margin-top: 4px;

  margin-left: auto;      /* ← 오른쪽 끝 고정 */
  align-self: flex-end;   /* ← 오른쪽 끝 고정 */
  text-align: right;

  opacity: 0;
  transform: translateY(-2px);
  transition: opacity .15s ease, transform .15s ease;
}
.cell-wrap:hover .hint{
  opacity: .9;
  transform: translateY(0);
}

/* Modal */
.modal-backdrop{
  position: fixed;
  inset: 0;
  background: rgba(3, 7, 18, 0.6);
  backdrop-filter: blur(4px);
  display:flex;
  align-items:center;
  justify-content:center;
  padding: clamp(12px, 2vw, 28px);
  z-index: 9999;
}
.modal-card{
  width: min(980px, 96vw);
  max-height: 85vh;
  background:#0b1221;
  border:1px solid #334155;
  border-radius: var(--radius);
  box-shadow: 0 20px 50px rgba(0,0,0,0.55);
  display:flex;
  flex-direction: column;
  overflow: hidden;
}
.modal-hd{
  display:flex;
  align-items:center;
  justify-content: space-between;
  padding: clamp(10px, 1.1vw, 16px);
  border-bottom:1px solid #1f2937;
}
.modal-actions{
  display:flex; gap:8px; align-items:center;
}
.modal-btn{
  width: auto !important;
  white-space: nowrap;
  padding-left: 14px;
  padding-right: 14px;
}

.modal-body{ padding: 0; overflow: auto; }

.modal-pre{
  margin: 0;
  padding: clamp(14px, 1.2vw, 18px);
  font-size: 1rem;
  line-height: 1.65;
  white-space: pre-wrap;
  word-break: break-word;
  user-select: text;
  color:#e5e7eb;
}

/* fade */
.fade-enter-active, .fade-leave-active { transition: opacity .15s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
