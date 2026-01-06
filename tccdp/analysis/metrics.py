"""
Performance metrics for training analysis.

This module provides comprehensive metrics for evaluating the performance
of trainable cell circuits, including convergence analysis, learning efficiency,
and statistical measures.
"""

from typing import List, Dict, Optional, Tuple
import numpy as np
from dataclasses import dataclass


@dataclass
class PerformanceMetrics:
    """Container for performance metrics.
    
    Attributes:
        final_loss: Final loss value at end of training
        min_loss: Minimum loss achieved during training
        convergence_epoch: Epoch at which convergence was achieved
        convergence_rate: Rate of convergence (loss reduction per epoch)
        learning_efficiency: Ratio of actual to theoretical learning progress
        mse: Mean squared error
        rmse: Root mean squared error
        mae: Mean absolute error
        r2_score: R-squared score (coefficient of determination)
        settling_time: Time to reach within 5% of final value
        overshoot: Maximum overshoot percentage
        steady_state_error: Final steady-state error
    """
    final_loss: float
    min_loss: float
    convergence_epoch: int
    convergence_rate: float
    learning_efficiency: float
    mse: float
    rmse: float
    mae: float
    r2_score: float
    settling_time: Optional[float] = None
    overshoot: Optional[float] = None
    steady_state_error: Optional[float] = None


def calculate_mse(predictions: np.ndarray, targets: np.ndarray) -> float:
    """Calculate Mean Squared Error.
    
    Args:
        predictions: Predicted values
        targets: Target values
        
    Returns:
        Mean squared error
        
    Example:
        >>> predictions = np.array([1.0, 2.0, 3.0])
        >>> targets = np.array([1.1, 2.1, 2.9])
        >>> mse = calculate_mse(predictions, targets)
        >>> print(f"MSE: {mse:.4f}")
        MSE: 0.0100
    """
    return float(np.mean((predictions - targets) ** 2))


def calculate_rmse(predictions: np.ndarray, targets: np.ndarray) -> float:
    """Calculate Root Mean Squared Error.
    
    Args:
        predictions: Predicted values
        targets: Target values
        
    Returns:
        Root mean squared error
    """
    return float(np.sqrt(calculate_mse(predictions, targets)))


def calculate_mae(predictions: np.ndarray, targets: np.ndarray) -> float:
    """Calculate Mean Absolute Error.
    
    Args:
        predictions: Predicted values
        targets: Target values
        
    Returns:
        Mean absolute error
    """
    return float(np.mean(np.abs(predictions - targets)))


def calculate_r2_score(predictions: np.ndarray, targets: np.ndarray) -> float:
    """Calculate R-squared (coefficient of determination).
    
    Args:
        predictions: Predicted values
        targets: Target values
        
    Returns:
        R-squared score (1.0 is perfect, 0.0 is baseline, negative is worse than baseline)
    """
    ss_res = np.sum((targets - predictions) ** 2)
    ss_tot = np.sum((targets - np.mean(targets)) ** 2)
    
    if ss_tot == 0:
        return 1.0 if ss_res == 0 else 0.0
    
    return float(1.0 - (ss_res / ss_tot))


def find_convergence_epoch(
    losses: List[float],
    threshold: float = 0.01,
    window: int = 10
) -> int:
    """Find the epoch at which training converged.
    
    Convergence is defined as when the loss variation in a sliding window
    falls below the threshold.
    
    Args:
        losses: List of loss values per epoch
        threshold: Maximum allowed variation for convergence
        window: Window size for calculating variation
        
    Returns:
        Epoch index where convergence occurred, or -1 if not converged
    """
    if len(losses) < window:
        return -1
    
    for i in range(window, len(losses)):
        window_losses = losses[i - window:i]
        variation = np.std(window_losses) / (np.mean(window_losses) + 1e-10)
        
        if variation < threshold:
            return i - window
    
    return -1


