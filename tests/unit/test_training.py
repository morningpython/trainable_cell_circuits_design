"""
Unit tests for Training Scheduler and Trainer.
"""

import pytest
import numpy as np

from tccdp.training.scheduler import (
    TrainingPhase, TrainingProtocol, TrainingScheduler,
    create_pavlovian_protocol, create_sleep_wake_protocol
)
from tccdp.training.trainer import Trainer, EarlyStopping, Callback
from tccdp.circuits.transcription_circuit import TranscriptionCircuit
from tccdp.core.learning_rule import AutoregulationRule


class TestTrainingPhase:
    """Test TrainingPhase dataclass."""
    
    def test_initialization(self):
        """Test phase initialization."""
        phase = TrainingPhase(
            duration=10.0,
            stimulus=50.0,
            label="stimulus"
        )
        
        assert phase.duration == 10.0
        assert phase.stimulus == 50.0
        assert phase.label == "stimulus"
        assert phase.reward is None
    
    def test_invalid_duration(self):
        """Test phase with invalid duration."""
        with pytest.raises(ValueError):
            TrainingPhase(duration=0.0, stimulus=50.0)
        
        with pytest.raises(ValueError):
            TrainingPhase(duration=-1.0, stimulus=50.0)
    
    def test_invalid_stimulus(self):
        """Test phase with invalid stimulus."""
        with pytest.raises(ValueError):
            TrainingPhase(duration=10.0, stimulus=-1.0)


class TestTrainingProtocol:
    """Test TrainingProtocol class."""
    
    def test_initialization(self):
        """Test protocol initialization."""
        phases = [
            TrainingPhase(10, 0, "baseline"),
            TrainingPhase(10, 100, "stimulus")
        ]
        protocol = TrainingProtocol(
            name="test",
            phases=phases,
            repeats=5
        )
        
        assert protocol.name == "test"
        assert len(protocol.phases) == 2
        assert protocol.repeats == 5
    
    def test_epoch_duration(self):
        """Test epoch duration calculation."""
        phases = [
            TrainingPhase(10, 0, "baseline"),
            TrainingPhase(10, 100, "stimulus")
        ]
        protocol = TrainingProtocol(
            name="test",
            phases=phases,
            repeats=5,
            rest_duration=20.0
        )
        
        # 2 phases × 5 repeats + 20 rest = 120
        expected = (10 + 10) * 5 + 20.0
        assert protocol.epoch_duration == expected
    
    def test_cycle_duration(self):
        """Test cycle duration (without rest)."""
        phases = [
            TrainingPhase(10, 0),
            TrainingPhase(10, 100)
        ]
        protocol = TrainingProtocol(
            name="test",
            phases=phases,
            repeats=5
        )
        
        # 2 phases × 5 repeats = 100
        expected = (10 + 10) * 5
        assert protocol.cycle_duration == expected
    
    def test_get_stimulus_at_time(self):
        """Test stimulus retrieval."""
        phases = [
            TrainingPhase(10, 0, "baseline"),
            TrainingPhase(10, 100, "stimulus")
        ]
        protocol = TrainingProtocol(
            name="test",
            phases=phases,
            repeats=2
        )
        
        # First phase
        assert protocol.get_stimulus_at_time(5.0) == 0.0
        
        # Second phase
        assert protocol.get_stimulus_at_time(15.0) == 100.0
        
        # After cycle (rest)
        assert protocol.get_stimulus_at_time(41.0) == 0.0
    
    def test_get_phase_at_time(self):
        """Test phase lookup."""
        phases = [
            TrainingPhase(10, 0, "baseline"),
            TrainingPhase(10, 100, "stimulus")
        ]
        protocol = TrainingProtocol(
            name="test",
            phases=phases,
            repeats=2
        )
        
        # First phase, first repeat
        phase, t_in_phase, repeat = protocol.get_phase_at_time(5.0)
        assert phase.stimulus == 0.0
        assert t_in_phase == 5.0
        assert repeat == 0
        
        # Second phase, first repeat
        phase, t_in_phase, repeat = protocol.get_phase_at_time(15.0)
        assert phase.stimulus == 100.0
        assert t_in_phase == 5.0
        assert repeat == 0
        
        # Second repeat
        phase, t_in_phase, repeat = protocol.get_phase_at_time(25.0)
        assert phase.stimulus == 0.0
        assert repeat == 1


class TestTrainingScheduler:
    """Test TrainingScheduler class."""
    
    def test_initialization(self):
        """Test scheduler initialization."""
        protocol = create_pavlovian_protocol()
        scheduler = TrainingScheduler(protocol, n_epochs=100, verbose=False)
        
        assert scheduler.current_epoch == 0
        assert scheduler.n_epochs == 100
        assert scheduler.is_finished is False
    
    def test_stimulus_at_epoch_and_time(self):
        """Test stimulus retrieval."""
        protocol = create_pavlovian_protocol(
            cs_duration=10,
            repeats_per_epoch=2,
            rest_duration=0
        )
        scheduler = TrainingScheduler(protocol, n_epochs=5, verbose=False)
        
        # Should get stimulus from protocol
        stim = scheduler.get_stimulus(0, 5.0)
        assert isinstance(stim, float)
        assert stim >= 0.0
    
    def test_advance_epoch(self):
        """Test epoch advancement."""
        protocol = create_pavlovian_protocol()
        scheduler = TrainingScheduler(protocol, n_epochs=10, verbose=False)
        
        assert scheduler.current_epoch == 0
        scheduler.advance_epoch()
        assert scheduler.current_epoch == 1
        
        # Advance to end
        for _ in range(9):
            scheduler.advance_epoch()
        assert scheduler.is_finished
    
    def test_get_progress(self):
        """Test progress reporting."""
        protocol = create_pavlovian_protocol()
        scheduler = TrainingScheduler(protocol, n_epochs=100, verbose=False)
        
        progress = scheduler.get_progress()
        assert progress['epoch'] == 0
        assert progress['total_epochs'] == 100
        assert 0 <= progress['progress'] <= 1.0


