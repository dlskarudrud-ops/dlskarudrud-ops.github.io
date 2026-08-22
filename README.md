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
│   ├── fire-vow.html           Fire Vow: Dark Fantasy 상세
│   └── project-taimanin-squad.html  Project_Taimanin Squad 시스템 & 전투 설계 상세
│
├── documents/
│   ├── career.html             경력 기술서
│   ├── postmortem.html         포스트모템
│   ├── combat-module-table.html      전투 모듈 테이블
│   ├── combat-presentation.html 캐릭터 연출
│   ├── turn-limit-damage-measure.html   턴 제한 피해 측정 콘텐츠
│   ├── tower.html              타워
│   └── tower-ui.html           타워 UI
│
├── assets/
│   ├── css/
│   │   ├── tokens.css          색 · 타이포 · 여백 · 모션 토큰 (테마 정의 포함)
│   │   ├── global.css          리셋 · 레이아웃 · 공통 컴포넌트
│   │   ├── home.css            홈 전용 레이아웃
│   │   ├── project.css         상세 · 문서 페이지 레이아웃
│   │   ├── wiki.css            실무 포트폴리오 · 타워 UI 보조 스타일
│   │   ├── combat-presentation.css 캐릭터 연출 16:9 레이아웃
│   │   └── print.css           인쇄 전용 스타일
│   │
│   ├── js/
│   │   ├── theme.js            다크 / 화이트 테마 전환과 저장
│   │   ├── main.js             내비게이션 · 섹션 추적 · PDF 링크 · 인쇄
│   │   ├── motion.js           스크롤 등장 효과
│   │   ├── lightbox.js         이미지 확대 보기
│   │   └── webgl/              전역 광원 · 홈/상세 히어로 (ambient · page · scene · materials · shaders)
│   │
│   ├── images/                 문서용 스크린샷 · 아트
│   └── icons/                  파비콘
│
├── pdf/
│   ├── dark/                   다크 모드 PDF
│   └── light/                  화이트 모드 PDF
│
└── pptx/                       캐릭터 연출 편집본
```

## 문서 연결 방식

각 PDF는 웹 페이지와 원본 두 갈래로 제공합니다.

| 문서 | 웹 버전 | 원본 PDF |
| --- | --- | --- |
| 이력서 | `resume.html` | `pdf/{테마}/resume.pdf` |
| 경력 기술서 | `documents/career.html` | `pdf/{테마}/career.pdf` |
| Project_Taimanin Squad | `projects/project-taimanin-squad.html` | `pdf/{테마}/project-taimanin-squad.pdf` |
| Fire Vow | `projects/fire-vow.html` | `pdf/{테마}/fire-vow.pdf` |
| 포스트모템 | `documents/postmortem.html` | `pdf/{테마}/postmortem.pdf` |
| 전투 모듈 테이블 | `documents/combat-module-table.html` | `pdf/{테마}/combat-module-table.pdf` |
| 캐릭터 연출 | `documents/combat-presentation.html` | `pdf/{테마}/combat-presentation.pdf` · `pptx/combat-presentation.pptx` |
| 턴 제한 피해 측정 콘텐츠 | `documents/turn-limit-damage-measure.html` | `pdf/{테마}/turn-limit-damage-measure.pdf` |
| 타워 | `documents/tower.html` | `pdf/{테마}/tower.pdf` |
| 타워 UI | `documents/tower-ui.html` | `pdf/{테마}/tower-ui.pdf` |

`data-pdf-variant`가 붙은 링크는 현재 테마에 맞춰 `pdf/dark/` ↔ `pdf/light/`
경로를 바꿉니다. JavaScript가 없으면 다크 버전이 그대로 열립니다.

위 다섯 문서의 PDF도 기존 포트폴리오와 같은 16:9 형식으로 다크·화이트 두 판을 제공합니다.

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

## 캐시

CSS · JS 링크에는 `?v=15` 같은 버전이 붙어 있습니다. GitHub Pages가 파일을 10분간
캐시하기 때문에, 이게 없으면 수정해도 옛날 화면이 그대로 보입니다.

**디자인을 고친 뒤 사이트가 안 바뀌면 이 숫자를 올리세요.** 여섯 개 HTML 파일과
중첩 WebGL 모듈 import의 `?v=15`를 함께 올립니다. 내용만 고쳤다면 건드릴 필요 없습니다.

## 로컬에서 확인하기

```bash
python -m http.server 8000
```

브라우저에서 `http://localhost:8000`을 엽니다. `file://`로 직접 열면 히어로 배경
(ES 모듈)이 동작하지 않습니다. 이 경우에도 CSS 폴백 배경이 대신 표시되므로 나머지
화면은 정상입니다.

## GitHub Pages 배포

이 `web/` 폴더의 내용을 저장소 루트에 올린 뒤 Settings → Pages에서 브랜치를
지정합니다. 별도의 빌드 단계는 없습니다.

## 외부 의존성

- **Pretendard** (jsDelivr) — 한글 본문 서체. 로드에 실패하면 시스템 서체로 대체됩니다.
- **three.js 0.169.0** (jsDelivr) — 전 페이지 고정 광원과 홈/상세 히어로에 사용합니다.
  로드에 실패하거나 데이터 절약 모드·WebGL 미지원 환경이면 CSS 그라데이션이 그대로
  남고 다른 동작에는 영향이 없습니다.

두 의존성 모두 버전을 고정했고, 없어도 페이지 내용과 이동은 모두 동작합니다.

## WebGL 연출

- 모든 페이지: 고정된 저해상도 GLSL 광원 필드가 문서 끝까지 이어집니다.
- 홈: 굴절 · 프레넬 · 카우스틱을 적용한 대형 광학 시트를 추가합니다.
- 이력서 · 문서 · 프로젝트: 읽기를 방해하지 않는 저강도 광학 리본을 히어로에만 둡니다.
- 다크 모드: 흑연 배경 위 골드 발광과 낮은 청색 분산을 사용합니다.
- 화이트 모드: 흰 배경과 골드 타이포를 유지하고 청색 굴절 그림자를 주조색으로 씁니다.
- `prefers-reduced-motion`에서는 정지 프레임만 렌더하고, 탭이 숨겨지면 렌더링을 멈춥니다.
