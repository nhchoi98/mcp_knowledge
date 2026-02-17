---
title: CSR
tags: []
created: ""
updated: ""
source: ""
status: draft
---
# CSR

## TTI (Time To Interactive)

## FID (First Input Delay)

## Preferch, Preload

|  | 번들 필요한 시점 | 부모 청크와의 관계 | 다운로드 시점 |
| --- | --- | --- | --- |
| **prefetch** | 미래의 언젠가 | 부모 청크가 다 로딩된 이후에 로딩 시작 | 브라우저가 idle 상태일 때 |
| **preload** | 현재 위치 | 부모 청크와 병렬로 불러와짐 | 요청 즉시 |

# Cache

# 정적 컨텐츠 서빙

## gzip

## Cache

### Cache control

### Max-age

### CDN

### Vite 와 연관성?

# Code chunk 분리와 CSR?

manual chunk 하면 이점이 생기나? 
chunk가 처음 리소스 로딩할떄 영향을 줘서 그런가.

# Reference

[https://velog.io/@devohda/리소스-로딩-최적화-prefetch-와-preload](https://velog.io/@devohda/%EB%A6%AC%EC%86%8C%EC%8A%A4-%EB%A1%9C%EB%94%A9-%EC%B5%9C%EC%A0%81%ED%99%94-prefetch-%EC%99%80-preload)