class TestPavlovianProtocol:
    """Test Pavlovian protocol factory."""
    
    def test_creation(self):
        """Test protocol creation."""
        protocol = create_pavlovian_protocol(
            cs_duration=10,
            cs_stimulus=50,
            us_duration=5,
            us_stimulus=100,
            iti_duration=10
        )
        
        assert protocol.name == "pavlovian_conditioning"
        assert len(protocol.phases) == 3
        assert protocol.repeats == 5  # default
    
    def test_phase_sequence(self):
        """Test protocol phase sequence."""
        protocol = create_pavlovian_protocol(
            cs_duration=10,
            repeats_per_epoch=2
        )
        
        # Check phases
        assert len(protocol.phases) == 3
        assert protocol.phases[0].label == "CS_alone"
        assert protocol.phases[1].label == "CS_US_overlap"
        assert protocol.phases[2].label == "ITI"


class TestSleepWakeProtocol:
    """Test Sleep-Wake protocol factory."""
    
    def test_creation(self):
        """Test protocol creation."""
        protocol = create_sleep_wake_protocol(
            wake_duration=30,
            wake_stimulus=50,
            sleep_duration=30
        )
        
        assert protocol.name == "sleep_wake_cycling"
        assert len(protocol.phases) == 2
    
    def test_stimulus_pattern(self):
        """Test stimulus pattern."""
        protocol = create_sleep_wake_protocol(
            wake_duration=10,
            wake_stimulus=100,
            sleep_duration=10
        )
        
        # Wake period
        assert protocol.get_stimulus_at_time(5.0) == 100.0
        
        # Sleep period
        assert protocol.get_stimulus_at_time(15.0) == 0.0


class TestEarlyStopping:
    """Test EarlyStopping callback."""
    
    def test_improvement(self):
        """Test early stopping with improving metric."""
        callback = EarlyStopping(metric='loss', patience=3)
        
        # Improving loss
        callback.on_epoch_end(0, {'loss': 1.0})
        assert callback.should_stop is False
        
        callback.on_epoch_end(1, {'loss': 0.9})
        assert callback.should_stop is False
    
    def test_plateau(self):
        """Test early stopping with plateauing metric."""
        callback = EarlyStopping(metric='loss', patience=2)
        
        # Initial improvement
        callback.on_epoch_end(0, {'loss': 1.0})
        callback.on_epoch_end(1, {'loss': 0.95})
        
        # Plateau
        callback.on_epoch_end(2, {'loss': 0.95})
        callback.on_epoch_end(3, {'loss': 0.95})
        
        # Should stop after patience exceeded
        assert callback.should_stop is True


class TestTrainer:
    """Test Trainer class."""
    
    def test_initialization(self):
        """Test trainer initialization."""
        circuit = TranscriptionCircuit()
        rule = AutoregulationRule(learning_rate=0.01)
        protocol = create_pavlovian_protocol(repeats_per_epoch=1)
        
        trainer = Trainer(
            circuit=circuit,
            learning_rule=rule,
            protocol=protocol,
            seed=42
        )
        
        assert trainer.circuit is circuit
        assert trainer.learning_rule is rule
    
    def test_train_basic(self):
        """Test basic training."""
        circuit = TranscriptionCircuit()
        rule = AutoregulationRule(learning_rate=0.01)
        protocol = create_pavlovian_protocol(repeats_per_epoch=1)
        
        trainer = Trainer(
            circuit=circuit,
            learning_rule=rule,
            protocol=protocol,
            seed=42
        )
        
        # Simple target function
        def target_fn(phase, t):
            if phase.label in ["CS_alone", "CS_US_overlap"]:
                return 100.0
            return 0.0
        
        history = trainer.train(
            n_epochs=5,
            dt=1.0,
            target_output=target_fn,
            verbose=False
        )
        
        # Check history
        assert 'epoch' in history
        assert 'loss' in history
        assert 'output' in history
        assert len(history['epoch']) == 5
    
    def test_train_with_early_stopping(self):
        """Test training with early stopping."""
        circuit = TranscriptionCircuit()
        rule = AutoregulationRule(learning_rate=0.01)
        protocol = create_pavlovian_protocol(repeats_per_epoch=1)
        
        trainer = Trainer(
            circuit=circuit,
            learning_rule=rule,
            protocol=protocol
        )
        
        callback = EarlyStopping(metric='loss', patience=50)
        
        def target_fn(phase, t):
            return 100.0 if phase.label in ["CS_alone", "CS_US_overlap"] else 0.0
        
        history = trainer.train(
            n_epochs=100,
            dt=1.0,
            target_output=target_fn,
            callbacks=[callback],
            verbose=False
        )
        
        # Should have trained with early stopping
        assert len(history['epoch']) > 0
    
    def test_simulate_episode(self):
        """Test episode simulation."""
        circuit = TranscriptionCircuit()
        rule = AutoregulationRule(learning_rate=0.01)
        protocol = create_pavlovian_protocol(repeats_per_epoch=1)
        
        trainer = Trainer(circuit, rule, protocol)
        
        times, states, outputs = trainer.simulate_episode(n_steps=50, dt=1.0)
        
        assert len(times) == 50
        assert states.shape[1] == 50
        assert len(outputs) == 50
