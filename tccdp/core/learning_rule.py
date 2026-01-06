"""Learning rules for molecular circuits."""

from abc import ABC, abstractmethod
from typing import Callable, Optional
import numpy as np
import numpy.typing as npt


class LearningRule(ABC):
    """Abstract base class for learning rules.
    
    Learning rules define how circuit parameters change during training
    to achieve desired input-output mappings.
    """
    
    def __init__(self, learning_rate: float = 0.01) -> None:
        """Initialize learning rule.
        
        Args:
            learning_rate: Learning rate for parameter updates
        """
        self.learning_rate = learning_rate
    
    @abstractmethod
    def compute_update(
        self,
        error: float,
        state: npt.NDArray[np.float64],
        stimulus: float
    ) -> dict[str, float]:
        """Compute parameter updates based on error signal.
        
        Args:
            error: Difference between desired and actual output
            state: Current circuit state
            stimulus: Input stimulus value
        
        Returns:
            Dictionary of parameter updates {param_name: delta_value}
        """
        pass


class AutoregulationRule(LearningRule):
    """Autoregulation-based learning rule.
    
    This rule implements learning through autoregulation strength (k_H),
    similar to the high-pass filter mechanism in the paper.
    """
    
    def __init__(
        self,
        learning_rate: float = 0.01,
        min_k_H: float = 0.0,
        max_k_H: float = 10.0
    ) -> None:
        """Initialize autoregulation learning rule.
        
        Args:
            learning_rate: Learning rate for k_H updates
            min_k_H: Minimum allowed k_H value
            max_k_H: Maximum allowed k_H value
        """
        super().__init__(learning_rate)
        self.min_k_H = min_k_H
        self.max_k_H = max_k_H
    
    def compute_update(
        self,
        error: float,
        state: npt.NDArray[np.float64],
        stimulus: float
    ) -> dict[str, float]:
        """Compute k_H update based on error.
        
        The autoregulation strength k_H is updated to reduce error:
        - Positive error (output too high) → increase k_H (more negative feedback)
        - Negative error (output too low) → decrease k_H (less negative feedback)
        
        Args:
            error: Output error (actual - desired)
            state: Current circuit state
            stimulus: Input stimulus
        
        Returns:
            Dictionary with k_H update
        """
        # Update k_H proportional to error
        delta_k_H = self.learning_rate * error
        
        return {"k_H": delta_k_H}
    
    def clip_params(self, params: dict[str, float]) -> dict[str, float]:
        """Clip parameters to allowed range.
        
        Args:
            params: Parameters to clip
        
        Returns:
            Clipped parameters
        """
        if "k_H" in params:
            params["k_H"] = np.clip(params["k_H"], self.min_k_H, self.max_k_H)
        return params


class HebbianRule(LearningRule):
    """Hebbian learning rule: strengthen connections that fire together.
    
    Implements the classic "neurons that fire together, wire together" rule,
    adapted for molecular circuits.
    """
    
    def __init__(
        self,
        learning_rate: float = 0.01,
        decay_rate: float = 0.001
    ) -> None:
        """Initialize Hebbian rule.
        
        Args:
            learning_rate: Learning rate for weight updates
            decay_rate: Weight decay to prevent unbounded growth
        """
        super().__init__(learning_rate)
        self.decay_rate = decay_rate
    
    def compute_update(
        self,
        error: float,
        state: npt.NDArray[np.float64],
        stimulus: float
    ) -> dict[str, float]:
        """Compute Hebbian weight updates.
        
        Args:
            error: Output error
            state: Current state (output activity)
            stimulus: Input stimulus (input activity)
        
        Returns:
            Dictionary of parameter updates
        """
        # Output activity (last state variable typically)
        output_activity = state[-1] if len(state) > 0 else 0.0
        
        # Hebbian update: Δw = η * input * output - decay * w
        # Note: actual weight (w) needs to be passed separately in practice
        delta_w = self.learning_rate * stimulus * output_activity
        
        return {"w": delta_w}


class GradientDescentRule(LearningRule):
    """Gradient descent learning rule.
    
    Updates parameters in the direction that reduces error,
    using numerical gradient estimation.
    """
    
    def __init__(
        self,
        learning_rate: float = 0.01,
        epsilon: float = 1e-5
    ) -> None:
        """Initialize gradient descent rule.
        
        Args:
            learning_rate: Learning rate for updates
            epsilon: Small value for numerical gradient estimation
        """
        super().__init__(learning_rate)
        self.epsilon = epsilon
    
    def compute_update(
        self,
        error: float,
        state: npt.NDArray[np.float64],
        stimulus: float
    ) -> dict[str, float]:
        """Compute gradient-based parameter updates.
        
        This is a simplified version. In practice, you would need
        to compute gradients with respect to specific parameters.
        
        Args:
            error: Output error
            state: Current state
            stimulus: Input stimulus
        
        Returns:
            Dictionary of parameter updates
        """
        # Simple gradient estimate (proportional to error)
        # In practice, this would involve backpropagation through the ODE
        return {}  # Placeholder - needs circuit-specific implementation


class RewardModulatedRule(LearningRule):
    """Reward-modulated learning rule.
    
    Similar to reinforcement learning, parameters are updated based on
    a reward signal (e.g., correct prediction = positive reward).
    """
    
    def __init__(
        self,
        learning_rate: float = 0.01,
        baseline: float = 0.0
    ) -> None:
        """Initialize reward-modulated rule.
        
        Args:
            learning_rate: Learning rate
            baseline: Baseline reward for variance reduction
        """
        super().__init__(learning_rate)
        self.baseline = baseline
    
    def compute_update(
        self,
        error: float,
        state: npt.NDArray[np.float64],
        stimulus: float
    ) -> dict[str, float]:
        """Compute reward-modulated updates.
        
        Args:
            error: Output error (negative reward)
            state: Current state
            stimulus: Input stimulus
        
        Returns:
            Dictionary of parameter updates
        """
        # Reward is negative error (lower error = higher reward)
        reward = -abs(error)
        advantage = reward - self.baseline
        
        # Update baseline (moving average)
        self.baseline = 0.9 * self.baseline + 0.1 * reward
        
        # Update proportional to advantage
        delta = self.learning_rate * advantage * stimulus
        
        return {"k_bind": delta}  # Example parameter


# Alias for backward compatibility
PavlovianRule = AutoregulationRule
