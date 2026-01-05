# Sprint Plan - Part 1: Epics & Stories

## 📋 Product Backlog Overview

**프로젝트**: Trainable Cell Circuits Design Platform (TCCDP)  
**기간**: 12주 (6 Sprints × 2주)  
**방법론**: Agile Scrum  
**UI 중심**: Figma 기반 디자인 우선 개발

---

## 🎯 Epic Overview

총 **6개의 Epic**으로 구성되며, 각 Epic은 하나 또는 여러 Sprint에 걸쳐 완료됩니다.

| Epic ID | Epic 이름 | 목표 | Story 수 | 총 Points |
|---------|----------|------|----------|-----------|
| E1 | 프로젝트 기반 및 UI 설계 | 전체 시스템 구조와 UI/UX 설계 | 8 | 34 |
| E2 | 전사 기반 학습 회로 구현 | 첫 번째 회로 타입 완전 구현 | 10 | 55 |
| E3 | 단백질 변형 기반 회로 구현 | 두 번째 회로 타입 및 확률적 시뮬레이션 | 9 | 50 |
| E4 | 대사 기반 회로 구현 | 세 번째 회로 타입 및 하이브리드 시뮬레이션 | 8 | 45 |
| E5 | 통합 및 분석 플랫폼 | 세 회로 통합과 분석 도구 | 11 | 58 |
| E6 | 문서화 및 배포 | 사용자 문서와 공개 릴리스 | 9 | 38 |

**총 Story 수**: 55  
**총 Points**: 280  
**평균 Sprint Velocity**: 46-47 points/sprint

---

## 📦 Epic 1: 프로젝트 기반 및 UI 설계

**목표**: 전체 프로젝트 인프라 구축 및 UI/UX 완전 설계  
**기간**: Sprint 1 (Week 1-2)  
**총 Points**: 34

### E1-S1: 개발 환경 설정 및 프로젝트 구조
**Points**: 5  
**Priority**: CRITICAL

**As a** 개발자  
**I want** 표준화된 개발 환경과 프로젝트 구조  
**So that** 팀원 모두가 일관된 환경에서 협업할 수 있다

**Description**:
- Python 3.10+ 가상환경 설정
- 프로젝트 디렉토리 구조 생성 (development_plan.md 참조)
- 의존성 관리 (requirements.txt, pyproject.toml)
- Docker 개발 환경 구성
- Git 저장소 초기화 및 .gitignore 설정

**Acceptance Criteria**:
- [ ] `pip install -e .`로 로컬 설치 가능
- [ ] Docker container에서 정상 실행
- [ ] 모든 필수 디렉토리 생성 완료
- [ ] requirements.txt에 모든 의존성 명시
- [ ] README.md에 설치 가이드 포함

---

### E1-S2: CI/CD 파이프라인 초기 설정
**Points**: 3  
**Priority**: HIGH

**As a** 개발자  
**I want** 자동화된 테스트 및 배포 파이프라인  
**So that** 코드 품질을 자동으로 검증하고 빠르게 배포할 수 있다

**Description**:
- GitHub Actions 워크플로우 설정
- 자동 테스트 실행 (pytest)
- 코드 품질 체크 (black, ruff, mypy)
- 커버리지 리포트 생성

**Acceptance Criteria**:
- [ ] PR 생성 시 자동 테스트 실행
- [ ] 테스트 실패 시 merge 불가
- [ ] 커버리지 80% 미만 시 경고
- [ ] main 브랜치 push 시 자동 배포 트리거

---

### E1-S3: 전체 UI/UX 디자인 (Figma)
**Points**: 8  
**Priority**: CRITICAL

**As a** 사용자  
**I want** 직관적이고 아름다운 인터페이스  
**So that** 복잡한 시뮬레이션을 쉽게 설정하고 결과를 이해할 수 있다

**Description**:
- Figma에서 전체 UI 프레임 설계
- 주요 화면: Dashboard, Circuit Builder, Training Controller, Analysis View, Results Gallery
- 컴포넌트 라이브러리 구축
- 색상/타이포그래피 시스템 정의
- 반응형 레이아웃 (Desktop 우선, Tablet 고려)

**Figma Screens**:
1. **Dashboard** (랜딩 페이지)
   - 프로젝트 개요
   - 최근 시뮬레이션 목록
   - Quick Start 버튼

2. **Circuit Builder** (회로 설계)
   - 회로 타입 선택 (Transcription / Protein Mod / Metabolic)
   - 파라미터 설정 패널
   - 시각적 회로 다이어그램
   - 프리셋 템플릿

3. **Training Controller** (훈련 설정)
   - 훈련 프로토콜 선택 (Pavlovian / Supervised / Custom)
   - 스케줄 타임라인 시각화
   - 실시간 모니터링 그래프

4. **Analysis View** (분석 결과)
   - 학습 곡선 그래프
   - 가중치 진화 그래프
   - 성능 지표 대시보드
   - 비교 분석 도구

5. **Results Gallery** (결과 저장소)
   - 저장된 실험 목록
   - 필터 및 검색
   - Export 기능

**Acceptance Criteria**:
- [ ] Figma 프로젝트에 5개 메인 화면 완성
- [ ] 재사용 가능한 컴포넌트 라이브러리 (20+ 컴포넌트)
- [ ] 디자인 시스템 문서 (색상, 타이포그래피, 간격)
- [ ] 모바일 반응형 고려 (최소 Tablet)
- [ ] 개발팀 리뷰 및 승인 완료
- [ ] **미구현 UI는 "Coming Soon" 표시 가능**

