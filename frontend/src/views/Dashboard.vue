<template>
  <div class="page">
    <transition name="fade">
      <div v-if="showOverlay" class="overlay">
        <video class="overlay-video" src="/law.mp4" autoplay loop muted playsinline></video>
      </div>
    </transition>

    <div class="grid">
      <!-- 입력 -->
      <section class="card">
        <header class="card-hd">
          <h3>명예훼손 AI</h3>
          <div class="muted">{{ text.length }} 자</div>
        </header>

        <div class="card-bd">
          <div class="field">
            <label class="label">Model</label>
            <select v-model="modelVersion" class="control">
              <option v-for="m in models" :key="m">{{ m }}</option>
            </select>
          </div>

          <div class="field">
            <label class="label">Text</label>
            <textarea
              v-model="text"
              class="control textarea"
              rows="8"
              placeholder="예) 그는 학력과 경력을 모두 속였다는 글을 봤는데 사실인가요?"
            ></textarea>
          </div>

          <div class="row gap">
            <button class="btn" :disabled="loading || !text.trim()" @click="onClassify">
              {{ loading ? 'Classifying...' : 'Classify' }}
            </button>
            <button class="btn ghost" :disabled="loading" @click="onClear">Clear</button>
          </div>
        </div>
      </section>

      <!-- 결과 -->
      <section class="card">
        <header class="card-hd"><h3>예상 판결</h3></header>
        <div class="card-bd">
          <div v-if="result" class="verdict">
            <div class="pill" :class="verdictView.cls">{{ verdictView.text }}</div>
            <pre class="json">{{ prettyResult }}</pre>
          </div>
          <div v-else class="muted">
            아직 결과가 없습니다. 왼쪽에서 텍스트를 입력해 분류해보세요.
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

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
  const v = result.value?.판단 || result.value?.verdict
  if (!v) return { text: '—', cls: 'none' }
  if (v.includes('유죄')) return { text: v, cls: 'guilty' }
  if (v.includes('무죄')) return { text: v, cls: 'notguilty' }
  return { text: v, cls: 'other' }
})

async function onClassify () {
  // TODO: 네 기존 classify 로직 유지
}
function onClear () { text.value = ''; result.value = null }
</script>

<style scoped>
/* =========================================================
   Responsive scale + centered container
   ========================================================= */
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

.grid{
  display:grid;
  grid-template-columns: 1fr 1fr;
  gap: clamp(12px, 1.2vw, 22px);
  align-items:start;
}

@media (max-width: 900px){
  .grid{ grid-template-columns: 1fr; }
}

.card{
  background:#111827;
  border:1px solid #1f2937;
  border-radius: var(--radius);
  color:#e5e7eb;
  min-width:0;
  overflow:hidden;
}

.card-hd{
  display:flex;
  justify-content:space-between;
  align-items:center;
  padding: var(--pad-hd);
  border-bottom:1px solid #1f2937;
  min-width:0;
}

.card-bd{ padding: var(--pad-bd); }

.field{
  display:grid;
  gap:6px;
  margin-bottom: clamp(10px, 0.8vw, 16px);
}

.label{ font-size:1rem; color:#cbd5e1; }

.control{
  background:#0b1221;
  border:1px solid #334155;
  color:#e5e7eb;
  border-radius: var(--radius);
  padding: var(--ctl-pad-v) 12px;
  width:100%;
  box-sizing:border-box;
  font-size:1rem;
}

.textarea{
  /* 큰 화면에선 더 시원하게 */
  min-height: clamp(180px, 22vh, 320px);
  resize: vertical;
  line-height: 1.5;
}

.row{ display:flex; }
.gap{ gap: clamp(8px, 0.8vw, 14px); }

.btn{
  background:#2563eb;
  color:#fff;
  border:none;
  border-radius: var(--radius);
  padding: var(--ctl-pad-v) 12px;
  font-weight:700;
  cursor:pointer;
  width:100%;
  font-size:1rem;
}

.btn.ghost{
  background:transparent;
  border:1px solid #334155;
  color:#e5e7eb;
}

.muted{ color:#94a3b8; font-size:.95rem; }

.verdict{ display:grid; gap: clamp(6px, 0.6vw, 10px); }

.pill{
  display:inline-flex;
  align-items:center;
  padding: clamp(6px, 0.5vw, 10px) clamp(10px, 0.7vw, 14px);
  border-radius:999px;
  font-weight:800;
  font-size:1rem;
}
.pill.guilty{ background:rgba(239,68,68,.15); color:#ef4444; }
.pill.notguilty{ background:rgba(34,197,94,.15); color:#22c55e; }
.pill.other{ background:rgba(148,163,184,.15); color:#cbd5e1; }
.pill.none{ background:rgba(148,163,184,.08); color:#94a3b8; }

.json{
  white-space:pre-wrap;
  word-break:break-word;
  background:#0b1221;
  border:1px solid #1f2937;
  border-radius: var(--radius);
  padding: clamp(10px, 0.8vw + 6px, 16px);
  font-size:1rem;
  line-height:1.5;
}
</style>
