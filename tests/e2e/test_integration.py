"""
End-to-end integration tests for TCCDP.

These tests verify that all components work together correctly
in realistic scenarios.
"""

import pytest
import tempfile
import os
import json
import numpy as np

from tccdp.circuits import TranscriptionCircuit
from tccdp.simulators import ODESimulator, StimulusProtocol
from tccdp.core import (
    AutoregulationRule,
    HebbianRule,
    GradientDescentRule,
)
from tccdp.analysis import compute_performance_metrics


class TestBasicSimulation:
    """Test basic simulation workflow."""
    
    def test_circuit_creation(self):
        """Test circuit creation."""
        circuit = TranscriptionCircuit()
        assert circuit is not None
    
    def test_simulator_creation(self):
        """Test simulator creation."""
        circuit = TranscriptionCircuit()
        simulator = ODESimulator(circuit=circuit)
        assert simulator is not None
    
    def test_basic_simulation(self):
        """Test basic simulation."""
        circuit = TranscriptionCircuit()
        simulator = ODESimulator(circuit=circuit)
        
        results = simulator.simulate(
            t_span=(0, 50),
            stimulus=lambda t: 1.0,
            n_points=500
        )
        
        assert results['success']
        assert len(results['t']) == 500
        assert len(results['output']) == 500
        assert all(not np.isnan(out) for out in results['output'])


class TestSimulusProtocols:
    """Test stimulus protocol functionality."""
    
    def test_constant_stimulus(self):
        """Test constant stimulus."""
        stim = StimulusProtocol.constant(2.0)
        assert stim(0) == 2.0
        assert stim(100) == 2.0
    
    def test_step_stimulus(self):
        """Test step stimulus."""
        stim = StimulusProtocol.step(step_time=10.0, amplitude=2.0)
        assert stim(5.0) == 0.0  # Before step
        assert stim(15.0) == 2.0  # After step
    
    def test_pulse_stimulus(self):
        """Test pulse stimulus."""
        stim = StimulusProtocol.pulse(start_time=10.0, duration=20.0, amplitude=3.0)
        assert stim(5.0) == 0.0  # Before pulse
        assert stim(15.0) == 3.0  # During pulse
        assert stim(35.0) == 0.0  # After pulse
    
    def test_ramp_stimulus(self):
        """Test ramp stimulus."""
        stim = StimulusProtocol.ramp(start_value=0.0, end_value=10.0, start_time=0.0, end_time=100.0)
        assert stim(0) == 0.0
        assert stim(100) == 10.0
        assert stim(50) == 5.0  # Midpoint


class TestSimulationWithProtocols:
    """Test simulations with different stimulus protocols."""
    
    def test_simulation_constant(self):
        """Test simulation with constant stimulus."""
        circuit = TranscriptionCircuit()
        simulator = ODESimulator(circuit=circuit)
        
        results = simulator.simulate(
            t_span=(0, 100),
            stimulus=StimulusProtocol.constant(1.5),
            n_points=1000
        )
        
        assert results['success']
        assert len(results['output']) == 1000
    
    def test_simulation_step(self):
        """Test simulation with step stimulus."""
        circuit = TranscriptionCircuit()
        simulator = ODESimulator(circuit=circuit)
        
        results = simulator.simulate(
            t_span=(0, 100),
            stimulus=StimulusProtocol.step(step_time=30.0, amplitude=2.0),
            n_points=1000
        )
        
        assert results['success']
        assert len(results['output']) == 1000
    
    def test_simulation_pulse(self):
        """Test simulation with pulse stimulus."""
        circuit = TranscriptionCircuit()
        simulator = ODESimulator(circuit=circuit)
        
        results = simulator.simulate(
            t_span=(0, 100),
            stimulus=StimulusProtocol.pulse(start_time=20.0, duration=30.0, amplitude=3.0),
            n_points=1000
        )
        
        assert results['success']
        assert len(results['output']) == 1000
    
    def test_simulation_ramp(self):
        """Test simulation with ramp stimulus."""
        circuit = TranscriptionCircuit()
        simulator = ODESimulator(circuit=circuit)
        
        results = simulator.simulate(
            t_span=(0, 100),
            stimulus=StimulusProtocol.ramp(start_value=0.0, end_value=5.0, start_time=0.0, end_time=100.0),
            n_points=1000
        )
        
        assert results['success']
        assert len(results['output']) == 1000