---

### E1-S4: 베이스 클래스 및 인터페이스 정의
**Points**: 5  
**Priority**: CRITICAL

**As a** 개발자  
**I want** 명확한 추상 베이스 클래스와 인터페이스  
**So that** 세 가지 회로 타입이 일관된 구조를 따를 수 있다

**Description**:
- `BaseCircuit` 추상 클래스 구현
- `BaseSimulator` 인터페이스 정의
- `BaseTrainer` 인터페이스 정의
- 공통 타입 정의 (TypedDict, Enum)

**Acceptance Criteria**:
- [ ] `tccdp/core/base.py` 작성 완료
- [ ] 모든 추상 메서드 docstring 포함
- [ ] 타입 힌팅 100% (mypy 통과)
- [ ] 유닛 테스트 작성 (추상 클래스 인스턴스화 금지 확인)

---

### E1-S5: 학습 알고리즘 핵심 구현
**Points**: 8  
**Priority**: CRITICAL

**As a** 시스템  
**I want** 고역통과 필터와 자율 조절 규칙  
**So that** 모든 회로가 동일한 학습 메커니즘을 사용할 수 있다

**Description**:
- `HighPassFilter` 클래스 구현
- `AutoregulationRule` 클래스 구현
- 필터 파라미터 튜닝 유틸리티
- 수치적 안정성 검증

**Acceptance Criteria**:
- [ ] `tccdp/core/learning.py` 완성
- [ ] 상수 입력에서 0 수렴 확인
- [ ] 스텝 입력에서 올바른 반응 확인
- [ ] 테스트 커버리지 > 90%
- [ ] 벤치마크 성능 테스트 (1M 업데이트 < 1초)

---

### E1-S6: 테스트 프레임워크 구축
**Points**: 3  
**Priority**: HIGH

**As a** 개발자  
**I want** 체계적인 테스트 구조  
**So that** 모든 기능을 자동으로 검증할 수 있다

**Description**:
- pytest 설정 및 구조화
- 테스트 유틸리티 함수 작성
- Fixture 라이브러리 구축
- Mock 객체 설정

**Acceptance Criteria**:
- [ ] `tests/` 디렉토리 구조 완성 (unit, integration, e2e)
- [ ] conftest.py에 공통 fixture 정의
- [ ] 테스트 실행 시간 < 10초 (unit tests)
- [ ] Coverage report 자동 생성

---

### E1-S7: 데이터 모델 및 설정 시스템
**Points**: 2  
**Priority**: MEDIUM

**As a** 사용자  
**I want** YAML/JSON 설정 파일로 시뮬레이션 제어  
**So that** 코드 수정 없이 파라미터를 조정할 수 있다

**Description**:
- Pydantic 모델로 설정 스키마 정의
- YAML 파서 구현
- 설정 검증 로직
- 프리셋 설정 파일 제공

**Acceptance Criteria**:
- [ ] `tccdp/config/` 모듈 생성
- [ ] CircuitConfig, TrainingConfig, SimulationConfig 클래스
- [ ] 잘못된 설정 시 명확한 에러 메시지
- [ ] 3+ 프리셋 설정 파일 (예: quick_test.yaml, full_training.yaml)

---

### E1-S8: 로깅 및 모니터링 인프라
**Points**: 2  
**Priority**: MEDIUM

**As a** 개발자  
**I want** 구조화된 로깅 시스템  
**So that** 디버깅과 성능 분석이 쉬워진다

**Description**:
- Loguru 기반 로깅 설정
- 로그 레벨 관리 (DEBUG, INFO, WARNING, ERROR)
- 파일 로깅 및 로테이션
- 성능 프로파일링 데코레이터

**Acceptance Criteria**:
- [ ] 통합 로깅 설정 (`tccdp/utils/logging.py`)
- [ ] 로그 파일 자동 로테이션 (10MB 단위)
- [ ] 컬러풀한 콘솔 출력
- [ ] 성능 측정 데코레이터 (`@profile_time`)

---

## 📦 Epic 2: 전사 기반 학습 회로 구현

**목표**: 첫 번째 회로 타입 완전 구현 및 검증  
**기간**: Sprint 2-3 (Week 3-6)  
**총 Points**: 55

### E2-S1: TranscriptionCircuit 클래스 구현
**Points**: 8  
**Priority**: CRITICAL

**As a** 시스템  
**I want** 전사 기반 회로의 ODE 시스템  
**So that** 분자 수준의 동역학을 시뮬레이션할 수 있다

**Description**:
- `TranscriptionCircuit` 클래스 구현 (BaseCircuit 상속)
- 상태 벡터 정의: [V, Hmon, C, Htot]
- ODE derivatives 메서드 구현
- 파라미터 기본값 설정

**Acceptance Criteria**:
- [ ] `tccdp/circuits/transcription.py` 완성
- [ ] 모든 ODE가 수학적으로 정확
- [ ] 초기 상태 설정 로직
- [ ] 파라미터 검증 (음수 방지 등)
- [ ] Docstring 100%

---

### E2-S2: ODE 시뮬레이터 통합 (SciPy)
**Points**: 5  
**Priority**: CRITICAL

**As a** 시스템  
**I want** 안정적인 ODE 솔버  
**So that** 연속 시간 동역학을 정확히 계산할 수 있다

**Description**:
- SciPy `solve_ivp` 래퍼 구현
- 적응형 시간 간격
- 솔버 옵션 (LSODA, DOP853 등) 선택 가능
- 수치적 안정성 검증

