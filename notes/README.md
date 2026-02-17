---
title: Knowledge Base
tags: []
created: ""
updated: ""
source: ""
status: draft
---
# Knowledge Base

정리된 개발 지식 아카이브입니다. 아래 상위 카테고리로 문서를 구조화합니다.

- `frontend/` : 프론트엔드 언어, 브라우저, 렌더링, 프레임워크, 상태관리, 테스팅 등
- `backend/` : 서버, 데이터 처리, 데이터베이스, 네트워크, 인프라 등
- `cs-basics/` : 자료구조, 운영체제, 컴퓨터구조, 네트워크, 보안, 언어 기초 등
- `process/` : 개발 방법론, 브랜치 전략 등 프로세스 관련
- `tools/` : 개발 생산성 도구, 빌드/번들러, 모노레포, IDE 등
- `glossary/` : 용어 정리

## 작성 원칙

- 모든 문서는 Frontmatter를 포함합니다:
  - `title`: 문서 제목
  - `tags`: 관련 키워드 배열
  - `created`: 최초 작성일 (ISO8601)
  - `updated`: 최근 수정일 (ISO8601)
  - `source`: 참고 링크 또는 출처
  - `status`: draft | wip | published
- 파일명 규칙: `topic-detail.md` 형태로 의미 있는 영문/한글 슬러그 사용
- 내부 링크는 상대경로를 사용합니다.

## 상위 카테고리 README

- [frontend/](frontend/README.md): 브라우저/HTML/CSS, 렌더링, React/Next.js/Vue, 상태관리, 테스트, 웹 기초
- [backend/](backend/README.md): FastAPI, 데이터 처리/캐싱, DB, 네트워크, 인프라
- [cs-basics/](cs-basics/README.md): 자료구조, OS, 컴퓨터구조, 네트워크, 보안, 언어 기초, 코딩연습
- [process/](process/README.md): 개발 방법론, 브랜치 전략
- [tools/](tools/README.md): 번들러/모노레포/보일러플레이트, IDE 등
- [glossary/](glossary/README.md): 용어 정리

## 도구

- Markdown lint: `.markdownlint.json`
- 링크 검사 설정: `.markdown-link-check.json` (markdown-link-check 사용 시)
