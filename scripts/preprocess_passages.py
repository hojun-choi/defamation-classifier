# scripts/preprocess_passages.py
import os, sys, json, re
from pathlib import Path
from typing import List
from transformers import AutoTokenizer

# ==== 경로 (scripts/의 부모를 루트로) ====
THIS = Path(__file__).resolve()
ROOT = THIS.parents[1]
DEFAULT_EXPORTS = ROOT / "exports"
DEFAULT_OUT = ROOT / "processed"

# 인자: [SRC_JSONL | 생략 시 exports 최신] [OUT_DIR]
SRC = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else None
OUT_DIR = Path(sys.argv[2]).resolve() if len(sys.argv) > 2 else DEFAULT_OUT
OUT_DIR.mkdir(parents=True, exist_ok=True)

# 토큰 타겟/오버랩(대략 200토큰, 20% 오버랩)
TARGET_TOK = int(os.getenv("PASSAGE_TOKENS", "200"))
OVERLAP_TOK = int(TARGET_TOK * 0.2)

# 문장 분할(구두점/줄바꿈)
_SPLIT = re.compile(r'(?<=[\.!?…。])\s+|[\r\n]+')
CTRL = re.compile(r"[\x00-\x08\x0b-\x1f]")
WS = re.compile(r"\s+")

def clean(s: str) -> str:
    s = (s or "").replace("\u3000", " ")
    s = CTRL.sub(" ", s)
    s = WS.sub(" ", s).strip()
    return s

def split_sents(t: str) -> List[str]:
    if not t: return []
    return [p.strip() for p in _SPLIT.split(t) if p and p.strip()]

def iter_jsonl(p: Path):
    with open(p, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                yield json.loads(line)

def main():
    # 소스 파일 자동 선택
    if SRC is None:
        cand = sorted(DEFAULT_EXPORTS.glob("cases_*.jsonl"))
        if not cand:
            print(f"[error] no cases_*.jsonl under {DEFAULT_EXPORTS}", file=sys.stderr)
            sys.exit(1)
        src = cand[-1]
    else:
        src = SRC

    tok = AutoTokenizer.from_pretrained("BAAI/bge-m3")
    def count_tokens(text: str) -> int:
        return len(tok(text, add_special_tokens=False)["input_ids"])

    out_passages = OUT_DIR / "passages.jsonl"
    out_sents    = OUT_DIR / "sentences.jsonl"   # (선택) 하이라이트용

    total_passages = 0
    total_sents = 0

    with open(out_passages, "w", encoding="utf-8") as pf, \
         open(out_sents, "w", encoding="utf-8") as sf:

        for doc in iter_jsonl(src):
            cid = doc["id"]
            disp = clean(doc.get("sections", {}).get("disposition", ""))
            reas = clean(doc.get("sections", {}).get("reasoning", ""))
            text = (disp + ("\n\n" if disp and reas else "") + reas).strip()

            sents = [clean(s) for s in doc.get("sentences") or split_sents(text)]
            sents = [s for s in sents if len(s) >= 4]

            # 문장 jsonl(옵션)
            for i, s in enumerate(sents):
                sf.write(json.dumps({
                    "case_id": cid,
                    "sid": f"{cid}:{i}",
                    "text": s,
                    "case_type": doc.get("case_type", ""),
                    "court_level": doc.get("court_level"),
                    "defamationN": doc.get("defamationN")
                }, ensure_ascii=False) + "\n")
                total_sents += 1

            # 패시지 생성(토큰 기준)
            i = 0
            while i < len(sents):
                cur = []
                cur_tok = 0
                j = i
                while j < len(sents):
                    t = sents[j]
                    tt = count_tokens(t)
                    if cur and cur_tok + tt > TARGET_TOK:
                        break
                    cur.append(t)
                    cur_tok += tt
                    j += 1

                if cur:
                    pf.write(json.dumps({
                        "case_id": cid,
                        "pid": f"{cid}:{i}-{j-1}",
                        "text": " ".join(cur),
                        "case_type": doc.get("case_type", ""),
                        "court_level": doc.get("court_level"),
                        "defamationN": doc.get("defamationN")
                    }, ensure_ascii=False) + "\n")
                    total_passages += 1

                # 오버랩(토큰 기준을 문장 개수로 대략 변환)
                # 너무 작은 경우 대비 최소 1문장 전진
                step = max(1, len(cur) - max(1, round(len(cur) * OVERLAP_TOK / max(1, TARGET_TOK))))
                i += step if step > 0 else len(cur) or 1

    print(f"✅ passages: {out_passages} (n={total_passages})")
    print(f"✅ sentences: {out_sents} (n={total_sents})")

if __name__ == "__main__":
    main()
