# local-knowledge-mcp (FastAPI)

로컬 디렉토리를 지식 저장소로 다루는 MCP 스타일 서버입니다.

## 1) 기능

- `list_docs`: 문서 목록 조회
- `read_doc`: 문서 읽기
- `search_docs`: 키워드 라인 검색
- `upsert_doc`: 문서 생성/갱신 (`overwrite`/`append`)
- `rebuild_summary`: 여러 문서를 요약/재구성해 새 파일로 저장
- `KNOWLEDGE_BACKEND=github` 설정 시 GitHub 저장소를 로컬에 동기화한 뒤 조작합니다.
- `sync_status`: GitHub 동기화 상태(스테이지/언스테이지/새 브랜치용 상태) 조회
- `create_pr`: 스테이징된 변경을 새 브랜치로 커밋 + push 하고 PR 비교 URL 생성

## 2) 보안 설계

- `KNOWLEDGE_ROOT` 하위 경로만 접근 가능
- `USE_GIT_ROOT=true`면 실행 시점의 현재 디렉토리부터 상위로 올라가 `.git`을 찾고, 찾으면 그 루트를 지식 루트로 사용
- 경로 탈출(`../`) 방지: resolve 후 루트 prefix 검사
- 확장자 allowlist (`ALLOWED_EXTENSIONS`, 기본 `.md,.txt`)
- 읽기 전용 모드 (`READ_ONLY=true`)에서 쓰기 계열 도구 차단
- 선택적 토큰 인증 (`MCP_API_TOKEN`)

- Cursor 연결 가이드: `CURSOR_MCP_SETUP.md`

## 3) 실행

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# 필요시 .env 값 수정
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Git repo를 바로 지식 저장소로 쓰고 싶다면:

```bash
export USE_GIT_ROOT=true
export ALLOWED_EXTENSIONS=.md,.txt,.py,.ts
```

GitHub 원격 저장소를 동기화 모드로 쓰려면:

```bash
KNOWLEDGE_BACKEND=github
GITHUB_REPO=owner/repo
GITHUB_REF=main
GITHUB_TOKEN=ghp_xxx   # private repo 또는 rate limit 완화용
ALLOWED_EXTENSIONS=.md,.txt,.py,.ts
```

위 값들을 `.env`에 넣으면 서버가 시작 시 자동으로 읽습니다.

`KNOWLEDGE_BACKEND=github`일 때:
- 조회(`list_docs`, `read_doc`, `search_docs`)는 동작 전 `git pull`을 실행하고 로컬 파일을 읽어 반환합니다.
- 수정(`upsert_doc`, `rebuild_summary`)은 로컬 파일 변경 후 `git add`로 staged 상태로 기록합니다.
- PR 전용으로 `sync_status` 툴로 상태를 확인하고, `create_pr` 툴로 브랜치 커밋 + push + PR URL 생성이 가능합니다.
- MCP manifest(`GET /mcp/manifest`, `tools/list`)의 description에 `source: github:<repo>@<ref>`가 자동 표기됩니다.
- GitHub 작업 폴더는 `KNOWLEDGE_ROOT/<owner>__<repo>` 입니다.

## 4) 빠른 테스트

```bash
curl http://127.0.0.1:8000/health

curl -X POST http://127.0.0.1:8000/mcp/call \
  -H 'content-type: application/json' \
  -d '{"name":"list_docs","arguments":{}}'
```

## 4-1) Notion 빠른 동기화(MVP)

Notion 통합 토큰과 루트 페이지 ID를 `.env`에 넣고 실행하면
`KNOWLEDGE_ROOT` 아래 `NOTION_SYNC_SUBDIR` 폴더(기본 `notion`)로 Markdown이 동기화됩니다.

```bash
set -a; source .env; set +a
python scripts/sync_notion.py
```

동기화 후 MCP 탐색 확인:

