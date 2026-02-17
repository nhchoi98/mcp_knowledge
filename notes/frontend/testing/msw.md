---
title: MSW(Mock service worker)
tags: []
created: ""
updated: ""
source: ""
status: draft
---
# MSW(Mock service worker)

# 핵심키워드

서비스워커, 

# 참고

1. [https://v1.mswjs.io/docs/](https://v1.mswjs.io/docs/)  (공식문서)

---
## Merged from 개발 관련 지식/React/MSW (Mock service worker) 29acee38e89a80cab35dced61ff88232.md

# MSW (Mock service worker)

# 개요

# 초기 폴더 구성

- handler.ts
- browser.ts
- db.ts
- server.ts

## Browser.ts

`*import* { setupWorker } *from* 'msw/browser';`

`*import* { handlers } *from* './handlers/index';`

`*export* const *worker* = *setupWorker*(...*handlers*);`

## Db.ts

`*export* const *db* = **{`

`};`