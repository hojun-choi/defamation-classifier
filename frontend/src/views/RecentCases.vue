<template>
  <section class="page card">
    <header class="card-hd">
      <div class="left">
        <h3>{{ modeLabel }}</h3>
        <span class="muted helper">{{ helperText }}</span>
      </div>

      <div class="controls">
        <!-- 보기 종류 (고정폭) -->
        <select v-model="mode" class="select small">
          <option value="court">실제 판례</option>
          <option value="model">최근 모델 분류</option>
        </select>

        <!-- 표시 개수 (고정폭) -->
        <select v-model.number="limit" class="select small">
          <option :value="5">5</option>
          <option :value="10">10</option>
          <option :value="20">20</option>
          <option :value="50">50</option>
        </select>

        <!-- 검색어 (남는 전폭) -->
        <input
          v-model="q"
          class="input"
          type="text"
          placeholder="검색어 입력"
          @keyup.enter="onSearch"
        />

        <!-- 검색 버튼 -->
        <button class="btn small" @click="onSearch">검색</button>
      </div>
    </header>

    <div class="card-bd">
      <table class="table">
        <thead>
          <tr>
            <th style="width:55%">상황</th>
            <th style="width:20%">판결</th>
            <th style="width:25%">형량</th>
          </tr>
        </thead>

        <tbody v-if="items.length">
          <tr v-for="it in items" :key="it.id">
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
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { fetchRecentCases } from '@/api/defamation'

// 실판례 API 준비 전까지 임시로 동일 엔드포인트 사용
async function fetchCourtCases(limit, q) {
  return fetchRecentCases(limit, q)
}

const mode = ref('court')       // 'court' | 'model'
const q = ref('')
const limit = ref(10)
const items = ref([])

const modeLabel = computed(() =>
  mode.value === 'court' ? '실제 판례' : '최근 모델 분류'
)

const helperText = computed(() =>
  mode.value === 'court'
    ? '실제 판례를 검색/열람합니다. 키워드와 표시 개수를 설정하세요.'
    : '최근 모델이 예측한 결과를 조회합니다. 키워드와 표시 개수를 설정하세요.'
)

async function onSearch() {
  const getter = mode.value === 'court' ? fetchCourtCases : fetchRecentCases
  const { items: list } = await getter(limit.value, q.value)
  items.value = list || []
}

// 최초 진입 시 기본값(관련 실제 판례 / 10건)으로 자동 조회
onMounted(onSearch)
</script>

<style scoped>
/* ===== Responsive base ===== */
.page{
  --fs-base: clamp(12px, 1vw + 0.5rem, 16px);
  --pad-hd: clamp(12px, 0.9vw + 6px, 18px);
  --ctl-pad-v: clamp(8px, 0.7vw + 4px, 12px);
  font-size: var(--fs-base);
  width: 100%;
  overflow-x: hidden; /* 가로 스크롤 방지 */
  min-width: 0;
}

/* Card */
.card{ background:#111827; border:1px solid #1f2937; border-radius:12px; color:#e5e7eb; }
.card-hd{
  display:flex; justify-content:space-between; align-items:flex-start;
  gap:12px; padding: var(--pad-hd); border-bottom:1px solid #1f2937;
  flex-wrap: wrap; /* 좁은 화면에서 줄바꿈 */
}
.card-bd{ padding: var(--pad-hd); min-width:0; }

.left{ display:flex; align-items:center; gap:10px; min-width:0; }
.helper{ white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.muted{ color:#94a3b8; font-size:.85rem; }

/* Controls row: [보기종류 180px] [표시개수 110px] [검색입력 1fr] [버튼 100px] */
.controls{
  display:grid;
  grid-template-columns: 180px 110px minmax(0,1fr) 100px;
  gap:12px; align-items:center; min-width:0;
  width: 100%;
}
@media (max-width: 900px){
  .controls{
    grid-template-columns: 1fr 1fr;
  }
  .controls .input{ grid-column: 1 / -1; } /* 검색어는 한 줄 전체 사용 */
}

/* Inputs & Buttons */
.select, .input{
  background:#0b1221; border:1px solid #334155; color:#e5e7eb;
  border-radius:10px; padding: var(--ctl-pad-v) 12px; font-size:1rem; width:100%;
  box-sizing: border-box;
}
.btn{
  background:#2563eb; color:#fff; border:none; border-radius:10px;
  padding: var(--ctl-pad-v) 14px; font-weight:700; cursor:pointer; font-size:1rem; width:100%;
}
.btn.small{ font-size:.95rem; }

/* Table */
.table{ width:100%; border-collapse:collapse; table-layout: fixed; }
.table th,.table td{
  border-top:1px solid #1f2937; padding:10px 12px; text-align:left; font-size:.95rem;
  word-break: break-word;
}
/* 빈 행 메시지 정확히 가운데 정렬 */
.table td.empty { text-align: center !important; color:#94a3b8; }
.empty{ text-align:center; padding:24px 12px; color:#94a3b8; }
</style>
