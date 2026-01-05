# Trainable Cell Circuits Design Platform (TCCDP)

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

> 유전자 변형 없이 학습 가능한 분자 회로를 설계하고 시뮬레이션하는 Python 플랫폼

---

## 🧬 프로젝트 개요

**TCCDP**는 2025년 bioRxiv 논문 "Molecular networks can learn without genetic modification"을 기반으로, 세포 내에서 학습 가능한 분자 회로를 시뮬레이션하고 설계할 수 있는 오픈소스 플랫폼입니다.

### 핵심 개념

기존의 합성생물학은 **회로를 설계(design)** 했다면, 이 프로젝트는 **회로가 스스로 학습(learn)** 하도록 만듭니다.

- 🎓 **학습하는 세포**: Pavlov의 개, 신경망처럼 자극에 반응하는 법을 배우는 분자 회로
- 🔬 **3가지 구현 방법**: 전사(Transcription), 단백질 변형(Protein Modification), 대사(Metabolic)
- 🧪 **유전자 변형 불필요**: 기존 세포의 분자 반응만으로 학습 구현

---

## ✨ 주요 기능

### 1. **세 가지 학습 회로**

| 회로 유형 | 메커니즘 | 시뮬레이션 방법 |
|-----------|----------|-----------------|
| **Transcription Circuit** | DNA 전사 조절 | ODE (결정론적) |
| **Protein Modification Circuit** | 단백질 인산화/탈인산화 | Gillespie (확률론적) |
| **Metabolic Circuit** | 리보스위치 기반 대사 | Hybrid (ODE + Gillespie) |

### 2. **강력한 시뮬레이션 엔진**

- **ODE Solver**: SciPy 기반 결정론적 시뮬레이션
- **Gillespie Algorithm**: 확률론적 화학 반응 시뮬레이션
- **Hybrid Simulation**: 빠르고 정확한 결합 시뮬레이션

### 3. **직관적인 사용자 인터페이스**

- 🖥️ **Streamlit Web UI**: 드래그 앤 드롭으로 회로 설계
- 📊 **실시간 시각화**: 분자 농도, 학습 곡선, 성능 메트릭
- 📈 **결과 분석**: 다양한 차트와 통계 분석

### 4. **완전한 개발 도구**

- 🛠️ **CLI**: 명령줄에서 시뮬레이션 실행
- 📓 **Jupyter Notebooks**: 10+ 예제 노트북
- 📚 **API Documentation**: 상세한 개발자 문서

---

## 🚀 빠른 시작

### 설치

```bash
# PyPI에서 설치 (v1.0.0 릴리스 후)
pip install tccdp

# 개발 버전 설치
git clone https://github.com/tccdp/trainable-cell-circuits.git
cd trainable-cell-circuits
pip install -e ".[dev]"
```

### 첫 시뮬레이션 실행

```python
from tccdp.circuits import TranscriptionCircuit
from tccdp.training import TrainingScheduler

# 회로 생성
circuit = TranscriptionCircuit(
    k_bind=0.1,
    k_unbind=0.01,
    k_tx=0.5,
    tau=50.0
)

# 훈련 스케줄러
scheduler = TrainingScheduler(
    protocol="pavlovian",
    n_epochs=100,
    stimulus_duration=10.0
)

# 훈련 실행
results = scheduler.train(circuit)

# 결과 시각화
results.plot_learning_curve()
```

### CLI 사용

```bash
# 기본 훈련
tccdp train --circuit transcription --protocol pavlovian

# 설정 파일 사용
tccdp train --config examples/configs/transcription.yaml

# 결과 분석
tccdp analyze results/run_001/ --output report.html
```

### Web UI 실행

```bash
# Streamlit 대시보드 실행
streamlit run tccdp/ui/app.py

# 브라우저에서 http://localhost:8501 열기
```

---

## 📖 프로젝트 구조

