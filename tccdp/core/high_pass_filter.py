"""High-pass filter implementation for molecular circuits.

The high-pass filter is a key component that enables learning by filtering out
persistent (low-frequency) signals while allowing transient (high-frequency)
signals to pass through. This is implemented through autoregulation.
"""

from typing import Optional
import numpy as np
import numpy.typing as npt


class HighPassFilter:
    """High-pass filter based on autoregulation.
    
    Implements the equation: dH/dt = (V - H) / τ
    where:
    - V: Input signal (voltage/concentration)
    - H: Filter state (slowly adapting variable)
    - τ: Time constant (larger τ = slower adaptation = higher cutoff frequency)
    
    The output is the difference: V - H
    This gives 0 for constant inputs (DC) and non-zero for changing inputs (AC).
    """
    
    def __init__(self, tau: float = 50.0, initial_state: float = 0.0) -> None:
        """Initialize high-pass filter.
        
        Args:
            tau: Time constant for adaptation (larger = slower, higher cutoff)
            initial_state: Initial value of H
        
        Raises:
            ValueError: If tau is not positive
        """
        if tau <= 0:
            raise ValueError("Time constant tau must be positive")
        
        self.tau = tau
        self.state = initial_state  # H variable
    
    def derivative(self, input_signal: float) -> float:
        """Compute derivative dH/dt.
        
        Args:
            input_signal: Current input value (V)
        
        Returns:
            Derivative dH/dt
        """
        return (input_signal - self.state) / self.tau
    
    def output(self, input_signal: float) -> float:
        """Compute filter output.
        
        Args:
            input_signal: Current input value (V)
        
        Returns:
            Filtered output (V - H)
        """
        return input_signal - self.state
    
    def update(self, input_signal: float, dt: float) -> float:
        """Update filter state using Euler method.
        
        Args:
            input_signal: Current input value (V)
            dt: Time step
        
        Returns:
            Updated filter output
        """
        dH_dt = self.derivative(input_signal)
        self.state += dH_dt * dt
        return self.output(input_signal)
    
    def reset(self, state: float = 0.0) -> None:
        """Reset filter state.
        
        Args:
            state: New state value (default: 0)
        """
        self.state = state
    
    def cutoff_frequency(self) -> float:
        """Calculate cutoff frequency (3dB point).
        
        Returns:
            Cutoff frequency in Hz (assuming time is in seconds)
        """
        return 1.0 / (2.0 * np.pi * self.tau)
    
    def step_response(
        self,
        duration: float,
        dt: float = 0.1,
        step_height: float = 1.0
    ) -> tuple[npt.NDArray[np.float64], npt.NDArray[np.float64]]:
        """Simulate step response.
        
        Args:
            duration: Simulation duration
            dt: Time step
            step_height: Height of step input
        
        Returns:
            Tuple of (time_points, output_values)
        """
        n_steps = int(duration / dt)
        time = np.linspace(0, duration, n_steps)
        output = np.zeros(n_steps)
        
        self.reset()
        
        for i, t in enumerate(time):
            output[i] = self.update(step_height, dt)
        
        return time, output
    
    def frequency_response(
        self,
        frequencies: npt.NDArray[np.float64]
    ) -> tuple[npt.NDArray[np.float64], npt.NDArray[np.float64]]:
        """Compute frequency response (Bode plot).
        
        Args:
            frequencies: Array of frequencies to evaluate (Hz)
        
        Returns:
            Tuple of (magnitude, phase) where:
            - magnitude: |H(jω)| in dB
            - phase: angle(H(jω)) in degrees
        """
        omega = 2 * np.pi * frequencies
        
        # Transfer function: H(s) = s*τ / (s*τ + 1)
        # At s = jω: H(jω) = jω*τ / (jω*τ + 1)
        numerator = 1j * omega * self.tau
        denominator = 1j * omega * self.tau + 1
        H = numerator / denominator
        
        magnitude_db = 20 * np.log10(np.abs(H))
        phase_deg = np.angle(H, deg=True)
        
        return magnitude_db, phase_deg
    
    def __repr__(self) -> str:
        """String representation."""
        return f"HighPassFilter(tau={self.tau:.2f}, state={self.state:.3f})"
    
    def __str__(self) -> str:
        """Human-readable string."""
        f_c = self.cutoff_frequency()
        return f"HighPassFilter(τ={self.tau:.1f}, f_c={f_c:.4f} Hz)"


class AdaptiveHighPassFilter(HighPassFilter):
    """High-pass filter with adaptive time constant.
    
    The time constant τ can be adjusted during learning to change
    the filter characteristics.
    """
    
    def __init__(
        self,
        tau: float = 50.0,
        min_tau: float = 1.0,
        max_tau: float = 1000.0,
        initial_state: float = 0.0
    ) -> None:
        """Initialize adaptive high-pass filter.
        
        Args:
            tau: Initial time constant
            min_tau: Minimum allowed tau
            max_tau: Maximum allowed tau
            initial_state: Initial filter state
        """
        super().__init__(tau, initial_state)
        self.min_tau = min_tau
        self.max_tau = max_tau
    
    def set_tau(self, new_tau: float) -> None:
        """Set new time constant with clipping.
        
        Args:
            new_tau: New time constant value
        """
        self.tau = np.clip(new_tau, self.min_tau, self.max_tau)
    
    def update_tau(self, delta_tau: float) -> None:
        """Update time constant by delta.
        
        Args:
            delta_tau: Change in tau
        """
        self.set_tau(self.tau + delta_tau)
