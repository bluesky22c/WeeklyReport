# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

> ⚠️ **AGENTS.md는 이 파일의 구버전입니다.** 유찬/황지환 추가 및 결재-회람함 수집 흐름이 반영되지 않아 outdated 상태입니다. 이 CLAUDE.md가 유일한 최신 기준입니다.

---

# 주간업무보고 자동 수집·저장 규칙

## 개요
KT Biz 그룹웨어(gwp.ktbizoffice.com)의 **결재-미결함 또는 결재-완료함**에서 주간업무보고를 추출해
담당자별 폴더에 날짜별 HTML 파일로 저장하는 자동화 절차.
- 수집 원본은 그룹웨어 결재 문서이며, 로컬 DOCX 파일을 원본으로 사용하지 않는다.
- 유찬, 황지환도 결재-미결함 또는 결재-완료함에 해당 주간업무보고가 있으면 해당 그룹웨어 문서를 우선 수집한다.
- 저장 파일은 `#message` iframe 안의 실제 업무 테이블을 셀 단위로 추출해 만든다.

---

## 0. 반복 작업 트리거 — 금주 주간업무보고 작성

사용자가 Claude Code에게 아래 문구 또는 유사 표현으로 요청하면, 단순 HTML 저장이 아니라 **팀원별 HTML 저장 → index.html 갱신 → 금주 통합 DOCX 작성**까지 전체 절차를 한 번에 수행한다.

트리거 문구:
- `금주주간업무보고 작성`
- `금주 주간업무보고 작성`
- `금주 주간 업무 보고 작성해줘`
- `이번주 주간업무보고 작성해줘`
- `이번주 주간 업무 보고 작성해줘`

실행 범위:
1. `D:\Temp\주간업무정리` 기준으로 그룹웨어 `결재-미결함`과 `결재-완료함`을 모두 확인한다.
2. 대상 팀원 주간업무보고를 수집해 각 팀원 폴더에 `YYYY-MM-DD.html`로 저장한다.
3. `#message` iframe 안의 실제 업무 테이블만 추출하고, 결재/작성자/문서분류/참조 같은 그룹웨어 폼 헤더는 저장하지 않는다.
4. 특정 팀원 문서가 `미결함`과 `완료함` 모두에 없을 때만 누락으로 기록한다. 로컬 DOCX나 통합 보고서에서 임의 생성하지 않는다.
5. 저장 후 `D:\Temp\주간업무정리\build_index.py`를 실행해 `index.html`을 갱신한다.
6. 전주 통합 DOCX 형식을 참고해 해당 주 `[보고_제어1팀]주간업무보고(YYMMDD).docx`를 생성한다.
7. 통합 DOCX 표 구조는 `프로젝트 / 금주 핵심 실적 / 담당자 / 내주 계획 / 목표일` 5열을 유지한다.
8. 통합 DOCX의 첫 타이틀 `주간업무 실적 및 계획 (제어1팀)`은 기존 형식을 유지하고, 나머지 작성일/작성자/표 헤더/표 본문/프로젝트 그룹 행 등 일반 텍스트는 8pt로 작성한다.
9. 완료 후 HTML 저장 인원, 누락 인원, 생성된 DOCX 파일, `index.html` 갱신 여부, 검증 결과를 요약한다.

검증 기준:
- 팀원별 `YYYY-MM-DD.html`에 `<p class="source">출처: ...</p>`가 있어야 한다.
- 저장 HTML에 그룹웨어 폼 헤더가 남아 있으면 `fix_all_headers.py`로 정리한 뒤 `index.html`을 다시 생성한다.
- DOCX는 `python-docx`로 로드 가능해야 하고, ZIP 구조 검사에서 오류가 없어야 한다.
- DOCX에 전주 날짜/파일명 흔적이 남아 있지 않아야 한다.
- DOCX에 금주/내주 기간과 주요 프로젝트명이 포함되어야 한다.
- DOCX의 타이틀 제외 일반 텍스트가 8pt인지 확인한다.

---

## 1. 저장 경로 및 구조

```
D:\Temp\주간업무정리\
├── 박주상\          ← 담당자별 폴더
│   ├── 2026-01-02.html
│   ├── 2026-01-09.html
│   └── ...
├── 주영모\
├── 김병걸\
├── 김현석\
├── 송유림\
├── 김성현\
├── 배유민\
├── 박장미\
├── 김도현\
├── 유찬\
├── 황지환\
├── index.html       ← 통합 뷰어 (편집 가능)
├── CLAUDE.md        ← 이 파일
└── file_server.py   ← (임시) 파일 저장용 로컬 서버
```

---

## 2. 대상 담당자 목록

```
박주상, 주영모, 김병걸, 김현석, 송유림, 김성현, 배유민, 박장미, 김도현, 유찬, 황지환
```

---

## 2-B. 팀원 경력 및 성과평가 반영 기준

주간업무보고를 기반으로 인사평가용 분기 성과를 판단할 때는 아래 경력 정보를 함께 반영한다.
경력은 단순 가산점이 아니라 각 연차에 맞는 기대 역할 수준을 보정하는 기준으로 사용한다.

