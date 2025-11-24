-- =========================================================
-- models (그대로 유지)
-- =========================================================
CREATE TABLE IF NOT EXISTS models (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(100) UNIQUE NOT NULL,
  display_name VARCHAR(100),
  enabled TINYINT(1) DEFAULT 1
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


-- =========================================================
-- classification_requests
--  - input: problem_situation (모델 입력 그대로)
--  - output 매핑:
--      case_names              <- 죄명 (list)
--      sentence_type           <- 형량.형종
--      sentence_value          <- 형량.벌금액
--      sentence_suspension     <- 형량.집행유예_기간_월
--      sentence_additional_order <- 형량.추가_조건
--      sentence_reason         <- 양형이유
--      sentence_judgment       <- 판단 (유죄/무죄)
--  - label: defamationN(-1/0/1) 결과 저장
-- =========================================================
CREATE TABLE IF NOT EXISTS classification_requests (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,

  -- input
  problem_situation LONGTEXT NOT NULL,

  case_names JSON NULL,                 -- ["정보통신망...", ...]  (죄명)

  sentence_type VARCHAR(50) NULL,       -- "벌금" / "징역" 등 (형종)
  sentence_value BIGINT NULL,           -- 벌금액(원 단위 숫자). 없으면 NULL
  sentence_suspension INT NULL,         -- 집행유예_기간_월 (월 단위). 없으면 NULL
  sentence_additional_order LONGTEXT NULL, -- 추가_조건
  sentence_reason LONGTEXT NULL,        -- 양형이유
  sentence_judgment VARCHAR(20) NULL,   -- 판단(유죄/무죄)

  is_deleted TINYINT(1) NOT NULL DEFAULT 0,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

  KEY idx_cls_created_at (created_at),

  FULLTEXT INDEX ftx_cls_text (
    problem_situation,
    sentence_reason,
    sentence_additional_order
  ) WITH PARSER ngram
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


-- =========================================================
-- cases
--  merged_dataset.jsonl keys 그대로 컬럼화:
--  ['problem_situation', 'participants', 'raw_id', 'case_names',
--   'case_type', 'court_level', 'defendant', 'label',
--   'sentence_type', 'sentence_value', 'sentence_suspension',
--   'sentence_additional_order', 'sentence_reason', 'sentence_judgment']
--  + created_at, is_deleted
-- =========================================================
CREATE TABLE IF NOT EXISTS cases (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,

  raw_id BIGINT NOT NULL,               -- 기존 원본 id 보존

  problem_situation LONGTEXT NOT NULL,
  participants TEXT NOT NULL,           -- "피고인(...)", "피해자..." 등

  case_names VARCHAR(255) NOT NULL,             -- "명예훼손" (casenames)
  case_type  VARCHAR(255) NOT NULL,     -- criminal/civil ...
  court_level TINYINT UNSIGNED NOT NULL, -- 1/2/3
  defendant VARCHAR(255) NULL,

  label TINYINT NOT NULL,               -- -1,0,1

  -- 형량(flatten)
  sentence_type VARCHAR(50) NULL,       -- 벌금/징역/집행유예 등
  sentence_value VARCHAR(100) NULL,     -- "70만 원" 같이 문자열(기존 데이터 호환)
  sentence_suspension VARCHAR(100) NULL,-- 집행유예 기간/여부 문자열
  sentence_additional_order LONGTEXT NULL,
  sentence_reason LONGTEXT NULL,
  sentence_judgment VARCHAR(20) NULL,   -- 유죄/무죄

  is_deleted TINYINT(1) NOT NULL DEFAULT 0,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

  UNIQUE KEY uq_cases_raw_id (raw_id),

  CHECK (label IN (-1, 0, 1)),
  CHECK (court_level IN (1, 2, 3)),

  INDEX idx_cases_type (case_type),
  INDEX idx_cases_level (court_level),
  INDEX idx_cases_label (label),
  KEY idx_cases_created_at (created_at),

  FULLTEXT INDEX ftx_cases_text (
    problem_situation,
    defendant,
    sentence_reason
  ) WITH PARSER ngram
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
