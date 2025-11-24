# export_judgments.py
import os, json, csv, hashlib, re, sys
from datetime import datetime
from dotenv import load_dotenv
import pymysql

load_dotenv()

CFG = {
    "host": os.getenv("MYSQL_HOST", "127.0.0.1"),
    "port": int(os.getenv("MYSQL_PORT", "3306")),
    "user": os.getenv("MYSQL_USER"),
    "password": os.getenv("MYSQL_PASSWORD"),
    "db": os.getenv("MYSQL_DB"),
    "table": os.getenv("MYSQL_TABLE", "cases"),
    "export_dir": os.getenv("EXPORT_DIR", "./exports"),
    "batch_size": int(os.getenv("BATCH_SIZE", "1000")),
    "export_csv": os.getenv("EXPORT_CSV", "false").lower() == "true",
    "max_doc_chars": int(os.getenv("MAX_DOC_CHARS", "200000")),  # 안전상 자르기
}

# ---- 아주 안전한 문장 분할기 ----
# 마침표/물음표/느낌표/말줄임/중국어 마침표 + 공백/줄바꿈을 기준으로 분할
_SENT_SPLIT_SIMPLE = re.compile(r'(?<=[\.!?…。])\s+|[\r\n]+')

def split_sentences(text: str):
    if not text:
        return []
    t = text[:CFG["max_doc_chars"]]
    parts = [p.strip() for p in _SENT_SPLIT_SIMPLE.split(t) if p and p.strip()]
    return parts

# ---- SELECT (네 cases 스키마) ----
SELECT_SQL = f"""
SELECT
  id,
  case_labels,
  case_type,
  court_level,
  defendant,
  defamationN,
  disposition,
  reasoning,
  created_at
FROM {CFG['table']}
WHERE 1=1
ORDER BY id ASC
LIMIT %s OFFSET %s
"""

def sha_id(*parts):
    m = hashlib.sha256()
    for p in parts:
        m.update((str(p) if p is not None else "").encode("utf-8"))
        m.update(b"\x1e")
    return m.hexdigest()[:24]

def normalize_dt(dtval):
    if not dtval:
        return None
    if isinstance(dtval, datetime):
        return dtval.isoformat(sep=" ")
    return str(dtval)

def row_to_doc(row):
    (
        rid, case_labels, case_type, court_level, defendant,
        defamationN, disposition, reasoning, created_at
    ) = row

    disp = (disposition or "").strip()
    reas = (reasoning or "").strip()
    text_full = (disp + ("\n\n" if disp and reas else "") + reas).strip()

    if len(text_full) > CFG["max_doc_chars"]:
        text_full = text_full[:CFG["max_doc_chars"]]

    sentences = split_sentences(text_full)

    uid = str(rid) if rid is not None else sha_id(case_type, court_level, defendant, created_at, text_full[:80])

    return {
        "id": uid,
        "case_labels": (case_labels or "").strip(),
        "case_type": (case_type or "").strip(),
        "court_level": court_level,
        "defendant": (defendant or "").strip(),
        "defamationN": defamationN,
        "created_at": normalize_dt(created_at),
        "sections": {
            "disposition": disp,
            "reasoning": reas,
        },
        "text_full": text_full,
        "sentences": sentences,
        "meta": {
            "source": "mysql",
            "exported_at": datetime.now().strftime("%Y%m%d_%H%M%S"),
            "len_chars": len(text_full),
            "num_sentences": len(sentences),
            "splitter": "punctuation",
        },
    }

def main():
    os.makedirs(CFG["export_dir"], exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    jsonl_path = os.path.join(CFG["export_dir"], f"cases_{ts}.jsonl")
    csv_path   = os.path.join(CFG["export_dir"], f"cases_{ts}.csv")

    conn = pymysql.connect(
        host=CFG["host"], port=CFG["port"], user=CFG["user"],
        password=CFG["password"], database=CFG["db"],
        charset="utf8mb4", cursorclass=pymysql.cursors.SSCursor  # 스트리밍
    )

    total = 0
    with conn, open(jsonl_path, "w", encoding="utf-8") as jf:
        csv_writer, cf = None, None
        if CFG["export_csv"]:
            cf = open(csv_path, "w", newline="", encoding="utf-8")
            csv_writer = csv.writer(cf)
            csv_writer.writerow([
                "id","case_labels","case_type","court_level","defendant",
                "defamationN","created_at","disposition","reasoning","text_full"
            ])

        offset = 0
        batch = CFG["batch_size"]
        with conn.cursor() as cur:
            while True:
                cur.execute(SELECT_SQL, (batch, offset))
                rows = cur.fetchall()
                if not rows:
                    break

                for r in rows:
                    doc = row_to_doc(r)
                    jf.write(json.dumps(doc, ensure_ascii=False) + "\n")
                    if csv_writer:
                        csv_writer.writerow([
                            doc["id"], doc["case_labels"], doc["case_type"], doc["court_level"],
                            doc["defendant"], doc["defamationN"], doc["created_at"],
                            doc["sections"]["disposition"], doc["sections"]["reasoning"],
                            doc["text_full"]
                        ])
                    total += 1
                    if total % 500 == 0:
                        print(f"[progress] exported {total} rows...", flush=True)

                offset += batch

        if cf:
            cf.close()

    print(f"✅ JSONL saved: {jsonl_path} (rows={total})")
    if CFG["export_csv"]:
        print(f"✅ CSV   saved: {csv_path} (rows={total})")

if __name__ == "__main__":
    main()