| 팀원 | 경력 | 평가 시 기대 기준 |
|------|------|------------------|
| 박주상 | 20년 | 고난도 업무 주도, 리스크 사전 대응, 팀 내 기준 제시 |
| 김병걸 | 20년 | 안정적 수행, 문제 해결 주도, 후배 지원 |
| 주영모 | 15년 | 복잡한 업무 조율, 품질 관리, 개선 제안 |
| 김현석 | 14년 | 독립적 업무 수행, 주요 이슈 해결, 일정·품질 책임 |
| 송유림 | 8년 | 안정적 실무 수행, 반복 이슈 개선, 협업 기여 (2026-06-01 복직으로 평가 재개) |
| 김성현 | 5년 | 담당 업무 완결성, 성장성, 일정 준수 |
| 배유민 | 3년 | 담당 업무 완결성, 실무 숙련도, 문제 대응력 |
| 박장미 | 1년 | 업무 습득 속도, 기본기, 보고·공유 성실성 |
| 김도현 | 6개월 | 적응도, 학습 태도, 지시 업무 수행 정확도 |
| 유찬 | 5년 | 담당 기능 완결성, 이슈 대응, 고객사 커뮤니케이션 능력 |
| 황지환 | 1.5년 | 기본 업무 정확도, 셋업·현장 대응 성실성, 학습 속도 |

성과평가 해석 원칙:
- 20년 이상은 최고난도 기술 판단, 복합 리스크 대응, 팀 표준 제시 여부를 중점 평가한다.
- 15년 이상은 단순 처리량보다 복잡한 업무 조율, 품질 관리, 개선 제안, 팀 기여를 중점 평가한다.
- 8~10년차는 독립 수행 능력, 품질, 문제 해결력을 중심으로 평가한다.
- 3~5년차는 담당 업무 완성도, 일정 준수, 실무 숙련도, 독립 수행 가능성을 균형 있게 평가한다.
- 1년 이하 구성원은 절대 성과보다 학습 속도, 기본 업무 정확도, 보고 습관, 개선 정도를 반영한다.
- 같은 점수라도 연차별 기대치가 다르므로, 경력 대비 기대 수준 초과 여부를 함께 기록한다.
- 경력은 가산점으로 사용하지 않는다. 경력이 높을수록 더 어려운 업무, 더 큰 책임, 더 높은 주도성을 수행했는지 판단하는 기대수준 기준으로 사용한다.

경력별 기대 난이도 기준:

| 경력 구간 | 기대 보정 난이도 | 기대 역할 |
|----------|----------------:|-----------|
| 20년 이상 | 4.6 | 최고난도 기술/현장 이슈 주도, 설계 판단, 리스크 대응, 팀 표준 제시 |
| 15년 이상 | 4.3 | 복잡한 업무 조율, 품질 관리, 개선 제안, 팀 기여 |
| 10년 이상 | 4.3 | 주요 프로젝트 독립 수행, 문제 해결, 일정·품질 책임 |
| 8년 이상 | 4.0 | 안정적 실무 수행, 반복 이슈 개선, 협업 기여 |
| 5년 이상 | 3.8 | 담당 기능 완결, 이슈 대응, 실무 숙련도 향상 |
| 3년 이상 | 3.4 | 담당 업무 독립 수행, 일정 준수, 기본 문제 대응 |
| 1년 이상 | 2.8 | 기본 업무 정확도, 학습 속도, 보고·공유 성실성 |
| 1년 미만 | 2.5 | 적응도, 교육 이수, 지시 업무 수행 정확도 |

경력 기대 충족도:

```text
경력 기대 충족도 = 개인별 보정 평균 난이도 - 경력별 기대 보정 난이도
```

최종 점수 산정 기준:

```text
최종 점수 =
3.5
+ (경력 기대 충족도 × 0.8)
+ 성과/완료도 보정(-0.3 ~ +0.5)
+ 주도성/책임 보정(-0.3 ~ +0.5)
+ 협업/공유 보정(-0.2 ~ +0.3)
+ 프로젝트 폭 보정 = min((통합 프로젝트 수 - 1) × 0.05, 0.25)
+ 업무량 보정 = min(원문 업무 행 수 × 0.01, 0.35)
```

점수 해석:
- `경력 기대 충족도`가 양수이면 연차 대비 기대보다 어려운 업무를 수행한 것으로 본다.
- `경력 기대 충족도`가 음수이면 수행 업무 자체가 나쁘다는 의미가 아니라, 연차 대비 기대 난이도에는 미달한 것으로 본다.
- 고경력자는 낮은 난이도 반복 업무만 수행하면 점수가 자동으로 높아지지 않는다.
- 저연차자는 절대 난이도가 낮아도 기대 난이도를 초과하고 학습·완료도가 좋으면 긍정 평가한다.

---

## 2-C. 프로젝트별 난이도 가중치

주간업무보고 기반 개인별 성과 분석 시 아래 프로젝트별 난이도 점수를 반영한다.
프로젝트명 `TOE`와 `ToE`는 1차 설비와 2차 설비로 구분한다.
보고서 본문에 `1호기`, `1차`, `1차 설비`가 있으면 `TOE 1차 설비`로 분류하고, `2호기`, `2차`, `2차 설비`, `신규건`이 있으면 `TOE 2차 설비`로 분류한다.
설비 차수를 판단할 단서가 없으면 `TOE 미구분`으로 둔다.
금주실적 본문에 `SEC RAS`, `RAS`, `신뢰성 평가 설비` 또는 `신뢰성 설비 프로그램` 단서가 있으면 대표 프로젝트명 `신뢰성 평가 시스템`으로 분류한다.
금주실적 본문에 `RAS Vision Part` 또는 `RAS Vision 알고리즘 개발` 단서가 있으면 대표 프로젝트명 `Vision 알고리즘 개발`로 분류한다.
프로젝트명 `세미`는 `세미나`로 통합한다.
프로젝트 분류는 프로젝트 컬럼 값을 반영하지 않고, 금주실적 본문에 나온 세부 설비/시스템명을 기준으로 한다.
예: `Multi-Probing Tester`, `Wafer Passive SPL Test System`, `신뢰성 평가 시스템`, `신뢰성 평가 설비`처럼 본문에 명시된 세부명을 프로젝트로 사용한다.

