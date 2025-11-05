```
# defamation-classifier

명예훼손 **이진 분류** 서비스를 위한 풀스택 템플릿입니다.
백엔드는 **Spring Boot 3 (Java 17, Gradle)**, 프런트는 **Vue + Vite**, DB는 **MySQL 8**을 사용합니다.
LLM 분류 모델(vLLM/OpenAI 호환)은 **추후 연결**하며, 지금은 **모델 자리는 mock 어댑터**로 비워둔 상태입니다.
데모 UI 목업 파일은 `/docs/demo.html` 참고(슬라이드/캡처용) :contentReference[oaicite:0]{index=0}

---

## 📐 아키텍처 개요

```

Client (Vue) ──> Spring API (MVC + WebClient) ──> vLLM(OpenAI 호환 /v1)

│

└──> MySQL + Flyway (이력/결과 저장)

```

- **REST API**: `/api/v1/...`
- **문서화**: Swagger UI `http://localhost:8080/swagger-ui/index.html`
- **DB 마이그레이션**: Flyway (`src/main/resources/db/migration/V*.sql`)
- **스트리밍/채팅**: WebClient + (필요 시) SSE/WebSocket 확장 예정

---

## 🧱 기술 스택

- **Backend**: Spring Boot 3.5.x, Java 17, Gradle 8, Spring Web (MVC), Spring WebFlux(WebClient), Spring Data JPA, Flyway, springdoc-openapi
- **DB**: MySQL 8 (로컬 개발)
- **Frontend**: Vue 3 + Vite (별도 폴더 `frontend/`)
- **Tooling**: VS Code, Extension Pack for Java, Spring Boot Extension Pack, Volar

---

## ✅ 사전 준비(Prerequisites)

- **JDK 17 LTS** (Adoptium/Temurin 또는 Oracle JDK)
  확인: `java -version` → 17.x
- **Node.js 20+**
  확인: `node -v` / `npm -v`
- **MySQL 8**
  확인: `mysql --version`

> Windows에서 JDK 17을 기본으로 쓰려면 `JAVA_HOME`을 JDK17로 설정하고 `PATH`에 `%JAVA_HOME%\bin`을 추가하세요.

---

## 🗂️ 폴더 구조 (제안)

```

defamation-classifier/

├─ backend/                  # Spring Boot 프로젝트

│  ├─ src/main/java/...

│  ├─ src/main/resources/

│  │  ├─ application.yml

│  │  ├─ application-local.yml

│  │  └─ db/migration/

│  │     └─ V1__init.sql

│  └─ build.gradle

├─ frontend/                 # Vue + Vite (추가 예정)

└─ docs/

└─ demo.html              # 데모 목업(캡처용)

```

---

## 🛢️ MySQL 초기화

```sql
-- DB 및 계정 생성(원하면 root 계정 사용 가능)
CREATE DATABASE defamation CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;
CREATE USER 'defamation_local'@'localhost' IDENTIFIED BY 'devpass';
GRANT ALL PRIVILEGES ON defamation.* TO 'defamation_local'@'localhost';
FLUSH PRIVILEGES;

```

> 로컬에서 발생하는 인증 이슈를 피하려면 JDBC URL에 allowPublicKeyRetrieval=true&useSSL=false를 붙이거나, 계정 인증 플러그인을 mysql_native_password로 변경하세요.
> 

---

## ⚙️ 백엔드 설정

### 1) `backend/src/main/resources/application.yml`

```yaml
spring:
  profiles:
    default: local  # bootRun만 해도 local 프로필이 자동 적용

```

### 2) `backend/src/main/resources/application-local.yml`

```yaml
spring:
  datasource:
    url: jdbc:mysql://localhost:3306/defamation?useSSL=false&allowPublicKeyRetrieval=true&serverTimezone=Asia/Seoul
    username: defamation_local    # root를 쓰면 root로 변경
    password: devpass            # root 비밀번호로 변경
  jpa:
    hibernate:
      ddl-auto: validate
    open-in-view: false
  flyway:
    enabled: true

server:
  port: 8080

app:
  cors:
    allowed-origins: "http://localhost:5173"   # Vite dev 서버
  model:
    adapter: mock
  vllm:
    base-url: "http://localhost:8000/v1"       # vLLM/OpenAI 호환 엔드포인트 자리
    api-key: ""                                # 필요 시 사용

```

### 3) `backend/src/main/resources/db/migration/V1__init.sql`

```sql
CREATE TABLE IF NOT EXISTS models (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(100) UNIQUE NOT NULL,
  display_name VARCHAR(100),
  enabled TINYINT(1) DEFAULT 1
);

CREATE TABLE IF NOT EXISTS classification_requests (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  req_id VARCHAR(64) UNIQUE NOT NULL,
  text MEDIUMTEXT NOT NULL,
  model_version VARCHAR(100) NOT NULL,
  label ENUM('DEFAMATION','NON_DEFAMATION') NOT NULL,
  confidence DECIMAL(5,4) DEFAULT 0.0000,
  rationale TEXT,
  latency_ms INT DEFAULT 0,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS cases (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  situation TEXT NOT NULL,
  verdict ENUM('유죄','무죄') NOT NULL,
  sentence VARCHAR(120),
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

```

