# API 계약 문서

파트 A · B · C 공통 참조. 변경 시 팀 전체 공유 필요.

---

## 진행 현황

| 기능 | 담당 | 상태 |
|---|---|---|
| POST /api/analyze — 텍스트 입력 | 파트 C | ✅ |
| POST /api/analyze — 이미지 입력 (OCR) | 파트 C | ✅ |
| GET /api/history | 파트 C | ✅ |
| POST /predict (AI 모델) | 파트 B | ⏳ |
| 프론트엔드 연동 | 파트 A | ⏳ |

---

## 파트 C 공개 API (파트 A가 호출)

Base URL (로컬): `http://localhost:7071/api`  
Base URL (배포 후): `https://smishingdet-functions.azurewebsites.net/api`

### POST /api/analyze

이미지 또는 텍스트를 받아 스팸 여부를 분석한다.

**이미지 입력:**
```
Content-Type: multipart/form-data
Body:
  file: <이미지 파일 (.jpg / .png / .webp)>
```

**텍스트 입력:**
```
Content-Type: application/json
Body:
{
  "text": "분석할 메시지 내용"
}
```

**성공 응답 (200):**
```json
{
  "id": 123,
  "input_type": "image",
  "label": "spam",
  "risk_level": "high",
  "confidence": 0.95,
  "reason": ["URL 포함", "금융 관련 키워드"],
  "created_at": "2026-05-21T10:00:00Z"
}
```

> `label` 가능 값: `"spam"` | `"suspicious"` | `"normal"`  
> `risk_level` 가능 값: `"high"` | `"medium"` | `"low"`  
> `confidence`: 0.0 ~ 1.0

**에러 응답:**
```json
{ "error": "에러 메시지" }
```
| 상태 코드 | 사유 |
|---|---|
| 400 | 입력값 없음 또는 형식 오류 |
| 500 | 서버 내부 오류 (Vision, SQL, 파트 B 호출 실패 등) |

---

### GET /api/history

분석 이력을 최신순으로 조회한다.

**쿼리 파라미터:**
| 파라미터 | 타입 | 기본값 | 설명 |
|---|---|---|---|
| limit | int | 20 | 한 번에 가져올 건수 (최대 100) |
| offset | int | 0 | 시작 오프셋 |

**성공 응답 (200):**
```json
{
  "items": [
    {
      "id": 123,
      "input_type": "text",
      "label": "spam",
      "risk_level": "high",
      "confidence": 0.95,
      "reason": ["URL 포함"],
      "created_at": "2026-05-21T10:00:00Z"
    }
  ],
  "total": 50
}
```

---

## 파트 B 내부 API (파트 C만 호출)

> 파트 B Container App이 배포되기 전까지 임시 mock 응답 사용.  
> 형식 변경 시 파트 B·C 협의 필요.

Base URL: `{CONTAINER_APP_URL}` (환경변수로 관리)

### POST /analyze

```
Content-Type: application/json
Body:
{
  "request_id": "<uuid>",
  "text": "전처리 없이 넘기는 원문 텍스트"
}
```

**응답:**
```json
{
  "request_id": "<uuid>",
  "label": "spam",
  "risk_level": "high",
  "confidence": 0.91,
  "reason": ["URL 포함", "금융 관련 키워드 탐지"]
}
```

> `label` 가능 값: `"spam"` | `"suspicious"` | `"normal"`  
> 파트 C는 파트 B 응답을 변환 없이 그대로 저장 및 전달

---

## CORS

파트 A(React) 개발 서버에서 호출하므로 Azure Functions에서 CORS 허용 필요.  
`host.json`의 `extensions.http.cors` 또는 Azure Portal에서 설정.
