"""
ODE Simulator for Deterministic Circuit Simulation

This module provides a deterministic simulator for molecular circuits
using scipy.integrate for solving ordinary differential equations (ODEs).
"""

from typing import Callable, Dict, List, Optional, Tuple, Union
import numpy as np
from numpy.typing import NDArray
from scipy.integrate import solve_ivp

from ..core.base_circuit import BaseCircuit


class StimulusProtocol:
    """
    Defines time-varying stimulus signals for circuit simulation.
    
    Supports various common stimulus patterns:
    - Constant: Fixed value throughout simulation
    - Step: Jumps from one value to another at specified time
    - Pulse: Brief high value, returns to baseline
    - Ramp: Linear increase from start to end value
    - Custom: User-defined function of time
    
    Example:
        >>> # Step stimulus: 0 → 100 nM at t=10 min
        >>> stim = StimulusProtocol.step(step_time=10.0, baseline=0.0, amplitude=100.0)
        >>> stim(5.0)   # Returns 0.0
        >>> stim(15.0)  # Returns 100.0
    """
    
    def __init__(self, func: Callable[[float], float]):
        """
        Initialize with custom stimulus function.
        
        Args:
            func: Function mapping time to stimulus value
        """
        self.func = func
    
    def __call__(self, t: float) -> float:
        """
        Evaluate stimulus at given time.
        
        Args:
            t: Time point [min]
        
        Returns:
            Stimulus value at time t
        """
        return self.func(t)
    
    @staticmethod
    def constant(value: float) -> 'StimulusProtocol':
        """
        Create constant stimulus.
        
        Args:
            value: Constant stimulus value
        
        Returns:
            Stimulus protocol
        """
        return StimulusProtocol(lambda t: value)
    
    @staticmethod
    def step(
        step_time: float, 
        baseline: float = 0.0, 
        amplitude: float = 100.0
    ) -> 'StimulusProtocol':
        """
        Create step stimulus (baseline → amplitude at step_time).
        
        Args:
            step_time: Time of step transition [min]
            baseline: Initial value before step
            amplitude: Value after step
        
        Returns:
            Stimulus protocol
        """
        def step_func(t: float) -> float:
            return amplitude if t >= step_time else baseline
        return StimulusProtocol(step_func)
    
    @staticmethod
    def pulse(
        start_time: float,
        duration: float,
        baseline: float = 0.0,
        amplitude: float = 100.0
    ) -> 'StimulusProtocol':
        """
        Create pulse stimulus (brief high value).
        
        Args:
            start_time: Pulse start time [min]
            duration: Pulse duration [min]
            baseline: Baseline value outside pulse
            amplitude: Value during pulse
        
        Returns:
            Stimulus protocol
        """
        def pulse_func(t: float) -> float:
            if start_time <= t < start_time + duration:
                return amplitude
            return baseline
        return StimulusProtocol(pulse_func)
    
    @staticmethod
    def ramp(
        start_value: float,
        end_value: float,
        start_time: float = 0.0,
        end_time: float = 100.0
    ) -> 'StimulusProtocol':
        """
        Create linear ramp stimulus.
        
        Args:
            start_value: Initial value
            end_value: Final value
            start_time: Ramp start time [min]
            end_time: Ramp end time [min]
        
        Returns:
            Stimulus protocol
        """
        def ramp_func(t: float) -> float:
            if t <= start_time:
                return start_value
            elif t >= end_time:
                return end_value
            else:
                # Linear interpolation
                progress = (t - start_time) / (end_time - start_time)
                return start_value + progress * (end_value - start_value)
        return StimulusProtocol(ramp_func)
    
    @staticmethod
    def custom(func: Callable[[float], float]) -> 'StimulusProtocol':
        """
        Create custom stimulus from function.
        
        Args:
            func: Custom function mapping time to stimulus
        
        Returns:
            Stimulus protocol
        """
        return StimulusProtocol(func)


