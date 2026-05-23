# 개발 환경 설정 가이드 (파트 C 백엔드)

## 필수 도구

| 도구 | 버전 | 설명 |
|---|---|---|
| Python | 3.11 | Azure Functions 지원 버전 |
| uv | 최신 | Python 가상환경 + 패키지 관리 |
| Azure Functions Core Tools | v4 | 로컬 실행 (`func start`) |
| ODBC Driver 18 for SQL Server | 18 | Azure SQL 연결 드라이버 |

---

## 설치

### Windows

```powershell
# uv 설치
winget install astral-sh.uv

# Azure Functions Core Tools v4
winget install Microsoft.AzureFunctionsCoreTools

# ODBC Driver 18
winget install Microsoft.msodbcsql.18
```

설치 후 **터미널을 완전히 재시작**해야 `func` 명령이 인식됨.

### macOS

```bash
# uv 설치
curl -LsSf https://astral.sh/uv/install.sh | sh

# Azure Functions Core Tools v4
brew tap azure/functions
brew install azure-functions-core-tools@4

# ODBC Driver 18
brew tap microsoft/mssql-release https://github.com/Microsoft/homebrew-mssql-release
brew install msodbcsql18
```

---

## 프로젝트 세팅

### 1. 클론

```bash
git clone <repository-url>
cd CCTermProject
```

### 2. Python 가상환경 생성 및 패키지 설치

```bash
cd backend
uv python install 3.11
uv venv --python 3.11
```

가상환경 활성화:
- Windows: `.venv\Scripts\activate`
- macOS/Linux: `source .venv/bin/activate`

```bash
uv pip install -r requirements.txt
```

### 3. 환경변수 설정

`backend/local.settings.json.example`을 복사해 `local.settings.json`을 만들고 Azure Portal에서 각 값을 채움.

```bash
cp local.settings.json.example local.settings.json
```

| 키 | 어디서 찾나 |
|---|---|
| `AZURE_VISION_ENDPOINT` | Azure Portal → Azure AI Vision 리소스 → 키 및 엔드포인트 |
| `AZURE_VISION_KEY` | 동일 |
| `BLOB_CONNECTION_STRING` | Azure Portal → 스토리지 계정 → 액세스 키 → 연결 문자열 |
| `BLOB_CONTAINER_NAME` | 스토리지 계정의 컨테이너 이름 (현재: `images`) |
| `SQL_CONNECTION_STRING` | Azure Portal → SQL Database → 연결 문자열 → ODBC |
| `CONTAINER_APP_URL` | 파트 B 배포 후 입력 (현재 비워둠) |

> `local.settings.json`은 `.gitignore`에 포함되어 있어 커밋되지 않음.

---

## 로컬 실행

```bash
cd backend
func start
```

정상 실행 시 출력:
```
Functions:
    analyze: [POST] http://localhost:7071/api/analyze
    history: [GET]  http://localhost:7071/api/history
```

---

## 동작 확인 (Postman)

**텍스트 분석:**
- Method: `POST`
- URL: `http://localhost:7071/api/analyze`
- Headers: `Content-Type: application/json`
- Body (raw JSON): `{"text": "테스트 메시지"}`

**이미지 분석:**
- Method: `POST`
- URL: `http://localhost:7071/api/analyze`
- Body: `form-data`, key=`file`, type=`File`, 이미지 파일 첨부

**이력 조회:**
- Method: `GET`
- URL: `http://localhost:7071/api/history?limit=10&offset=0`
