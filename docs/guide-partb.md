# 파트 B 연동 가이드

파트 C(백엔드)와 연동하기 위해 파트 B가 해야 할 것들을 정리한 문서.

---

## 파트 C에게 받을 정보

| 항목 | 설명 |
|---|---|
| `AZURE_LANGUAGE_ENDPOINT` | Azure AI Language 엔드포인트 URL |
| `AZURE_LANGUAGE_KEY` | Azure AI Language API 키 |
| `ACR_SERVER` | Container Registry 서버 주소 (예: `smishingdetregistry.azurecr.io`) |
| `ACR_USERNAME` | Registry 로그인 사용자명 |
| `ACR_PASSWORD` | Registry 로그인 비밀번호 |

---

## Docker 이미지 빌드 및 Push

파트 B 모델 서버를 Docker 이미지로 빌드한 뒤 파트 C의 Registry에 push.

```bash
# 1. Registry 로그인
docker login <ACR_SERVER> -u <ACR_USERNAME> -p <ACR_PASSWORD>

# 2. 이미지 빌드
docker build -t <ACR_SERVER>/smishing-model:latest .

# 3. 이미지 push
docker push <ACR_SERVER>/smishing-model:latest
```

push 완료 후 파트 C에게 아래 정보 전달:
- 이미지 전체 경로 (예: `smishingdetregistry.azurecr.io/smishing-model:latest`)
- 앱이 사용하는 포트 번호
- 필요한 환경변수 목록 (있을 경우)

파트 C가 이 정보를 바탕으로 Container App을 생성하고 URL을 공유해줌.

---

## 구현할 API 스펙

파트 C가 호출하는 엔드포인트. 아래 스펙에 맞게 구현 필요.

### `POST /predict`

**요청:**
```json
{
  "text": "분석할 텍스트 (이미지는 파트 C에서 OCR 완료 후 전달)"
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

| 필드 | 타입 | 값 |
|---|---|---|
| `result` | string | `"spam"` \| `"suspicious"` \| `"normal"` |
| `confidence` | float | 0.0 ~ 1.0 |
| `reasons` | string[] | 판단 근거 목록 (빈 배열도 허용) |

> 이미지 OCR은 파트 C에서 처리하므로 `/predict`는 텍스트 입력만 처리하면 됨.

---

## Azure AI Language 사용

파트 C가 제공한 키로 Azure AI Language(엔티티 인식 등) 호출.

```
AZURE_LANGUAGE_ENDPOINT=<파트 C에게 받은 값>
AZURE_LANGUAGE_KEY=<파트 C에게 받은 값>
```

SDK 문서: https://learn.microsoft.com/ko-kr/azure/ai-services/language-service/

---

## 연동 흐름 요약

```
파트 A(프론트) → 파트 C(Functions) → 파트 B(/predict) → 파트 C → 파트 A
                     ↓
              이미지면 OCR 후 텍스트만 B에게 전달
              결과를 SQL에 저장 후 A에 반환
```
