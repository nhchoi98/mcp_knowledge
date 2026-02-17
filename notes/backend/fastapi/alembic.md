---
title: Alembic
tags: []
created: ""
updated: ""
source: ""
status: draft
---
# Alembic

# DB 처음 연결할 때

alembic stamp head

# 모델과 DB를 비교해서 migration 자동 생성

alembic revision --autogenerate -m "Detect changes from current DB state"

# Migration 적용

alembic upgrade head