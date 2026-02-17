---
title: 라우터
tags: []
created: ""
updated: ""
source: ""
status: draft
---
# 라우터 설계 메모

- 리소스형 Path: `/users/123/posts/456`
- 필터/검색/정렬은 쿼리스트링: `/posts?search=hello&page=1&sort=newest`
- 중첩 경로는 의미 단위로만 사용, 파라미터는 `:id` 형태로 명확히

## 체크리스트
- [ ] Path는 리소스/액션을 드러내는 단어로 구성
- [ ] 검색/필터/정렬은 쿼리스트링으로 표현
- [ ] 시간/정렬 파라미터는 ISO, enum 등 표준화
