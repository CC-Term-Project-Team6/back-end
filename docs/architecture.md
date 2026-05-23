## 시스템 구조

**입력 레이어 (파트 A)**

```
이미지 업로드         텍스트 직접 입력
(스크린샷·사진)       (붙여넣기)
        ↓                   ↓
```

**Azure Functions (파트 C)**

```
API 게이트웨이 · 라우팅 · 입력 분기
    ↓ 이미지면              ↓ 텍스트면
Azure AI Vision         그대로 전달
(OCR · 텍스트 추출)
Blob Storage
(이미지 저장)
    ↓ 추출된 텍스트         ↓ 텍스트
    └──────────────────────┘
                ↓ 텍스트만 전달
```

**Container Apps (파트 B)**

```
전처리 파이프라인
  유니코드 정규화 → 이모지 제거 → 문자 치환
  자모 복원 → URL 토큰화 → 구두점 복원
        ↓
KLUE-BERT 파인튜닝 모델    Azure AI Language
(Korean_message 학습)     (엔티티·URL 감지)
        ↓                       ↓
        └──── 종합 판정 로직 ────┘
                ↓ 결과 JSON 반환
```

**Azure Functions (파트 C) — 결과 처리**

```
Azure SQL 저장          결과 카드 반환
(분석 결과·이력)         (스팸/의심/정상·신뢰도·근거)
        ↓                       ↓
        └──────────────────────┘
                ↓
```

**프론트엔드 결과 표시 (파트 A)**

```
React · Azure Static Web Apps
(이력 조회 ← Azure SQL)
```