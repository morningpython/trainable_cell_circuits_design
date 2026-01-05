"""Unit tests for learning rules."""

import pytest
import numpy as np
from tccdp.core.learning_rule import (
    AutoregulationRule,
    HebbianRule,
    GradientDescentRule,
    RewardModulatedRule,
)


class TestAutoregulationRule:
    """Test suite for AutoregulationRule."""
    
    def test_initialization(self):
        """Test rule initializes correctly."""
        rule = AutoregulationRule(learning_rate=0.05)
        
        assert rule.learning_rate == 0.05
        assert rule.min_k_H == 0.0
        assert rule.max_k_H == 10.0
    
    def test_compute_update_positive_error(self):
        """Test update with positive error (output too high)."""
        rule = AutoregulationRule(learning_rate=0.1)
        error = 0.5  # Positive error
        state = np.array([1.0, 2.0])
        stimulus = 1.0
        
        update = rule.compute_update(error, state, stimulus)
        
        assert "k_H" in update
        assert update["k_H"] > 0  # Should increase k_H
        assert update["k_H"] == pytest.approx(0.05)
    
    def test_compute_update_negative_error(self):
        """Test update with negative error (output too low)."""
        rule = AutoregulationRule(learning_rate=0.1)
        error = -0.3  # Negative error
        state = np.array([1.0, 2.0])
        stimulus = 1.0
        
        update = rule.compute_update(error, state, stimulus)
        
        assert update["k_H"] < 0  # Should decrease k_H
        assert update["k_H"] == pytest.approx(-0.03)
    
    def test_clip_params(self):
        """Test parameter clipping."""
        rule = AutoregulationRule(min_k_H=0.0, max_k_H=10.0)
        
        # Test clipping to min
        params = {"k_H": -5.0}
        clipped = rule.clip_params(params)
        assert clipped["k_H"] == 0.0
        
        # Test clipping to max
        params = {"k_H": 20.0}
        clipped = rule.clip_params(params)
        assert clipped["k_H"] == 10.0
        
        # Test no clipping
        params = {"k_H": 5.0}
        clipped = rule.clip_params(params)
        assert clipped["k_H"] == 5.0


class TestHebbianRule:
    """Test suite for HebbianRule."""
    
    def test_initialization(self):
        """Test Hebbian rule initializes correctly."""
        rule = HebbianRule(learning_rate=0.01, decay_rate=0.001)
        
        assert rule.learning_rate == 0.01
        assert rule.decay_rate == 0.001
    
    def test_compute_update(self):
        """Test Hebbian update computation."""
        rule = HebbianRule(learning_rate=0.1)
        error = 0.0  # Not used in Hebbian
        state = np.array([1.0, 2.0, 0.5])  # Last value is output
        stimulus = 1.0
        
        update = rule.compute_update(error, state, stimulus)
        
        assert "w" in update
        # δw = η * input * output = 0.1 * 1.0 * 0.5 = 0.05
        assert update["w"] == pytest.approx(0.05)
    
    def test_hebbian_with_zero_stimulus(self):
        """Test Hebbian update with zero stimulus."""
        rule = HebbianRule(learning_rate=0.1)
        state = np.array([0.5])
        stimulus = 0.0
        
        update = rule.compute_update(0.0, state, stimulus)
        
        assert update["w"] == 0.0
    
    def test_hebbian_with_empty_state(self):
        """Test Hebbian update with empty state."""
        rule = HebbianRule(learning_rate=0.1)
        state = np.array([])
        stimulus = 1.0
        
        update = rule.compute_update(0.0, state, stimulus)
        
        assert update["w"] == 0.0


class TestGradientDescentRule:
    """Test suite for GradientDescentRule."""
    
    def test_initialization(self):
        """Test gradient descent rule initializes correctly."""
        rule = GradientDescentRule(learning_rate=0.01, epsilon=1e-5)
        
        assert rule.learning_rate == 0.01
        assert rule.epsilon == 1e-5
    
    def test_compute_update(self):
        """Test gradient descent update (placeholder)."""
        rule = GradientDescentRule(learning_rate=0.01)
        error = 0.5
        state = np.array([1.0, 2.0])
        stimulus = 1.0
        
        update = rule.compute_update(error, state, stimulus)
        
        # Currently returns empty dict (placeholder)
        assert isinstance(update, dict)


class TestRewardModulatedRule:
    """Test suite for RewardModulatedRule."""
    
    def test_initialization(self):
        """Test reward-modulated rule initializes correctly."""
        rule = RewardModulatedRule(learning_rate=0.01, baseline=0.0)
        
        assert rule.learning_rate == 0.01
        assert rule.baseline == 0.0
    
    def test_compute_update(self):
        """Test reward-modulated update."""
        rule = RewardModulatedRule(learning_rate=0.1, baseline=0.0)
        error = -0.5  # Negative error = positive reward
        state = np.array([1.0])
        stimulus = 1.0
        
        update = rule.compute_update(error, state, stimulus)
        
        assert "k_bind" in update
        # Reward = -|error| = -0.5, advantage = -0.5 - 0.0 = -0.5
        # δ = 0.1 * (-0.5) * 1.0 = -0.05
        assert update["k_bind"] == pytest.approx(-0.05)
    
    def test_baseline_update(self):
        """Test that baseline is updated."""
        rule = RewardModulatedRule(learning_rate=0.1, baseline=0.0)
        
        initial_baseline = rule.baseline
        rule.compute_update(-0.5, np.array([1.0]), 1.0)
        
        # Baseline should have changed
        assert rule.baseline != initial_baseline
    
    def test_multiple_updates(self):
        """Test multiple updates adjust baseline."""
        rule = RewardModulatedRule(learning_rate=0.1, baseline=0.0)
        
        # Multiple updates
        for _ in range(10):
            rule.compute_update(-0.5, np.array([1.0]), 1.0)
        
        # Baseline should converge toward reward
        assert rule.baseline < 0  # Moving toward -0.5
