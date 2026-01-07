# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Phase 4: Model Integration and Deployment (planned)

## [0.3.0] - 2026-01-07

### Added - Sprint 3: Molecular Dynamics & Stochastic Simulation

#### E3-S1: ProteinModificationCircuit (8pts)
- `ProteinModificationCircuit`: Protein phosphorylation/dephosphorylation signaling circuit
- 3 state variables: U (unphosphorylated), P (phosphorylated), Htot (hidden integrator)
- 6 chemical reactions: phosphorylation, dephosphorylation, degradation, feedback
- ODE system integration: `get_derivatives(t, y, stimulus)` for deterministic simulation
- Stochastic propensities: `get_propensities()` for Gillespie algorithm integration
- Stoichiometry matrix: `get_stoichiometry()` for reaction dynamics
- 3 example circuits: `fast_kinase_response()`, `balanced_dynamics()`, `slow_phosphatase()`
- Factory function: `create_protein_modification_circuit(circuit_type)`
- Parameter validation and biological constraint checking
- 19 test cases with 97% code coverage

#### E3-S2: Gillespie Stochastic Simulator (8pts)
- `GillespieSimulator`: Exact stochastic simulation using Gillespie Direct Method
- Exponential time sampling for event-based kinetic Monte Carlo
- Weighted reaction selection with stoichiometry application
- Ensemble simulation support: Multiple independent trajectories (100-1000 runs)
- Statistical validation: Mean/std computation from ensemble data
- Performance optimization: <1sec for 10K reactions, <10sec for 1000-run ensembles
- Edge case handling: Zero propensity, negative state prevention, boundary conditions
- `CircuitGillespieAdapter`: Convenience adapter for BaseCircuit integration
- 18 test cases with 96% code coverage

### Technical Achievements
- Successfully integrated stochastic simulation with deterministic circuit framework
- Maintained 85% overall code coverage across entire project
- 230/230 unit tests passing (up from 193 in Sprint 2)
- All abstract base class requirements properly implemented
- Comprehensive test coverage for edge cases and ensemble statistics

## [0.2.0] - 2026-01-08

### Added - Sprint 2: Training Pipeline

#### E2-S4: Trainer Implementation
- `Trainer` class with training loop
- `TrainingScheduler` for epoch-based training
- `PavlovianScheduler`: Stimulus-response protocol (CS+ followed by US)
- `SleepWakeScheduler`: Circadian rhythm protocol with sleep/wake cycles
- Early stopping callback with patience and min_delta parameters
- Protocol implementation framework
- 22 test cases covering all trainer functionality

#### E2-S5: Monitoring System
- `TrainingMonitor` orchestrator
- `MonitoringCallback` abstract base class
- `ProgressBarCallback`: Real-time tqdm-based progress display
- `HistoryCallback`: Epoch-level metric recording
- `VisualizationCallback`: Periodic plot generation during training
- `TrainingMetrics` and `TrainingHistory` dataclasses
- 22 test cases for monitoring components

#### E2-S6: Visualization Tools
- `LearningCurveVisualizer`: 4-panel loss/output/stimulus analysis
- `CircuitDynamicsVisualizer`: State evolution and phase portraits
- `save_training_report()`: Complete report generation
- Publication-quality matplotlib figures with configurable DPI
- Graceful handling of missing matplotlib (test-mode compatible)
- 12 test cases covering visualization functionality

#### E2-S7: Command-Line Interface
- CLI with argparse
- `train` command: Execute training with configurable parameters
- `info` command: Display system information and defaults
- `version` command: Show package version
- JSON export for history and summary
- Automatic output directory creation
- 16 test cases for parser, commands, and integration

### Testing & Quality
- **Total Tests**: 163/163 passing (100%)
- **Code Coverage**: 90% (1051 statements, 109 uncovered)
- **Test Modules**: 9 comprehensive test files
- **Key Coverage**:
  - TranscriptionCircuit: 100%
  - ODESimulator: 100%
  - Trainer: 95%
  - TrainingMonitor: 93%
  - CLI: 88%

### Bug Fixes
- Fixed floating-point assertions with pytest.approx()
- Removed conflicting old test files
- Fixed TranscriptionCircuit parameter handling in CLI
- Fixed ODESimulator initialization in CLI

## [0.1.0] - 2026-01-05

### Added
- Project kickoff
- Repository initialization
- Core package structure (tccdp/)
- Testing framework setup
- GitHub Actions CI/CD
- Pre-commit hooks configuration
- Project documentation (README, LICENSE)
- Planning documents (Business Plan, Sprint Plans, GitHub Strategy)

### Infrastructure
- Python package configuration (pyproject.toml)
- .gitignore for Python projects
- Basic unit test samples
- Modular architecture (core, circuits, simulators, training, analysis, ui)

---

*Sprint 1 (Week 1-2): Foundation - In Progress* 🚀
