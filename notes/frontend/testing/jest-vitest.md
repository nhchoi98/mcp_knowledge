---
title: Jest, Vitest
tags: []
created: ""
updated: ""
source: ""
status: draft
---
# Jest, Vitest

## Matcher (매처)

테스트에서 값을 검증할 때 사용하는 함수들입니다. `expect()` 뒤에 붙여서 사용합니다.

**자주 쓰는 matcher들:**

- `toBe()`: 정확히 같은지 (===)
- `toEqual()`: 값이 같은지 (객체/배열 내용 비교)
- `toBeTruthy()` / `toBeFalsy()`: 참/거짓 여부
- `toContain()`: 배열/문자열에 포함되는지
- `toBeInTheDocument()`: DOM에 존재하는지 (jest-dom)

## Test Suite (테스트 스위트)

`describe()` 블록으로 만드는 테스트들의 그룹입니다. 관련된 테스트들을 묶어서 정리합니다.

## Test Case (테스트 케이스)

개별 테스트 하나를 의미합니다. `test()` 또는 `it()` 함수로 작성합니다.

## Setup / Teardown (설정 / 정리)

테스트 실행 전후에 필요한 준비 작업이나 정리 작업을 하는 함수들입니다.

## Mock (모킹)

실제 함수나 모듈을 가짜로 대체하는 것입니다.

## Spy (스파이)

실제 함수를 그대로 실행하되, 호출 여부나 인자를 감시합니다.

## Assertion (단언/검증)

"이 값은 이래야 한다"고 선언하는 것입니다. `expect()`로 시작하는 전체 구문을 의미합니다.

## Helper / Utility (헬퍼/유틸리티)

테스트 작성을 돕는 보조 함수들입니다.

## Vi란?

- `vi.fn()`: 함수 호출 추적
- `vi.mock()`: 모듈 전체 교체
- `vi.spyOn()`: 원본 유지하며 감시
- `mockReturnValue()`: 반환값 설정
- `mockResolvedValue()`: Promise 성공 케이스
- `mockRejectedValue()`: Promise 실패 케이스
- `vi.clearAllMocks()`: 호출 기록 초기화

## JSDOM