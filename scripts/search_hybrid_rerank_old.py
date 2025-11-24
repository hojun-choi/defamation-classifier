# scripts/search_hybrid_rerank.py
import os, sys, json, pickle, re, argparse
from pathlib import Path
from collections import defaultdict
import numpy as np
from sentence_transformers import SentenceTransformer
from annoy import AnnoyIndex
from FlagEmbedding import FlagReranker

# --------- utils ---------
_SPLIT = re.compile(r'(?<=[\.!?…。])\s+|[\r\n]+')

def split_sents(t: str):
    t = (t or "").strip()
    if not t: return []
    parts = [p.strip() for p in _SPLIT.split(t) if p and p.strip()]
    return parts or [t]

def load_mapping(p: Path):
    rows=[]
    with open(p,"r",encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows

def to_cos_from_angular(d: float) -> float:
    return 1.0 - (d*d)/2.0

def rrf_fuse(rank_lists, k=60):
    scores = defaultdict(float)
    for lst in rank_lists:
        for r, idx in enumerate(lst, start=1):
            scores[idx] += 1.0 / (k + r)
    return sorted(scores.items(), key=lambda x: x[1], reverse=True)

# --------- main ---------
def main():
    # paths
    THIS = Path(__file__).resolve()
    ROOT = THIS.parents[1]

    parser = argparse.ArgumentParser(description="Hybrid (BM25 + dense) + Rerank search")
    parser.add_argument("dense_dir", nargs="?", default=str(ROOT / "index_passage_dense"),
                        help="Dense index dir (vectors.npy, mapping.jsonl, index.ann)")
    parser.add_argument("bm25_dir", nargs="?", default=str(ROOT / "index_passage_bm25"),
                        help="BM25 index dir (bm25.pkl, mapping.jsonl)")
    parser.add_argument("--query", "-q", required=True, help="검색 쿼리 텍스트")
    parser.add_argument("--topk-dense", type=int, default=int(os.getenv("TOPK_DENSE", "200")))
    parser.add_argument("--topk-bm25", type=int, default=int(os.getenv("TOPK_BM25", "200")))
    parser.add_argument("--rrf-k", type=int, default=int(os.getenv("RRF_K", "60")))
    parser.add_argument("--candidates", type=int, default=int(os.getenv("CAND_FINAL", "60")),
                        help="재랭킹에 넣을 후보 개수")
    parser.add_argument("--top-cases", type=int, default=int(os.getenv("TOP_CASES", "5")))
    parser.add_argument("--emb-model", default=os.getenv("EMB_MODEL", "BAAI/bge-m3"))
    parser.add_argument("--rerank-model", default=os.getenv("RERANK_MODEL", "BAAI/bge-reranker-v2-m3"))
    args = parser.parse_args()

    DENSE_DIR = Path(args.dense_dir).resolve()
    BM25_DIR  = Path(args.bm25_dir).resolve()
    QUERY     = args.query

    # --- dense ---
    vecs = np.load(DENSE_DIR / "vectors.npy")
    mapping_dense = load_mapping(DENSE_DIR / "mapping.jsonl")
    dim = vecs.shape[1]
    ann = AnnoyIndex(dim, "angular")
    ann.load(str(DENSE_DIR / "index.ann"))
    emb = SentenceTransformer(args.emb_model, device="cpu")

    # --- bm25 ---
    with open(BM25_DIR / "bm25.pkl", "rb") as f:
        bm25_obj = pickle.load(f)["bm25"]
    mapping_bm25 = load_mapping(BM25_DIR / "mapping.jsonl")
    assert len(mapping_dense) == len(mapping_bm25), "dense/bm25 mapping size mismatch"

    # 1) 쿼리 분할 → 각 쿼리별 랭크 추출
    q_sents = split_sents(QUERY)
    if not q_sents: q_sents = [QUERY.strip()]

    dense_ranks = []
    for s in q_sents:
        qv = emb.encode([f"query: {s}"], normalize_embeddings=True)[0]
        idxs, dists = ann.get_nns_by_vector(qv, args.topk_dense, include_distances=True)
        dense_ranks.append(list(idxs))

    def bm25_rank(q: str):
        toks = re.findall(r"[ㄱ-힣A-Za-z0-9_]+", q.lower())
        scores = bm25_obj.get_scores(toks)
        return np.argsort(scores)[::-1][:args.topk_bm25].tolist()

    bm25_ranks = [bm25_rank(s) for s in q_sents]

    # 2) RRF 융합 → 후보 추림
    fused = rrf_fuse(dense_ranks + bm25_ranks, k=args.rrf_k)
    cand_ids = [idx for idx, _ in fused[:args.candidates]]

    # 3) 재랭킹 (크로스 인코더)
    reranker = FlagReranker(args.rerank_model, use_fp16=False)  # CPU
    pair_texts = [(QUERY, mapping_dense[i]["text"]) for i in cand_ids]
    rerank_scores = reranker.compute_score(pair_texts, normalize=True)
    reranked = sorted(zip(cand_ids, rerank_scores), key=lambda x: x[1], reverse=True)

    # 4) 사건 집계 + 출력
    case_scores = defaultdict(list)
    evidence = defaultdict(list)
    case_meta = {}
    for pid, sc in reranked:
        row = mapping_dense[pid]
        cid = row["case_id"]
        case_scores[cid].append(float(sc))
        if cid not in case_meta:
            case_meta[cid] = {
                "case_type": row.get("case_type", ""),
                "court_level": row.get("court_level"),
                "defamationN": row.get("defamationN"),
            }
        if len(evidence[cid]) < 3:
            text = row["text"].replace("\n", " ")
            if len(text) > 200: text = text[:200] + "…"
            evidence[cid].append({"text": text, "score": float(sc)})

    final = []
    for cid, arr in case_scores.items():
        arr.sort(reverse=True)
        top3 = arr[:3]
        score = sum(top3)/len(top3)
        score = score*0.7 + max(arr)*0.3
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
