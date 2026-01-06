"""
Training Loop and Learning Implementation

Implements the training pipeline with error feedback,
parameter updates, and learning dynamics.
"""

from typing import Dict, List, Optional, Tuple, Callable
import numpy as np
from numpy.typing import NDArray
from abc import ABC, abstractmethod

from ..core.base_circuit import BaseCircuit
from ..core.learning_rule import LearningRule, AutoregulationRule
from ..simulators.ode_simulator import ODESimulator, StimulusProtocol
from .scheduler import TrainingScheduler, TrainingProtocol


class Callback(ABC):
    """
    Base callback for monitoring training.
    
    Callbacks are called at various points during training
    to enable monitoring, early stopping, and checkpointing.
    """
    
    @abstractmethod
    def on_epoch_begin(self, epoch: int, logs: Dict) -> None:
        """Called at the start of each epoch."""
        pass
    
    @abstractmethod
    def on_epoch_end(self, epoch: int, logs: Dict) -> None:
        """Called at the end of each epoch."""
        pass


class EarlyStopping(Callback):
    """
    Early stopping callback.
    
    Stops training if validation metric plateaus.
    """
    
    def __init__(self, metric: str = 'loss', patience: int = 20):
        """
        Initialize early stopping.
        
        Args:
            metric: Metric to monitor
            patience: Number of epochs to wait for improvement
        """
        self.metric = metric
        self.patience = patience
        self.best_value = float('inf')
        self.wait_count = 0
        self.should_stop = False
    
    def on_epoch_begin(self, epoch: int, logs: Dict) -> None:
        """Not used."""
        pass
    
    def on_epoch_end(self, epoch: int, logs: Dict) -> None:
        """Check if should stop."""
        current = logs.get(self.metric, float('inf'))
        
        if current < self.best_value:
            self.best_value = current
            self.wait_count = 0
        else:
            self.wait_count += 1
            if self.wait_count >= self.patience:
                self.should_stop = True