**Acceptance Criteria**:
- [ ] `tccdp/simulators/ode_solver.py` 구현
- [ ] 여러 솔버 비교 테스트
- [ ] Stiff system 처리 확인
- [ ] 에러 핸들링 (발산 감지)

---

### E2-S3: Tellurium/Antimony 통합 (선택)
**Points**: 3  
**Priority**: LOW

**As a** 고급 사용자  
**I want** Antimony 언어로 모델 정의  
**So that** SBML 표준을 따르고 다른 도구와 호환할 수 있다

**Description**:
- Tellurium 라이브러리 통합
- Antimony 모델 파싱
- SBML export 기능

**Acceptance Criteria**:
- [ ] Antimony 문자열 → Circuit 변환
- [ ] SBML 파일 export
- [ ] Tellurium roadrunner로 시뮬레이션 실행
- [ ] 예제 Antimony 모델 3개

---

### E2-S4: Pavlovian 조건화 훈련 프로토콜
**Points**: 8  
**Priority**: CRITICAL

**As a** 연구자  
**I want** 파블로프 조건화 실험  
**So that** 세포가 중립 자극에 반응하도록 학습하는지 검증할 수 있다

**Description**:
- `TrainingScheduler` 클래스 구현
- `pavlovian_conditioning` 메서드
- Sleep-Wake 사이클 구현
- 학습 업데이트 로직

**Acceptance Criteria**:
- [ ] `tccdp/training/scheduler.py` 구현
- [ ] 1000 에포크 훈련 정상 완료
- [ ] 학습 곡선 MSE 감소 확인
- [ ] 재현성 테스트 (seed 고정)
- [ ] 훈련 진행 상황 tqdm 표시

---

### E2-S5: 학습 모니터링 및 콜백
**Points**: 3  
**Priority**: MEDIUM

**As a** 사용자  
**I want** 훈련 중 실시간 피드백  
**So that** 학습 진행 상황을 파악하고 조기 중단할 수 있다

**Description**:
- 콜백 시스템 구현
- EarlyStopping 콜백
- ModelCheckpoint 콜백
- TensorBoard 로깅 (선택)

**Acceptance Criteria**:
- [ ] `tccdp/training/callbacks.py` 구현
- [ ] EarlyStopping (patience=100)
- [ ] 최적 모델 자동 저장
- [ ] 콜백 체인 지원

---

### E2-S6: 시각화 도구 (학습 곡선)
**Points**: 5  
**Priority**: HIGH

**As a** 사용자  
**I want** 학습 과정을 시각적으로 확인  
**So that** 모델이 올바르게 학습하는지 판단할 수 있다

**Description**:
- Matplotlib 기반 플로팅 함수
- 학습 곡선 (MSE, 출력, 가중치)
- 실시간 업데이트 (선택)
- 고품질 export (PNG, SVG)

**Acceptance Criteria**:
- [ ] `tccdp/analysis/visualization.py` 기본 구현
- [ ] `plot_learning_curve()` 함수
- [ ] `plot_weight_evolution()` 함수
- [ ] 커스터마이징 가능 (색상, 레이블 등)
- [ ] 예제 노트북에 포함

---

### E2-S7: 성능 지표 계산
**Points**: 3  
**Priority**: MEDIUM

**As a** 연구자  
**I want** 정량적 성능 평가  
**So that** 다른 설정을 객관적으로 비교할 수 있다

**Description**:
- MSE, MAE, R² 계산
- 수렴 시간 측정
- 학습 효율 지표
- 비교 리포트 생성

**Acceptance Criteria**:
- [ ] `tccdp/analysis/metrics.py` 구현
- [ ] 5+ 지표 함수
- [ ] 배치 계산 지원
- [ ] Pandas DataFrame 출력

---

### E2-S8: Jupyter 노트북 예제 1 (Pavlovian)
**Points**: 5  
**Priority**: HIGH

**As a** 신규 사용자  
**I want** 따라하기 쉬운 튜토리얼  
**So that** 빠르게 시작하고 결과를 확인할 수 있다

**Description**:
- 단계별 설명이 포함된 노트북
- Pavlovian 조건화 전체 워크플로우
- 결과 해석 가이드
- 파라미터 실험 섹션

**Acceptance Criteria**:
- [ ] `examples/notebooks/01_pavlovian_conditioning.ipynb` 작성
- [ ] 셀 실행 시간 < 5분
- [ ] 주석과 Markdown 설명 풍부
- [ ] 최종 결과 그래프 포함
- [ ] Binder/Colab 호환

---

### E2-S9: 유닛 테스트 (전사 회로)
**Points**: 5  
**Priority**: HIGH

**As a** 개발자  
**I want** 전사 회로의 모든 기능 테스트  
**So that** 리팩토링 시에도 안정성을 보장한다

**Description**:
- `test_transcription.py` 작성
- ODE 계산 정확성 테스트
- 학습 수렴 테스트
- 엣지 케이스 처리

**Acceptance Criteria**:
- [ ] 20+ 테스트 케이스
- [ ] 커버리지 > 90%
- [ ] 모든 테스트 < 30초
- [ ] Parametrize로 다양한 조건 테스트

---

### E2-S10: 통합 테스트 (End-to-End)
**Points**: 8  
**Priority**: HIGH

**As a** QA  
**I want** 전체 워크플로우 통합 테스트  
**So that** 실제 사용 시나리오가 문제없이 작동함을 확인한다

