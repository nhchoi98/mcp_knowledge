---
title: fecth와 XHR
tags: []
created: ""
updated: ""
source: ""
status: draft
---
# fecth와 XHR

| 항목 | `fetch` | `XMLHttpRequest(XHR)` |
| --- | --- | --- |
| 스타일 | Promise 기반 | 콜백/이벤트 기반 |
| 환경 | 브라우저, **Node/Next.js 서버**(전역 `fetch`) | **브라우저 전용** |
| 에러 처리 | 네트워크 에러만 reject, `res.ok` 직접 체크 | `onerror`(네트워크), `status` 직접 체크 |
| 취소 | `AbortController` | `xhr.abort()` |
| 타임아웃 | 내장 없음 → `AbortController`로 구현 | `xhr.timeout` 지원 |
| 쿠키/자격증명 | 기본 same-origin만 포함, CORS 쿠키는 `credentials:'include'` | same-origin 자동, CORS 쿠키는 `withCredentials=true` |
| 진행률(Progress) | **표준 이벤트 없음**(다운로드는 Stream으로 계산 가능) | **업로드/다운로드 진행률 이벤트 지원** |
| 스트리밍 | **ReadableStream**으로 본문 스트리밍 처리 용이 | 부분 문자열/프로gress는 가능하나 스트림 처리 제약 |
| 바이너리 | `res.arrayBuffer()/blob()` | `responseType='arraybuffer' |
| 리다이렉트 | `redirect:'follow' | 'manual'` |
| 동기 요청 | **불가** | (메인 스레드 동기 XHR은 금지 수준, 사실상 비권장) |

# Next.js에서의 관점

- **서버/Route Handler/서버 액션**: `fetch`만 사용 가능(XHR 없음).
- **클라이언트 컴포넌트**: 둘 다 가능하지만, **기본은 `fetch`**.
    
    단, **파일 업로드 진행률**이 필요하면 XHR(또는 XHR 기반 라이브러리인 Axios의 `onUploadProgress`)이 편합니다.
    
- **MSW**: 브라우저에선 Service Worker가 **fetch/XHR 모두 인터셉트**합니다. Node(테스트) 환경은 `fetch` 인터셉트.

# 언제 무엇을?

- **대부분**: `fetch` (단순, 서버/클라 공통, 스트리밍/캐싱 친화적)
- **업로드/다운로드 진행률 이벤트 필요**: XHR/Axios
- **레거시 코드/라이브러리 호환**: XHR

# Axios에 대하여

# fetch/XHR 대비 핵심 차이

- **일관된 에러 처리**: Axios는 **2xx가 아니면 reject**(커스터마이즈 가능: `validateStatus`). `fetch`는 네트워크 에러만 reject.
- **타임아웃 기본 제공**: `timeout: 10000` 옵션. `fetch`는 AbortController로 직접 구현해야 함.
- **요청/응답 변환 자동화**: JS 객체 전송 시 JSON 자동 직렬화, 응답은 `res.data`로 바로 사용.
- **인터셉터**: 토큰 주입, 리프레시 토큰 재시도, 로깅 등을 **미들웨어처럼** 삽입(`request/response interceptors`).
- **진행률 이벤트**: 업로드/다운로드 **progress**(브라우저) 쉽게 처리. `fetch`는 업로드 progress가 표준화되어 있지 않음.
- **취소**: `signal`(AbortController) 지원.
- **파라미터 직렬화**: `params`/`paramsSerializer`로 쿼리 빌드 편리.
- **Node 적합성**: 쿠키/프록시/스트림 등 서버 사이드 옵션 풍부.

# 언제 Axios가 유리해?

- **인증 토큰 주입/갱신** 등 공통 로직을 인터셉터로 관리하고 싶을 때
- **파일 업로드 진행률** UI가 필요할 때
- **에러/타임아웃/재시도 정책**을 중앙에서 강제하고 싶을 때
- **Node & 브라우저 공용** 데이터 레이어를 한 API로 쓰고 싶을 때

# Next.js 관점 팁

- **App Router의 서버(SSR/Route Handler/서버 액션)**: **`fetch`가 1순위** (Next의 캐싱/리밸리데이트·태깅 기능을 그대로 활용 가능).
    
    내부 서버 코드에서 “자기 자신 API”를 Axios로 다시 치는 건 비권장 → **서비스 함수 직접 호출** 권장.
    
- **클라이언트 컴포넌트/브라우저 전용 로직**: Axios 선택 👍 (진행률/인터셉터 이점 큼).
- **Edge Runtime**: 기본 Axios 어댑터는 **동작 제한** 가능 → Edge에선 `fetch` 사용 권장.

# MSW와 궁합

- **브라우저**: Axios는 XHR 기반 → **MSW가 인터셉트** 가능.
- **테스트(Node)**: Axios의 http 요청도 **msw/node**가 잡아줌 → 성공/실패/엣지 케이스 시나리오 모킹에 적합.