| 프로젝트 | 난이도 | 판단 기준 |
|----------|-------:|-----------|
| SEC | 4.3 | 주요 고객/현장 대응, 설비 셋업, Vision, PG, Wafer, 프로토콜, Auto Run 등 복합 난이도 높음 |
| TOE 1차 설비 | 3.0 | 운영 프로그램, CIM, 셋업, 검수, 통신, TSP 검사 등 개발·현장 대응 복합 |
| TOE 2차 설비 | 4.5 | 운영 프로그램, CIM, 셋업, 검수, 통신, TSP 검사 등 개발·현장 대응 복합 |
| TOE 미구분 | 4.5 | TOE/ToE 보고 중 1차·2차 설비를 판단할 단서가 없는 경우 |
| WHTM | 4.3 | AGV/EIP 통신, ACAControlSystem, Recipe, Alarm, Motion 등 제어·통신 이슈 포함 |
| AR | 4.5 | 검사 알고리즘, AF, ND Filter, 이미지 촬상, 개조 대응 등 Vision/검사 난이도 있음 |
| LGD | 3.9 | 티칭, 셋업, 프로토콜 분석, UI 수정, 신규 모델 대응 등 실무 난이도 중상 |
| KOPTI | 3.8 | 현장 적용, 상태 확인, 인터락/정지 이슈 대응 등 문제 해결 성격 있음 |
| VISIONOX | 3.7 | ACAControlSystem 기능 대응, Channel 상태 표시 등 개발성 업무 포함 |
| ELP | 3.0 | WPF, 이미지 렌더링, Vision UI, 알고리즘 테스트 등 개발 난이도 중상 |
| CTP | 2.5 | 티칭, 점등검사, 셋업 대응 중심. 현장성은 있으나 범위는 상대적으로 제한적 |
| MTP | 2.5 | Cell Log, 패턴, 휘도계 좌표 등 기능 대응 중심 |
| RAS | 4.7 | `신뢰성 평가 시스템`으로 통합 인식해 계산 |
| SEC 4종설비 | 3.8 | Flicker Mes 기능 수정 등 SEC 계열이나 보고상 범위가 제한적 |
| SEC RAS | 4.7 | `신뢰성 평가 시스템`으로 통합 인식해 계산 |
| 세미나 | 1.0 | 발표/자료 정리/업무 보조 성격. 직접 개발·현장 성과보다 낮게 반영 |
| 교육 | 1.0 | 학습/역량 강화 활동. 신입·저연차에는 긍정 반영하되 프로젝트 성과 난이도는 낮음 |
| 세미 | 1.0 | 세미나로 통합 |
| ETC | 2.0 | 금주실적 본문만으로 구체 프로젝트 식별이 어려운 경우 적용 |

### 세부 프로젝트별 난이도 가중치

주간업무 본문에서 아래 세부 프로젝트명이 확인되면 상위 프로젝트보다 세부 프로젝트 가중치를 우선 적용한다.
비전 알고리즘 개발, 검사 알고리즘 개발, 픽셀 검사 알고리즘, 이미지 분석/매핑 알고리즘 등 핵심 Vision 알고리즘 개발성 업무는 기술적 난이도 최상위권으로 보고 4.7을 적용한다.

| 세부 프로젝트 | 난이도 | 판단 기준 |
|----------------|-------:|-----------|
| Vision 알고리즘 개발 | 4.7 | 비전 검사 알고리즘, 픽셀 검사, 이미지 분석, 매핑/Addressing, 불량 판정 로직 등 핵심 알고리즘 개발 |
| 검사 알고리즘 개발 | 4.7 | 검사 판정 조건, 불량 코드, 이미지 처리, 알고리즘 비교·검증 업무 |
| Multi-Probing Tester | 4.5 | EPI-SE1000, Wafer F/O Sample Run, Wafer Map, 운영 프로그램, 고객/기술부서 대응 |
| Wafer Passive SPL Test System | 2.0 | Multi-Probing Tester와 분리 계산. UI/시퀀스 일부 개발 중심으로 낮은 난이도 적용 |
| 신뢰성 평가 시스템 | 4.7 | 제어 프로그램, Auto Run, Inspection PC 통신, PG/Alarm/Status 프로토콜, 인터락, 셋업 |
| 신뢰성 평가 설비 | 4.7 | `신뢰성 평가 시스템`으로 통합 인식해 계산 |
| SEC 4종설비 1D/2D | 3.8 | Flicker, Image Rotate, 1D/2D 프로그램 기능 추가·수정 |
| RAS Vision Part | 4.7 | `Vision 알고리즘 개발`로 통합 인식해 계산 |
| RAS Vision 알고리즘 개발 | 4.7 | `Vision 알고리즘 개발`로 통합 인식해 계산 |
| TOE CIM | 3.5 | TOE 운영 프로그램과 분리해 계산 |
| TOE 운영 프로그램 | 4.5 | `TOE 2차 설비`로 통합 인식해 계산 |
| WHTM ACAControlSystem | 4.5 | G6 ACAControlSystem, Recipe, Lot Loading, Alarm, AGV/EIP 통신 |
| WHTM Loader/Unloader System | 4.3 | G4.5 Loader/Unloader, Motion, Sensor, Alarm, 충돌방지, 현장 대응 |
| AR System | 4.5 | AR 검사/운영, AF, ND Filter, PKG 개조, 이미지 촬상, 현장 대응 |
| Vision UI/WPF Framework | 4.2 | WPF 기반 Vision UI, 이미지 뷰어/렌더링, ROI/Overlay, Framework, DataGrid/PropertyGrid 구성 |
| LGD ICBSystem | 3.9 | LGD ICBSystem, C310V2 통신, Cell 계측 Flow, Debug |
| LGD LifeTimeSystem | 3.9 | `LGD ICBSystem`으로 통합 인식해 계산 |
| SDC LifeTime/MVT System | 3.8 | SDC/S6 LifeTime, MVT, Turn On, IO Check, Recipe 기능 수정 |
| KOPTI Sorter/Prober | 3.8 | KOPTI Sorter/Prober 설비 이동, 현장 적용, 정지/상태 확인 이슈 대응 |
| KOPTI Micro LED 검사 설비 | 4.3 | KOPTI Micro LED 검사 설비, Recipe GUI, Teaching 위치 GUI, MVVM 구조, Motor DLL, ACS/Fastech 축 파라미터 정리 |
| MTP Cell Log | 3.2 | MTP Cell Log, 패턴별 휘도계 좌표, Header 대응, CSV 저장 이슈 |
| 세미나/자료정리 | 2.0 | 발표, 자료 정리, 프로세스 정리, 업무 보조성 문서 작업 |
| 교육/학습 | 1.0 | 교육 참석, 신입 교육, 기본 학습 활동 |

