"""
Unit tests for performance metrics module.
"""

import pytest
import numpy as np
from tccdp.analysis.metrics import (
    PerformanceMetrics,
    calculate_mse,
    calculate_rmse,
    calculate_mae,
    calculate_r2_score,
    find_convergence_epoch,
    calculate_convergence_rate,
    calculate_learning_efficiency,
    calculate_settling_time,
    calculate_overshoot,
    calculate_steady_state_error,
    compute_performance_metrics,
    print_metrics_summary,
)


class TestBasicMetrics:
    """Tests for basic error metrics."""
    
    def test_calculate_mse_perfect(self):
        """Test MSE with perfect predictions."""
        predictions = np.array([1.0, 2.0, 3.0])
        targets = np.array([1.0, 2.0, 3.0])
        mse = calculate_mse(predictions, targets)
        assert mse == 0.0
    
    def test_calculate_mse_nonzero(self):
        """Test MSE with prediction errors."""
        predictions = np.array([1.0, 2.0, 3.0])
        targets = np.array([1.1, 2.1, 2.9])
        mse = calculate_mse(predictions, targets)
        expected = np.mean([0.01, 0.01, 0.01])
        assert abs(mse - expected) < 1e-6
    
    def test_calculate_rmse(self):
        """Test RMSE calculation."""
        predictions = np.array([1.0, 2.0, 3.0])
        targets = np.array([1.1, 2.1, 2.9])
        rmse = calculate_rmse(predictions, targets)
        expected = np.sqrt(0.01)
        assert abs(rmse - expected) < 1e-6
    
    def test_calculate_mae(self):
        """Test MAE calculation."""
        predictions = np.array([1.0, 2.0, 3.0])
        targets = np.array([1.1, 1.9, 3.2])
        mae = calculate_mae(predictions, targets)
        expected = np.mean([0.1, 0.1, 0.2])
        assert abs(mae - expected) < 1e-6
    
    def test_calculate_r2_score_perfect(self):
        """Test R² score with perfect fit."""
        predictions = np.array([1.0, 2.0, 3.0, 4.0])
        targets = np.array([1.0, 2.0, 3.0, 4.0])
        r2 = calculate_r2_score(predictions, targets)
        assert abs(r2 - 1.0) < 1e-6
    
    def test_calculate_r2_score_baseline(self):
        """Test R² score at baseline (predicting mean)."""
        targets = np.array([1.0, 2.0, 3.0, 4.0])
        predictions = np.full_like(targets, np.mean(targets))
        r2 = calculate_r2_score(predictions, targets)
        assert abs(r2 - 0.0) < 1e-6
    
    def test_calculate_r2_score_negative(self):
        """Test R² score worse than baseline."""
        targets = np.array([1.0, 2.0, 3.0, 4.0])
        predictions = np.array([4.0, 3.0, 2.0, 1.0])
        r2 = calculate_r2_score(predictions, targets)
        assert r2 < 0.0