class Trainer:
    """
    Training loop for circuit learning.
    
    Implements the full training pipeline:
    1. Simulation with stimulus protocol
    2. Error computation vs. target
    3. Learning update via learning rule
    4. Callback execution
    
    Example:
        >>> circuit = TranscriptionCircuit()
        >>> learning_rule = AutoregulationRule(alpha=0.01)
        >>> protocol = create_pavlovian_protocol()
        >>> trainer = Trainer(circuit, learning_rule, protocol)
        >>> 
        >>> result = trainer.train(
        ...     n_epochs=100,
        ...     dt=1.0,
        ...     target_output=lambda t, phase: 100 if phase.label == "stimulus" else 0
        ... )
    """
    
    def __init__(
        self,
        circuit: BaseCircuit,
        learning_rule: LearningRule,
        protocol: TrainingProtocol,
        simulator: Optional[ODESimulator] = None,
        seed: Optional[int] = None
    ):
        """
        Initialize trainer.
        
        Args:
            circuit: Circuit to train
            learning_rule: Learning algorithm
            protocol: Training protocol
            simulator: ODE simulator (default: RK45)
            seed: Random seed for reproducibility
        """
        self.circuit = circuit
        self.learning_rule = learning_rule
        self.protocol = protocol
        self.simulator = simulator or ODESimulator(circuit)
        
        if seed is not None:
            np.random.seed(seed)
    
    def train(
        self,
        n_epochs: int = 100,
        dt: float = 1.0,
        target_output: Optional[Callable] = None,
        target_learning_param: Optional[Callable] = None,
        callbacks: Optional[List[Callback]] = None,
        verbose: bool = True
    ) -> Dict[str, NDArray]:
        """
        Run training loop.
        
        Args:
            n_epochs: Number of training epochs
            dt: Integration time step [min]
            target_output: Function(phase, t) → target output
            target_learning_param: Function(phase, t) → target param
            callbacks: List of callbacks
            verbose: Whether to print progress
        
        Returns:
            Dictionary with training history
        """
        callbacks = callbacks or []
        scheduler = TrainingScheduler(self.protocol, n_epochs, verbose=verbose)
        
        # Initialize history
        history = {
            'epoch': [],
            'loss': [],
            'output': [],
            'learning_param': [],
            'stimulus': []
        }
        
        # Training loop
        for epoch in range(n_epochs):
            epoch_logs = {}
            
            # Callbacks: epoch begin
            for cb in callbacks:
                cb.on_epoch_begin(epoch, epoch_logs)
            
            # Run one epoch
            epoch_loss, epoch_output, epoch_stim = self._run_epoch(
                epoch=epoch,
                dt=dt,
                target_output=target_output,
                target_learning_param=target_learning_param
            )
            
            # Record history
            history['epoch'].append(epoch)
            history['loss'].append(epoch_loss)
            history['output'].append(epoch_output)
            history['learning_param'].append(
                self.circuit.get_param('H_tot_min') if 'H_tot_min' in self.circuit.params else 0.0
            )
            history['stimulus'].append(epoch_stim)
            
            epoch_logs['loss'] = epoch_loss
            epoch_logs['output'] = epoch_output
            
            # Callbacks: epoch end
            for cb in callbacks:
                cb.on_epoch_end(epoch, epoch_logs)
                if isinstance(cb, EarlyStopping) and cb.should_stop:
                    print(f"Early stopping at epoch {epoch}")
                    break
            
            # Advance scheduler
            scheduler.advance_epoch()
        
        # Convert to arrays
        for key in history:
            if key != 'epoch':
                history[key] = np.array(history[key])
        
        return history
    
    def _run_epoch(
        self,
        epoch: int,
        dt: float,
        target_output: Optional[Callable],
        target_learning_param: Optional[Callable]
    ) -> Tuple[float, float, float]:
        """
        Run one training epoch.
        
        Args:
            epoch: Epoch number
            dt: Time step
            target_output: Target output function
            target_learning_param: Target parameter function
        
        Returns:
            Tuple of (mean_loss, mean_output, mean_stimulus)
        """
        y = self.circuit.get_initial_state()
        epoch_duration = self.protocol.epoch_duration
        cycle_duration = self.protocol.cycle_duration
        
        # Simulate over cycle (not including rest)
        losses = []
        outputs = []
        stimuli = []
        
        t = 0.0
        while t < cycle_duration:
            # Get current phase
            stim = self.protocol.get_stimulus_at_time(t)
            stimuli.append(stim)
            
            # Compute one step
            dydt = self.circuit.get_derivatives(t, y, stim)
            y = y + dydt * dt
            
            # Get output
            output = self.circuit.get_output(y)
            outputs.append(output)
            
            # Compute error if target specified
            if target_output is not None:
                # Get phase for context
                try:
                    phase, t_in_phase, _ = self.protocol.get_phase_at_time(t)
                    target = target_output(phase, t_in_phase)
                    error = target - output
                    loss = error ** 2
                    losses.append(loss)
                    
                    # Update learning rule
                    state_update = self.learning_rule.compute_update(
                        error=error,
                        state=y,
                        stimulus=stim
                    )
                    # Apply learning parameter updates to state
                    state_names = self.circuit.get_state_names()
                    for param_name, delta in state_update.items():
                        if param_name in state_names:
                            idx = state_names.index(param_name)
                            y[idx] = y[idx] + delta * dt
                except ValueError:
                    # In rest period
                    pass
            
            t += dt
        
        # Compute epoch statistics
        mean_loss = np.mean(losses) if losses else 0.0
        mean_output = np.mean(outputs) if outputs else 0.0
        mean_stimulus = np.mean(stimuli) if stimuli else 0.0
        
        return mean_loss, mean_output, mean_stimulus
    
    def simulate_episode(
        self,
        n_steps: int = 100,
        dt: float = 1.0
    ) -> Tuple[NDArray, NDArray, NDArray]:
        """
        Simulate one episode without training.
        
        Args:
            n_steps: Number of steps
            dt: Time step
        
        Returns:
            Tuple of (time, state_trajectory, output_trajectory)
        """
        y = self.circuit.get_initial_state()
        
        times = []
        states = []
        outputs = []
        
        t = 0.0
        for _ in range(n_steps):
            times.append(t)
            states.append(y.copy())
            outputs.append(self.circuit.get_output(y))
            
            # Random stimulus or zero
            stim = 0.0
            dydt = self.circuit.get_derivatives(t, y, stim)
            y = y + dydt * dt
            t += dt
        
        return (
            np.array(times),
            np.array(states).T,
            np.array(outputs)
        )