### 프로젝트별 확정 투입인원

투입인원 보정은 자동 산출값보다 아래 확정 투입인원 표를 우선 적용한다.
같은 프로젝트로 묶인 항목은 대표 프로젝트명으로 통합해 계산하고, 투입인원 보정은 통합 그룹 내 확정 투입인원의 평균값을 적용한다.

같은 프로젝트 통합 기준:
- `신뢰성 평가 설비`, `RAS`, `신뢰성 평가 시스템`은 `신뢰성 평가 시스템`으로 인식해 계산한다.
- `RAS Vision Part`, `RAS Vision 알고리즘 개발`은 `Vision 알고리즘 개발`로 인식해 계산한다.
- `LGD LifeTimeSystem`, `LGD ICBSystem`은 `LGD ICBSystem`으로 인식해 계산한다.

| 프로젝트 | 확정 투입인원 | 투입자 |
|----------|-------------:|--------|
| TOE 운영 프로그램 | 2명 | 김현석, 김성현 (`TOE 2차 설비`로 통합) |
| TOE 1차 설비 | 1명 | 배유민 |
| TOE CIM | 1명 | 김성현 |
| 교육/학습 | 1명 |  |
| ETC | 1명 |  |
| Vision UI/WPF Framework | 1명 | 박주상 |
| AR System | 2명 | 송유림, 박장미 |
| MTP Cell Log | 2명 | 송유림, 박장미 |
| SDC LifeTime/MVT System | 1명 | 주영모 |
| SEC 4종설비 1D/2D | 1명 | 주영모 |
| Vision 알고리즘 개발 | 1명 | 박주상 |
| WHTM Loader/Unloader System | 2명 | 주영모 |
| 세미나/자료정리 | 1명 |  |
| KOPTI Sorter/Prober | 1명 | 주영모 |
| KOPTI Micro LED 검사 설비 | 1명 | 박주상 |
| 신뢰성 평가 설비 | 1명 | 주영모 |
| LGD ICBSystem | 2명 | 주영모, 박장미 |
| LGD LifeTimeSystem | 1명 | 주영모 |
| 신뢰성 평가 시스템 | 3명 | 김병걸, 주영모, 박주상 |
| RAS Vision 알고리즘 개발 | 1명 | 박주상 (`Vision 알고리즘 개발`로 통합) |
| WHTM ACAControlSystem | 1명 | 주영모 |
| Wafer Passive SPL Test System | 1명 | 배유민 |
| Multi-Probing Tester | 2명 | 김병걸, 배유민 |