def calculate_convergence_rate(losses: List[float]) -> float:
    """Calculate the rate of convergence.
    
    Uses linear regression on log(loss) to estimate exponential decay rate.
    
    Args:
        losses: List of loss values per epoch
        
    Returns:
        Convergence rate (negative value indicates decay)
    """
    if len(losses) < 2:
        return 0.0
    
    # Filter out zero or negative losses
    valid_losses = [(i, loss) for i, loss in enumerate(losses) if loss > 0]
    
    if len(valid_losses) < 2:
        return 0.0
    
    epochs = np.array([i for i, _ in valid_losses])
    log_losses = np.log([loss for _, loss in valid_losses])
    
    # Linear regression: log(loss) = a * epoch + b
    coeffs = np.polyfit(epochs, log_losses, 1)
    
    return float(coeffs[0])


def calculate_learning_efficiency(
    initial_loss: float,
    final_loss: float,
    n_epochs: int,
    theoretical_rate: Optional[float] = None
) -> float:
    """Calculate learning efficiency.
    
    Compares actual learning progress to theoretical optimal progress.
    
    Args:
        initial_loss: Loss at start of training
        final_loss: Loss at end of training
        n_epochs: Number of training epochs
        theoretical_rate: Theoretical optimal convergence rate (default: -0.01)
        
    Returns:
        Learning efficiency ratio (1.0 is optimal, >1.0 is better than expected)
    """
    if theoretical_rate is None:
        theoretical_rate = -0.01
    
    if initial_loss <= 0 or final_loss <= 0 or n_epochs <= 0:
        return 0.0
    
    actual_rate = np.log(final_loss / initial_loss) / n_epochs
    
    return float(abs(actual_rate / theoretical_rate))


