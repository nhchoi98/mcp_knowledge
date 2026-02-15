# Cursor MCP 연결 가이드

이 문서는 로컬 MCP 서버(`local-knowledge-mcp`)를 Cursor에서 붙이는 방법을 설명합니다.

## 1) 권장 실행 방식

- MCP 서버를 `127.0.0.1:8000`에서 실행
- Cursor에서 HTTP(또는 Streamable HTTP) 기반 MCP 연결 사용
- 인증이 필요한 경우 `MCP_API_TOKEN`으로 Bearer 토큰 전달

```bash
export KNOWLEDGE_ROOT=/home/me/knowledge
# 또는 .git 루트 자동 사용
export USE_GIT_ROOT=true

export ALLOWED_EXTENSIONS=.md,.txt,.py,.ts
export MCP_API_TOKEN=dev-token-123

uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

### 운영용 예시 환경변수 (ALLOWED_ORIGINS + READ_ONLY + Git root)

```bash
export USE_GIT_ROOT=true
export ALLOWED_EXTENSIONS=.md,.txt,.py,.ts,.json
export READ_ONLY=false
export MCP_API_TOKEN=ops-token-please-rotate
export ALLOWED_ORIGINS=http://127.0.0.1:8000,https://127.0.0.1:8000,http://localhost:3000,https://localhost:3000
export MAX_READ_BYTES=2000000
```

## 2) MCP 서버에 노출된 엔드포인트

- `POST /mcp` : MCP JSON-RPC 엔드포인트 (권장)
- `GET /mcp/manifest` : 디버그용 매니페스트 조회
- `POST /mcp/call` : 디버그용 툴 직접 호출
- `GET /mcp/sse` : SSE 스트림(선택)

## 3) Cursor에 등록하기

### A. URL 방식(Streamable HTTP)

1. Cursor의 MCP 설정 화면(또는 Settings)에서 새 MCP 서버를 추가
2. 아래 형식으로 서버를 등록
3. URL: `http://127.0.0.1:8000/mcp`
4. 인증 필요 시 Header에 `Authorization: Bearer <MCP_API_TOKEN>` 추가

Cursor 설정 예시

```json
{
  "mcpServers": {
    "local-knowledge": {
      "type": "http",
      "url": "http://127.0.0.1:8000/mcp",
      "headers": {
        "Authorization": "Bearer dev-token-123"
      }
    }
  }
}
```

### 운영용 템플릿 (ALLOWED_ORIGINS 포함)

```json
{
  "mcpServers": {
    "local-knowledge": {
      "type": "http",
      "url": "http://127.0.0.1:8000/mcp",
      "headers": {
        "Authorization": "Bearer ops-token-please-rotate",
        "Origin": "http://127.0.0.1:3000"
      }
    }
  }
}
```

### Read-only + Git root + 보안 헤더 템플릿

```json
{
  "mcpServers": {
    "local-knowledge-ro": {
      "type": "http",
      "url": "http://127.0.0.1:8000/mcp",
      "headers": {
        "Authorization": "Bearer read-only-token-123",
        "Origin": "http://localhost:3000"
      }
    }
  }
}
```

서버 쪽 실행 예시:

```bash
export USE_GIT_ROOT=true
export READ_ONLY=true
export MCP_API_TOKEN=read-only-token-123
export ALLOWED_EXTENSIONS=.md,.txt
export ALLOWED_ORIGINS=http://localhost:3000,https://localhost:3000,http://127.0.0.1:3000
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

### B. stdio를 쓰는 환경(권장 아님)

만약 Cursor가 stdio 모드만 지원하는 버전이면, stdio 래퍼를 별도 구성해야 합니다. 예시 개념:

```json
{
  "mcpServers": {
    "local-knowledge-stdio": {
      "command": "python",
      "args": [
        "-m",
        "uvicorn",
        "app.main:app",
        "--host",
        "127.0.0.1",
        "--port",
        "8000"
      ],
      "env": {
        "MCP_API_TOKEN": "dev-token-123"
      }
    }
  }
}
```

참고: 실제 Cursor 버전에 따라 설정 스키마가 다를 수 있으므로, 실 UI 화면 기준으로 `type`, `command`, `env`, `url` 키 이름이 다르면 그에 맞춰 조정하세요.

## 4) Cursor 동작 확인 체크리스트

- 서버 `/health`가 정상 응답
- Cursor의 tool 목록에서 아래가 보임
  - `list_docs`
  - `read_doc`
  - `search_docs`
  - `upsert_doc`
  - `rebuild_summary`
- `KNOWLEDGE_ROOT`에 지정한 위치에서 파일 목록 조회가 되는지 확인

## 5) 최소 보안 설정

- 외부 노출 시 `MCP_API_TOKEN` 필수화
- `ALLOWED_ORIGINS`에 필요한 Cursor Origin 추가
- 쓰기 금지면 `READ_ONLY=true`
- 검색 범위를 줄이려면 `ALLOWED_EXTENSIONS` 축소

## 6) 트러블슈팅

- 툴이 안 보임: `/mcp` 반환값, `tools/list` 응답 확인
- 토큰 오류: `401`이면 토큰/헤더 형식(`Bearer ` 접두사) 확인
- 접근 오류: `FORBIDDEN`이면 `KNOWLEDGE_ROOT` 또는 경로 traversal 검사 조건 재확인

## 7) 재분류/정리 TODO 연동

- 상세 실행 TODO는 `CURSOR_SETUP_TODO.md`를 기준으로 진행
- Manifest 확장 후보: `reclassify_docs`, `rebuild_topic_index`
- 운영은 1) `list_docs` → 2) `search_docs` → 3) `read_doc` → 4) `rebuild_summary` → 5) (필요 시 재분류 Tool)
