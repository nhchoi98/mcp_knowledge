---
title: 데이터 전송
tags: []
created: ""
updated: ""
source: ""
status: draft
---
# 데이터 전송 (HTML 폼 & Fetch)

## 전송 방식
- `application/x-www-form-urlencoded`: 기본 폼(텍스트/소규모 데이터)
- `multipart/form-data`: 파일 업로드, 텍스트+바이너리 혼합
- `application/json`: API 호출 시 Fetch로 사용

## FormData/Multipart 핵심
- boundary는 브라우저가 자동 생성
- 각 파트는 개별 `Content-Type` 가질 수 있음
- 파일 입력은 `<input type="file" multiple>` + `formData.append('file', file)`

```js
const fd = new FormData();
fd.append('username', 'hong');
fd.append('avatar', fileInput.files[0]);
await fetch('/upload', { method: 'POST', body: fd });
```

## 모범 사례
- 파일 업로드는 `multipart/form-data`, JSON API는 `application/json`
- CSRF 고려: 쿠키 인증 시 토큰/헤더 포함
- 대용량 업로드: 파일 크기 제한, 진행 상태/취소(AbortController) 제공
- 민감 정보는 GET 쿼리스트링에 넣지 않기