**Description**:
- 설정 파일 로드 → 회로 생성 → 훈련 → 분석 → 저장
- 대규모 시뮬레이션 (10K 에포크)
- 메모리 누수 검증
- 재현성 검증

**Acceptance Criteria**:
- [ ] `tests/integration/test_transcription_workflow.py`
- [ ] 3+ 시나리오 (quick, full, custom)
- [ ] 메모리 프로파일링
- [ ] 성능 벤치마크 기록

---

## 📦 Epic 3: 단백질 변형 기반 회로 구현

**목표**: 확률적 시뮬레이션 및 단일세포 분석  
**기간**: Sprint 3-4 (Week 5-8)  
**총 Points**: 50

### E3-S1: ProteinModificationCircuit 클래스 구현
**Points**: 8  
**Priority**: CRITICAL

**As a** 시스템  
**I want** 단백질 인산화/탈인산화 동역학  
**So that** 빠른 신호 전달 회로를 모델링할 수 있다

**Description**:
- `ProteinModificationCircuit` 클래스
- 상태: [U, P, Htot] (비변형, 변형, 숨겨진 총량)
- 키나아제/포스파테이스 동역학
- 동시성 검출 로직

**Acceptance Criteria**:
- [ ] `tccdp/circuits/protein_mod.py` 완성
- [ ] ODE 및 확률적 반응 정의
- [ ] 파라미터 기본값
- [ ] 테스트 커버리지 > 85%

---

### E3-S2: Gillespie 시뮬레이터 구현
**Points**: 8  
**Priority**: CRITICAL

**As a** 시스템  
**I want** 정확한 확률적 시뮬레이션  
**So that** 단일세포 수준의 변동성을 모델링할 수 있다

**Description**:
- Gillespie 알고리즘 구현 (처음부터 또는 GillesPy2 래핑)
- 반응 propensity 계산
- 이벤트 샘플링
- 최적화 (Direct Method / First Reaction)

**Acceptance Criteria**:
- [ ] `tccdp/simulators/gillespie.py` 구현
- [ ] 테스트: 단순 반응(A → B)의 분포 확인
- [ ] 성능: 10K 반응 < 1초
- [ ] GillesPy2 대비 검증

---

### E3-S3: GillesPy2 통합
**Points**: 3  
**Priority**: MEDIUM

**As a** 고급 사용자  
**I want** GillesPy2 라이브러리 사용  
**So that** 검증된 구현을 활용할 수 있다

**Description**:
- GillesPy2 Model 변환 유틸리티
- 결과 파싱
- 성능 비교

**Acceptance Criteria**:
- [ ] Circuit → GillesPy2 Model 변환
- [ ] 시뮬레이션 결과 일치 확인
- [ ] 예제 스크립트

---

### E3-S4: 단일세포 vs 집단 시뮬레이션
**Points**: 5  
**Priority**: HIGH

**As a** 연구자  
**I want** 단일세포와 집단 평균 비교  
**So that** 확률적 효과를 이해할 수 있다

**Description**:
- 다중 세포 시뮬레이션 (100-1000개)
- 병렬 실행
- 평균/분산 계산
- ODE와 비교

**Acceptance Criteria**:
- [ ] 100 세포 시뮬레이션 < 5분
- [ ] 평균이 ODE와 일치 (오차 < 5%)
- [ ] 분포 시각화 (히스토그램, 박스플롯)

---

### E3-S5: 훈련 프로토콜 적응 (빠른 동역학)
**Points**: 5  
**Priority**: HIGH

**As a** 시스템  
**I want** 단백질 변형에 최적화된 훈련  
**So that** 빠른 반응 속도에 맞춰 학습할 수 있다

**Description**:
- 짧은 펄스 스케줄
- 동시성 검출 강화
- 적응형 학습률

**Acceptance Criteria**:
- [ ] 펄스 폭 1-5분 (전사 기반보다 짧음)
- [ ] 학습 수렴 확인
- [ ] 노이즈 환경 테스트

---

### E3-S6: 확률적 노이즈 분석 도구
**Points**: 3  
**Priority**: MEDIUM

**As a** 연구자  
**I want** 노이즈의 영향 정량화  
**So that** 강건성을 평가할 수 있다

**Description**:
- Fano factor 계산
- CV (변동 계수) 분석
- 노이즈 전파 분석

**Acceptance Criteria**:
- [ ] `tccdp/analysis/noise.py` 모듈
- [ ] 3+ 노이즈 지표
- [ ] 시각화 함수

---

### E3-S7: Jupyter 노트북 예제 2 (단일세포)
**Points**: 5  
**Priority**: HIGH

**As a** 사용자  
**I want** 확률적 시뮬레이션 예제  
**So that** 단일세포 수준의 학습을 이해할 수 있다

**Description**:
- 단일세포 추적 노트북
- 확률적 변동성 시각화
- 집단 분포 분석

**Acceptance Criteria**:
- [ ] `examples/notebooks/02_stochastic_single_cell.ipynb`
- [ ] 10개 세포 궤적 시각화
- [ ] 분포 히트맵
- [ ] 실행 시간 < 10분

---

### E3-S8: 성능 최적화 (확률적 시뮬레이션)
**Points**: 5  
**Priority**: MEDIUM

**As a** 개발자  
**I want** 빠른 확률적 시뮬레이션  
**So that** 대규모 파라미터 탐색이 가능하다

**Description**:
- 병목 구간 프로파일링
- NumPy 벡터화
- Cython 확장 (선택)
- 병렬 실행