```bash
curl -s http://127.0.0.1:8000/mcp/call \
  -H 'content-type: application/json' \
  -d '{"name":"list_docs","arguments":{}}'
```

토큰을 켠 경우:

```bash
-H "Authorization: Bearer $MCP_API_TOKEN"
```

## 5) MCP 엔드포인트

- `POST /mcp` : JSON-RPC 스타일 MCP 요청 (`initialize`, `tools/list`, `tools/call`, `ping`)
- `GET /mcp/manifest` : 디버그용 툴/스키마 목록
- `POST /mcp/call` : 디버그용 단일 툴 실행
- `GET /mcp/sse` : 선택적 SSE heartbeat/manifest 스트림

## 6) Cursor 연결 예시

Cursor 버전에 따라 MCP 연결 방식이 다를 수 있어, 아래 둘 중 맞는 방식을 사용하세요.

### A. HTTP(원격/로컬 URL) 연결을 지원하는 경우

- MCP 서버 URL을 `http://127.0.0.1:8000/mcp` 로 등록
- 토큰 사용 시 `Authorization: Bearer <token>` 헤더 추가
- `ALLOWED_ORIGINS`에 Cursor에서 요청하는 Origin을 포함

### B. stdio 기반만 허용되는 경우

- 이 FastAPI 서버를 그대로 두고, 별도 stdio 프록시를 두어 `/mcp`로 포워딩
- 또는 같은 툴 로직을 stdio MCP 서버로 래핑

Cursor가 `Streamable HTTP`를 지원하면 이 서버를 그대로 붙일 수 있습니다.

## 7) 툴 입력/출력 예시

### `list_docs`

```json
{
  "subdir": "project-a"
}
```

### `read_doc`

```json
{
  "path": "project-a/notes.md"
}
```

### `search_docs`

```json
{
  "query": "latency",
  "limit": 20,
  "case_sensitive": false
}
```

GitHub 백엔드에서는 `search_docs`가 허용 확장자 파일을 순회하며 내용을 조회하므로,
문서 수가 많으면 API 호출 수가 증가할 수 있습니다.

### `upsert_doc`

```json
{
  "path": "project-a/meeting.md",
  "content": "# Weekly Notes\n...",
  "mode": "overwrite"
}
```

### `rebuild_summary`

```json
{
  "paths": ["project-a/notes.md", "project-a/spec.md"],
  "output_path": "project-a/summary.md",
  "style": "spec"
}
```

`rebuild_summary`에 전달하는 `paths`는 **파일 경로만** 허용됩니다.
`Backend/FastAPI` 같은 폴더 경로, 절대 경로(`/foo.md`)는 서버에서 거부되며,
유효한 값은 `KNOWLEDGE_ROOT` 기준의 상대 경로(`project-a/notes.md`)여야 합니다.

## 8) 다음 단계 제안

- 검색 품질 향상이 필요하면 `search_docs`를 BM25/임베딩 인덱스로 교체
- `rebuild_summary`를 외부 LLM 호출 버전으로 분리 (현재는 규칙 기반 요약)
- 프로덕션에서는 토큰 인증 + TLS + 감사 로그 추가

## 9) MCP 표준 학습 문서 (공식)

- MCP 공식 문서 홈: https://modelcontextprotocol.io/introduction
- MCP 스펙 인덱스: https://modelcontextprotocol.io/specification
- 최신 스펙 릴리즈 노트(2025-11-25): https://modelcontextprotocol.io/specification/2025-11-05/changelog#2025-11-25
- 전송(Transports) 문서: https://modelcontextprotocol.io/specification/2025-11-05/basic/transports
- Streamable HTTP 보안 고려사항(Origin 검증 포함): https://modelcontextprotocol.io/specification/2025-11-05/basic/transports#security-warning
- 공식 Python SDK: https://github.com/modelcontextprotocol/python-sdk
- Cursor MCP 문서: https://docs.cursor.com/context/model-context-protocol