---

## ▶️ 백엔드 실행

### 0) 위치 이동

- **Windows PowerShell / CMD**
    
    ```powershell
    cd .\defamation-classifier\backend
    
    ```
    
- **macOS / Linux**
    
    ```bash
    cd defamation-classifier/backend
    
    ```
    

### 1) 빌드

- **PowerShell/CMD**: `gradlew clean build`
- **macOS/Linux(Git Bash)**: `./gradlew clean build`

> 테스트가 DB 세팅 이슈로 실패하면 일단 -x test로 빌드 가능:
> 
> 
> ```
> gradlew clean build -x test
> 
> ```
> 

### 2) 실행

- **기본(애플리케이션이 local 프로필로 실행됨)**
    
    ```
    gradlew bootRun
    
    ```
    
- **프로필을 명시하고 싶다면**
    
    ```
    gradlew bootRun -Dspring-boot.run.profiles=local
    # 또는
    gradlew bootRun --args="--spring.profiles.active=local"
    
    ```
    

### 3) 확인

- Swagger UI: http://localhost:8080/swagger-ui/index.html
- 정상 로그 예:
    
    ```
    Tomcat started on port 8080 (http)
    Successfully applied 1 migration ... now at version v1
    Started BackendApplication in X.XXX seconds
    
    ```
    

> :bootRun 80% EXECUTING 으로 보이는 건 앱이 실행 중이란 뜻이며 정상입니다. 종료는 Ctrl + C.
> 

---

## 🧪 테스트 전용 DB(H2) 사용(선택)

테스트에서 MySQL 대신 H2(메모리)를 쓰고 싶다면:

1. `backend/build.gradle`에 추가

```groovy
testRuntimeOnly 'com.h2database:h2'

```

1. `src/test/resources/application-test.yml`

```yaml
spring:
  datasource:
    url: jdbc:h2:mem:defamation;MODE=MySQL;DB_CLOSE_DELAY=-1;DB_CLOSE_ON_EXIT=FALSE
    username: sa
    password:
    driver-class-name: org.h2.Driver
  jpa:
    hibernate:
      ddl-auto: validate
  flyway:
    enabled: true
    locations: classpath:db/migration

```

1. 기본 생성된 테스트에 프로필 지정

```java
@ActiveProfiles("test")
@SpringBootTest
class BackendApplicationTests { ... }

```

---

## 🌐 프런트엔드(초안)

> frontend/ 폴더는 이 README 이후 생성 예정. Vite 템플릿을 사용합니다.
> 
1. 프로젝트 생성 (예: Vue + TypeScript 옵션 선택 가능)

```bash
cd defamation-classifier
npm create vite@latest frontend -- --template vue
cd frontend
npm i

```

1. API 베이스 URL 설정
    
    `frontend/.env.development`
    

```
VITE_API_BASE=http://localhost:8080

```

1. CORS
    
    백엔드의 `application-local.yml`에 `app.cors.allowed-origins`가 `http://localhost:5173`로 되어 있으므로 dev 서버에서 호출 가능.
    
2. 실행

```bash
npm run dev

```

---

## 🧰 자주 만나는 이슈 & 해결

### 1) `Public Key Retrieval is not allowed`

- **원인**: MySQL 8 기본 인증(`caching_sha2_password`)과 JDBC 연결 시 공개키 획득 차단
- **해결**: JDBC URL에 `allowPublicKeyRetrieval=true&useSSL=false` 추가 (README의 `application-local.yml` 참고)
    
    또는 사용자 인증 플러그인 변경:
    
    ```sql
    ALTER USER 'defamation_local'@'localhost'
    IDENTIFIED WITH mysql_native_password BY 'devpass';
    FLUSH PRIVILEGES;
    
    ```
    

### 2) 프로필이 적용 안 됨

- 실행 시 `Dspring-boot.run.profiles=local` 사용
    
    또는 `application.yml`의 `spring.profiles.default=local` 확인
    

### 3) Flyway가 마이그레이션을 못 찾음

- 파일 경로/이름 확인: `src/main/resources/db/migration/V1__init.sql`
    
    (`V` + 숫자 + `__` + 설명 + `.sql`)
    

### 4) 포트 충돌

- 8080 사용 중이면 `application-local.yml`에서 `server.port` 변경

---

## 📄 라이선스

개인/학습/포트폴리오 목적 사용 자유. 상업적 사용 시 각 라이브러리 라이선스를 확인하세요.

---

## 🧭 다음 단계(로드맵)

- `/api/v1/defamation/predict` 분류 실행 API (Request DTO/Response DTO)
- `/api/v1/defamation/cases?limit=5` 최근 5건 조회
- `/api/v1/defamation/models?limit=5` 사용 모델 이력 조회
- SSE/WebSocket 기반 채팅/스트리밍 응답 (WebClient + vLLM 프록시)
- Vue UI 연동(현재 Demo UI를 참고해 실제 API 바인딩)