---
title: 쿠키, 세션스토리지, 로컬스토리지
tags: []
created: ""
updated: ""
source: ""
status: draft
---
# 쿠키, 세션스토리지, 로컬스토리지

### 🍪 쿠키 (Cookie)

- 브라우저 ↔ 서버 간 자동으로 전송되는 작은 데이터(4KB 제한)
- 기본적으로 HTTP 요청 시 `Cookie` 헤더에 실려 서버에 전송
- **만료일 설정 가능** (세션 쿠키 / 영속 쿠키)
- `HttpOnly`, `Secure`, `SameSite` 같은 옵션으로 보안 강화 가능
- 전통적으로 세션 ID나 인증 토큰 저장에 자주 사용됨

### 📦 세션스토리지 (SessionStorage)

- 브라우저 탭(세션) 단위 저장소
- 탭 닫으면 데이터 삭제됨
- 자동으로 서버에 전송되지 않음 (JS로 직접 꺼내서 써야 함)
- 용량은 쿠키보다 큼 (5MB 정도)
- 주로 **임시 상태 데이터** 저장 용도로 사용

### 💾 로컬스토리지 (LocalStorage)

- 브라우저에 **영구 저장**되는 저장소 (명시적으로 지우거나 캐시/스토리지 삭제 전까지 유지)
- 자동으로 서버에 전송되지 않음
- 용량도 큼 (5MB 이상, 브라우저마다 다름)
- 주로 **로그인 상태 유지, 사용자 환경 설정 저장** 등에 사용됨

### 🔑 JWT (JSON Web Token)

- JSON 기반 인증 토큰 (Header.Payload.Signature)
- 서버에서 서명(Signature)하여 위변조 방지
- 자체적으로 유저 정보(claims)와 만료 시간(exp)을 포함 가능
- **Stateless 인증** 가능 → 서버가 세션을 따로 안 들고, 토큰 자체가 인증 근거

| 구분 | 쿠키 (Cookie) | 세션스토리지 (SessionStorage) | 로컬스토리지 (LocalStorage) | JWT (Token) |
| --- | --- | --- | --- | --- |
| 용량 | ~4KB | ~5MB | ~5MB+ | 수백~수천 바이트 |
| 수명 | 만료일 or 브라우저 종료 시 삭제 | 탭 종료 시 삭제 | 영구 저장(삭제 전까지) | `exp` 필드에 따라 달라짐 |
| 서버 자동 전송 | ✅ O | ❌ X | ❌ X | 저장소 방식에 따라 달라짐 |
| 보안 옵션 | HttpOnly, Secure, SameSite | 없음 | 없음 | 서명(Signature) 내장 |
| 보안 취약점 | CSRF 가능성 | XSS에 취약 | XSS에 취약 | 저장 위치에 따라 달라짐 |
| 인증 활용 | 세션 ID / JWT 저장 | JWT 저장 (임시 인증) | JWT 저장 (자동 로그인 등) | 인증 자체를 표현 |

# 쿠키

쿠키(Cookie)는 **브라우저가 관리하는 작은 데이터 조각**이에요.

어디 저장되는지는 **쿠키 종류(세션 쿠키 / 영속 쿠키)**와 **브라우저 동작 방식**에 따라 달라집니다.

---

## 1. 세션 쿠키 (Session Cookie)

- **저장 위치**: 브라우저 메모리 (RAM)
- 브라우저(탭/창)를 닫으면 쿠키가 삭제됨
- `Expires`나 `Max-Age` 속성이 없는 경우 기본적으로 세션 쿠키

---

## 2. 영속 쿠키 (Persistent Cookie)

- **저장 위치**: 브라우저의 **쿠키 저장소 (파일 DB)**
- 브라우저를 껐다 켜도 유지됨
- `Expires` 또는 `Max-Age` 속성이 설정된 경우 해당 시간까지 저장

브라우저별 저장 위치 예시:

- **Chrome/Edge (Chromium 기반)**:
    - OS 사용자 디렉터리에 있는 SQLite DB 파일 (`Cookies` 파일)
    - 예: `~/.config/google-chrome/Default/Cookies`
- **Firefox**:
    - `cookies.sqlite` 파일에 저장
- **Safari**:
    - macOS의 WebKit 기반 DB (`Cookies.binarycookies`)

---

## 3. 보안 옵션과 저장

쿠키는 저장 방식보다 **옵션 설정**이 보안에 더 큰 영향을 줍니다.

- `HttpOnly`: JS `document.cookie`로 접근 불가 (XSS 방어)
- `Secure`: HTTPS 연결에서만 전송
- `SameSite`: CSRF 방어 (`Strict`, `Lax`, `None`)

사용자가 쿠키를 "취득"하는 건 **브라우저가 서버 응답의 `Set-Cookie`를 받은 순간**입니다

## CSRF란 무엇인가?

사용자가 **로그인해 인증이 붙은 상태**를 악용해, **다른 사이트**에서 피해자 브라우저로 하여금 **의도치 않은 요청**(송금, 비밀번호 변경 등)을 **자동으로 보내게 하는 공격**입니다.

핵심은 **쿠키/HTTP 인증 같은 “자동 첨부 자격증명”**이 브라우저에 의해 같이 전송된다는 점이에요.

필요 시 **JSON+커스텀 헤더**로 CORS 프리플라이트 유도