반영 원칙:
- 주간업무 내용 분석 시 프로젝트 컬럼의 `SEC`, `TOE`, `LGD` 같은 고객/대분류명은 프로젝트 분류에 사용하지 않는다.
- 프로젝트 분류는 금주실적 본문에 반복 등장하는 설비명·시스템명·프로그램명을 기준으로 한다.
- 금주실적 본문에 여러 세부 프로젝트가 함께 있으면 가능한 한 세부 프로젝트별로 나누어 반영한다. 자동 분리가 어렵거나 기여 비중이 불명확하면 대표 세부 프로젝트를 사용하고 근거 문구를 남긴다.
- 세부 프로젝트 가중치가 별도로 정의되지 않은 경우 상위 프로젝트 가중치를 임시 적용하되, 평가 결과에는 `가중치 미정` 또는 `상위 가중치 적용`으로 표시한다.
- 세부 프로젝트 분류 또는 가중치 적용이 애매하면 임의로 확정하지 말고 사용자에게 질문한다.
- 프로젝트 난이도는 개인별 최종 점수 산정 시 업무성과/기여도와 난이도 보정 근거로 사용한다.
- 투입인원이 많으면 개인별 부담·책임이 분산되므로 개인평가용 난이도에서 `0.25 × (투입인원 - 1)`만큼 차감한다. 단, 차감 한도는 최대 0.6점으로 한다.
- 투입인원 보정 시 위 `프로젝트별 확정 투입인원` 표를 우선 적용한다.
- 같은 프로젝트 통합 기준에 포함된 항목은 대표 프로젝트명과 대표 프로젝트 난이도로 계산하되, 투입인원은 통합 그룹 내 확정 투입인원의 평균값을 적용한다.
- 난이도만으로 평가를 결정하지 않고, 완료 근거·업무 완성도·문제 해결·협업 기여와 함께 판단한다.
- 통합 프로젝트 수가 같아도 원문 업무 행 수가 많으면 지속 투입·반복 처리 업무량으로 보고 `업무량 보정`을 추가 반영한다.
- 업무량 보정은 원문 업무 행 수 기준으로 계산하고 최대 0.35점까지만 반영한다.
- 동일 프로젝트명이 대소문자나 표기 차이로 나뉘면 위 표 기준으로 통합한다.
- `TOE`와 `ToE`는 본문 단서에 따라 `TOE 1차 설비`, `TOE 2차 설비`, `TOE 미구분`으로 구분한다.
- 금주실적 본문에 `SEC RAS`, `RAS`, `신뢰성 평가 설비` 또는 `신뢰성 설비 프로그램` 단서가 있으면 `신뢰성 평가 시스템`으로 통합해 평가한다.
- `RAS Vision Part`, `RAS Vision 알고리즘 개발`은 `Vision 알고리즘 개발`로 통합해 평가한다.
- `TOE CIM`은 `TOE 운영 프로그램`과 분리해 평가한다.
- `LGD LifeTimeSystem`은 `LGD ICBSystem`으로 통합해 평가한다.
- `Wafer Passive SPL Test System`은 `Multi-Probing Tester`와 분리해 평가한다.
- `세미`는 `세미나`로 통합해 평가한다.
- 기존 ETC 항목 중 아래는 세부 프로젝트로 확정 분류한다.
- 박주상 ELP/WPF 관련 항목은 `Vision UI/WPF Framework`로 분류한다.
- 주영모 SEC 4종 VA/2D 항목은 `SEC 4종설비 1D/2D`로 분류한다.
- 주영모 SDC/S6 LifeTime/MVT 항목은 `SDC LifeTime/MVT System`으로 분류한다.
- 주영모 LG Mobile OLED 신뢰성 시스템 항목은 `LGD ICBSystem`으로 분류한다.
- 주영모 업무 중 `ICBSystem`, `LG Mobile OLED`, `IVL`, `PG Control`, `Voltage Sweep`, `MTP/IVL Test` 관련 항목은 `MTP` 단서가 함께 있어도 `LGD ICBSystem`으로 우선 분류한다.
- 박주상 `KOPTI Mirco LED`, `KOPTI Micro LED`, `Micro LED 검사`, `Recipe GUI`, `MVVM`, `Motor DLL`, `ACS/Fastech` 관련 항목은 `KOPTI Sorter/Prober`가 아니라 `KOPTI Micro LED 검사 설비`로 분류한다.
- 송유림 MTP Cell Log 항목은 `MTP Cell Log`로 분류한다.
- 박장미 AR 이미지/검사/AF/Mapping 항목은 `AR System`으로 분류하되, 알고리즘 개발성이 명확하면 `Vision 알고리즘 개발`로 분류한다.
- 김도현 RAS Vision Part 항목은 `Vision 알고리즘 개발`로 분류한다.
- 박주상 RAS 업무 중 알고리즘/이미지 분석/매핑/불량 판정은 `Vision 알고리즘 개발`로 분류한다.
- 박장미 업무는 `Vision 알고리즘 개발`로 분류하지 않는다. AR 이미지/검사/AF/Mapping 관련 항목은 `AR System`으로 분류한다.
- 김현석의 `SDC LifeTime/MVT System` 분류는 제외하고, 해당 항목은 주영모 담당으로 본다.
- 박장미 업무는 `TOE 운영 프로그램`으로 분류하지 않는다.
- 배유민 업무는 `Vision UI/WPF Framework`로 분류하지 않는다.
- 배유민 업무는 `TOE 운영 프로그램`으로 분류하지 않는다. 단, ToE/TOE 본문 단서 중 `1호기`, `1차`, `1차 설비`가 명확하면 `TOE 1차 설비`로 분류한다. 그 외에는 확정 투입 프로젝트인 `Wafer Passive SPL Test System`, `Multi-Probing Tester` 또는 구체 단서가 부족하면 `ETC`로 분류한다.
- 김성현 업무는 `교육/학습`으로 분류하지 않는다.
- 김성현의 `TOE 운영 프로그램` 업무는 핵심 주도자가 아니라 보조/부분 담당으로 반영한다. 프로젝트 난이도는 유지하되, 개인 평가의 주도성/책임 보정은 낮게 적용한다.
- 주영모 업무는 `Vision UI/WPF Framework`로 분류하지 않는다.
- 김도현 업무는 `SEC 4종설비 1D/2D`로 분류하지 않는다.
- 김도현 업무는 `TOE 운영 프로그램`으로 분류하지 않는다. 신입 인수인계·코드 분석·교육 성격이면 `교육/학습` 또는 구체 단서가 부족하면 `ETC`로 분류한다.
- 김병걸 업무는 `TOE 운영 프로그램`으로 분류하지 않는다. `안전 검수` 표현만으로 TOE로 분류하지 않는다.

---

## 3. 수집 절차 (단계별)

### 최신 수집 원칙 — 결재-미결함/완료함 iframe 업무 테이블 직접 추출

2026-05-11 기준 실제 성공한 방식은 아래 흐름이다. 이 절차가 아래의 예전 body 저장 방식, 회람함 분리 방식, DOCX 기반 추출보다 우선한다.

