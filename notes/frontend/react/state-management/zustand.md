---
title: Zustand
tags: []
created: ""
updated: ""
source: ""
status: draft
---
# Zustand

## Zustand는 언제 쓰는 게 좋냐?

지금 상황 기준으로 정리하면:

- **서버에서 받아오는 데이터 (목록, 상세, 페이징된 페이지들 등)**
→ **React Query**가 최적 (캐시, 중복 요청 방지, refetch, 에러 상태, 로딩 상태 등 내장)
- **UI 전용 상태 (모달 열림/닫힘, 선택된 탭, 정렬 옵션, 임시 로컬 폼 값 등)**
→ 이런 건 Zustand로 관리하면 편