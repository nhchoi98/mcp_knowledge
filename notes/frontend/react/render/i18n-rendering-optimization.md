---
title: 다국어 관련 렌더링 최적화
tags: []
created: ""
updated: ""
source: ""
status: draft
---
# 다국어 관련 렌더링 최적화

`react-i18next`를 사용하면서 CSR 방식을 유지하되, 하이브리드(서버의 효율성 + 클라이언트의 타입 안정성)로 가는 핵심은 **"전체 언어팩을 한 번에 다 받지 않고, 필요한 언어/네임스페이스만 Lazy Loading(지연 로딩)하는 것"**입니다.

운영툴에서 CSR의 장점을 살리면서 성능까지 챙기는 구현 전략을 정리해 드릴게요.

---

### 1. 전략: 네임스페이스(Namespace) 기반 코드 분할

모든 번역을 `resources` 객체에 넣으면 번들 크기가 커집니다. 이를 방지하기 위해 **언어별, 기능별로 파일을 쪼개고** 필요할 때만 호출합니다.

### (1) 타입 정의 (방식 2의 장점 활용)

타입 안정성을 위해 `i18next.d.ts` 파일을 만들어 전체 구조를 정의합니다. 이렇게 하면 개발 환경에서 자동 완성이 지원됩니다.

TypeScript

`// @types/i18next.d.ts
import 'i18next';
import common from '../public/locales/ko/common.json';
import admin from '../public/locales/ko/admin.json';

declare module 'i18next' {
  interface CustomTypeOptions {
    defaultNS: 'common';
    resources: {
      common: typeof common;
      admin: typeof admin;
    };
  }
}`

### (2) Backend 플러그인을 통한 Lazy Loading

`i18next-http-backend`를 사용하면 클라이언트가 현재 필요한 언어와 페이지(네임스페이스)의 JSON만 서버(또는 CDN)에서 동적으로 가져옵니다.

TypeScript

`import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import HttpApi from 'i18next-http-backend';

i18n
  .use(HttpApi) // JSON 파일을 동적으로 로드
  .use(initReactI18next)
  .init({
    fallbackLng: 'ko',
    ns: ['common', 'auth'], // 기본적으로 필요한 네임스페이스
    defaultNS: 'common',
    backend: {
      loadPath: '/locales/{{lng}}/{{ns}}.json', // public 폴더의 경로
    },
    interpolation: { escapeValue: false }
  });`

---

### 2. 컴포넌트 수준에서의 하이브리드 최적화

특정 메뉴(예: Admin 설정)에 진입할 때만 해당 번역 파일을 로드하도록 설정합니다.

TypeScript

`import { useTranslation } from 'react-i18next';

export function AdminPanel() {
  // 'admin' 네임스페이스가 로드될 때까지 Suspense가 동작하거나 
  // 내부적으로 로딩을 기다린 후 렌더링합니다.
  const { t } = useTranslation('admin');

  return <h1>{t('admin:setting_title')}</h1>;
}`

---

### 3. 왜 이 방식이 운영툴에 좋은가? (면접 답변 포인트)

1. **초기 번들 크기 감소:** 사용자가 한국어 운영툴에 접속하면 영어/중국어 파일은 아예 다운로드하지 않습니다. 또한, '메인 화면'에 있을 때는 '어드민 설정' 관련 번역 파일도 받지 않습니다.
2. **타입 안정성 유지:** `d.ts` 설정을 통해 개발 시에는 `t('common:invalid_key')` 같은 실수를 컴파일 단계에서 잡아낼 수 있습니다. (방식 2의 장점)
3. **CSR의 사용자 경험:** 페이지 이동 시 필요한 번역 파일만 가볍게 fetch하므로, 전체 페이지를 새로고침하는 SSR보다 전환이 부드럽습니다.

---

### 4. 면접 대비: "왜 굳이 이렇게 복잡하게 구현했나?"

> 답변 가이드:
"기존의 정적 매핑 방식은 개발이 편하지만, 서비스 규모가 커질수록 모든 다국어 리소스가 초기 번들에 포함되어 Lighthouse 성능 점수와 초기 로딩 속도를 저하시키는 문제가 있었습니다.
이를 해결하기 위해 i18next-http-backend를 도입하여 **네임스페이스 단위로 번역 리소스를 분할(Code Splitting)**했습니다. 덕분에 CSR의 매끄러운 UX를 유지하면서도, 사용자가 실제 사용하는 언어와 메뉴의 데이터만 전송받는 효율적인 구조를 구축했습니다."
> 

---

**추가 팁:** 만약 운영툴의 속도를 더 극단적으로 올리고 싶다면, Nginx 설정에 `.json` 파일에 대한 `gzip` 압축과 `Cache-Control`을 강하게 걸어두는 것을 추천합니다.

이 구현 방식 중에서 코드 구조를 더 자세히 보고 싶은 부분이 있으신가요?

### 면접용 답변 정리

> "캐시 컨트롤을 길게 잡으면 리소스 업데이트가 즉시 반영되지 않는 문제가 생길 수 있습니다. 이를 방지하기 위해 저희는 두 가지 전략을 병행합니다.
> 
> 
> 첫째, Nginx 설정에서 JSON 리소스에 대해 `no-cache`와 `must-revalidate`를 설정하여 브라우저가 항상 서버에 변경 여부를 확인하게 합니다.
> 둘째, 앱 배포 시마다 **쿼리 스트링으로 버전(v=1.0.x)**을 관리하여, 앱 업데이트가 일어날 때 강제로 새로운 번역 파일을 로드하도록 설계했습니다. 이를 통해 성능(캐시 활용)과 정합성(최신 데이터 반영)을 동시에 잡았습니다."
>