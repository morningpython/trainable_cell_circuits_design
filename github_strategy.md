# GitHub Strategy: Development Workflow & Best Practices

## 🎯 Overview

**프로젝트**: Trainable Cell Circuits Design Platform (TCCDP)  
**저장소**: `github.com/[organization]/trainable-cell-circuits`  
**방법론**: Agile Scrum + GitFlow (Sprint-adapted)  
**목표**: 안정적이고 추적 가능한 개발 워크플로우 구축

---

## 📋 Table of Contents

1. [Branch Strategy](#branch-strategy)
2. [Commit Convention](#commit-convention)
3. [Pull Request Process](#pull-request-process)
4. [Code Review Guidelines](#code-review-guidelines)
5. [Testing Strategy](#testing-strategy)
6. [Release Management](#release-management)
7. [Issue & Project Management](#issue-project-management)
8. [CI/CD Pipeline](#cicd-pipeline)
9. [Security & Permissions](#security-permissions)

---

## 🌳 Branch Strategy

### Branch Hierarchy

```
main (protected)
  │
  ├── sprint-1 (2주 단위)
  │   ├── feature/E1-S1-dev-environment
  │   ├── feature/E1-S3-ui-design
  │   └── bugfix/fix-import-error
  │
  ├── sprint-2
  │   ├── feature/E2-S1-transcription-circuit
  │   └── feature/E2-S4-pavlovian-training
  │
  └── hotfix/critical-bug-fix (긴급 수정)
```

### Branch Types

#### 1. `main` (Protected)
**목적**: 프로덕션 준비 완료 코드  
**보호 규칙**:
- Direct push 금지
- PR 필수 (최소 1명 승인)
- CI 통과 필수
- Sprint 브랜치에서만 merge 허용

**업데이트 시점**:
- Sprint 종료 시 (2주마다)
- Hotfix 완료 시

**태그**:
- Sprint 완료: `v0.1.0`, `v0.2.0`, ...
- 릴리스: `v1.0.0`, `v1.1.0`, ...

#### 2. `sprint-N` (Sprint Branch)
**목적**: 각 Sprint의 통합 브랜치  
**생명주기**: 2주 (Sprint 기간)

**생성**:
```bash
# Sprint 시작 시
git checkout main
git pull origin main
git checkout -b sprint-1
git push origin sprint-1
```

**관리**:
- Feature 브랜치들이 이 브랜치로 merge
- Sprint 진행 중 안정화
- 테스트 통과 후 main으로 merge

**종료**:
```bash
# Sprint 종료 시
git checkout main
git merge sprint-1 --no-ff
git tag v0.1.0 -m "Sprint 1 completion"
git push origin main --tags
git branch -d sprint-1  # 선택사항 (보관 가능)
```

#### 3. `feature/` (Feature Branch)
**목적**: 개별 User Story 구현  
**명명 규칙**: `feature/[Epic-Story-ID]-[short-description]`

**예시**:
- `feature/E1-S1-dev-environment`
- `feature/E2-S4-pavlovian-training`
- `feature/E5-S3-web-ui-dashboard`

**생성 및 작업**:
```bash
# Sprint 브랜치에서 분기
git checkout sprint-1
git pull origin sprint-1
git checkout -b feature/E1-S3-ui-design

# 작업
git add .
git commit -m "feat(ui): add Dashboard screen in Figma"

# 정기적으로 push
git push origin feature/E1-S3-ui-design
```

**완료 및 PR**:
```bash
# Sprint 브랜치와 동기화
git checkout sprint-1
git pull origin sprint-1
git checkout feature/E1-S3-ui-design
git merge sprint-1

# Conflict 해결 후
git push origin feature/E1-S3-ui-design

# GitHub에서 PR 생성: feature/E1-S3-ui-design → sprint-1
```

#### 4. `bugfix/` (Bugfix Branch)
**목적**: Sprint 내 발견된 버그 수정  
**명명 규칙**: `bugfix/[issue-number]-[short-description]`

**예시**:
- `bugfix/123-fix-import-error`
- `bugfix/456-correct-ode-calculation`

**프로세스**: Feature 브랜치와 동일

#### 5. `hotfix/` (Hotfix Branch)
**목적**: 프로덕션 긴급 수정  
**명명 규칙**: `hotfix/[version]-[short-description]`

**예시**:
- `hotfix/v1.0.1-critical-memory-leak`
- `hotfix/v1.0.2-security-patch`

**특별 규칙**:
- `main`에서 직접 분기
- `main`과 현재 `sprint-N` 양쪽에 merge
- 즉시 릴리스 (v1.0.1, v1.0.2 등)

```bash
# Hotfix 생성
git checkout main
git pull origin main
git checkout -b hotfix/v1.0.1-memory-leak

# 수정 및 커밋
git commit -m "fix(core): resolve memory leak in Gillespie simulator"

# 테스트 후 main에 merge
git checkout main
git merge hotfix/v1.0.1-memory-leak --no-ff
git tag v1.0.1 -m "Hotfix: memory leak"
git push origin main --tags

# 현재 Sprint 브랜치에도 merge
git checkout sprint-3
git merge hotfix/v1.0.1-memory-leak
git push origin sprint-3

# Hotfix 브랜치 삭제
git branch -d hotfix/v1.0.1-memory-leak
```

---

## 📝 Commit Convention

**표준**: Conventional Commits 1.0.0

### Commit Message Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Type (필수)

| Type | 설명 | 예시 |
|------|------|------|
| `feat` | 새로운 기능 추가 | `feat(circuits): add MetabolicCircuit class` |
| `fix` | 버그 수정 | `fix(gillespie): correct propensity calculation` |
| `docs` | 문서 변경 | `docs(readme): update installation guide` |
| `style` | 코드 포맷팅 (기능 변경 없음) | `style(core): apply black formatting` |
| `refactor` | 리팩토링 | `refactor(training): simplify scheduler logic` |
| `test` | 테스트 추가/수정 | `test(unit): add HighPassFilter tests` |
| `chore` | 빌드/설정 변경 | `chore(deps): update numpy to 1.24.0` |
| `perf` | 성능 개선 | `perf(gillespie): optimize loop with NumPy` |
| `ci` | CI/CD 변경 | `ci(github): add coverage report` |
| `revert` | 커밋 되돌리기 | `revert: revert "feat(ui): add dashboard"` |

### Scope (선택, 권장)

**주요 Scope**:
- `core`: 핵심 엔진 (`tccdp/core/`)
- `circuits`: 회로 구현 (`tccdp/circuits/`)
- `simulators`: 시뮬레이터 (`tccdp/simulators/`)
- `training`: 훈련 파이프라인 (`tccdp/training/`)
- `analysis`: 분석 도구 (`tccdp/analysis/`)
- `ui`: 사용자 인터페이스
- `cli`: 명령줄 도구
- `tests`: 테스트
- `docs`: 문서

### Subject (필수)

- 50자 이내
- 소문자 시작
- 마침표 없음
- 명령형 ("add", "fix", not "added", "fixed")
- 영어 사용

### Body (선택)

- 72자마다 줄바꿈
- "무엇을" 그리고 "왜" 변경했는지 설명
- "어떻게"는 코드로 설명

### Footer (선택)

- Breaking changes: `BREAKING CHANGE: <description>`
- Issue 참조: `Closes #123`, `Fixes #456`
- 리뷰어 언급: `Reviewed-by: @username`

### 예시

#### 좋은 예시 ✅

```
feat(circuits): add TranscriptionCircuit with ODE system

Implement the first circuit type for transcription-based learning.
Includes state variables [V, Hmon, C, Htot] and ODE derivatives.
Uses BaseCircuit interface for consistency.

Closes #12
```

```
fix(gillespie): correct propensity calculation for unbinding

Previous implementation incorrectly calculated unbinding rate,
causing simulation divergence. Now uses correct mass-action kinetics.

Fixes #45
```

```
docs(readme): update installation with Docker instructions

Add step-by-step guide for Docker setup.
Include troubleshooting section for common issues.
```

#### 나쁜 예시 ❌

```
updated stuff
```

```
Fixed bug
```

```
WIP
```

### Atomic Commits

**원칙**: 하나의 커밋은 하나의 논리적 변경

**좋은 예시** ✅:
```bash
# 3개의 작은 커밋
git commit -m "feat(core): add HighPassFilter class"
git commit -m "test(core): add HighPassFilter unit tests"
git commit -m "docs(core): add HighPassFilter docstring"
```

**나쁜 예시** ❌:
```bash
# 하나의 큰 커밋
git commit -m "feat: add entire learning algorithm module"
```

---

## 🔀 Pull Request Process

### PR 생성 전 체크리스트

- [ ] 최신 Sprint 브랜치와 동기화
- [ ] 모든 유닛 테스트 로컬 통과
- [ ] 린팅 통과 (`ruff check .`, `black --check .`)
- [ ] 커밋 메시지 규칙 준수
- [ ] 불필요한 파일 제거 (`.pyc`, `__pycache__` 등)

### PR 템플릿

```markdown
## 📋 Description

[Story ID와 간략한 설명]

Implements E1-S3: Complete UI/UX design in Figma

## 🎯 Changes

- Added Dashboard screen with project overview
- Created Circuit Builder with parameter forms
- Designed Training Controller with timeline visualization
- Built component library (20+ components)

## 🧪 Testing

- [ ] Unit tests added/updated
- [ ] All tests passing locally
- [ ] Manual testing completed

### Test Coverage
- Before: 75%
- After: 78%

## 📸 Screenshots (if applicable)

[Figma screenshots or UI screenshots]

## 🔗 Related Issues

Closes #12

## ✅ Checklist

- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Docstrings added/updated
- [ ] Tests added for new functionality
- [ ] Documentation updated
- [ ] No breaking changes (or documented)

## 👥 Reviewers

@tech-lead @backend-dev
```

### PR 제목 규칙

PR 제목도 Conventional Commits 따름:

```
feat(ui): complete Figma design for 5 main screens [E1-S3]
fix(gillespie): resolve simulation divergence issue [E3-S2]
docs(guide): add user installation guide [E6-S2]
```

### PR 크기 가이드

| 크기 | 변경 라인 | 리뷰 시간 | 권장사항 |
|------|-----------|----------|----------|
| XS | < 10 | < 10분 | 이상적 |
| S | 10-100 | < 30분 | 좋음 |
| M | 100-500 | 1-2시간 | 허용 |
| L | 500-1000 | 2-4시간 | 분할 고려 |
| XL | > 1000 | > 4시간 | 반드시 분할 |

**원칙**: 가능한 작게 유지 (하루 작업량 = 1 PR)

### PR 라벨

| 라벨 | 색상 | 용도 |
|------|------|------|
| `feat` | 🟢 Green | 새 기능 |
| `fix` | 🔴 Red | 버그 수정 |
| `docs` | 📘 Blue | 문서 |
| `test` | 🟡 Yellow | 테스트 |
| `WIP` | ⚫ Black | 작업 중 (리뷰 보류) |
| `ready-for-review` | 🟣 Purple | 리뷰 요청 |
| `approved` | 🟢 Green | 승인됨 |
| `needs-changes` | 🟠 Orange | 수정 필요 |
| `blocked` | 🔴 Red | 블로킹 이슈 있음 |

---

## 👀 Code Review Guidelines

### Reviewer 책임

1. **기능 검증**
   - 요구사항 충족 확인
   - Acceptance Criteria 체크

2. **코드 품질**
   - 가독성, 유지보수성
   - DRY, SOLID 원칙
   - 적절한 추상화

3. **테스트**
   - 테스트 커버리지
   - 엣지 케이스 처리
   - 테스트 품질

4. **문서화**
   - Docstring 완성도
   - 주석 명확성
   - README 업데이트

5. **성능**
   - 병목 구간 식별
   - 메모리 누수
   - 불필요한 연산

### Review Comment Types

#### 1. **P0 (Must Fix)** - 반드시 수정
```markdown
**P0**: This will cause a crash when Htot is zero.
Please add a check for division by zero.
```

#### 2. **P1 (Should Fix)** - 강력 권장
```markdown
**P1**: This logic is hard to follow.
Consider extracting to a separate method with a descriptive name.
```

#### 3. **P2 (Nice to Have)** - 선택사항
```markdown
**P2 (nit)**: Minor style inconsistency.
Could use list comprehension here for conciseness.
```

#### 4. **Question** - 이해를 위한 질문
```markdown
**Q**: Why did you choose tau=50 here?
Is this from the paper or empirical testing?
```

#### 5. **Praise** - 좋은 코드 칭찬
```markdown
**👍**: Excellent docstring! Very clear explanation.
```

### Review Turnaround Time

| Priority | SLA |
|----------|-----|
| Hotfix | 2시간 이내 |
| Critical (블로커) | 1일 이내 |
| Normal | 2일 이내 |
| Low (docs, refactor) | 3일 이내 |

### Approval 기준

**최소 승인 수**: 1명 (작은 PR), 2명 (큰 PR, 핵심 기능)

**승인 전 확인사항**:
- [ ] CI 통과 (모든 체크 ✅)
- [ ] P0 코멘트 모두 해결
- [ ] P1 코멘트 대부분 해결 (또는 후속 이슈 생성)
- [ ] 테스트 커버리지 기준 충족
- [ ] 충돌(Conflict) 없음

### Self-Review Checklist

PR 생성 전 스스로 체크:

```markdown
## Self-Review Checklist

### Code Quality
- [ ] No commented-out code
- [ ] No debug print statements
- [ ] Consistent naming conventions
- [ ] No magic numbers (use constants)

### Testing
- [ ] All new functions have tests
- [ ] Edge cases covered
- [ ] Error handling tested

### Documentation
- [ ] Docstrings for public APIs
- [ ] Complex logic has comments
- [ ] README updated if needed

### Performance
- [ ] No obvious performance issues
- [ ] Large datasets handled efficiently
- [ ] Memory usage reasonable

### Security
- [ ] No hardcoded secrets
- [ ] Input validation present
- [ ] No SQL injection risks
```

---

## 🧪 Testing Strategy

### Test Pyramid (Recap)

```
       /\
      /E2E\       10% (느림, 비쌈)
     /------\
    /Component\   30% (중간)
   /------------\
  /    Unit     \ 60% (빠름, 저렴)
 /----------------\
```

### Pre-Commit Hooks (권장)

```bash
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black
  
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.0.260
    hooks:
      - id: ruff
  
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.2.0
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
  
  - repo: local
    hooks:
      - id: pytest-quick
        name: pytest-quick
        entry: pytest tests/unit/ -v --maxfail=1
        language: system
        pass_filenames: false
```

설치:
```bash
pip install pre-commit
pre-commit install
```

### Testing Workflow

```bash
# 개발 중 (빠른 피드백)
pytest tests/unit/test_my_module.py -v

# 커밋 전 (유닛 테스트만)
pytest tests/unit/ -v

# PR 전 (전체)
pytest tests/ -v --cov=tccdp --cov-report=html

# Sprint 종료 전 (E2E 포함)
pytest tests/ -v --slow --cov=tccdp
```

### Coverage Requirements

| Sprint | Target | Gate |
|--------|--------|------|
| 1-2 | 70% | 65% (warning) |
| 3-4 | 80% | 75% (warning) |
| 5-6 | 85% | 80% (fail) |

**CI Gate**: 커버리지가 최소 기준 미달 시 PR merge 차단

---

## 📦 Release Management

### Versioning (Semantic Versioning)

**Format**: `vMAJOR.MINOR.PATCH`

- **MAJOR**: Breaking changes (v1.0.0 → v2.0.0)
- **MINOR**: 새 기능 (v1.0.0 → v1.1.0)
- **PATCH**: 버그 수정 (v1.0.0 → v1.0.1)

### Version Timeline

| Sprint | Version | Type | Notes |
|--------|---------|------|-------|
| 1 | v0.1.0 | Alpha | 프로젝트 기반 |
| 2 | v0.2.0 | Alpha | 전사 회로 핵심 |
| 3 | v0.3.0 | Beta | 전사 완성 + 확률적 시작 |
| 4 | v0.4.0 | Beta | 확률적 완성 + 대사 시작 |
| 5 | v0.5.0 | RC | 대사 완성 + UI |
| 6 | **v1.0.0** | **Release** | 공개 릴리스 |

### Release Process

#### Sprint 종료 시 (Minor Release)

```bash
# 1. Sprint 브랜치를 main에 merge
git checkout main
git pull origin main
git merge sprint-3 --no-ff -m "chore(release): Sprint 3 completion"

# 2. 버전 태그
git tag v0.3.0 -a -m "Sprint 3: Transcription complete + Stochastic start"

# 3. CHANGELOG 업데이트 (자동 또는 수동)
# ... edit CHANGELOG.md ...
git add CHANGELOG.md
git commit -m "docs(changelog): update for v0.3.0"

# 4. Push
git push origin main --tags
```

#### 최종 릴리스 (v1.0.0)

```bash
# 1. Release 브랜치 생성
git checkout main
git checkout -b release/v1.0.0

# 2. 버전 번호 업데이트
# tccdp/__init__.py
__version__ = "1.0.0"

# pyproject.toml
version = "1.0.0"

git commit -am "chore(release): bump version to 1.0.0"

# 3. 최종 테스트
pytest tests/ -v --slow
pytest tests/e2e/ -v

# 4. Main에 merge
git checkout main
git merge release/v1.0.0 --no-ff
git tag v1.0.0 -a -m "Release v1.0.0: First public release"

# 5. GitHub Release 생성 (웹 UI 또는 CLI)
gh release create v1.0.0 \
  --title "v1.0.0 - First Public Release" \
  --notes-file RELEASE_NOTES.md

# 6. PyPI 배포
python -m build
twine upload dist/*

# 7. Docker 배포
docker build -t tccdp/platform:1.0.0 .
docker push tccdp/platform:1.0.0
docker tag tccdp/platform:1.0.0 tccdp/platform:latest
docker push tccdp/platform:latest
```

### CHANGELOG Format

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.0] - 2026-03-30

### Added
- TranscriptionCircuit with ODE simulation
- ProteinModificationCircuit with Gillespie simulation
- MetabolicCircuit with hybrid simulation
- Streamlit web UI (Dashboard, Circuit Builder, Training)
- CLI tool (`tccdp train`, `tccdp analyze`)
- 10+ Jupyter notebook examples
- Comprehensive documentation (API, User Guide)

### Changed
- Improved performance of Gillespie simulator (2x faster)

### Fixed
- Memory leak in long-running simulations (#234)
- Division by zero in HighPassFilter (#189)

### Deprecated
- Old config format (use YAML instead)

### Security
- Updated dependencies to patch vulnerabilities

## [0.5.0] - 2026-03-16

...
```

---

## 📋 Issue & Project Management

### Issue Templates

#### Bug Report
```markdown
---
name: Bug Report
about: Report a bug or unexpected behavior
labels: bug
assignees: ''
---

**Describe the bug**
A clear description of what the bug is.

**To Reproduce**
Steps to reproduce:
1. Run `tccdp train --config config.yaml`
2. See error

**Expected behavior**
What you expected to happen.

**Actual behavior**
What actually happened.

**Environment:**
- OS: [e.g., Ubuntu 22.04]
- Python version: [e.g., 3.10.5]
- TCCDP version: [e.g., 0.3.0]

**Logs/Screenshots**
Paste relevant logs or screenshots.

**Additional context**
Any other context about the problem.
```

#### Feature Request
```markdown
---
name: Feature Request
about: Suggest a new feature
labels: enhancement
assignees: ''
---

**Is your feature request related to a problem?**
A clear description of the problem.

**Describe the solution you'd like**
What you want to happen.

**Describe alternatives you've considered**
Other solutions you've thought about.

**Additional context**
Any other context or screenshots.
```

#### User Story (Internal)
```markdown
---
name: User Story
about: New user story for sprint planning
labels: story
assignees: ''
---

**Story ID:** E3-S5

**As a** [role]
**I want** [feature]
**So that** [benefit]

**Description:**
[Detailed description]

**Acceptance Criteria:**
- [ ] Criterion 1
- [ ] Criterion 2

**Estimation:** [points]

**Dependencies:**
- E3-S1, E3-S2
```

### Issue Labels

| Category | Labels | Color |
|----------|--------|-------|
| **Type** | `bug`, `enhancement`, `docs`, `question` | 🔴🟢📘🟡 |
| **Priority** | `P0-critical`, `P1-high`, `P2-medium`, `P3-low` | 🔴🟠🟡🟢 |
| **Status** | `todo`, `in-progress`, `blocked`, `done` | ⚫🔵🔴🟢 |
| **Epic** | `E1-foundation`, `E2-transcription`, ... | 🟣 |
| **Component** | `core`, `circuits`, `ui`, `tests`, `docs` | 🔵 |

### Project Board (GitHub Projects)

**Structure**: Kanban Board per Sprint

**Columns**:
1. **Backlog** - Sprint에 포함될 Story들
2. **Todo** - Sprint에 선택됨, 아직 시작 안 함
3. **In Progress** - 현재 작업 중
4. **In Review** - PR 생성됨, 리뷰 중
5. **Done** - Sprint 내 완료

**Automation**:
- Issue 생성 → Backlog
- PR 생성 → In Review
- PR merge → Done

---

## ⚙️ CI/CD Pipeline

### GitHub Actions Workflow

#### Main CI Pipeline

```yaml
# .github/workflows/ci.yml

name: CI

on:
  push:
    branches: [main, sprint-*]
  pull_request:
    branches: [main, sprint-*]

jobs:
  lint:
    name: Lint & Format Check
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          pip install ruff black mypy
      
      - name: Run ruff
        run: ruff check .
      
      - name: Run black
        run: black --check .
      
      - name: Run mypy
        run: mypy tccdp

  test:
    name: Test Suite
    needs: lint
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
        python-version: ['3.10', '3.11']
    
    runs-on: ${{ matrix.os }}
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}
      
      - name: Install dependencies
        run: |
          pip install -e .
          pip install -r requirements-dev.txt
      
      - name: Run unit tests
        run: pytest tests/unit/ -v --cov=tccdp --cov-report=xml
      
      - name: Run component tests
        run: pytest tests/component/ -v
      
      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
          flags: unittests
          name: codecov-${{ matrix.os }}-py${{ matrix.python-version }}

  e2e:
    name: E2E Tests
    needs: test
    runs-on: ubuntu-latest
    if: github.event_name == 'pull_request' && contains(github.base_ref, 'sprint')
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          pip install -e .
          pip install -r requirements-dev.txt
      
      - name: Run E2E tests
        run: pytest tests/e2e/ -v --slow
        timeout-minutes: 30

  coverage-gate:
    name: Coverage Gate
    needs: test
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          pip install -e .
          pip install -r requirements-dev.txt
      
      - name: Check coverage
        run: |
          pytest --cov=tccdp --cov-report=term --cov-fail-under=80
```

#### Release Pipeline

```yaml
# .github/workflows/release.yml

name: Release

on:
  push:
    tags:
      - 'v*'

jobs:
  build:
    name: Build & Publish
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install build tools
        run: |
          pip install build twine
      
      - name: Build package
        run: python -m build
      
      - name: Publish to PyPI
        env:
          TWINE_USERNAME: __token__
          TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
        run: twine upload dist/*
      
      - name: Create GitHub Release
        uses: softprops/action-gh-release@v1
        with:
          files: |
            dist/*.tar.gz
            dist/*.whl
          generate_release_notes: true
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}

  docker:
    name: Build & Push Docker Image
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2
      
      - name: Login to Docker Hub
        uses: docker/login-action@v2
        with:
          username: ${{ secrets.DOCKER_USERNAME }}
          password: ${{ secrets.DOCKER_PASSWORD }}
      
      - name: Extract version from tag
        id: get_version
        run: echo "VERSION=${GITHUB_REF#refs/tags/v}" >> $GITHUB_OUTPUT
      
      - name: Build and push
        uses: docker/build-push-action@v4
        with:
          context: .
          push: true
          tags: |
            tccdp/platform:${{ steps.get_version.outputs.VERSION }}
            tccdp/platform:latest
```

### Status Checks (Required)

PR이 merge되기 전 통과해야 할 체크:

- ✅ **Lint** (ruff, black, mypy)
- ✅ **Unit Tests** (모든 OS/Python 버전)
- ✅ **Component Tests**
- ✅ **Coverage Gate** (>= 80%)
- ✅ **Code Review** (최소 1명 승인)

선택 (Sprint 종료 시):
- ⭕ **E2E Tests** (느림, Sprint merge 전에만)

---

## 🔒 Security & Permissions

### Branch Protection Rules

#### `main` Branch
```yaml
Protection Rules:
  Require pull request reviews:
    - Required approving reviews: 2
    - Dismiss stale reviews: true
    - Require review from Code Owners: true
  
  Require status checks to pass:
    - Require branches to be up to date: true
    - Status checks:
      - lint
      - test (ubuntu, 3.10)
      - test (windows, 3.10)
      - coverage-gate
  
  Require conversation resolution: true
  Require signed commits: false (권장: true)
  Require linear history: true
  
  Restrictions:
    - Allow force pushes: false
    - Allow deletions: false
```

#### `sprint-*` Branches
```yaml
Protection Rules:
  Require pull request reviews:
    - Required approving reviews: 1
  
  Require status checks to pass:
    - Status checks:
      - lint
      - test (ubuntu, 3.10)
  
  Allow force pushes: false
  Allow deletions: false (Sprint 종료 후 삭제 가능)
```

### Repository Permissions

| Role | Permissions | Members |
|------|-------------|---------|
| **Admin** | Full access, settings | Tech Lead |
| **Maintainer** | Push to protected branches (with PR) | Core team (4명) |
| **Write** | Create branches, PRs | Contributors |
| **Read** | View code, clone | Public |

### Secrets Management

**GitHub Secrets** (Settings → Secrets):
- `PYPI_API_TOKEN`: PyPI 배포용 토큰
- `DOCKER_USERNAME`, `DOCKER_PASSWORD`: Docker Hub
- `CODECOV_TOKEN`: Codecov 통합
- `SLACK_WEBHOOK`: 알림용 (선택)

**절대 커밋하지 말 것**:
- API keys, tokens
- 비밀번호
- 개인 식별 정보

**`.gitignore`에 추가**:
```
.env
.env.local
secrets.yaml
*.key
*.pem
```

### Dependency Security

**Dependabot 활성화**:
```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 10
```

**정기 스캔**:
```bash
# 보안 취약점 스캔
pip install safety
safety check --json

# 라이선스 확인
pip install pip-licenses
pip-licenses --format=markdown
```

---

## 📊 Metrics & Monitoring

### Development Metrics

**추적 지표**:
1. **Velocity**: Sprint당 완료된 Story Points
2. **Lead Time**: Issue 생성 → PR merge
3. **PR Size**: 평균 변경 라인 수
4. **Review Time**: PR 생성 → 첫 리뷰
5. **Merge Time**: PR 생성 → merge
6. **Test Coverage**: 전체 코드 커버리지
7. **Build Success Rate**: CI 통과율

**Dashboard**: GitHub Insights 활용

### Code Quality Metrics

**SonarQube/CodeClimate** (선택):
- 코드 중복률
- 복잡도 (Cyclomatic Complexity)
- 기술 부채
- 보안 취약점

---

## 🎯 Best Practices Summary

### ✅ Do's

1. **작은 PR**: 하루 작업량, 500줄 이내
2. **자주 커밋**: 논리적 단위로 나눠서
3. **명확한 메시지**: Conventional Commits
4. **테스트 먼저**: TDD 권장
5. **리뷰 요청**: Draft PR로 조기 피드백
6. **문서화**: 코드와 함께 문서 업데이트
7. **동기화**: 자주 pull/rebase
8. **CI 신뢰**: 로컬 통과 != CI 통과

### ❌ Don'ts

1. **직접 push**: main/sprint 브랜치에 절대 금지
2. **WIP 커밋**: "WIP", "temp" 등 금지
3. **거대한 PR**: 1000줄 이상 피하기
4. **테스트 스킵**: CI 통과 필수
5. **리뷰 없이 merge**: 최소 1명 승인 필수
6. **Force push**: 공유 브랜치에 금지
7. **Squash 남용**: 히스토리 보존 중요
8. **무의미한 커밋**: "fix", "update" 금지

---

## 📚 Resources

### References
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Semantic Versioning](https://semver.org/)
- [Keep a Changelog](https://keepachangelog.com/)
- [GitHub Flow](https://guides.github.com/introduction/flow/)
- [Git Best Practices](https://git-scm.com/book/en/v2)

### Tools
- [GitHub CLI](https://cli.github.com/)
- [pre-commit](https://pre-commit.com/)
- [commitizen](https://commitizen-tools.github.io/commitizen/)
- [semantic-release](https://semantic-release.gitbook.io/)

---

## 🎉 Conclusion

이 GitHub Strategy는 **12주간의 안정적이고 추적 가능한 개발**을 보장합니다.

**핵심 원칙**:
- 🌳 **명확한 브랜치 전략**: Sprint 중심 GitFlow
- 📝 **표준화된 커밋**: Conventional Commits
- 🔀 **체계적인 PR**: 작고 자주, 철저한 리뷰
- 🧪 **자동화된 테스트**: CI/CD로 품질 보장
- 🔒 **보안 중심**: Protected branches, secrets 관리

**성공 지표**:
- ✅ PR merge 시간 < 2일
- ✅ CI 통과율 > 95%
- ✅ 커버리지 > 85%
- ✅ 브랜치 충돌률 < 5%

**이제 Sprint 1을 시작할 준비가 완료되었습니다! 🚀**

---

*Trainable Cell Circuits Design Platform*  
*GitHub Strategy v1.0 - Clean Code, Clean History*
