# scripts/build_dense_index.py
import os, sys, json
from pathlib import Path
import numpy as np
from sentence_transformers import SentenceTransformer
from annoy import AnnoyIndex

THIS = Path(__file__).resolve()
ROOT = THIS.parents[1]
DATA = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else (ROOT / "processed" / "passages.jsonl")
OUT  = Path(sys.argv[2]).resolve() if len(sys.argv) > 2 else (ROOT / "index_passage_dense")
OUT.mkdir(parents=True, exist_ok=True)

MODEL = os.getenv("EMB_MODEL", "BAAI/bge-m3")
BATCH = int(os.getenv("EMB_BATCH", "64"))
METRIC = "angular"

vec_path = OUT / "vectors.npy"
map_path = OUT / "mapping.jsonl"
ann_path = OUT / "index.ann"

def iter_jsonl(p: Path):
    with open(p, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                yield json.loads(line)

def main():
    print(f"[info] DATA={DATA}")
    print(f"[info] OUT ={OUT}")
    print(f"[info] MODEL={MODEL}")

    model = SentenceTransformer(MODEL, device="cpu")
    texts, metas = [], []
    for row in iter_jsonl(DATA):
        texts.append(row["text"])
        metas.append(row)

    if not texts:
        print("[error] no passages")
        sys.exit(1)

    enc = [f"passage: {t}" for t in texts]  # bge 권장 프리픽스
    embs = model.encode(enc, batch_size=BATCH, show_progress_bar=True, normalize_embeddings=True)
    embs = np.asarray(embs, dtype=np.float32)
    np.save(vec_path, embs)

    with open(map_path, "w", encoding="utf-8") as f:
        for m in metas:
            f.write(json.dumps(m, ensure_ascii=False) + "\n")

    dim = embs.shape[1]
    ann = AnnoyIndex(dim, METRIC)
    for i in range(len(embs)):
        ann.add_item(i, embs[i])
    ann.build(50)
    ann.save(str(ann_path))

    print(f"✅ dense index saved: {OUT} (n={len(embs)}, dim={dim})")

if __name__ == "__main__":
    main()