def calculate_settling_time(
    outputs: np.ndarray,
    times: np.ndarray,
    final_value: Optional[float] = None,
    tolerance: float = 0.05
) -> float:
    """Calculate settling time (time to reach within tolerance of final value).
    
    Args:
        outputs: Output values over time
        times: Time points
        final_value: Final steady-state value (default: mean of last 10%)
        tolerance: Tolerance band (default: 5%)
        
    Returns:
        Settling time in same units as times
    """
    if len(outputs) < 10:
        return float(times[-1])
    
    if final_value is None:
        # Use mean of last 10% as final value
        n_final = max(1, len(outputs) // 10)
        final_value = np.mean(outputs[-n_final:])
    
    lower_bound = final_value * (1 - tolerance)
    upper_bound = final_value * (1 + tolerance)
    
    # Find first time when output enters and stays in tolerance band
    for i in range(len(outputs) - 1, -1, -1):
        if not (lower_bound <= outputs[i] <= upper_bound):
            if i < len(outputs) - 1:
                return float(times[i + 1])
            return float(times[-1])
    
    return float(times[0])


def calculate_overshoot(
    outputs: np.ndarray,
    final_value: Optional[float] = None
) -> float:
    """Calculate maximum overshoot percentage.
    
    Args:
        outputs: Output values over time
        final_value: Final steady-state value (default: mean of last 10%)
        
    Returns:
        Overshoot percentage (0.0 to 100.0+)
    """
    if len(outputs) < 10:
        return 0.0
    
    if final_value is None:
        n_final = max(1, len(outputs) // 10)
        final_value = np.mean(outputs[-n_final:])
    
    if final_value == 0:
        return 0.0
    
    max_value = np.max(outputs)
    overshoot = ((max_value - final_value) / abs(final_value)) * 100
    
    return float(max(0.0, overshoot))


def calculate_steady_state_error(
    outputs: np.ndarray,
    target: float,
    n_samples: Optional[int] = None
) -> float:
    """Calculate steady-state error.
    
    Args:
        outputs: Output values over time
        target: Target value
        n_samples: Number of final samples to average (default: last 10%)
        
    Returns:
        Absolute steady-state error
    """
    if n_samples is None:
        n_samples = max(1, len(outputs) // 10)
    
    final_output = np.mean(outputs[-n_samples:])
    
    return float(abs(target - final_output))


def compute_performance_metrics(
    history: Dict,
    target_value: float = 1.0,
    theoretical_rate: Optional[float] = None
) -> PerformanceMetrics:
    """Compute comprehensive performance metrics from training history.
    
    Args:
        history: Training history dictionary with keys:
            - 'losses': List of loss values
            - 'outputs': List of output values
            - 'epochs': List of epoch numbers (optional)
            - 'stimuli': List of stimuli (optional)
        target_value: Target output value
        theoretical_rate: Theoretical optimal convergence rate
        
    Returns:
        PerformanceMetrics object with all computed metrics
        
    Example:
        >>> history = {
        ...     'losses': [1.0, 0.5, 0.25, 0.15, 0.1],
        ...     'outputs': [0.0, 0.5, 0.8, 0.9, 0.95],
        ...     'epochs': [0, 1, 2, 3, 4]
        ... }
        >>> metrics = compute_performance_metrics(history, target_value=1.0)
        >>> print(f"Final loss: {metrics.final_loss:.4f}")
        >>> print(f"R² score: {metrics.r2_score:.4f}")
    """
    losses = np.array(history['losses'])
    outputs = np.array(history['outputs'])
    
    # Basic metrics
    final_loss = float(losses[-1])
    min_loss = float(np.min(losses))
    
    # Convergence analysis
    convergence_epoch = find_convergence_epoch(losses.tolist())
    convergence_rate = calculate_convergence_rate(losses.tolist())
    
    # Learning efficiency
    learning_efficiency = calculate_learning_efficiency(
        initial_loss=float(losses[0]),
        final_loss=final_loss,
        n_epochs=len(losses),
        theoretical_rate=theoretical_rate
    )
    
    # Error metrics
    targets = np.full_like(outputs, target_value)
    mse = calculate_mse(outputs, targets)
    rmse = calculate_rmse(outputs, targets)
    mae = calculate_mae(outputs, targets)
    r2 = calculate_r2_score(outputs, targets)
    
    # Time-domain metrics (if time information available)
    settling_time = None
    overshoot = None
    steady_state_error = None
    
    if 'epochs' in history or len(outputs) > 10:
        times = np.array(history.get('epochs', range(len(outputs))))
        settling_time = calculate_settling_time(outputs, times, target_value)
        overshoot = calculate_overshoot(outputs, target_value)
        steady_state_error = calculate_steady_state_error(outputs, target_value)
    
    return PerformanceMetrics(
        final_loss=final_loss,
        min_loss=min_loss,
        convergence_epoch=convergence_epoch,
        convergence_rate=convergence_rate,
        learning_efficiency=learning_efficiency,
        mse=mse,
        rmse=rmse,
        mae=mae,
        r2_score=r2,
        settling_time=settling_time,
        overshoot=overshoot,
        steady_state_error=steady_state_error
    )


def print_metrics_summary(metrics: PerformanceMetrics) -> str:
    """Generate a formatted summary of performance metrics.
    
    Args:
        metrics: PerformanceMetrics object
        
    Returns:
        Formatted string summary
    """
    lines = [
        "=" * 60,
        "Performance Metrics Summary",
        "=" * 60,
        "",
        "Loss Metrics:",
        f"  Final Loss:        {metrics.final_loss:.6f}",
        f"  Minimum Loss:      {metrics.min_loss:.6f}",
        "",
        "Convergence Analysis:",
        f"  Convergence Epoch: {metrics.convergence_epoch if metrics.convergence_epoch >= 0 else 'Not converged'}",
        f"  Convergence Rate:  {metrics.convergence_rate:.6f}",
        f"  Learning Efficiency: {metrics.learning_efficiency:.4f}",
        "",
        "Error Metrics:",
        f"  MSE:               {metrics.mse:.6f}",
        f"  RMSE:              {metrics.rmse:.6f}",
        f"  MAE:               {metrics.mae:.6f}",
        f"  R² Score:          {metrics.r2_score:.6f}",
    ]
    
    if metrics.settling_time is not None:
        lines.extend([
            "",
            "Time-Domain Metrics:",
            f"  Settling Time:     {metrics.settling_time:.2f}",
            f"  Overshoot:         {metrics.overshoot:.2f}%",
            f"  SS Error:          {metrics.steady_state_error:.6f}",
        ])
    
    lines.append("=" * 60)
    
    return "\n".join(lines)