class TestConvergenceMetrics:
    """Tests for convergence analysis."""
    
    def test_find_convergence_epoch_converged(self):
        """Test finding convergence epoch when converged."""
        losses = [1.0, 0.5, 0.3, 0.25, 0.24, 0.24, 0.24, 0.24, 0.24, 0.24, 0.24, 0.24]
        epoch = find_convergence_epoch(losses, threshold=0.01, window=5)
        assert epoch >= 0
        assert epoch < len(losses)
    
    def test_find_convergence_epoch_not_converged(self):
        """Test when training hasn't converged."""
        losses = [1.0, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1]
        epoch = find_convergence_epoch(losses, threshold=0.01, window=5)
        assert epoch == -1
    
    def test_find_convergence_epoch_short_history(self):
        """Test with history shorter than window."""
        losses = [1.0, 0.5, 0.3]
        epoch = find_convergence_epoch(losses, threshold=0.01, window=10)
        assert epoch == -1
    
    def test_calculate_convergence_rate_decay(self):
        """Test convergence rate calculation with exponential decay."""
        # Exponential decay: loss = exp(-0.1 * epoch)
        epochs = np.arange(20)
        losses = np.exp(-0.1 * epochs)
        rate = calculate_convergence_rate(losses.tolist())
        assert rate < 0  # Should be negative (decay)
        assert abs(rate - (-0.1)) < 0.05  # Should be close to -0.1
    
    def test_calculate_convergence_rate_short(self):
        """Test with single loss value."""
        losses = [1.0]
        rate = calculate_convergence_rate(losses)
        assert rate == 0.0
    
    def test_calculate_learning_efficiency(self):
        """Test learning efficiency calculation."""
        efficiency = calculate_learning_efficiency(
            initial_loss=1.0,
            final_loss=0.1,
            n_epochs=100,
            theoretical_rate=-0.01
        )
        assert efficiency > 0
    
    def test_calculate_learning_efficiency_no_learning(self):
        """Test efficiency when no learning occurred."""
        efficiency = calculate_learning_efficiency(
            initial_loss=1.0,
            final_loss=1.0,
            n_epochs=100
        )
        assert efficiency == 0.0


class TestTimeDomainMetrics:
    """Tests for time-domain analysis."""
    
    def test_calculate_settling_time(self):
        """Test settling time calculation."""
        # Step response that settles quickly
        times = np.linspace(0, 10, 100)
        outputs = 1.0 - np.exp(-times)  # Exponential approach to 1.0
        settling_time = calculate_settling_time(outputs, times, final_value=1.0)
        assert settling_time > 0
        assert settling_time < times[-1]
    
    def test_calculate_settling_time_default_final(self):
        """Test settling time with default final value."""
        times = np.linspace(0, 10, 100)
        outputs = np.ones_like(times)
        outputs[:50] = 0.5
        settling_time = calculate_settling_time(outputs, times)
        assert settling_time >= 0
    
    def test_calculate_overshoot_none(self):
        """Test overshoot calculation with no overshoot."""
        outputs = np.linspace(0, 1, 100)
        overshoot = calculate_overshoot(outputs, final_value=1.0)
        assert overshoot == 0.0
    
    def test_calculate_overshoot_present(self):
        """Test overshoot calculation with overshoot."""
        outputs = np.concatenate([
            np.linspace(0, 1.2, 50),  # Overshoot to 1.2
            np.linspace(1.2, 1.0, 50)  # Settle to 1.0
        ])
        overshoot = calculate_overshoot(outputs, final_value=1.0)
        assert overshoot > 0
        assert overshoot <= 20.0  # 20% overshoot
    
    def test_calculate_steady_state_error(self):
        """Test steady-state error calculation."""
        outputs = np.full(100, 0.95)
        error = calculate_steady_state_error(outputs, target=1.0)
        assert abs(error - 0.05) < 1e-6
    
    def test_calculate_steady_state_error_perfect(self):
        """Test with zero steady-state error."""
        outputs = np.full(100, 1.0)
        error = calculate_steady_state_error(outputs, target=1.0)
        assert abs(error) < 1e-6