1. Browser/Playwright 세션에서 `https://gwp.ktbizoffice.com/ezapproval/main/indexapproval`로 이동한다.
2. 그룹웨어 로그인 상태를 확보한 뒤 왼쪽 메뉴의 `미결함`과 `완료함`을 확인한다.
3. `li[name="DocList_TR"]` 목록에서 대상 팀원 이름과 주간업무보고 제목을 기준으로 문서를 찾는다.
4. 문서를 클릭한 뒤 `#message` iframe이 로드되면 iframe 안의 `table` 목록을 뒤에서부터 검사한다.
5. 첫 행 또는 테이블 텍스트에 `프로젝트`, `금주`, `내주`가 모두 포함된 가장 안쪽 테이블을 업무 테이블로 본다.
6. 해당 테이블의 `tr`과 `th,td`를 Playwright locator로 순회해 셀 텍스트를 추출한다. `innerHTML` 전체 body 저장은 사용하지 않는다.
7. `D:\Temp\주간업무정리\{팀원}\YYYY-MM-DD.html`에 저장한다. 파일 상단에는 `출처: {그룹웨어 문서 제목}`을 남긴다.
8. 모든 저장 후 `build_index.py`를 실행해 `index.html`을 재생성한다.

추출 기준:
- 업무 테이블 컬럼은 보통 `프로젝트`, `금주실적`, `담당자`, `내주계획`, `담당자`, `목표일` 구조다.
- 결재/작성자/참조/문서분류 같은 그룹웨어 폼 헤더는 저장하지 않는다.
- 저장 후 각 파일에서 `<p class="source">출처: ...</p>`가 있는지 확인해 실제 그룹웨어 문서에서 추출한 파일인지 검증한다.
- 결재-미결함과 결재-완료함 모두에서 특정 팀원 문서가 보이지 않으면 임의로 DOCX나 통합 보고서에서 만들지 말고, 누락으로 기록한다.
- `index.html` 생성 시 컬럼 헤더(`thead th`, `thead td`)만 하늘색 배경을 적용하고, 본문 데이터(`tbody td`)는 항상 흰색 배경으로 표시한다.
- 예전 파일 호환용으로 `thead`가 없는 테이블의 첫 행만 헤더 색상을 적용하되, `thead`가 있는 신규 추출 파일의 첫 데이터 행은 하늘색으로 칠하지 않는다.

### STEP 1 — 로컬 파일 서버 시작

브라우저 → 로컬 디스크 파일 저장을 위한 Python HTTP 서버를 실행한다.

```python
# srv.py
# 포트: 18765
```

실행 명령:
```
C:\Users\bluesky22c\AppData\Local\Programs\Python\Python313\python.exe D:\Temp\주간업무정리\srv.py
```

서버 동작 확인: 브라우저에서 fetch POST 테스트로 확인.

> ⚠️ srv.py는 Desktop Commander `start_process`로 시작해야 Windows에서 실행됨.
> bash sandbox에서 시작하면 Linux 환경에서 실행되어 `D:\` 경로에 접근 불가.
> srv.py 내부는 UTF-8 한글 파일 저장을 위해 루프 읽기 방식으로 구현되어 있음 (partial read 방지).

---

### STEP 2 — 그룹웨어 결재-미결함/완료함 이동

- URL: `https://gwp.ktbizoffice.com/ezapproval/main/indexapproval`
- Chrome MCP 탭 ID: 매 세션마다 `tabs_context_mcp`로 확인
- 미결함과 완료함을 모두 확인함

---

### STEP 3 — 수집 대상 항목 파악

브라우저 JavaScript로 현재 페이지의 문서 목록에서 대상자·날짜 파악:

```javascript
const targetPeople = ['박주상','주영모','김병걸','김현석','송유림','김성현','배유민','박장미','김도현', '유찬', '황지환'];
const items = Array.from(document.querySelectorAll('li[name="DocList_TR"]'));

// 대상 항목 필터링
const targetItems = items.filter(item => {
  const text = item.textContent.replace(/\s+/g,' ').trim();
  const dateMatch = text.match(/(\d{4}-\d{2}-\d{2})/);
  if (!dateMatch) return false;
  return targetPeople.some(n => text.startsWith(n));
});
```

- 이미 저장된 파일과 비교해 **신규 항목만** 처리
- 기존 파일 목록은 Python으로 확인: `os.listdir('D:\\Temp\\주간업무정리\\{이름}')`

---

### STEP 4 — 문서 내용 순차 수집

각 항목을 클릭 → iframe 로드 대기(2.8초) → 내용 추출:

```javascript
window._newContents = {};
window._newCount = 0;
window._newDone = false;

(async () => {
  for (let i = 0; i < window._newItems.length; i++) {
    const item = window._newItems[i];
    const text = item.textContent.replace(/\s+/g,' ').trim();
    const dateMatch = text.match(/(\d{4}-\d{2}-\d{2})/);
    const date = dateMatch ? dateMatch[1] : 'unknown';
    let name = '';
    for (const n of targetPeople) { if (text.startsWith(n)) { name = n; break; } }

    item.click();
    await new Promise(r => setTimeout(r, 2800));

    const iframe = document.getElementById('message');
    if (iframe && iframe.contentDocument && iframe.contentDocument.body) {
      if (!window._newContents[name]) window._newContents[name] = {};
      window._newContents[name][date] = iframe.contentDocument.body.innerHTML;
      window._newCount++;
    }
  }
  window._newDone = true;
})();
```

진행 확인: `window._newCount + ' / ' + window._newItems.length + ', done: ' + window._newDone`

---

### STEP 5 — HTML 파일 생성 및 저장

수집된 내용을 최소화된 HTML로 변환 후 로컬 서버를 통해 저장.

#### 5-A. 기존 팀원 (결재-미결함/완료함, 전체 body 저장 방식)

