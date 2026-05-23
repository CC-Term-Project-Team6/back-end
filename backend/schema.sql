-- 분석 결과 저장 테이블
-- B-C API 형식 확정 후 reasons 컬럼 구조 재검토 필요
CREATE TABLE analyses (
    id            INT IDENTITY(1,1) PRIMARY KEY,
    input_type    VARCHAR(10)    NOT NULL,   -- 'image' | 'text'
    original_text NVARCHAR(MAX),
    blob_url      VARCHAR(500),              -- 이미지 입력인 경우 Blob URL
    result        VARCHAR(20)    NOT NULL,   -- 'spam' | 'suspicious' | 'normal'
    confidence    FLOAT,
    reasons       NVARCHAR(MAX),             -- JSON 배열 문자열 ex) ["URL 포함", "금융 키워드"]
    created_at    DATETIME2      DEFAULT GETDATE()
);

-- 이력 조회 최적화 인덱스
CREATE INDEX idx_analyses_created_at ON analyses (created_at DESC);