class TestPerformanceMetricsIntegration:
    """Integration tests for complete metrics computation."""
    
    def test_compute_performance_metrics_basic(self):
        """Test computing complete performance metrics."""
        history = {
            'losses': [1.0, 0.5, 0.25, 0.15, 0.1, 0.08, 0.07],
            'outputs': [0.0, 0.5, 0.8, 0.9, 0.95, 0.97, 0.98],
            'epochs': [0, 1, 2, 3, 4, 5, 6]
        }
        
        metrics = compute_performance_metrics(history, target_value=1.0)
        
        assert isinstance(metrics, PerformanceMetrics)
        assert metrics.final_loss > 0
        assert metrics.min_loss > 0
        assert metrics.mse >= 0
        assert metrics.rmse >= 0
        assert metrics.mae >= 0
        assert metrics.r2_score <= 1.0
        assert metrics.convergence_rate < 0  # Loss should be decreasing
    
    def test_compute_performance_metrics_with_time_domain(self):
        """Test metrics with time-domain analysis."""
        n_epochs = 100
        epochs = np.arange(n_epochs)
        losses = np.exp(-0.05 * epochs)
        outputs = 1.0 - np.exp(-0.1 * epochs)
        
        history = {
            'losses': losses.tolist(),
            'outputs': outputs.tolist(),
            'epochs': epochs.tolist()
        }
        
        metrics = compute_performance_metrics(history, target_value=1.0)
        
        assert metrics.settling_time is not None
        assert metrics.overshoot is not None
        assert metrics.steady_state_error is not None
        assert metrics.settling_time > 0
        assert metrics.overshoot >= 0
    
    def test_compute_performance_metrics_minimal(self):
        """Test with minimal history (no epochs)."""
        history = {
            'losses': [1.0, 0.5, 0.25],
            'outputs': [0.0, 0.5, 0.8],
        }
        
        metrics = compute_performance_metrics(history)
        
        assert metrics.final_loss == 0.25
        assert metrics.mse > 0
    
    def test_print_metrics_summary(self):
        """Test metrics summary formatting."""
        metrics = PerformanceMetrics(
            final_loss=0.1,
            min_loss=0.05,
            convergence_epoch=50,
            convergence_rate=-0.02,
            learning_efficiency=1.5,
            mse=0.01,
            rmse=0.1,
            mae=0.08,
            r2_score=0.95,
            settling_time=45.0,
            overshoot=5.0,
            steady_state_error=0.02
        )
        
        summary = print_metrics_summary(metrics)
        
        assert isinstance(summary, str)
        assert "Performance Metrics Summary" in summary
        assert "0.1" in summary  # Final loss
        assert "0.95" in summary  # R² score
        assert "45.0" in summary  # Settling time
    
    def test_print_metrics_summary_no_time_domain(self):
        """Test summary without time-domain metrics."""
        metrics = PerformanceMetrics(
            final_loss=0.1,
            min_loss=0.05,
            convergence_epoch=-1,
            convergence_rate=-0.02,
            learning_efficiency=1.5,
            mse=0.01,
            rmse=0.1,
            mae=0.08,
            r2_score=0.95
        )
        
        summary = print_metrics_summary(metrics)
        
        assert isinstance(summary, str)
        assert "Not converged" in summary
        assert "Settling Time" not in summary


class TestEdgeCases:
    """Tests for edge cases and error handling."""
    
    def test_empty_arrays(self):
        """Test with empty arrays."""
        predictions = np.array([])
        targets = np.array([])
        
        # Should handle gracefully (NumPy will return nan)
        mse = calculate_mse(predictions, targets)
        assert np.isnan(mse)
    
    def test_single_value(self):
        """Test with single value."""
        predictions = np.array([1.0])
        targets = np.array([1.1])
        
        mse = calculate_mse(predictions, targets)
        assert abs(mse - 0.01) < 1e-6
    
    def test_zero_target_r2(self):
        """Test R² with constant zero targets."""
        predictions = np.array([0.1, 0.2, 0.3])
        targets = np.array([0.0, 0.0, 0.0])
        
        r2 = calculate_r2_score(predictions, targets)
        assert r2 == 0.0  # Special case handling
    
    def test_convergence_all_zeros(self):
        """Test convergence with all zero losses."""
        losses = [0.0] * 20
        epoch = find_convergence_epoch(losses)
        assert epoch >= 0  # Should find convergence
    
    def test_learning_efficiency_zero_loss(self):
        """Test efficiency with zero final loss."""
        efficiency = calculate_learning_efficiency(
            initial_loss=1.0,
            final_loss=0.0,
            n_epochs=100
        )
        assert efficiency == 0.0  # Should handle gracefully