class ODESimulator:
    """
    Deterministic ODE simulator for molecular circuits.
    
    Uses scipy.integrate.solve_ivp for robust ODE integration with
    adaptive step size control and multiple solver algorithms.
    
    Features:
    - Multiple integration methods (RK45, RK23, DOP853, BDF, LSODA)
    - Adaptive time stepping
    - Event detection (threshold crossings, etc.)
    - Time-varying stimulus protocols
    - Error tolerance control
    
    Example:
        >>> from tccdp.circuits import TranscriptionCircuit
        >>> circuit = TranscriptionCircuit()
        >>> simulator = ODESimulator(circuit)
        >>> stimulus = StimulusProtocol.step(step_time=10.0, amplitude=100.0)
        >>> result = simulator.simulate(
        ...     t_span=(0, 100),
        ...     stimulus=stimulus,
        ...     n_points=1000
        ... )
        >>> t, y = result['t'], result['y']
        >>> output = result['output']
    """
    
    def __init__(
        self,
        circuit: BaseCircuit,
        method: str = 'RK45',
        rtol: float = 1e-6,
        atol: float = 1e-9
    ):
        """
        Initialize ODE simulator.
        
        Args:
            circuit: Circuit to simulate
            method: Integration method ('RK45', 'RK23', 'DOP853', 'BDF', 'LSODA')
            rtol: Relative tolerance for solver
            atol: Absolute tolerance for solver
        """
        self.circuit = circuit
        self.method = method
        self.rtol = rtol
        self.atol = atol
    
    def simulate(
        self,
        t_span: Tuple[float, float],
        stimulus: Union[float, StimulusProtocol],
        y0: Optional[NDArray[np.float64]] = None,
        n_points: int = 1000,
        events: Optional[List[Callable]] = None
    ) -> Dict[str, NDArray[np.float64]]:
        """
        Run deterministic ODE simulation.
        
        Args:
            t_span: Time interval (t_start, t_end) [min]
            stimulus: Stimulus signal (constant value or protocol)
            y0: Initial state (uses circuit default if None)
            n_points: Number of time points to return
            events: Optional list of event functions for solve_ivp
        
        Returns:
            Dictionary with keys:
                't': Time points [min]
                'y': State trajectories [state_vars × time]
                'output': Output signal trajectory
                'stimulus': Stimulus values at time points
                'success': Whether integration succeeded
        """
        # Get initial state
        if y0 is None:
            y0 = self.circuit.get_initial_state()
        
        # Convert stimulus to protocol if constant
        if isinstance(stimulus, (int, float)):
            stim_protocol = StimulusProtocol.constant(float(stimulus))
        else:
            stim_protocol = stimulus
        
        # Define ODE function for solve_ivp
        def ode_func(t: float, y: NDArray[np.float64]) -> NDArray[np.float64]:
            stim_value = stim_protocol(t)
            return self.circuit.get_derivatives(t, y, stim_value)
        
        # Create evaluation time points
        t_eval = np.linspace(t_span[0], t_span[1], n_points)
        
        # Solve ODE system
        sol = solve_ivp(
            fun=ode_func,
            t_span=t_span,
            y0=y0,
            method=self.method,
            t_eval=t_eval,
            rtol=self.rtol,
            atol=self.atol,
            events=events
        )
        
        # Extract output signal at each time point
        output = np.array([self.circuit.get_output(y) for y in sol.y.T])
        
        # Extract stimulus values
        stimulus_values = np.array([stim_protocol(t) for t in sol.t])
        
        return {
            't': sol.t,
            'y': sol.y,
            'output': output,
            'stimulus': stimulus_values,
            'success': sol.success,
            'message': sol.message
        }
    
    def simulate_multiple(
        self,
        t_span: Tuple[float, float],
        stimuli: List[Union[float, StimulusProtocol]],
        y0: Optional[NDArray[np.float64]] = None,
        n_points: int = 1000,
        reset_between: bool = True
    ) -> List[Dict[str, NDArray[np.float64]]]:
        """
        Run multiple simulations with different stimuli.
        
        Useful for training datasets or parameter sweeps.
        
        Args:
            t_span: Time interval for each simulation
            stimuli: List of stimulus protocols
            y0: Initial state (uses circuit default if None)
            n_points: Number of time points per simulation
            reset_between: Whether to reset to y0 between simulations
        
        Returns:
            List of result dictionaries (one per stimulus)
        """
        results = []
        current_y0 = y0
        
        for stim in stimuli:
            result = self.simulate(
                t_span=t_span,
                stimulus=stim,
                y0=current_y0,
                n_points=n_points
            )
            results.append(result)
            
            if not reset_between:
                # Use final state as next initial state
                current_y0 = result['y'][:, -1]
            else:
                # Reset to original y0
                current_y0 = y0
        
        return results
    
    def find_steady_state(
        self,
        stimulus: Union[float, StimulusProtocol],
        y0: Optional[NDArray[np.float64]] = None,
        t_max: float = 1000.0,
        threshold: float = 1e-6
    ) -> Tuple[NDArray[np.float64], bool]:
        """
        Find steady state for given stimulus.
        
        Simulates until derivatives are below threshold or t_max reached.
        
        Args:
            stimulus: Stimulus value or protocol
            y0: Initial state
            t_max: Maximum simulation time
            threshold: Convergence threshold for derivatives
        
        Returns:
            Tuple of (steady_state, converged)
        """
        result = self.simulate(
            t_span=(0, t_max),
            stimulus=stimulus,
            y0=y0,
            n_points=100
        )
        
        # Check if final derivatives are small
        final_state = result['y'][:, -1]
        stim_value = stimulus if isinstance(stimulus, (int, float)) else stimulus(t_max)
        final_derivatives = self.circuit.get_derivatives(t_max, final_state, stim_value)
        
        converged = np.all(np.abs(final_derivatives) < threshold)
        
        return final_state, converged
    
    def __repr__(self) -> str:
        """String representation."""
        return (
            f"ODESimulator("
            f"circuit={self.circuit.__class__.__name__}, "
            f"method={self.method}, "
            f"rtol={self.rtol:.1e}, "
            f"atol={self.atol:.1e})"
        )