**Acceptance Criteria**:
- [ ] 1000 세포 × 1000 에포크 < 10분
- [ ] 메모리 효율화 (< 2GB)
- [ ] 프로파일링 리포트

---

### E3-S9: 유닛 및 통합 테스트 (단백질 변형)
**Points**: 8  
**Priority**: HIGH

**As a** QA  
**I want** 단백질 변형 회로 검증  
**So that** 확률적 시뮬레이션의 정확성을 보장한다

**Description**:
- 유닛 테스트 (Gillespie 알고리즘)
- 통합 테스트 (전체 워크플로우)
- 통계적 검증 (Chi-square 테스트)

**Acceptance Criteria**:
- [ ] `tests/unit/test_protein_mod.py`
- [ ] `tests/integration/test_stochastic_workflow.py`
- [ ] 커버리지 > 85%
- [ ] 통계 테스트 p > 0.05

---

## 📦 Epic 4: 대사 기반 회로 구현

**목표**: 하이브리드 시뮬레이션 및 집단 분포 학습  
**기간**: Sprint 4-5 (Week 7-10)  
**총 Points**: 45

### E4-S1: MetabolicCircuit 클래스 구현
**Points**: 8  
**Priority**: CRITICAL

**As a** 시스템  
**I want** 대사 풀 동역학과 리보스위치  
**So that** 대사 기반 학습 회로를 모델링할 수 있다

**Description**:
- `MetabolicCircuit` 클래스
- 상태: [M, Htot, O] (대사물질, 숨겨진 총량, 출력)
- Hill 함수 기반 리보스위치
- 대사 플럭스

**Acceptance Criteria**:
- [ ] `tccdp/circuits/metabolic.py` 완성
- [ ] Hill 함수 파라미터 (Kd, n)
- [ ] 테스트 커버리지 > 85%

---

### E4-S2: 하이브리드 시뮬레이터 (연속 + 확률적)
**Points**: 8  
**Priority**: CRITICAL

**As a** 시스템  
**I want** 타임스케일이 다른 프로세스 결합  
**So that** 대사(연속)와 번역(확률적)을 함께 시뮬레이션할 수 있다

**Description**:
- 타우리핑 (Tau-leaping) 구현
- 연속-확률 하이브리드 솔버
- 타임스케일 분리 처리

**Acceptance Criteria**:
- [ ] `tccdp/simulators/hybrid.py` 구현
- [ ] 빠른/느린 반응 자동 분류
- [ ] 정확성 검증 (순수 Gillespie와 비교)

---

### E4-S3: 집단 수준 학습 (Bet-Hedging)
**Points**: 5  
**Priority**: HIGH

**As a** 연구자  
**I want** 세포 집단의 베팅 전략 학습  
**So that** 환경 통계를 반영하는지 확인할 수 있다

**Description**:
- 다중 표현형 분포
- KL divergence 최소화
- 환경 변동성 반영

**Acceptance Criteria**:
- [ ] 100+ 세포 시뮬레이션
- [ ] KL divergence 계산
- [ ] 분포 수렴 확인

---

### E4-S4: KL Divergence 및 분포 비교 도구
**Points**: 3  
**Priority**: MEDIUM

**As a** 연구자  
**I want** 분포 간 유사도 측정  
**So that** 학습 성능을 정량화할 수 있다

**Description**:
- KL divergence 계산
- Wasserstein distance
- Jensen-Shannon divergence
- 시각화 (분포 오버레이)

**Acceptance Criteria**:
- [ ] `tccdp/analysis/distributions.py` 모듈
- [ ] 3+ 분포 거리 지표
- [ ] 히스토그램 비교 플롯

---

### E4-S5: 리보스위치 모델링 상세화
**Points**: 3  
**Priority**: MEDIUM

**As a** 시스템  
**I want** 현실적인 리보스위치 반응  
**So that** 실험 데이터와 비교할 수 있다

**Description**:
- 협동성 (cooperativity) 모델링
- 온도 의존성 (선택)
- 리간드 결합 동역학

**Acceptance Criteria**:
- [ ] Hill coefficient 범위 테스트 (n=1-4)
- [ ] Kd 파라미터 스윕
- [ ] 실험 데이터 피팅 예제 (선택)

---

### E4-S6: Jupyter 노트북 예제 3 (집단 분포)
**Points**: 5  
**Priority**: HIGH

**As a** 사용자  
**I want** 집단 수준 학습 예제  
**So that** 베팅 전략이 어떻게 학습되는지 이해할 수 있다

**Description**:
- 집단 시뮬레이션 노트북
- 표현형 분포 진화
- 환경 통계와 비교

**Acceptance Criteria**:
- [ ] `examples/notebooks/03_population_bet_hedging.ipynb`
- [ ] 분포 애니메이션 (선택)
- [ ] KL divergence 시계열
- [ ] 실행 시간 < 15분

---

### E4-S7: 파라미터 스윕 도구
**Points**: 5  
**Priority**: MEDIUM

**As a** 연구자  
**I want** 자동 파라미터 탐색  
**So that** 최적 설정을 찾을 수 있다

**Description**:
- 그리드 서치
- 랜덤 서치
- 베이지안 최적화 (선택)
- 병렬 실행

**Acceptance Criteria**:
- [ ] `tccdp/optimization/sweep.py` 모듈
- [ ] 그리드 & 랜덤 서치 지원
- [ ] 결과 저장 및 시각화
- [ ] 병렬 실행 (multiprocessing)

---

### E4-S8: 유닛 및 통합 테스트 (대사 회로)
**Points**: 8  
**Priority**: HIGH

