# Defamation Classifier

명예훼손 판결문 데이터를 기반으로 한 명예훼손 여부 예측 서비스입니다.  
Spring Boot 백엔드, Vue 3 프론트엔드, 그리고 Python 기반의 검색/LLM 예측 엔진으로 구성되어 있습니다.

---

## 🏗 아키텍처 (Architecture)

* **Frontend**: Vue 3 + Vite (Pinia, Vue Router, Axios)
* **Backend**: Spring Boot 3.5.7 (Java 17, Spring Data JPA, WebFlux)
* **Database**: MySQL 8 (Fulltext Search, ngram parser)
* **AI**
  * Python 3.11 기반 **Hybrid Search** (BM25 + Dense Retrieval + Reranking)
  * Google Colab + FastAPI + ngrok 기반 **LLM 판결 예측 서버**  
    (Qwen3-4B 기반 명예훼손 판결문 파인튜닝 모델)

---

## 🚀 시작하기 (Getting Started)

### 1. 사전 준비 (Prerequisites)

* **Java 17** (JDK 17+)
* **Node.js 20+**
* **MySQL 8.0+**
* **Python 3.11+** (검색 엔진/스크립트 및 ngrok 스크립트 실행 시)
* (선택) **Google Colab 계정** – LLM 예측 서버 실행용

---

### 2. 데이터베이스 설정 (Required)

프로젝트 실행 전, 반드시 아래 SQL을 실행하여 데이터베이스와 계정을 생성해야 합니다.

```sql
CREATE DATABASE defamation CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;

CREATE USER 'defamation_local'@'localhost' IDENTIFIED BY 'devpass';
GRANT ALL PRIVILEGES ON defamation.* TO 'defamation_local'@'localhost';
FLUSH PRIVILEGES;
````

> **참고**: 테이블 스키마는 백엔드 실행 시
> `backend/src/main/resources/schema.sql` 에 의해 자동으로 생성됩니다.

---

### 3. 백엔드 실행 (Backend – 개발 모드)

`backend` 디렉토리로 이동하여 Spring Boot 서버를 실행합니다.

```bash
cd backend

# Windows
gradlew bootRun

