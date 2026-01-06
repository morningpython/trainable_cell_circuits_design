"""
Training Protocol Scheduler

Implements various training protocols for molecular circuits:
- Pavlovian conditioning
- Supervised learning
- Reinforcement learning
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
import numpy as np
from numpy.typing import NDArray

from ..simulators.ode_simulator import StimulusProtocol


@dataclass
class TrainingPhase:
    """
    Single phase of training protocol.
    
    Attributes:
        duration: Phase duration [min]
        stimulus: Stimulus value or protocol
        label: Name for this phase (e.g., "conditioned_stimulus")
        reward: Reward signal (for RL-based learning)
    """
    duration: float
    stimulus: float
    label: str = "phase"
    reward: Optional[float] = None
    
    def __post_init__(self):
        """Validate phase parameters."""
        if self.duration <= 0:
            raise ValueError(f"Duration must be positive, got {self.duration}")
        if self.stimulus < 0:
            raise ValueError(f"Stimulus must be non-negative, got {self.stimulus}")


@dataclass
class TrainingProtocol:
    """
    Complete training protocol with multiple phases.
    
    A protocol defines a repeating sequence of phases that
    constitutes one training epoch.
    
    Attributes:
        name: Protocol name
        phases: List of training phases
        repeats: Number of times to repeat this protocol in one epoch
        rest_duration: Rest time between epochs [min]
    """
    name: str
    phases: List[TrainingPhase] = field(default_factory=list)
    repeats: int = 1
    rest_duration: float = 0.0
    
    def __post_init__(self):
        """Validate protocol."""
        if not self.phases:
            raise ValueError("Protocol must have at least one phase")
        if self.repeats < 1:
            raise ValueError(f"Repeats must be >= 1, got {self.repeats}")
        if self.rest_duration < 0:
            raise ValueError(f"Rest duration must be non-negative, got {self.rest_duration}")
    
    @property
    def epoch_duration(self) -> float:
        """
        Total duration of one epoch (all repeats + rest).
        
        Returns:
            Duration in minutes
        """
        phase_duration = sum(p.duration for p in self.phases)
        total = phase_duration * self.repeats + self.rest_duration
        return total
    
    @property
    def cycle_duration(self) -> float:
        """
        Duration of one complete cycle (without rest).
        
        Returns:
            Duration in minutes
        """
        return sum(p.duration for p in self.phases) * self.repeats
    
    def get_phase_at_time(
        self, 
        t_within_epoch: float
    ) -> Tuple[TrainingPhase, float, int]:
        """
        Get which phase is active at given time within epoch.
        
        Args:
            t_within_epoch: Time within current epoch [min]
        
        Returns:
            Tuple of (phase, time_within_phase, repeat_number)
        
        Raises:
            ValueError: If time exceeds cycle duration
        """
        cycle_duration = self.cycle_duration
        if t_within_epoch >= cycle_duration:
            raise ValueError(
                f"Time {t_within_epoch} exceeds cycle duration {cycle_duration}"
            )
        
        # Find which phase and repeat
        phase_sequence_duration = sum(p.duration for p in self.phases)
        
        # Which repeat?
        repeat_num = int(t_within_epoch // phase_sequence_duration)
        t_in_repeat = t_within_epoch % phase_sequence_duration
        
        # Which phase within repeat?
        elapsed = 0.0
        for phase in self.phases:
            if elapsed + phase.duration > t_in_repeat:
                time_in_phase = t_in_repeat - elapsed
                return phase, time_in_phase, repeat_num
            elapsed += phase.duration
        
        # Shouldn't reach here
        raise ValueError("Phase lookup failed")
    
    def get_stimulus_at_time(self, t_within_epoch: float) -> float:
        """
        Get stimulus value at time within epoch.
        
        Args:
            t_within_epoch: Time within current epoch [min]
        
        Returns:
            Stimulus value
        """
        cycle_duration = self.cycle_duration
        
        # Rest period has no stimulus
        if t_within_epoch >= cycle_duration:
            return 0.0
        
        phase, time_in_phase, _ = self.get_phase_at_time(t_within_epoch)
        return phase.stimulus
    
    def get_phases_sequence(self) -> List[TrainingPhase]:
        """
        Get the sequence of phases in one epoch.
        
        Returns:
            List of phases (repeats expanded)
        """
        sequence = []
        for _ in range(self.repeats):
            sequence.extend(self.phases)
        return sequence


class TrainingScheduler:
    """
    Manages training schedule and epoch progression.
    
    Tracks which epoch and phase the training is in,
    and provides stimulus values at any given time.
    
    Example:
        >>> protocol = TrainingProtocol(
        ...     name="pavlovian",
        ...     phases=[
        ...         TrainingPhase(10, 0, "baseline"),
        ...         TrainingPhase(10, 100, "stimulus")
        ...     ],
        ...     repeats=5
        ... )
        >>> scheduler = TrainingScheduler(protocol, n_epochs=100)
        >>> stimulus = scheduler.get_stimulus(0, 5)  # Epoch 0, 5 min
        >>> scheduler.advance_epoch()
    """
    
    def __init__(
        self,
        protocol: TrainingProtocol,
        n_epochs: int = 100,
        verbose: bool = True
    ):
        """
        Initialize training scheduler.
        
        Args:
            protocol: Training protocol to follow
            n_epochs: Total number of epochs
            verbose: Whether to print progress
        """
        self.protocol = protocol
        self.n_epochs = n_epochs
        self.verbose = verbose
        
        self.current_epoch = 0
        self.current_time = 0.0  # Total elapsed time [min]
    
    @property
    def epoch_duration(self) -> float:
        """Duration of one epoch."""
        return self.protocol.epoch_duration
    
    @property
    def total_training_time(self) -> float:
        """Total training time for all epochs."""
        return self.epoch_duration * self.n_epochs
    
    @property
    def is_finished(self) -> bool:
        """Whether training is complete."""
        return self.current_epoch >= self.n_epochs
    
    def get_stimulus(
        self, 
        epoch: int, 
        time_in_epoch: float
    ) -> float:
        """
        Get stimulus at given epoch and time.
        
        Args:
            epoch: Epoch number
            time_in_epoch: Time within epoch [min]
        
        Returns:
            Stimulus value
        """
        if epoch >= self.n_epochs:
            return 0.0
        
        return self.protocol.get_stimulus_at_time(time_in_epoch)
    
    def get_current_stimulus(self, time_in_epoch: float) -> float:
        """
        Get stimulus at current epoch and given time.
        
        Args:
            time_in_epoch: Time within current epoch [min]
        
        Returns:
            Stimulus value
        """
        return self.get_stimulus(self.current_epoch, time_in_epoch)
    
    def advance_epoch(self) -> bool:
        """
        Advance to next epoch.
        
        Returns:
            Whether training is now complete
        """
        self.current_epoch += 1
        self.current_time += self.epoch_duration
        
        if self.verbose and self.current_epoch % 10 == 0:
            print(f"Epoch {self.current_epoch}/{self.n_epochs} "
                  f"(t={self.current_time:.1f} min)")
        
        return self.is_finished
    
    def advance_time(self, dt: float) -> None:
        """
        Advance by given time.
        
        Updates epoch if time exceeds epoch duration.
        
        Args:
            dt: Time increment [min]
        """
        self.current_time += dt
        
        # Update epoch based on total time
        new_epoch = min(int(self.current_time // self.epoch_duration), self.n_epochs)
        if new_epoch > self.current_epoch:
            self.current_epoch = new_epoch
            if self.verbose and self.current_epoch % 10 == 0:
                print(f"Epoch {self.current_epoch}/{self.n_epochs} "
                      f"(t={self.current_time:.1f} min)")
    
    def get_progress(self) -> Dict[str, float]:
        """
        Get training progress.
        
        Returns:
            Dictionary with progress metrics
        """
        return {
            'epoch': self.current_epoch,
            'total_epochs': self.n_epochs,
            'time': self.current_time,
            'total_time': self.total_training_time,
            'progress': self.current_epoch / self.n_epochs if self.n_epochs > 0 else 0.0
        }
    
    def __repr__(self) -> str:
        """String representation."""
        return (
            f"TrainingScheduler("
            f"protocol={self.protocol.name}, "
            f"epoch={self.current_epoch}/{self.n_epochs}, "
            f"time={self.current_time:.1f}/{self.total_training_time:.1f})"
        )


def create_pavlovian_protocol(
    cs_duration: float = 10.0,
    cs_stimulus: float = 50.0,
    us_duration: float = 5.0,
    us_stimulus: float = 100.0,
    iti_duration: float = 10.0,
    repeats_per_epoch: int = 5,
    rest_duration: float = 0.0
) -> TrainingProtocol:
    """
    Create Pavlovian conditioning protocol.
    
    Structure: CS → [CS+US overlap] → Rest period
    
    Args:
        cs_duration: Conditioned stimulus duration [min]
        cs_stimulus: Conditioned stimulus value [nM]
        us_duration: Unconditioned stimulus duration [min]
        us_stimulus: Unconditioned stimulus value [nM]
        iti_duration: Intertrial interval (rest) [min]
        repeats_per_epoch: Number of CS-US pairs per epoch
        rest_duration: Sleep/rest period between epochs [min]
    
    Returns:
        Configured TrainingProtocol
    
    Example:
        >>> protocol = create_pavlovian_protocol(
        ...     cs_duration=10, us_duration=5, repeats_per_epoch=5
        ... )
        >>> scheduler = TrainingScheduler(protocol, n_epochs=100)
    """
    # Phase 1: CS alone
    cs_phase = TrainingPhase(
        duration=cs_duration - us_duration,
        stimulus=cs_stimulus,
        label="CS_alone"
    )
    
    # Phase 2: CS + US overlap
    overlap_phase = TrainingPhase(
        duration=us_duration,
        stimulus=cs_stimulus + us_stimulus,  # Combined stimulus
        label="CS_US_overlap",
        reward=1.0  # Positive reward for correct response
    )
    
    # Phase 3: Intertrial interval (rest)
    iti_phase = TrainingPhase(
        duration=iti_duration,
        stimulus=0.0,
        label="ITI"
    )
    
    return TrainingProtocol(
        name="pavlovian_conditioning",
        phases=[cs_phase, overlap_phase, iti_phase],
        repeats=repeats_per_epoch,
        rest_duration=rest_duration
    )


def create_sleep_wake_protocol(
    wake_duration: float = 30.0,
    wake_stimulus: float = 50.0,
    sleep_duration: float = 30.0,
    repeats_per_epoch: int = 2
) -> TrainingProtocol:
    """
    Create Sleep-Wake cycling protocol.
    
    Structure: Wake period (stimulus) → Sleep period (no stimulus)
    
    Args:
        wake_duration: Waking period duration [min]
        wake_stimulus: Stimulus during wake [nM]
        sleep_duration: Sleep period duration [min]
        repeats_per_epoch: Cycles per epoch
    
    Returns:
        Configured TrainingProtocol
    """
    wake_phase = TrainingPhase(
        duration=wake_duration,
        stimulus=wake_stimulus,
        label="wake"
    )
    
    sleep_phase = TrainingPhase(
        duration=sleep_duration,
        stimulus=0.0,
        label="sleep"
    )
    
    return TrainingProtocol(
        name="sleep_wake_cycling",
        phases=[wake_phase, sleep_phase],
        repeats=repeats_per_epoch,
        rest_duration=0.0
    )