**As a** QA  
**I want** 대사 회로 및 하이브리드 시뮬레이션 검증  
**So that** 복잡한 시스템의 정확성을 보장한다

**Description**:
- 유닛 테스트 (하이브리드 솔버)
- 통합 테스트 (집단 시뮬레이션)
- 성능 테스트

**Acceptance Criteria**:
- [ ] `tests/unit/test_metabolic.py`
- [ ] `tests/integration/test_hybrid_simulation.py`
- [ ] 커버리지 > 85%
- [ ] 대규모 시뮬레이션 메모리 누수 없음

---

## 📦 Epic 5: 통합 및 분석 플랫폼

**목표**: 세 회로 통합, UI 구현, 고급 분석  
**기간**: Sprint 5-6 (Week 9-12)  
**총 Points**: 58

### E5-S1: 통합 API 및 팩토리 패턴
**Points**: 5  
**Priority**: CRITICAL

**As a** 사용자  
**I want** 일관된 API로 모든 회로 제어  
**So that** 회로 타입에 관계없이 동일한 방식으로 사용할 수 있다

**Description**:
- CircuitFactory 구현
- 통합 TrainingPipeline
- 설정 기반 회로 생성

**Acceptance Criteria**:
- [ ] `tccdp/factory.py` 구현
- [ ] `CircuitFactory.create(circuit_type='transcription')`
- [ ] 모든 회로 타입 지원
- [ ] 통합 테스트

---

### E5-S2: CLI 도구 개발
**Points**: 5  
**Priority**: HIGH

**As a** 사용자  
**I want** 명령줄에서 시뮬레이션 실행  
**So that** 스크립트 자동화 및 배치 실행이 가능하다

**Description**:
- Click 기반 CLI
- 명령: `tccdp train`, `tccdp simulate`, `tccdp analyze`
- 진행 상황 표시
- 로그 출력

**Acceptance Criteria**:
- [ ] `tccdp/cli/commands.py` 구현
- [ ] `tccdp train --config config.yaml` 작동
- [ ] Help 문서 자동 생성
- [ ] 예제 명령어 5개

---

### E5-S3: 웹 대시보드 UI 프레임워크 (React/Streamlit)
**Points**: 13  
**Priority**: HIGH

**As a** 사용자  
**I want** 웹 기반 인터페이스  
**So that** 코드 없이도 시뮬레이션을 설정하고 실행할 수 있다

**Description**:
- Streamlit 또는 React 선택
- Figma 디자인 구현
- 5개 메인 화면 구현
- **미구현 기능은 "Coming Soon" 표시**

**UI Screens** (우선순위):
1. **Dashboard** (필수)
   - 프로젝트 목록
   - Quick Start

2. **Circuit Builder** (필수)
   - 회로 타입 선택
   - 파라미터 입력 폼
   - 프리셋 로드

3. **Training Controller** (필수)
   - 프로토콜 선택
   - 시작/중지 버튼
   - 실시간 그래프 (선택)

4. **Analysis View** (중간 우선순위)
   - 결과 그래프 표시
   - Export 버튼

5. **Results Gallery** (낮은 우선순위)
   - 저장된 실험 목록
   - **미구현 가능**

**Acceptance Criteria**:
- [ ] Streamlit app 실행 (`streamlit run app.py`)
- [ ] Dashboard, Circuit Builder, Training Controller 작동
- [ ] Figma 디자인 80% 반영
- [ ] 반응형 레이아웃 (Desktop)
- [ ] 미구현 섹션 명확히 표시

---

### E5-S4: 실시간 모니터링 (WebSocket/Polling)
**Points**: 5  
**Priority**: MEDIUM

**As a** 사용자  
**I want** 훈련 중 실시간 업데이트  
**So that** 진행 상황을 즉시 확인할 수 있다

**Description**:
- 백그라운드 작업 (Celery 또는 multiprocessing)
- WebSocket 연결
- 실시간 그래프 업데이트

**Acceptance Criteria**:
- [ ] 훈련 시작 → 백그라운드 실행
- [ ] 매 10 에포크마다 업데이트
- [ ] Stop 버튼으로 중단 가능
- [ ] 진행률 표시 (%)

---

### E5-S5: 결과 저장 및 로드 시스템
**Points**: 3  
**Priority**: HIGH

**As a** 사용자  
**I want** 실험 결과 자동 저장  
**So that** 나중에 다시 불러와 분석할 수 있다

**Description**:
- HDF5/Pickle 기반 저장
- 메타데이터 (파라미터, 타임스탬프 등)
- 버전 관리

**Acceptance Criteria**:
- [ ] `tccdp/io/` 모듈
- [ ] `save_experiment()`, `load_experiment()` 함수
- [ ] 압축 지원
- [ ] 하위 호환성

---

### E5-S6: 비교 분석 도구
**Points**: 5  
**Priority**: MEDIUM

**As a** 연구자  
**I want** 여러 실험 결과 비교  
**So that** 파라미터 효과를 분석할 수 있다

**Description**:
- 다중 실험 로드
- 나란히 비교 시각화
- 통계적 유의성 검정

**Acceptance Criteria**:
- [ ] `tccdp/analysis/compare.py` 모듈
- [ ] 최대 10개 실험 동시 비교
- [ ] 박스플롯, 바이올린 플롯
- [ ] t-test, ANOVA 지원

---

### E5-S7: 고급 시각화 (인터랙티브)
**Points**: 5  
**Priority**: MEDIUM

