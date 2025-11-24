# scripts/search_hybrid_rerank.py
import os, sys, json, pickle, re, argparse
from pathlib import Path
from collections import defaultdict
import numpy as np
from sentence_transformers import SentenceTransformer, CrossEncoder
from annoy import AnnoyIndex
from FlagEmbedding import FlagReranker

# ---------- utils ----------
_SPLIT = re.compile(r'(?<=[\.!?…。])\s+|[\r\n]+')
TOKEN = re.compile(r"[ㄱ-힣A-Za-z0-9_]+")

def split_sents(t: str):
    t = (t or "").strip()
    if not t: return []
    parts = [p.strip() for p in _SPLIT.split(t) if p and p.strip()]
    return parts or [t]

def tokenize(s: str):
    return [m.group(0).lower() for m in TOKEN.finditer(s or "")]

def load_mapping(p: Path):
    rows=[]
    with open(p,"r",encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows

def rrf_fuse(rank_lists, k=60):
    scores = defaultdict(float)
    for lst in rank_lists:
        for r, idx in enumerate(lst, start=1):
            scores[idx] += 1.0 / (k + r)
    return sorted(scores.items(), key=lambda x: x[1], reverse=True)

def safe_truncate(txt: str, max_chars: int = 1200) -> str:
    if txt is None: return ""
    t = txt.replace("\n", " ").strip()
    return t if len(t) <= max_chars else (t[:max_chars] + "…")

# ---------- reranker factory ----------
def make_reranker(model_name: str, device: str = "cpu", fp16: bool = False):
    """
    Returns a scorer(pairs:list[(q, p)], batch_size:int) -> list[float in 0..1]
    - BAAI/bge-reranker-*  -> FlagReranker (normalize=True)
    - else                 -> Sentence-Transformers CrossEncoder (min-max normalize per batch)
    """
    if model_name.lower().startswith("baai/bge-reranker"):
        rr = FlagReranker(model_name, use_fp16=fp16, device=device)
        def scorer(pairs, batch_size=32):
            return rr.compute_score(pairs, batch_size=batch_size, normalize=True)
        return scorer
    else:
        ce = CrossEncoder(model_name, device=device)
        def scorer(pairs, batch_size=32):
            scores = ce.predict(pairs, batch_size=batch_size)
            if len(scores) <= 1:
                return [float(1/(1+np.exp(-float(scores[0]))))] if len(scores)==1 else []
            s = np.asarray(scores, dtype=np.float32)
            mn, mx = float(s.min()), float(s.max())
            if mx - mn < 1e-6:
                return [0.5 for _ in scores]
            return [float((v - mn) / (mx - mn)) for v in s]
        return scorer

# ---------- main ----------
def main():
    THIS = Path(__file__).resolve()
    ROOT = THIS.parents[1]

    ap = argparse.ArgumentParser(description="Hybrid (BM25+Dense) + (two-stage) Rerank")
    ap.add_argument("dense_dir", nargs="?", default=str(ROOT / "index_passage_dense"))
    ap.add_argument("bm25_dir",  nargs="?", default=str(ROOT / "index_passage_bm25"))
    ap.add_argument("--query", "-q", required=True, help="검색 쿼리 텍스트")
    ap.add_argument("--mode", choices=["fast","quality","turbo"], default="fast")

    # 후보/융합
    ap.add_argument("--topk-dense", type=int, default=int(os.getenv("TOPK_DENSE","200")))
    ap.add_argument("--topk-bm25",  type=int, default=int(os.getenv("TOPK_BM25","200")))
    ap.add_argument("--rrf-k",      type=int, default=int(os.getenv("RRF_K","60")))
    ap.add_argument("--candidates", type=int, default=int(os.getenv("CAND_FINAL","60")),
                    help="재랭킹에 넣을 총 후보 수(최대)")
    ap.add_argument("--per-case-cap", type=int, default=3,
                    help="재랭킹에 케이스당 최대 패시지 수")

    # 임베딩/재랭커 모델
    ap.add_argument("--emb-model", default=os.getenv("EMB_MODEL","BAAI/bge-m3"))
    ap.add_argument("--rerank-light", default=os.getenv("RERANK_LIGHT","BAAI/bge-reranker-base"))
    ap.add_argument("--rerank-heavy", default=os.getenv("RERANK_HEAVY","BAAI/bge-reranker-v2-m3"))

    # 성능 파라미터
    ap.add_argument("--batch-size", type=int, default=32)
    ap.add_argument("--max-chars", type=int, default=1200)
    ap.add_argument("--device", default=os.getenv("DEVICE","cpu"))     # "cpu" or "cuda"
    ap.add_argument("--fp16", action="store_true")
    ap.add_argument("--top-cases", type=int, default=5)
    args = ap.parse_args()

    # 모드별 기본값 조정
    if args.mode == "quality":
        args.candidates = max(args.candidates, 60)
        args.batch_size = max(args.batch_size, 16)
        args.max_chars = max(args.max_chars, 1600)
    elif args.mode == "turbo":  # GPU 가정
        args.candidates = max(args.candidates, 60)
        args.batch_size = max(args.batch_size, 64)
        args.device = "cuda"
        args.fp16 = True
    else:  # fast (CPU 최적)
        args.candidates = min(args.candidates, 60)
        args.batch_size = max(args.batch_size, 32)
        args.max_chars = min(args.max_chars, 1200)

    DENSE_DIR = Path(args.dense_dir).resolve()
    BM25_DIR  = Path(args.bm25_dir).resolve()
    QUERY     = args.query

    # --- dense index load ---
    vecs = np.load(DENSE_DIR / "vectors.npy")
    mapping = load_mapping(DENSE_DIR / "mapping.jsonl")
    dim = vecs.shape[1]
    ann = AnnoyIndex(dim, "angular")
    ann.load(str(DENSE_DIR / "index.ann"))
    emb = SentenceTransformer(args.emb_model, device="cpu")  # 질의 임베딩만 CPU로도 충분

    # --- bm25 index load ---
    with open(BM25_DIR / "bm25.pkl", "rb") as f:
        bm25_obj = pickle.load(f)["bm25"]
    # sanity
    assert len(mapping) == len(load_mapping(BM25_DIR / "mapping.jsonl")), "dense/bm25 mapping mismatch"

    # 1) 후보 생성 (문장 분할 → Dense/BM25 각각 TopK → RRF)
    q_sents = split_sents(QUERY) or [QUERY.strip()]

    dense_ranks = []
    for s in q_sents:
        qv = emb.encode([f"query: {s}"], normalize_embeddings=True)[0]
        idxs = ann.get_nns_by_vector(qv, args.topk_dense, include_distances=False)
        dense_ranks.append(list(idxs))

    def bm25_rank(q: str):
        scores = bm25_obj.get_scores(tokenize(q))
        return np.argsort(scores)[::-1][:args.topk_bm25].tolist()

    bm25_ranks = [bm25_rank(s) for s in q_sents]

    fused = rrf_fuse(dense_ranks + bm25_ranks, k=args.rrf_k)

    # per-case cap 적용하며 상위 후보 추리기
    cand_ids = []
    per_case_cnt = defaultdict(int)
    for idx, _ in fused:
        cid = mapping[idx]["case_id"]
        if per_case_cnt[cid] >= args.per_case_cap:
            continue
        cand_ids.append(idx)
        per_case_cnt[cid] += 1
        if len(cand_ids) >= args.candidates:
            break

    # 2) 두 단계 재랭킹 (라이트 -> 헤비 일부)
    light_scorer = make_reranker(args.rerank_light, device=args.device, fp16=args.fp16)
    heavy_scorer = make_reranker(args.rerank_heavy, device=args.device, fp16=args.fp16)

    pairs_light = [(QUERY, safe_truncate(mapping[i]["text"], args.max_chars)) for i in cand_ids]
    scores_light = light_scorer(pairs_light, batch_size=args.batch_size)
    reranked_light = sorted(zip(cand_ids, scores_light), key=lambda x: x[1], reverse=True)

    topN_heavy = len(reranked_light) if args.mode == "quality" else min(15, len(reranked_light))
    heavy_ids = [pid for pid, _ in reranked_light[:topN_heavy]]

    pairs_heavy = [(QUERY, safe_truncate(mapping[i]["text"], args.max_chars)) for i in heavy_ids]
    scores_heavy = heavy_scorer(pairs_heavy, batch_size=args.batch_size)
    heavy_scored = dict(zip(heavy_ids, scores_heavy))

    # 최종 점수(헤비 있으면 헤비, 아니면 라이트)
    final_pairs = []
    for pid, sc in reranked_light:
        final_pairs.append((pid, float(heavy_scored.get(pid, sc))))

    # 3) 사건 단위 집계 + 출력
    case_scores = defaultdict(list)
    evidence = defaultdict(list)
    case_meta = {}
    for pid, sc in sorted(final_pairs, key=lambda x: x[1], reverse=True):
        row = mapping[pid]
        cid = row["case_id"]
        case_scores[cid].append(sc)
        if cid not in case_meta:
            case_meta[cid] = {
                "case_type": row.get("case_type", ""),
                "court_level": row.get("court_level"),
                "defamationN": row.get("defamationN"),
            }
        if len(evidence[cid]) < 3:
            evidence[cid].append({"text": safe_truncate(row["text"], 200), "score": sc})

    final = []
    for cid, arr in case_scores.items():
        arr.sort(reverse=True)
        top3 = arr[:3]
        score = (sum(top3)/len(top3))*0.7 + max(arr)*0.3
        final.append((cid, score))
    final.sort(key=lambda x: x[1], reverse=True)

    for rank, (cid, sc) in enumerate(final[:args.top_cases], start=1):
        meta = case_meta.get(cid, {})
        print(f"\n[{rank}] CASE {cid} | score={sc:.4f} "
              f"| type={meta.get('case_type','')} "
              f"| court_level={meta.get('court_level')} "
              f"| defamationN={meta.get('defamationN')}")
        for ev in evidence[cid]:
            print(f"  - {ev['score']:.3f} :: {ev['text']}")

if __name__ == "__main__":
    main()
