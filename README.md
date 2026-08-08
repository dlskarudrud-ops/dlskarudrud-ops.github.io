# 이남경 · 시스템 / 전투 기획 포트폴리오

정적 HTML / CSS / JavaScript 웹 포트폴리오입니다. 빌드 도구 없이 파일을 그대로
올리면 동작하며, GitHub Pages에 바로 배포할 수 있습니다.

## 구조

```
web/
├── index.html                  홈 (프로필 · 역량 · 경력 · 프로젝트 · 문서 · 연락)
├── resume.html                 이력서
│
├── projects/
│   ├── fire-vow.html           FireVow: DarkFantasy 상세
│   └── project-ts.html         Project-TS 시스템 & 전투 설계 상세
│
├── documents/
│   ├── career.html             경력 기술서
│   └── postmortem.html         포스트모템
│
├── assets/
│   ├── css/
│   │   ├── tokens.css          색 · 타이포 · 여백 · 모션 토큰 (테마 정의 포함)
│   │   ├── global.css          리셋 · 레이아웃 · 공통 컴포넌트
│   │   ├── home.css            홈 전용 레이아웃
│   │   ├── project.css         상세 · 문서 페이지 레이아웃
│   │   └── print.css           인쇄 전용 스타일
│   │
│   ├── js/
│   │   ├── theme.js            다크 / 화이트 테마 전환과 저장
│   │   ├── main.js             내비게이션 · 섹션 추적 · PDF 링크 · 인쇄
│   │   ├── motion.js           스크롤 등장 효과
│   │   ├── lightbox.js         이미지 확대 보기
│   │   └── webgl/              홈 히어로 배경 (scene · materials · shaders)
│   │
│   ├── images/                 원본 PDF에서 추출한 실제 스크린샷 · 아트
│   └── icons/                  파비콘
│
└── pdf/
    ├── dark/                   다크 모드 PDF 5종
    └── light/                  화이트 모드 PDF 5종
```

## 문서 연결 방식

각 PDF는 웹 페이지와 원본 두 갈래로 제공합니다.

| 문서 | 웹 버전 | 원본 PDF |
| --- | --- | --- |
| 이력서 | `resume.html` | `pdf/{테마}/resume.pdf` |
| 경력 기술서 | `documents/career.html` | `pdf/{테마}/career.pdf` |
| Project-TS | `projects/project-ts.html` | `pdf/{테마}/project-ts.pdf` |
| Fire Vow | `projects/fire-vow.html` | `pdf/{테마}/fire-vow.pdf` |
| 포스트모템 | `documents/postmortem.html` | `pdf/{테마}/postmortem.pdf` |

`data-pdf-variant`가 붙은 링크는 현재 테마에 맞춰 `pdf/dark/` ↔ `pdf/light/`
경로를 바꿉니다. JavaScript가 없으면 다크 버전이 그대로 열립니다.

## 디자인 규칙

**폰트 크기는 다섯 단계만 사용합니다.** 그 외의 차이는 굵기 · 색 · 자간 · 대소문자로
표현하고, 새로운 크기를 만들지 않습니다.

| 단계 | 토큰 | 쓰임 |
| --- | --- | --- |
| 타이틀 | `--fs-title` | 이름, 페이지 제목 |
| 제목 | `--fs-heading` | 섹션 제목, 큰 수치 |
| 소제목 | `--fs-sub` | 카드 제목, 리드 문장 |
| 설명 | `--fs-body` | 본문, 설명 |
| 태그 | `--fs-tag` | 태그, 라벨, 캡션 |

테마는 같은 토큰 이름에 다른 값을 주는 방식으로만 구현합니다. 스타일시트를 테마별로
복제하지 않습니다.

## 로컬에서 확인하기

```bash
python -m http.server 8000
```

브라우저에서 `http://localhost:8000` 을 엽니다. `file://` 로 직접 열면 히어로 배경
(ES 모듈)이 동작하지 않습니다. 이 경우에도 CSS 폴백 배경이 대신 표시되므로 나머지
화면은 정상입니다.

## GitHub Pages 배포

이 `web/` 폴더의 내용을 저장소 루트에 올린 뒤 Settings → Pages에서 브랜치를
지정합니다. 별도의 빌드 단계는 없습니다.

## 외부 의존성

- **Pretendard** (jsDelivr) — 한글 본문 서체. 로드에 실패하면 시스템 서체로 대체됩니다.
- **three.js 0.169.0** (jsDelivr) — 홈 히어로 배경에만 사용합니다. 로드에 실패하거나
  WebGL을 쓸 수 없으면 CSS 배경이 그대로 남고 다른 동작에는 영향이 없습니다.

두 의존성 모두 버전을 고정했고, 없어도 페이지 내용과 이동은 모두 동작합니다.