**As a** 사용자  
**I want** 인터랙티브 그래프  
**So that** 데이터를 탐색적으로 분석할 수 있다

**Description**:
- Plotly 기반 인터랙티브 플롯
- 줌, 팬, 호버 정보
- 애니메이션 (시간 경과)

**Acceptance Criteria**:
- [ ] Plotly 통합
- [ ] 3+ 인터랙티브 플롯 타입
- [ ] HTML export
- [ ] 예제 노트북

---

### E5-S8: 민감도 분석 (Sobol)
**Points**: 5  
**Priority**: MEDIUM

**As a** 연구자  
**I want** 파라미터 민감도 정량화  
**So that** 중요한 파라미터를 식별할 수 있다

**Description**:
- Sobol 민감도 분석
- SALib 라이브러리 통합
- 민감도 인덱스 시각화

**Acceptance Criteria**:
- [ ] `tccdp/analysis/sensitivity.py` 모듈
- [ ] Sobol 분석 함수
- [ ] 파라미터 순위 리포트
- [ ] 예제 스크립트

---

### E5-S9: 자동 리포트 생성
**Points**: 3  
**Priority**: LOW

**As a** 사용자  
**I want** 실험 결과 자동 문서화  
**So that** 공유 및 발표가 쉬워진다

**Description**:
- Markdown/PDF 리포트 생성
- 그래프 자동 포함
- 템플릿 커스터마이징

**Acceptance Criteria**:
- [ ] `tccdp/reporting/` 모듈
- [ ] `generate_report()` 함수
- [ ] Markdown → PDF 변환 (pandoc)
- [ ] 예제 템플릿 3개

---

### E5-S10: 성능 벤치마크 및 최적화
**Points**: 5  
**Priority**: MEDIUM

**As a** 개발자  
**I want** 시스템 성능 측정  
**So that** 병목 구간을 최적화할 수 있다

**Description**:
- 프로파일링 (cProfile, line_profiler)
- 메모리 프로파일링 (memory_profiler)
- 최적화 (NumPy, Cython)
- 벤치마크 스위트

**Acceptance Criteria**:
- [ ] `scripts/benchmark.py` 스크립트
- [ ] 주요 작업 성능 측정 (시뮬레이션, 훈련, 분석)
- [ ] 최적화 전후 비교 리포트
- [ ] CI에서 자동 실행

---

### E5-S11: 종합 통합 테스트
**Points**: 8  
**Priority**: CRITICAL

**As a** QA  
**I want** 전체 시스템 통합 검증  
**So that** 릴리스 전 안정성을 확보한다

**Description**:
- 세 회로 모두 포함
- 대규모 시뮬레이션
- UI 통합 테스트 (Selenium/Playwright)
- 성능 회귀 테스트

**Acceptance Criteria**:
- [ ] `tests/integration/test_full_platform.py`
- [ ] 세 회로 순차 실행
- [ ] UI E2E 테스트 (Streamlit)
- [ ] 전체 테스트 시간 < 30분

---

## 📦 Epic 6: 문서화 및 배포

**목표**: 완벽한 문서화 및 공개 릴리스  
**기간**: Sprint 6 (Week 11-12)  
**총 Points**: 38

### E6-S1: API 문서 자동 생성 (Sphinx)
**Points**: 5  
**Priority**: HIGH

**As a** 개발자  
**I want** 자동 생성 API 문서  
**So that** 모든 함수와 클래스가 문서화된다

**Description**:
- Sphinx 설정
- Autodoc 확장
- Napoleon (Google/NumPy 스타일)
- Read the Docs 배포

**Acceptance Criteria**:
- [ ] `docs/` 디렉토리 설정
- [ ] 모든 공개 API 문서화
- [ ] HTML 빌드 성공
- [ ] Read the Docs 배포

---

### E6-S2: 사용자 가이드 작성
**Points**: 8  
**Priority**: CRITICAL

**As a** 신규 사용자  
**I want** 단계별 가이드  
**So that** 빠르게 시작하고 고급 기능을 배울 수 있다

**Description**:
- 설치 가이드
- Quick Start (5분)
- 튜토리얼 (3개 회로 각각)
- 고급 사용법
- FAQ

**Acceptance Criteria**:
- [ ] `docs/user_guide/` 섹션 완성
- [ ] 10+ 페이지
- [ ] 스크린샷 및 코드 예제 포함
- [ ] 초보자도 따라할 수 있는 수준

---

### E6-S3: Jupyter 노트북 갤러리 (10+)
**Points**: 8  
**Priority**: HIGH

**As a** 사용자  
**I want** 다양한 예제 노트북  
**So that** 내 사용 사례에 맞는 시작점을 찾을 수 있다

**Description**:
- 기존 3개 + 추가 7개 노트북
- 다양한 사용 사례 (분류, 회귀, 패턴 학습 등)
- 실험 데이터 피팅 (선택)
- Binder/Colab 링크

**추가 노트북 아이디어**:
4. Supervised Learning (Iris 분류)
5. 파라미터 스윕 및 최적화
6. 민감도 분석
7. 여러 회로 비교
8. 커스텀 훈련 프로토콜
9. 실험 데이터 재현
10. 고급: 커스텀 회로 정의

**Acceptance Criteria**:
- [ ] `examples/notebooks/` 에 10+ 노트북
- [ ] 모두 에러 없이 실행
- [ ] 평균 실행 시간 < 10분
- [ ] README에 노트북 목록 및 설명

---

### E6-S4: 비디오 튜토리얼 (선택)
**Points**: 3  
**Priority**: LOW

