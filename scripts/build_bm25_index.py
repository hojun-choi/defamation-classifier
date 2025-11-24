# scripts/build_bm25_index.py
import sys, json, pickle, re
from pathlib import Path
from rank_bm25 import BM25Okapi

THIS = Path(__file__).resolve()
ROOT = THIS.parents[1]
DATA = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else (ROOT / "processed" / "passages.jsonl")
OUT  = Path(sys.argv[2]).resolve() if len(sys.argv) > 2 else (ROOT / "index_passage_bm25")
OUT.mkdir(parents=True, exist_ok=True)

map_path = OUT / "mapping.jsonl"
bm25_path = OUT / "bm25.pkl"

TOKEN = re.compile(r"[ㄱ-힣A-Za-z0-9_]+")

def iter_jsonl(p: Path):
    with open(p, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                yield json.loads(line)

def tokenize(s: str):
    return [m.group(0).lower() for m in TOKEN.finditer(s or "")]

def main():
    corpus = []
    metas = []
    for row in iter_jsonl(DATA):
        corpus.append(tokenize(row["text"]))
        metas.append(row)

    if not corpus:
        print("[error] no passages")
        sys.exit(1)

    bm25 = BM25Okapi(corpus)

    with open(bm25_path, "wb") as f:
        pickle.dump({"bm25": bm25}, f)

    with open(map_path, "w", encoding="utf-8") as f:
        for m in metas:
            f.write(json.dumps(m, ensure_ascii=False) + "\n")

    print(f"✅ bm25 index saved: {OUT} (n={len(corpus)})")

if __name__ == "__main__":
    main()
