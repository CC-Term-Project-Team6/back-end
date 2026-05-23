## 각 파트별 Azure 서비스 정리

### 파트 A — 프론트엔드

| 서비스 | 용도 | 시점 |
| --- | --- | --- |
| Azure Static Web Apps | React 앱 배포 | 배포 때만 |

### 파트 B — AI 파이프라인

| 서비스 | 용도 | 직접 설정 여부 |
| --- | --- | --- |
| Azure AI Language | 엔티티 인식 API 호출 | 키만 받아서 사용 (C에게 받음) |
| Azure Container Registry | KLUE-BERT 모델 이미지 저장소 | 이미지 push만 담당 (자격증명 C에게 받음) |
| Azure Container Apps | KLUE-BERT 모델 서빙 | 이미지 push 후 **C가 배포** |

**리소스 생성 및 Container App 배포는 파트 C 담당.** 파트 B는 Docker 이미지 빌드 + push와 AI Language API 호출만 담당.

```
파트 B 로컬 개발 환경
.env
AZURE_LANGUAGE_ENDPOINT=... ← 파트 C에게 받음
AZURE_LANGUAGE_KEY=...      ← 파트 C에게 받음
ACR_SERVER=...              ← 파트 C에게 받음 (이미지 push용)
ACR_USERNAME=...            ← 파트 C에게 받음
ACR_PASSWORD=...            ← 파트 C에게 받음
```

### 파트 C — 백엔드/인프라

| 서비스 | 용도 | 직접 설정 여부 |
| --- | --- | --- |
| Azure Functions | API 게이트웨이, 라우팅, 입력 분기 | 직접 개발 + 배포 |
| Azure AI Vision | OCR 호출 (이미지 → 텍스트) | 직접 리소스 생성 + 호출 |
| Blob Storage | 원본 이미지 저장 | 직접 설정 |
| Azure SQL | 분석 결과 + 이력 저장 | 직접 설정 + 스키마 설계 |
| Azure Container Apps | 환경 생성 + Container App 배포 | 환경 생성 + 배포 모두 담당 |
| Azure Container Registry | 도커 이미지 저장소 | 직접 설정 |