**As a** 시각적 학습자  
**I want** 비디오 가이드  
**So that** 보면서 따라할 수 있다

**Description**:
- 화면 녹화 (OBS Studio)
- Quick Start 비디오 (5분)
- 회로별 튜토리얼 (각 10분)
- YouTube 업로드

**Acceptance Criteria**:
- [ ] 3+ 비디오
- [ ] YouTube 플레이리스트
- [ ] 문서에 링크 포함

---

### E6-S5: Docker 이미지 및 배포
**Points**: 3  
**Priority**: HIGH

**As a** 사용자  
**I want** Docker로 즉시 실행  
**So that** 환경 설정 없이 시작할 수 있다

**Description**:
- Dockerfile 작성
- Docker Compose (Jupyter + Streamlit)
- Docker Hub 배포
- 사용 가이드

**Acceptance Criteria**:
- [ ] `docker pull tccdp/platform:latest` 작동
- [ ] `docker-compose up` 으로 전체 스택 실행
- [ ] README에 Docker 사용법
- [ ] 이미지 크기 < 2GB

---

### E6-S6: PyPI 패키지 배포
**Points**: 3  
**Priority**: CRITICAL

**As a** 사용자  
**I want** pip install로 설치  
**So that** 쉽게 프로젝트에 통합할 수 있다

**Description**:
- setup.py / pyproject.toml 완성
- 빌드 및 테스트
- PyPI 업로드
- 버전 관리

**Acceptance Criteria**:
- [ ] `pip install tccdp` 작동
- [ ] 모든 의존성 자동 설치
- [ ] PyPI 페이지 정보 완성
- [ ] 버전 태그 (v1.0.0)

---

### E6-S7: GitHub 릴리스 및 Changelog
**Points**: 2  
**Priority**: HIGH

**As a** 사용자  
**I want** 버전별 변경사항 확인  
**So that** 업데이트 내용을 알 수 있다

**Description**:
- CHANGELOG.md 작성
- GitHub Release 생성
- 릴리스 노트
- 다운로드 가능한 아카이브

**Acceptance Criteria**:
- [ ] CHANGELOG.md (Keep a Changelog 형식)
- [ ] GitHub Release v1.0.0
- [ ] 릴리스 노트 (주요 기능, 버그 수정)
- [ ] 소스 코드 아카이브

---

### E6-S8: 라이선스 및 법적 검토
**Points**: 2  
**Priority**: CRITICAL

**As a** 프로젝트 관리자  
**I want** 명확한 오픈소스 라이선스  
**So that** 법적 문제 없이 배포할 수 있다

**Description**:
- 라이선스 선택 (MIT 또는 Apache 2.0)
- LICENSE 파일 추가
- 의존성 라이선스 확인
- NOTICE 파일 (필요 시)

**Acceptance Criteria**:
- [ ] LICENSE 파일 (MIT 권장)
- [ ] README에 라이선스 뱃지
- [ ] 의존성 라이선스 호환성 확인
- [ ] 저작권 표시

---

### E6-S9: 커뮤니티 론칭 준비
**Points**: 4  
**Priority**: MEDIUM

**As a** 프로젝트 관리자  
**I want** 커뮤니티 참여 유도  
**So that** 사용자 피드백과 기여를 받을 수 있다

**Description**:
- CONTRIBUTING.md 작성
- CODE_OF_CONDUCT.md
- Issue 템플릿
- PR 템플릿
- GitHub Discussions 활성화
- 블로그 포스트 작성

**Acceptance Criteria**:
- [ ] CONTRIBUTING.md (기여 가이드)
- [ ] CODE_OF_CONDUCT.md (행동 강령)
- [ ] .github/ISSUE_TEMPLATE/ (버그, 기능 요청)
- [ ] .github/PULL_REQUEST_TEMPLATE.md
- [ ] 론칭 블로그 포스트 초안

---

## 📊 Story Point 가이드

Story Point는 **복잡도 × 불확실성 × 노력**을 나타냅니다:

| Points | 복잡도 | 시간 (예상) | 예시 |
|--------|--------|-------------|------|
| 1 | 매우 간단 | 1-2 시간 | 설정 파일 추가, 간단한 함수 |
| 2 | 간단 | 2-4 시간 | 유틸리티 함수, 간단한 테스트 |
| 3 | 보통 | 4-8 시간 | 작은 기능, 문서 작성 |
| 5 | 중간 | 1-2 일 | 클래스 구현, 통합 작업 |
| 8 | 복잡 | 2-4 일 | 복잡한 알고리즘, 새로운 모듈 |
| 13 | 매우 복잡 | 4-7 일 | 대규모 기능, UI 구현 |
| 21 | Epic 분할 필요 | > 1 주 | 너무 큼, 더 작은 스토리로 분할 |

---

## 🎯 우선순위 정의

| Priority | 의미 | 처리 |
|----------|------|------|
| CRITICAL | 프로젝트 핵심, 없으면 진행 불가 | Sprint 내 최우선 |
| HIGH | 주요 기능, 릴리스 필수 | Sprint 내 처리 |
| MEDIUM | 개선 사항, 릴리스 권장 | 시간 되면 처리 |
| LOW | 선택 사항, 미래 버전 가능 | Backlog 유지 |

---

## 📝 다음 단계

이제 **Part 2: Sprint Breakdown**에서:
- 각 Sprint별 구체적 계획
- 일일 태스크 분배
- Definition of Done
- Sprint 목표 및 데모

를 작성하겠습니다.