# macOS/Linux
./gradlew bootRun
```

* **API 서버**: `http://localhost:8080`
* **Swagger UI**: [http://localhost:8080/swagger-ui/index.html](http://localhost:8080/swagger-ui/index.html)

---

### 4. 프론트엔드 실행 (Frontend – 개발 모드)

`frontend` 디렉토리로 이동하여 의존성을 설치하고 개발 서버를 실행합니다.

```bash
cd frontend

npm install
npm run dev
```

* **웹 클라이언트**: [http://localhost:5173](http://localhost:5173)

개발 모드에서는:

* 프론트: `http://localhost:5173`
* 백엔드 API: `http://localhost:8080/api/...`
* Vite dev 서버가 `/api` 경로를 백엔드로 **프록시**하도록 설정되어 있습니다.

---

### 5. 프론트엔드 빌드 후 Spring에서 함께 서빙 (시연/배포용)

시연 또는 단일 포트(8080)로 프론트+백엔드를 함께 띄우고 싶다면:

1. **프론트 빌드**

```bash
cd frontend
npm install
npm run build   # dist/ 폴더 생성
```

2. **빌드 결과를 Spring 정적 리소스 경로로 복사**

```bash
# 프로젝트 루트(defamation-classifier) 기준
cp -r frontend/dist/* backend/src/main/resources/static/
# Windows Powershell 예시:
# Copy-Item -Recurse -Force frontend/dist/* backend/src/main/resources/static/
```

3. **백엔드 실행**

```bash
cd backend
./gradlew bootRun
```

* 이제 `http://localhost:8080` 접속 시 Vue 앱이 바로 뜨고,
  동일 도메인에서 `/api/...` 로 백엔드 API가 호출됩니다.
* 시연 시에는 이 모드(8080 하나만) + ngrok을 함께 사용하는 것을 추천합니다.

---

### 6. LLM 예측 서버 (Colab + FastAPI + ngrok)

명예훼손 판결 예측은 Google Colab에서 실행되는 FastAPI + Qwen3 기반 LLM 서버와 연동됩니다.
이 서버는 ngrok을 통해 퍼블릭 URL(`/predict`)을 노출하고,
Spring 백엔드는 해당 URL로 HTTP 요청을 보내 결과를 받아옵니다.

#### 6-1. Colab 노트북 준비

예시로 다음 두 개의 노트북을 Colab에 업로드하여 사용합니다.

* `chanwoo_ngrok.ipynb`
* `kwkun_ngrok.ipynb`

각 노트북은 아래와 같은 공통 구조를 가집니다.

* Qwen3-4B + LoRA 명예훼손 판결문 모델 로드
* FastAPI 앱 생성 및 `/predict` 엔드포인트 정의
* pyngrok을 사용해 `http://localhost:8000` → `https://{subdomain}.ngrok-free.dev` 터널 생성
* 실행 시 다음과 같은 로그 출력:

```text
🚀 [API 주소]: https://{서브도메인}.ngrok-free.dev/predict
웹 서비스 코드의 API_URL을 위 주소로 변경해서 사용하세요.
```

#### 6-2. Colab에서 실행 순서

각 모델마다:

1. Colab에서 `chanwoo_ngrok.ipynb` 또는 `kwkun_ngrok.ipynb` 열기
2. 상단부터 셀을 순서대로 **모두 실행** (토큰/모델 로드 → FastAPI/uvicorn → ngrok 연결)
3. 마지막 셀에서 출력되는 `🚀 [API 주소]` 값을 확인
   예: `https://rachele-unhappi-jin.ngrok-free.dev/predict`

#### 6-3. Spring 설정(application.yaml) 연동

Colab에서 확인한 `/predict` URL을
`backend/src/main/resources/application.yaml` 의 `defamation.model-endpoints`에 매핑합니다.

예시:

```yaml
defamation:
  model-endpoints:
    # modelId = 1인 경우 사용할 LLM 서버
    1: "https://chasmed-sariah-rainily.ngrok-free.dev/predict"

    # modelId = 4인 경우 사용할 LLM 서버
    4: "https://rachele-unhappi-jin.ngrok-free.dev/predict"
```

* 프론트에서 `modelId`를 1 또는 4으로 선택해 요청하면,

  * Spring이 위 URL을 조회해서
  * 해당 Colab FastAPI 서버의 `/predict`로 `{"inputs": "...사실관계..."}`를 전송합니다.
* Colab LLM 서버는 JSON 문자열을 생성해 `generated_text` 필드로 응답하고,
  Spring은 이를 DB에 저장한 뒤 프론트로 반환합니다.

> ⚠️ **주의**: Colab 노트북을 종료하면 해당 ngrok URL도 더 이상 유효하지 않으므로,
> 실행할 때마다 새로 출력된 URL을 `application.yaml`에 반영해야 합니다.

---

### 7. 로컬 Spring + Vue를 ngrok으로 외부 시연용으로 공개하기

Spring(8080)에서 프론트+백엔드를 함께 서빙하는 상태에서,
로컬 서버를 ngrok으로 외부에 노출해 시연할 수 있습니다.

#### 7-1. Python 의존성 설치

프로젝트 루트에서 (가상환경 활성화 후):

```bash
pip install pyngrok python-dotenv
```

#### 7-2. `.env` 설정

프로젝트 루트(`defamation-classifier/`)에 `.env2` 파일을 생성하고 다음 내용을 작성합니다.

```env
# ngrok 인증 토큰 (ngrok 대시보드에서 복사)
NGROK_AUTHTOKEN=여기에_네_토큰_붙여넣기

# (선택) 예약 도메인이 있다면 설정, 없다면 이 줄은 생략 가능
NGROK_HOSTNAME=

# Spring 서버 포트 (기본 8080)
APP_PORT=8080
```

#### 7-3. `run_ngrok_8080.py` 실행

실행 순서:

1. **Spring 서버 실행 (8080)**
   (프론트 빌드 + 정적 리소스 복사 완료 상태)

   ```bash
   cd backend
   ./gradlew bootRun
   ```

2. 다른 터미널에서 ngrok 스크립트 실행

   ```bash
   cd defamation-classifier   # 루트
   python run_ngrok_8080.py
   ```

3. 출력된 `외부 접속` URL로 접속하면,
   로컬에서 보던 Vue + Spring + LLM 연동 화면을 그대로 외부에서 시연할 수 있습니다.

---

## 📂 프로젝트 구조

```text
defamation-classifier/
├── backend/                      # Spring Boot Backend Project
│   ├── src/main/resources/
│   │   ├── application.yml
│   │   ├── schema.sql            # DB 초기화 스크립트
│   │   └── static/               # (프론트 빌드 후 정적 리소스 복사 위치)
│   └── build.gradle
├── frontend/                     # Vue 3 Frontend Project
│   ├── src/
│   └── package.json
├── scripts/                      # Python Search & Indexing Scripts (BM25, Dense, Hybrid)
├── index_passage_bm25/           # BM25 Index Data
├── index_passage_dense/          # Dense Index Data
├── run_ngrok_8080.py             # 로컬 8080을 ngrok으로 공개하는 스크립트
├── .env                          # ngrok 설정 (NGROK_AUTHTOKEN, APP_PORT 등)
├── *.jsonl                       # Dataset Files (판결문 / 학습 데이터)
└── README.md
```

(Colab용 `chanwoo_ngrok.ipynb`, `kwkun_ngrok.ipynb`는 Repo 외부에서 관리하거나,
`/colab` 디렉토리 하위에 두고 사용해도 됩니다.)

---

## 🧱 기술 스택 상세

### Backend

* **Framework**: Spring Boot 3.5.7
* **Language**: Java 17
* **Build Tool**: Gradle
* **Database**: MySQL 8 (InnoDB, utf8mb4)
* **API Documentation**: SpringDoc OpenAPI (Swagger)

### Frontend

* **Framework**: Vue 3
* **Build Tool**: Vite
* **State Management**: Pinia
* **HTTP Client**: Axios
* **Routing**: Vue Router

### AI / Search / LLM

* **Language**: Python 3.11
* **Search**: Hybrid Retrieval (BM25 + Dense + Reranking)
* **LLM**: Qwen3-4B 기반 한국어 명예훼손 판결문 파인튜닝 모델
* **Serving**

  * Google Colab + FastAPI + ngrok (LLM 추론 서버)
  * Spring Boot → Colab LLM 서버로 HTTP 호출 (JSON 기반 `/predict` API)
* **Libraries**: (예시) scikit-learn, PyTorch, Transformers, faiss, rank-bm25 등
