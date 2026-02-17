---
title: 특수 페이지들
tags: []
created: ""
updated: ""
source: ""
status: draft
---
# 특수 페이지들

_error.tsx, 404.tsx, 500.tsx, _document.tsx

`app/layout.tsx`가 `_app.tsx`와 `_document.tsx` 역할을 **대체**하고, `<head>`는 **Metadata API**로 관리합니다. 폰트는 `next/font`를 쓰는 게 권장입니다.

# 페이지 이동시 …

<a> 대신 <Link>

window.location.push 대신, router.push