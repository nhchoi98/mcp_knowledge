---
title: 보안
tags: []
created: ""
updated: ""
source: ""
status: draft
---
# 보안

# XSS

과거에는 자바스크립트에서 `innerHTML` 같은 속성을 사용해 데이터를 화면에 바로 넣었습니다. 이때 악의적인 사용자가 `<script>공격코드</script>`를 삽입하면 그대로 실행되어 버리는 **XSS 공격**에 노출될 위험이 컸습니다.

# CSRF

# CSP

**CSP(Content-Security-Policy)** 설정에 `require-trusted-types-for 'script'` 지표가 빠져 있기 때문입니다.
A strong Content Security Policy (CSP) significantly reduces the risk of cross-site scripting (XSS) attacks. 

The Cross-Origin-Opener-Policy (COOP) can be used to isolate the top-level window from other documents such as pop-ups.

The `X-Frame-Options` (XFO) header or the `frame-ancestors` directive in the `Content-Security-Policy` (CSP) header control where a page can be embedded. These can mitigate clickjacking attacks by blocking some or all sites from embedding the page.

Deployment of the HSTS header significantly reduces the risk of downgrading HTTP connections and eavesdropping attacks. A rollout in stages, starting with a low max-age is recommended.