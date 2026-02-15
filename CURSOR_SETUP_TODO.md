# Cursor MCP 실행 TODO (Export 이후 재분류/정리 포함)

`NOTION`에서 export해 로컬로 가져온 데이터가 있다고 가정했을 때의 Cursor 연동 세팅/운영 TODO.

## 0) 전제

- local MCP(`local-knowledge-mcp`)가 실행 중이어야 함
- `KNOWLEDGE_ROOT`가 문서 저장 폴더를 가리킴
- Cursor는 다중 MCP 서버 등록 가능
- Notion 원본은 이미 export되어 `.md` 또는 텍스트로 정리되어 있음

## 1) Cursor MCP 서버 등록

- local MCP (`http`): `http://127.0.0.1:8000/mcp`
- 헤더:
  - `Authorization: Bearer <MCP_API_TOKEN>` (토큰 사용 시)

예시 스니펫은 `CURSOR_MCP_SETUP.md` 참고.

## 2) MANIFEST 기준 Tool 사용 순서

현재 추천 순서:

1. `list_docs`로 임포트된 파일 목록 확인
2. `search_docs`로 중복/중심 키워드(주제 후보) 추출
3. `read_doc`로 대표 문서를 검토
4. `rebuild_summary`로 상위 노트/인덱스 초안 생성
5. (선택) `reclassify_and_reorganize`를 Manifest에 추가 후 실행

## 3) 정리/재분류 파이프라인 TODO

1. 주제 후보군 정의
   - 예: `architecture`, `api`, `deploy`, `incident`, `faq`
2. 폴더 규칙 정리
   - 예: `projectA/architecture`, `projectA/api`, `projectA/faq`
3. 파일 규칙 정리
   - 제목 접두사(`arch-`, `faq-`) 또는 키워드 기반 이동 규칙
4. `upsert_doc`로 규칙 기반 이동/재저장을 수행
5. `list_docs`로 이동 결과 검증
6. `rebuild_summary`로 주간/주제별 개요문 생성
7. 지식 루트 루트에 `index.json` 또는 `summary.md` 저장

## 4) Manifest에 넣으면 좋은 추가 Tool(권장)

현재 운영에는 직접 추가 가능한 커스텀 Tool 2개를 권장:

- `reclassify_docs`
  - 입력: `paths`, `rules`, `target_root`, `mode(dry_run|apply)`
  - 동작: 키워드/경로 패턴으로 문서 이동/재배치 초안 또는 실제 반영
- `rebuild_topic_index`
  - 입력: `root`, `style(notes|spec|faq)`, `output_path`
  - 동작: 주제별 문서 인덱스/요약 생성

추가되면 Cursor의 자동 워크플로에서 사람 개입 없이도 정리 루틴을 반복 실행할 수 있습니다.

## 5) 일별/주간 자동화 제안

1. 매일: `search_docs` + `rebuild_summary`로 신규 변경 감지 후 개요 업데이트
2. 매주: 재분류 규칙 점검 + `reclassify_docs` dry-run 점검
3. 승인 후 apply 실행
4. 최종 점검 문서(`summary.md`, `index.json`)를 버전 관리

## 6) 보안/안정성 체크

- `READ_ONLY` 여부 확인
- `ALLOWED_EXTENSIONS` 최소 범위 유지
- `ALLOWED_ORIGINS`에 Cursor Origin만 허용
- `MCP_API_TOKEN` 미설정 상태는 로컬 전용 전용이라면 허용, 외부면 필수
