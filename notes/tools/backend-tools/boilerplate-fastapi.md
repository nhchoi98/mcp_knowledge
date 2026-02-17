---
title: FastAPI
tags: []
created: ""
updated: ""
source: ""
status: draft
---
# FastAPI

# 하이어라키 구조

```jsx
app/
  main.py
  core/
    config.py          # 환경 변수/세팅
    security.py        # 인증/인가 공통 로직
    exceptions.py      # 커스텀 예외, 에러 핸들링
  db/
    session.py         # create_engine, SessionLocal, get_session()
    init.py            # startup 시 테이블 생성 등
  models/
    user.py
    post.py
    __init__.py
  schemas/
    user.py
    post.py
    __init__.py
  repositories/
    user_repository.py # DB 접근(SELECT/INSERT/UPDATE/DELETE)
    post_repository.py
    __init__.py
  services/
    user_service.py    # 비즈니스 규칙 / 유즈케이스
    post_service.py
    __init__.py
  routers/
    user_router.py     # HTTP 레이어(요청 파싱, response_model)
    post_router.py
    __init__.py
```

- **router**
    - FastAPI 엔드포인트 (`@router.get`, `@router.post`, …)
    - 요청을 받고, 스키마로 validate하고, 적절한 service로 호출만 함
    - HTTP status / response_model 같은 HTTP concern 담당
- **service**
    - 비즈니스 로직 / 유즈케이스
    - “이 사용자를 생성할 때 닉네임 중복 체크하고, 초기 포인트 지급하고, 이벤트 로그 남겨라” 같은 규칙
    - 트랜잭션 commit/rollback 책임을 여기서 지는 경우가 많다
- **repository**
    - DB 접근만 담당.
    - `session.exec(select(User).where(...))` 이런 것들
    - 서비스 레이어가 DB를 직접 만지는 대신 repository 함수를 부른다 → 나중에 DB 변경/캐시 추가하기 쉬움
- **models**
    - 실제 DB 테이블과 매핑되는 ORM 클래스(SQLModel or SQLAlchemy)
- **schemas**
    - 요청/응답에 쓰는 Pydantic/SQLModel 모델 (create/update/read 등)