```
trainable_cell_circuits_design/
├── tccdp/                      # 메인 패키지
│   ├── core/                   # 핵심 추상 클래스
│   │   ├── base_circuit.py     # BaseCircuit 인터페이스
│   │   ├── learning_rule.py    # 학습 규칙 정의
│   │   └── high_pass_filter.py # 고주파 필터
│   ├── circuits/               # 회로 구현
│   │   ├── transcription.py    # 전사 기반 회로
│   │   ├── protein_mod.py      # 단백질 변형 회로
│   │   └── metabolic.py        # 대사 회로
│   ├── simulators/             # 시뮬레이션 엔진
│   │   ├── ode_solver.py       # ODE 시뮬레이터
│   │   ├── gillespie.py        # Gillespie 시뮬레이터
│   │   └── hybrid.py           # 하이브리드 시뮬레이터
│   ├── training/               # 훈련 파이프라인
│   │   ├── scheduler.py        # 훈련 스케줄러
│   │   ├── protocols.py        # 훈련 프로토콜
│   │   └── callbacks.py        # 콜백 함수
│   ├── analysis/               # 분석 도구
│   │   ├── metrics.py          # 성능 메트릭
│   │   └── visualization.py    # 시각화
│   ├── models/                 # SBML/Antimony 모델
│   ├── cli/                    # CLI 도구
│   └── ui/                     # Streamlit UI
├── tests/                      # 테스트
│   ├── unit/                   # 유닛 테스트 (60%)
│   ├── component/              # 컴포넌트 테스트 (30%)
│   └── e2e/                    # E2E 테스트 (10%)
├── docs/                       # 문서
├── examples/                   # 예제 노트북
└── planning/                   # 프로젝트 계획 문서
    ├── business_plan.md
    ├── executive_summary.md
    ├── development_plan.md
    ├── sprint_plan_part1_epics_and_stories.md
    ├── sprint_plan_part2_sprint_breakdown.md
    └── github_strategy.md
```

---

## 🧪 예제

### Example 1: 기본 Pavlovian 학습

```python
from tccdp.circuits import TranscriptionCircuit
from tccdp.training import TrainingScheduler

circuit = TranscriptionCircuit()
scheduler = TrainingScheduler(protocol="pavlovian")
results = scheduler.train(circuit)
results.plot()
```

### Example 2: 확률론적 시뮬레이션

```python
from tccdp.circuits import ProteinModificationCircuit
from tccdp.simulators import GillespieSimulator

circuit = ProteinModificationCircuit()
simulator = GillespieSimulator(n_runs=100)
results = simulator.simulate(circuit, t_max=200)
```

### Example 3: 사용자 정의 회로

```python
from tccdp.core import BaseCircuit
import numpy as np

class MyCustomCircuit(BaseCircuit):
    def get_derivatives(self, t, y, stimulus):
        # 커스텀 ODE 정의
        dydt = np.zeros_like(y)
        # ... your equations ...
        return dydt
    
    def get_output(self, state):
        return state[-1]  # 마지막 상태 변수 반환

circuit = MyCustomCircuit()
# 훈련 및 시뮬레이션...
```

---

## 🛠️ 개발

### 개발 환경 설정

```bash
# 저장소 클론
git clone https://github.com/tccdp/trainable-cell-circuits.git
cd trainable-cell-circuits

# 가상환경 생성
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 개발 의존성 설치
pip install -e ".[dev]"

# Pre-commit hooks 설치
pre-commit install
```

### 테스트 실행

```bash
# 전체 테스트
pytest

# 유닛 테스트만
pytest tests/unit/ -v

# 커버리지 리포트
pytest --cov=tccdp --cov-report=html
```

### 코드 품질

```bash
# 포맷팅
black tccdp tests

# 린팅
ruff check .

# 타입 체크
mypy tccdp
```

---

## 📊 개발 로드맵

### Sprint 1 (Week 1-2) - 완료 ✅
- [x] 프로젝트 인프라 구축
- [x] Git 저장소 초기화
- [x] UI/UX 설계 (Figma)

### Sprint 2 (Week 3-4) - 진행 예정
- [ ] TranscriptionCircuit 구현
- [ ] ODE 시뮬레이터
- [ ] 기본 훈련 파이프라인

### Sprint 3-6 (Week 5-12)
- [ ] ProteinModificationCircuit
- [ ] MetabolicCircuit
- [ ] Web UI 개발
- [ ] 문서 및 예제 완성

**v1.0.0 릴리스 목표**: 2026년 3월 30일

---

## 🤝 기여하기

기여를 환영합니다! 자세한 내용은 [CONTRIBUTING.md](CONTRIBUTING.md)를 참조하세요.

### 기여 방법

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/E2-S3-amazing-feature`)
3. Commit your changes (`git commit -m 'feat(circuits): add amazing feature'`)
4. Push to the branch (`git push origin feature/E2-S3-amazing-feature`)
5. Open a Pull Request

---

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

---

## 📚 참고 문헌

- **Main Paper**: "Molecular networks can learn without genetic modification" (2025, bioRxiv)
- **Related**: Pavlovian learning, Hebbian plasticity, Synthetic biology

---

## 👥 팀

- **Tech Lead**: [@tech-lead](https://github.com/tech-lead)
- **Core Team**: 4명의 개발자
- **Community**: 기여자들에게 감사드립니다!

---

## 📞 연락처

- **Email**: team@tccdp.org
- **GitHub Issues**: [Issue Tracker](https://github.com/tccdp/trainable-cell-circuits/issues)
- **Discussions**: [GitHub Discussions](https://github.com/tccdp/trainable-cell-circuits/discussions)

---

**TCCDP** - 세포가 스스로 학습하는 미래를 만듭니다 🧬✨
