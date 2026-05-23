# API 계약 문서

파트 A · B · C 공통 참조. 변경 시 팀 전체 공유 필요.

---

## 파트 C 공개 API (파트 A가 호출)

Base URL (로컬): `http://localhost:7071/api`  
Base URL (배포 후): Azure Functions URL

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
  "result": "spam",
  "confidence": 0.95,
  "reasons": ["URL 포함", "금융 관련 키워드"],
  "created_at": "2026-05-21T10:00:00Z"
}
```

> `result` 가능 값: `"spam"` | `"suspicious"` | `"normal"`  
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
      "result": "spam",
      "confidence": 0.95,
      "reasons": ["URL 포함"],
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

### POST /predict

```
Content-Type: application/json
Body:
{
  "text": "전처리 없이 넘기는 원문 텍스트"
}
```

**응답:**
```json
{
  "result": "spam",
  "confidence": 0.95,
  "reasons": ["URL 포함", "금융 관련 키워드"]
}
```

> `result` 가능 값: `"spam"` | `"suspicious"` | `"normal"`

---

## CORS

파트 A(React) 개발 서버에서 호출하므로 Azure Functions에서 CORS 허용 필요.  
`host.json`의 `extensions.http.cors` 또는 Azure Portal에서 설정.
