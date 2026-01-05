# Contributing to TCCDP

Thank you for your interest in contributing to the Trainable Cell Circuits Design Platform! 🎉

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/trainable-cell-circuits.git
   cd trainable-cell-circuits
   ```
3. **Set up development environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   pip install -e ".[dev]"
   pre-commit install
   ```

## Development Workflow

### 1. Create a Branch

Follow our branch naming convention:

```bash
# For features (User Stories)
git checkout -b feature/E2-S4-pavlovian-training

# For bug fixes
git checkout -b bugfix/123-fix-import-error

# For documentation
git checkout -b docs/improve-readme
```

### 2. Make Changes

- Write clean, readable code
- Follow PEP 8 style guidelines
- Add docstrings to all public APIs
- Write tests for new functionality

### 3. Run Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/unit/test_my_module.py -v

# Check coverage
pytest --cov=tccdp --cov-report=html
```

### 4. Format and Lint

```bash
# Auto-format code
black tccdp tests

# Check for issues
ruff check .

# Type checking
mypy tccdp
```

### 5. Commit Changes

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```bash
git add .
git commit -m "feat(circuits): add MetabolicCircuit implementation"
```

**Commit message format**:
- `feat(scope): description` - New feature
- `fix(scope): description` - Bug fix
- `docs(scope): description` - Documentation
- `test(scope): description` - Tests
- `refactor(scope): description` - Code refactoring
- `chore(scope): description` - Build/config changes

### 6. Push and Create PR

```bash
git push origin feature/E2-S4-pavlovian-training
```

Then create a Pull Request on GitHub with:
- Clear title following conventional commits
- Description of changes
- Link to related issues
- Screenshots (if UI changes)

## Code Style

### Python

- **Line length**: 88 characters (Black default)
- **Imports**: Sorted with `isort`
- **Docstrings**: Google style
- **Type hints**: Required for public APIs

**Example**:

```python
from typing import Optional
import numpy as np


def train_circuit(
    circuit: BaseCircuit,
    protocol: str,
    n_epochs: int = 100,
    learning_rate: Optional[float] = None,
) -> TrainingResults:
    """Train a molecular circuit using specified protocol.

    Args:
        circuit: The circuit to train
        protocol: Training protocol name (e.g., "pavlovian")
        n_epochs: Number of training epochs
        learning_rate: Learning rate (None for auto)

    Returns:
        Training results with metrics and trajectories

    Raises:
        ValueError: If protocol is unknown
    """
    # Implementation...
    pass
```

### Testing

- **Unit tests**: 60% of test suite
- **Component tests**: 30%
- **E2E tests**: 10%
- **Coverage goal**: 85%+

**Test naming**:
```python
def test_transcription_circuit_initialization():
    """Test TranscriptionCircuit initializes with correct parameters."""
    pass

def test_gillespie_simulator_handles_zero_propensity():
    """Test Gillespie simulator handles zero propensity correctly."""
    pass
```

## Pull Request Guidelines

### PR Checklist

- [ ] Code follows style guidelines
- [ ] Tests added/updated
- [ ] All tests passing
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] No merge conflicts

### PR Size

Keep PRs focused and reasonably sized:
- **XS**: < 10 lines (ideal for docs/fixes)
- **S**: 10-100 lines (good)
- **M**: 100-500 lines (acceptable)
- **L**: 500-1000 lines (consider splitting)
- **XL**: > 1000 lines (must split)

### Review Process

1. **Self-review**: Review your own PR first
2. **CI checks**: Ensure all checks pass
3. **Code review**: Wait for team review (1-2 reviewers)
4. **Address feedback**: Make requested changes
5. **Approval**: Get approval from reviewer(s)
6. **Merge**: Squash and merge to target branch

## Issue Guidelines

### Bug Reports

Use the bug report template:

```markdown
**Describe the bug**
Clear description of the bug

**To Reproduce**
1. Run `tccdp train --config config.yaml`
2. See error

**Expected behavior**
What should happen

**Environment**
- OS: Ubuntu 22.04
- Python: 3.10.5
- TCCDP: 0.3.0
```

### Feature Requests

Explain:
- The problem you're trying to solve
- Proposed solution
- Alternative approaches considered

## Questions?

- **GitHub Discussions**: For general questions
- **GitHub Issues**: For bug reports and features
- **Email**: team@tccdp.org

---

Thank you for contributing! 🚀
