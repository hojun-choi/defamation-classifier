# Defamation Classifier

명예훼손 판결문 데이터를 기반으로 한 명예훼손 여부 예측 서비스입니다.
Spring Boot 백엔드, Vue 3 프론트엔드, 그리고 Python 기반의 하이브리드 검색(BM25 + Dense Retrieval) 엔진으로 구성되어 있습니다.

---

## 🏗 아키텍처 (Architecture)

*   **Frontend**: Vue 3 + Vite (Pinia, Vue Router, Axios)
*   **Backend**: Spring Boot 3.5.7 (Java 17, Spring Data JPA, WebFlux)
*   **Database**: MySQL 8 (Fulltext Search, ngram parser)
*   **AI/Search**: Python 3.11 (Hybrid Search: BM25 + Dense Embedding + Reranking)

---

## 🚀 시작하기 (Getting Started)

### 1. 사전 준비 (Prerequisites)

*   **Java 17** (JDK 17+)
*   **Node.js 20+**
*   **MySQL 8.0+**
*   **Python 3.11+** (검색 엔진/스크립트 실행 시)

### 2. 데이터베이스 설정 (Required)

프로젝트 실행 전, 반드시 아래 SQL을 실행하여 데이터베이스와 계정을 생성해야 합니다.

```sql
CREATE DATABASE defamation CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;

CREATE USER 'defamation_local'@'localhost' IDENTIFIED BY 'devpass';
GRANT ALL PRIVILEGES ON defamation.* TO 'defamation_local'@'localhost';
FLUSH PRIVILEGES;
```

> **참고**: 테이블 스키마는 백엔드 실행 시 `backend/src/main/resources/schema.sql`에 의해 자동으로 생성됩니다.

### 3. 백엔드 실행 (Backend)

`backend` 디렉토리로 이동하여 Spring Boot 서버를 실행합니다.

```bash
cd backend

# Windows
gradlew bootRun

# macOS/Linux
./gradlew bootRun
```

*   **API 서버**: `http://localhost:8080`
*   **Swagger UI**: [http://localhost:8080/swagger-ui/index.html](http://localhost:8080/swagger-ui/index.html)

### 4. 프론트엔드 실행 (Frontend)

`frontend` 디렉토리로 이동하여 의존성을 설치하고 개발 서버를 실행합니다.

```bash
cd frontend

npm install
npm run dev
```

*   **웹 클라이언트**: [http://localhost:5173](http://localhost:5173)

### 5. 검색 엔진 및 데이터 처리 (Scripts)

`scripts` 디렉토리에는 데이터 전처리 및 검색 인덱스 생성을 위한 Python 스크립트가 포함되어 있습니다.

*   `build_bm25_index.py`: BM25 인덱스 생성
*   `build_dense_index.py`: Dense Vector 인덱스 생성
*   `search_hybrid_rerank.py`: 하이브리드 검색 및 리랭킹 로직

```bash
# Python 가상환경 활성화 (예시)
source venv311/bin/activate  # 또는 Windows: venv311\Scripts\activate

# 필요한 패키지 설치 후 스크립트 실행
# python scripts/build_bm25_index.py
```

---

## 📂 프로젝트 구조

```
defamation-classifier/
├── backend/                # Spring Boot Backend Project
│   ├── src/main/resources/
│   │   ├── application.yml
│   │   └── schema.sql      # DB 초기화 스크립트
│   └── build.gradle
├── frontend/               # Vue 3 Frontend Project
│   ├── src/
│   └── package.json
├── scripts/                # Python Search & Indexing Scripts
├── index_passage_bm25/     # BM25 Index Data
├── index_passage_dense/    # Dense Index Data
├── *.jsonl                 # Dataset Files
└── README.md
```

## 🧱 기술 스택 상세

### Backend
*   **Framework**: Spring Boot 3.5.7
*   **Language**: Java 17
*   **Build Tool**: Gradle
*   **Database**: MySQL 8 (InnoDB, utf8mb4)
*   **API Documentation**: SpringDoc OpenAPI (Swagger)

### Frontend
*   **Framework**: Vue 3
*   **Build Tool**: Vite
*   **State Management**: Pinia
*   **HTTP Client**: Axios
*   **Routing**: Vue Router

### AI / Search
*   **Language**: Python 3.11
*   **Search**: Hybrid Retrieval (BM25 + Dense)
*   **Libraries**: (Scikit-learn, PyTorch, Transformers 등 프로젝트 구성에 따름)