class TestLearningRules:
    """Test learning rule creation."""
    
    def test_autoregulation_rule(self):
        """Test Autoregulation learning rule."""
        rule = AutoregulationRule(learning_rate=0.01)
        assert rule.learning_rate == 0.01
    
    def test_hebbian_rule(self):
        """Test Hebbian learning rule."""
        rule = HebbianRule(learning_rate=0.01)
        assert rule.learning_rate == 0.01
    
    def test_gradient_descent_rule(self):
        """Test Gradient Descent learning rule."""
        rule = GradientDescentRule(learning_rate=0.01)
        assert rule.learning_rate == 0.01


class TestReproducibility:
    """Test that results are reproducible."""
    
    def test_deterministic_simulation(self):
        """Test that simulations produce consistent results."""
        circuit = TranscriptionCircuit()
        simulator = ODESimulator(circuit=circuit)
        
        results1 = simulator.simulate(
            t_span=(0, 50),
            stimulus=lambda t: 1.0,
            n_points=500
        )
        
        results2 = simulator.simulate(
            t_span=(0, 50),
            stimulus=lambda t: 1.0,
            n_points=500
        )
        
        # Should be identical
        assert np.allclose(results1['output'], results2['output'])


class TestDataFlowValidity:
    """Test that data flows correctly between components."""
    
    def test_simulation_output_bounds(self):
        """Test that outputs are within reasonable bounds."""
        circuit = TranscriptionCircuit()
        simulator = ODESimulator(circuit=circuit)
        
        results = simulator.simulate(
            t_span=(0, 100),
            stimulus=1.0,
            n_points=1000
        )
        
        # Check for numerical issues
        assert not np.any(np.isnan(results['output']))
        assert not np.any(np.isinf(results['output']))
    
    def test_initial_state_consistency(self):
        """Test that initial state is consistent."""
        circuit1 = TranscriptionCircuit()
        circuit2 = TranscriptionCircuit()
        
        state1 = circuit1.get_initial_state()
        state2 = circuit2.get_initial_state()
        
        # Should be identical
        assert np.allclose(state1, state2)


class TestDataPersistence:
    """Test saving and loading results."""
    
    def test_simulation_results_json(self):
        """Test that simulation results can be saved to JSON."""
        circuit = TranscriptionCircuit()
        simulator = ODESimulator(circuit=circuit)
        
        results = simulator.simulate(
            t_span=(0, 50),
            stimulus=lambda t: 1.0,
            n_points=100
        )
        
        # Convert to JSON-serializable format
        def serialize(obj):
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, (np.floating, float)):
                return float(obj)
            elif isinstance(obj, (np.integer, int)):
                return int(obj)
            elif isinstance(obj, bool):
                return bool(obj)
            raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = os.path.join(tmpdir, 'results.json')
            
            # Save to JSON
            with open(output_file, 'w') as f:
                json.dump(results, f, default=serialize)
            
            # Verify file exists
            assert os.path.exists(output_file)
            
            # Load and verify
            with open(output_file, 'r') as f:
                loaded = json.load(f)
            
            assert 't' in loaded
            assert 'output' in loaded
            assert len(loaded['t']) == 100


class TestPerformanceMetrics:
    """Test performance metrics computation."""
    
    def test_metrics_from_simple_history(self):
        """Test metrics computation from simple training history."""
        # Create simple training history
        history = {
            'losses': [1.0, 0.9, 0.8, 0.7, 0.6, 0.5],
            'outputs': [
                [0.5, 0.6, 0.7],
                [0.6, 0.7, 0.8],
                [0.7, 0.8, 0.9],
                [0.75, 0.85, 0.95],
                [0.8, 0.9, 0.96],
                [0.85, 0.93, 0.97],
            ]
        }
        
        # Compute metrics
        metrics = compute_performance_metrics(history, target_value=1.0)
        
        # Verify basic metrics exist and are reasonable
        assert metrics.final_loss > 0
        assert metrics.final_loss < 1.0
        assert metrics.mse >= 0
        assert metrics.r2_score <= 1.0


class TestScalability:
    """Test behavior with various problem sizes."""
    
    def test_long_time_simulation(self):
        """Test simulation for long time periods."""
        circuit = TranscriptionCircuit()
        simulator = ODESimulator(circuit=circuit)
        
        results = simulator.simulate(
            t_span=(0, 500),
            stimulus=lambda t: 1.0 if (t % 100) < 50 else 0.0,
            n_points=5000
        )
        
        assert results['success']
        assert len(results['output']) == 5000
        assert not np.any(np.isnan(results['output']))
    
    def test_fine_grained_time_points(self):
        """Test simulation with many time points."""
        circuit = TranscriptionCircuit()
        simulator = ODESimulator(circuit=circuit)
        
        results = simulator.simulate(
            t_span=(0, 100),
            stimulus=1.0,
            n_points=10000
        )
        
        assert results['success']
        assert len(results['output']) == 10000
