# API 요약

> 상세 스펙: [`api-contract.md`](api-contract.md)

---

## 파트 C — 공개 API

Base URL (로컬): `http://localhost:7071/api`  
Base URL (배포): Azure Functions URL (추후 업데이트)

| 엔드포인트 | 메서드 | 설명 | 상태 |
|---|---|---|---|
| `/api/analyze` | POST | 이미지 또는 텍스트 스팸 분석 | ✅ 구현 완료 |
| `/api/history` | GET | 분석 이력 조회 | ✅ 구현 완료 |

### POST /api/analyze

| 입력 방식 | Content-Type | Body |
|---|---|---|
| 이미지 | `multipart/form-data` | `file`: 이미지 파일 |
| 텍스트 | `application/json` | `{"text": "내용"}` |

**응답:**
```json
{
  "id": 1,
  "input_type": "image | text",
  "result": "spam | suspicious | normal",
  "confidence": 0.95,
  "reasons": ["URL 포함", "금융 키워드"]
}
```

### GET /api/history

| 쿼리 파라미터 | 기본값 | 설명 |
|---|---|---|
| `limit` | 20 | 가져올 건수 (최대 100) |
| `offset` | 0 | 시작 오프셋 |

**응답:** `{"items": [...], "total": 50}`

---

## 파트 B — 내부 API (파트 C → 파트 B)

| 엔드포인트 | 메서드 | 설명 | 상태 |
|---|---|---|---|
| `/predict` | POST | 텍스트 스팸 분류 | ⏳ 연결 대기 중 |

**요청:** `{"text": "분석할 텍스트"}`  
**응답:** `{"result": "spam | suspicious | normal", "confidence": 0.95, "reasons": [...]}`

> 파트 B Container App 배포 후 `CONTAINER_APP_URL` 환경변수에 URL 입력하면 자동 연결됨.

---

## 진행 현황

| 기능 | 담당 | 상태 |
|---|---|---|
| POST /api/analyze — 텍스트 입력 | 파트 C | ✅ |
| POST /api/analyze — 이미지 입력 (OCR) | 파트 C | ✅ |
| GET /api/history | 파트 C | ✅ |
| POST /predict (AI 모델) | 파트 B | ⏳ |
| 프론트엔드 연동 | 파트 A | ⏳ |
