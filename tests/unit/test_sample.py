"""Sample unit test to ensure test framework is working."""

import pytest


def test_sample():
    """Basic test to verify pytest is configured correctly."""
    assert True


def test_imports():
    """Test that main package can be imported."""
    import tccdp

    assert tccdp.__version__ == "0.1.0"


def test_fixtures(sample_timepoints, default_params):
    """Test that fixtures are working."""
    assert len(sample_timepoints) == 1001
    assert "k_bind" in default_params
