# CCTermProject — Claude 협업 가이드

## 프로젝트 개요

피싱/스팸 탐지 앱. Azure 클라우드 컴퓨팅 수업 팀 프로젝트.

- **파트 A**: React 프론트엔드 (Azure Static Web Apps)
- **파트 B**: AI 파이프라인 (KLUE-BERT + Azure Container Apps)
- **파트 C**: 백엔드/인프라 — **현재 담당 파트**

## 핵심 문서

- 시스템 구조: [`docs/architecture.md`](docs/architecture.md)
- Azure 서비스 정리: [`docs/Azure_services.md`](docs/Azure_services.md)
- API 계약: [`docs/api-contract.md`](docs/api-contract.md)

## 기술 스택 (파트 C)

- Azure Functions (Python 3.11, v2 프로그래밍 모델)
- Azure AI Vision — 이미지 OCR
- Azure Blob Storage — 원본 이미지 저장
- Azure SQL — 분석 결과 + 이력 저장
- Azure Container Apps 환경 (파트 B 모델 호스팅)

## 협업 방식 (AI 사용 제한 반영)

코드는 사용자가 직접 작성한다. Claude는 다음 방식으로 지원한다.

- 구현 방향과 접근법 설명 (왜 이렇게 하는지 위주)
- 의사코드(pseudocode) 또는 함수 구조 제시
- 작성한 코드 리뷰 및 버그 지적
- Azure SDK 사용법과 공식 문서 안내
- 에러 메시지 해석 및 해결 방향 제시

**하지 않는 것:** 완성된 함수·파일을 통째로 작성해주지 않음

## 완성된 기능

| 날짜 | 기능 | 파일 | 비고 |
|------|------|------|------|
| 2026-05-21 | POST /api/analyze — 텍스트 입력 + SQL 저장 | backend/function_app.py | 파트 B 연결은 mock, 이미지 경로 미구현 |
| 2026-05-21 | GET /api/history — SQL 조회 + 페이지네이션 | backend/function_app.py | limit/offset 지원 |
| 2026-05-21 | POST /api/analyze — 이미지 입력 (Blob + Vision OCR) | backend/function_app.py | Blob 컨테이너명 "images", 파트 B 연결은 mock |
