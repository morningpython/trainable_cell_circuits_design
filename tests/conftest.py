"""Pytest configuration and fixtures for TCCDP tests."""

import pytest
import numpy as np


@pytest.fixture
def sample_timepoints():
    """Sample time points for simulations."""
    return np.linspace(0, 100, 1001)


@pytest.fixture
def default_params():
    """Default parameters for testing."""
    return {
        "k_bind": 0.1,
        "k_unbind": 0.01,
        "k_tx": 0.5,
        "k_tl": 0.3,
        "k_deg": 0.05,
    }