```javascript
const htmlTemplate = (name, date, body) => `<!DOCTYPE html>
<html lang="ko"><head><meta charset="UTF-8">
<title>${name} - 주간업무보고 (${date})</title>
<style>
body{font-family:'맑은 고딕',sans-serif;margin:20px;font-size:12px}
table{border-collapse:collapse;width:100%}
td,th{border:1px solid #999;padding:8px;vertical-align:top;word-break:keep-all;white-space:pre-wrap}
th{background:#ddeeff;font-weight:bold;text-align:center}
h2{color:#003366}
p{margin:2px 0;line-height:1.7}
</style></head><body>
<h2>${name} - 주간업무보고서 (${date})</h2>
${body}
</body></html>`;

window._saveResults = { done: 0, failed: 0, errors: [] };

(async () => {
  for (const name of Object.keys(window._newContents)) {
    for (const date of Object.keys(window._newContents[name])) {
      const parser = new DOMParser();
      const doc = parser.parseFromString('<body>' + window._newContents[name][date] + '</body>', 'text/html');
      doc.querySelectorAll('script,style,img,link').forEach(el => el.remove());
      doc.querySelectorAll('*').forEach(el => {
        const keep = ['colspan','rowspan'];
        Array.from(el.attributes).forEach(attr => {
          if (!keep.includes(attr.name)) el.removeAttribute(attr.name);
        });
      });
      const cleanBody = doc.body.innerHTML.replace(/\s+/g,' ').trim();
      const content = htmlTemplate(name, date, cleanBody);
      const path = 'D:\\Temp\\주간업무정리\\' + name + '\\' + date + '.html';
      const r = await fetch('http://127.0.0.1:18765/', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({path, content})
      });
      if (r.ok) window._saveResults.done++;
      else window._saveResults.errors.push(path);
    }
  }
  window._saveResults.finished = true;
})();
```

#### 5-B. 회람함 팀원 (유찬, 황지환) — 업무 테이블 추출 방식

회람함 수집본은 그룹웨어 폼 헤더(결재/작성자/참조)가 포함된 복잡한 중첩 구조임.
단순 body 저장이 아닌, **업무 테이블만 추출**하는 함수를 사용해야 한다.

> ⚠️ 주의: 기존 `extractWorkRows` 방식은 outermost TR의 textContent가 내부 중첩 테이블
> 텍스트까지 포함하므로 잘못된 행에서 매칭될 수 있다. 반드시 아래 `extractWorkTable`을 사용한다.

```javascript
// 핵심 업무 테이블 추출: 프로젝트|금주실적|담당자|내주계획|담당자|목표일 구조
function extractWorkTable(rawHtml) {
  const parser = new DOMParser();
  const doc = parser.parseFromString('<body>' + rawHtml + '</body>', 'text/html');
  const tables = Array.from(doc.querySelectorAll('table'));
  let bestTable = null;
  for (const tbl of tables) {
    const firstRow = tbl.querySelector('tr');
    if (!firstRow) continue;
    const t = firstRow.textContent;
    // 첫 번째 행에 프로젝트+금주(실적)+내주(계획) 키워드가 모두 있는 가장 안쪽 테이블
    if (t.includes('프로젝트') && (t.includes('금주') || t.includes('실적')) && (t.includes('내주') || t.includes('계획'))) {
      bestTable = tbl; // 마지막으로 매칭된 = 가장 안쪽 테이블
    }
  }
  if (!bestTable) return null;
  // colspan/rowspan만 유지, 나머지 속성 제거
  const keep = ['colspan', 'rowspan'];
  bestTable.querySelectorAll('*').forEach(el => {
    Array.from(el.attributes).forEach(attr => {
      if (!keep.includes(attr.name)) el.removeAttribute(attr.name);
    });
  });
  Array.from(bestTable.attributes).forEach(a => bestTable.removeAttribute(a.name));
  return '<table><tbody>' + Array.from(bestTable.querySelectorAll('tr')).map(r => r.outerHTML).join('') + '</tbody></table>';
}

// 수집 변수명: 1페이지=window._collected, 2페이지=window._collected2 (key: "이름|날짜")
const allRaw = Object.assign({}, window._collected || {}, window._collected2 || {});
window._cleanTables = {};
let ok = 0, fail = 0;
for (const key of Object.keys(allRaw)) {
  const result = extractWorkTable(allRaw[key]);
  if (result) { window._cleanTables[key] = result; ok++; }
  else fail++;
}
JSON.stringify({ok, fail}); // fail > 0 이면 해당 항목 수동 확인 필요

// 저장
const htmlTemplate2 = (name, date, tableHtml) => `<!DOCTYPE html>
<html lang="ko"><head><meta charset="UTF-8">
<title>${name} - 주간업무보고 (${date})</title>
<style>
body{font-family:'맑은 고딕',sans-serif;margin:20px;font-size:12px}
table{border-collapse:collapse;width:100%}
td,th{border:1px solid #999;padding:8px;vertical-align:top;word-break:keep-all;white-space:pre-wrap}
th{background:#ddeeff;font-weight:bold;text-align:center}
h2{color:#003366}
p{margin:2px 0;line-height:1.7}
</style></head><body>
<h2>${name} - 주간업무보고서 (${date})</h2>
${tableHtml}
</body></html>`;

window._saveResults2 = { done: 0, failed: 0, errors: [] };
(async () => {
  for (const key of Object.keys(window._cleanTables)) {
    const [name, date] = key.split('|');
    const content = htmlTemplate2(name, date, window._cleanTables[key]);
    const path = 'D:\\Temp\\주간업무정리\\' + name + '\\' + date + '.html';
    try {
      const r = await fetch('http://127.0.0.1:18765/', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({path, content})
      });
      if ((await r.text()) === 'ok') window._saveResults2.done++;
      else window._saveResults2.failed++;
    } catch(e) { window._saveResults2.failed++; }
  }
  window._saveResults2.finished = true;
})();
```

저장 완료 확인: `JSON.stringify(window._saveResults2)`

---

### STEP 5-C — 그룹웨어 폼 헤더 제거 (필수)

저장된 HTML 파일에는 결재/작성자/문서분류/참조/제목 등 그룹웨어 폼 헤더가 포함됨.
**반드시** 아래 스크립트로 제거한 뒤 index.html을 재생성한다.

```
C:\Users\bluesky22c\AppData\Local\Programs\Python\Python313\python.exe D:\Temp\주간업무정리\fix_all_headers.py
```

**스크립트 위치:** `D:\Temp\주간업무정리\fix_all_headers.py`

**처리 로직 (두 가지 케이스 자동 처리):**

| 케이스 | 파일 유형 | 업무 테이블 추출 방법 |
|--------|----------|----------------------|
| A | `formid=` 속성이 있는 파일 (최초 수집본) | formid td 내부 첫 번째 table 추출 |
| B | 속성 제거된 파일 (colspan/rowspan만 존재) | `<td rowspan="1" colspan="3">` 내부 table 추출 |

**건너뜀 판별:** `결재`, `작성자`, `참조` 키워드가 2개 미만인 파일은 이미 처리된 것으로 간주.

---

### STEP 6 — index.html 재생성 (선택)

새 파일이 추가된 경우 통합 뷰어를 업데이트.

> ⚠️ **반드시 Windows(Desktop Commander)에서 실행할 것.**
> Linux bash 샌드박스는 CIFS 마운트 캐시 문제로 최신 파일을 읽지 못할 수 있음.

Desktop Commander의 `start_process` 도구로 실행:
```
C:\Users\bluesky22c\AppData\Local\Programs\Python\Python313\python.exe D:\Temp\주간업무정리\build_index.py
```

`D:\Temp\주간업무정리\build_index.py`가 `D:\Temp\주간업무정리` 폴더 전체를 읽어
`index.html`을 재생성함.

파일 유효성 검증 스크립트 (Desktop Commander에서 실행):
```
C:\Users\bluesky22c\AppData\Local\Programs\Python\Python313\python.exe C:\Temp\check_html.py
```

---

## 4. 이미 저장된 파일 확인 방법

```python
# C:\Temp\check2.py
import os
base = r'D:\Temp\주간업무정리'
for name in sorted(os.listdir(base)):
    folder = os.path.join(base, name)
    if os.path.isdir(folder):
        htmls = sorted([f for f in os.listdir(folder) if f.endswith('.html')])
        if htmls:
            print(f"{name}: {len(htmls)}개 | 최신: {htmls[-1].replace('.html','')}")
```

---

## 5. 신규 항목 판별 로직

저장 전에 이미 있는 파일은 건너뛴다:

```javascript
// Python으로 기존 파일 목록을 JSON으로 출력한 후 JS에서 참조
// 또는 JS에서 직접 fetch로 서버에 존재 여부 질의

// 간단한 방법: 저장 시 이미 존재하면 덮어쓰지 않도록 서버에서 처리
// → file_server.py에 'skip_if_exists' 옵션 추가 가능
```

현재는 덮어쓰기 방식. 필요 시 서버 로직에 존재 확인 추가.

---

## 6. 주요 환경 정보

| 항목 | 값 |
|------|-----|
| Python 경로 | `C:\Users\bluesky22c\AppData\Local\Programs\Python\Python313\python.exe` |
| 파일 서버 | `D:\Temp\주간업무정리\srv.py` (포트 18765) |
| 빌드 스크립트 | `D:\Temp\주간업무정리\build_index.py` |
| 폼헤더 제거 | `D:\Temp\주간업무정리\fix_all_headers.py` |
| 헤더 스타일 | `D:\Temp\주간업무정리\add_header_style.py` |
| 그룹웨어 URL | `https://gwp.ktbizoffice.com/ezapproval/main/indexapproval` |
| iframe ID | `message` |
| 문서 항목 선택자 | `li[name="DocList_TR"]` |
| 대기 시간 | 클릭 후 2800ms (iframe 로드 대기) |

---

## 7. 사용 방법 요약

매주 보고서가 추가되면 Claude에게 다음과 같이 요청:

> **"금주주간업무보고 작성"**

또는

> **"금주 주간 업무 보고 작성해줘"**

Claude는 위 요청을 받으면 이 CLAUDE.md의 `0. 반복 작업 트리거` 규칙에 따라 아래 절차를 자동 수행:
1. 그룹웨어 `결재-미결함`과 `결재-완료함` 모두 확인
2. 금주 대상 팀원별 주간업무보고 수집
3. 팀원별 `YYYY-MM-DD.html` 저장
4. `index.html` 재생성
5. 전주 DOCX 형식을 참고해 금주 `[보고_제어1팀]주간업무보고(YYMMDD).docx` 생성
6. 통합 DOCX에 프로젝트별 금주 실적/내주 계획을 정리
7. 타이틀 제외 일반 텍스트 8pt 적용 및 검증

HTML 저장만 필요할 때는 다음과 같이 요청:

> **"추가된 주간업무보고 저장해줘"**

Claude는 이 경우 DOCX 생성 없이 HTML 저장과 index 갱신 중심으로 수행:
1. 기존 저장 파일 목록 확인
2. 그룹웨어에서 신규 항목 파악
3. 내용 수집 → HTML 저장
4. **폼 헤더 제거** (`D:\Temp\주간업무정리\fix_all_headers.py` 실행)
5. index.html 재생성
