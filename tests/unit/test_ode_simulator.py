"""
Unit tests for ODE Simulator and Stimulus Protocols.
"""

import numpy as np
import pytest

from tccdp.circuits.transcription_circuit import TranscriptionCircuit
from tccdp.simulators.ode_simulator import ODESimulator, StimulusProtocol


class TestStimulusProtocol:
    """Test stimulus protocol generators."""
    
    def test_constant_stimulus(self):
        """Test constant stimulus protocol."""
        stim = StimulusProtocol.constant(50.0)
        
        assert stim(0.0) == 50.0
        assert stim(10.0) == 50.0
        assert stim(100.0) == 50.0
    
    def test_step_stimulus(self):
        """Test step stimulus protocol."""
        stim = StimulusProtocol.step(
            step_time=10.0,
            baseline=0.0,
            amplitude=100.0
        )
        
        assert stim(5.0) == 0.0
        assert stim(10.0) == 100.0
        assert stim(15.0) == 100.0
    
    def test_pulse_stimulus(self):
        """Test pulse stimulus protocol."""
        stim = StimulusProtocol.pulse(
            start_time=10.0,
            duration=5.0,
            baseline=0.0,
            amplitude=100.0
        )
        
        assert stim(5.0) == 0.0
        assert stim(12.0) == 100.0
        assert stim(20.0) == 0.0
    
    def test_ramp_stimulus(self):
        """Test ramp stimulus protocol."""
        stim = StimulusProtocol.ramp(
            start_value=0.0,
            end_value=100.0,
            start_time=0.0,
            end_time=100.0
        )
        
        assert stim(-10.0) == 0.0
        assert abs(stim(50.0) - 50.0) < 1e-10
        assert stim(150.0) == 100.0
    
    def test_custom_stimulus(self):
        """Test custom stimulus protocol."""
        # Sinusoidal stimulus
        stim = StimulusProtocol.custom(lambda t: 50 + 50 * np.sin(t))
        
        assert abs(stim(0.0) - 50.0) < 1e-10
        assert abs(stim(np.pi/2) - 100.0) < 1e-10


class TestODESimulatorInitialization:
    """Test simulator initialization."""
    
    def test_default_initialization(self):
        """Test initialization with default parameters."""
        circuit = TranscriptionCircuit()
        simulator = ODESimulator(circuit)
        
        assert simulator.circuit is circuit
        assert simulator.method == 'RK45'
        assert simulator.rtol == 1e-6
        assert simulator.atol == 1e-9
    
    def test_custom_initialization(self):
        """Test initialization with custom parameters."""
        circuit = TranscriptionCircuit()
        simulator = ODESimulator(
            circuit,
            method='LSODA',
            rtol=1e-8,
            atol=1e-12
        )
        
        assert simulator.method == 'LSODA'
        assert simulator.rtol == 1e-8
        assert simulator.atol == 1e-12
    
    def test_repr(self):
        """Test string representation."""
        circuit = TranscriptionCircuit()
        simulator = ODESimulator(circuit)
        repr_str = repr(simulator)
        
        assert 'ODESimulator' in repr_str
        assert 'TranscriptionCircuit' in repr_str
        assert 'RK45' in repr_str


class TestODESimulatorBasicSimulation:
    """Test basic simulation functionality."""
    
    def test_simulate_constant_stimulus(self):
        """Test simulation with constant stimulus."""
        circuit = TranscriptionCircuit()
        simulator = ODESimulator(circuit)
        
        result = simulator.simulate(
            t_span=(0, 100),
            stimulus=0.0,
            n_points=101
        )
        
        assert 't' in result
        assert 'y' in result
        assert 'output' in result
        assert 'stimulus' in result
        assert result['success']
        
        # Check shapes
        assert len(result['t']) == 101
        assert result['y'].shape[0] == 4  # 4 state variables
        assert result['y'].shape[1] == 101
        assert len(result['output']) == 101
        assert len(result['stimulus']) == 101
    
    def test_simulate_step_stimulus(self):
        """Test simulation with step stimulus."""
        circuit = TranscriptionCircuit()
        simulator = ODESimulator(circuit)
        
        stim = StimulusProtocol.step(
            step_time=50.0,
            baseline=0.0,
            amplitude=100.0
        )
        
        result = simulator.simulate(
            t_span=(0, 100),
            stimulus=stim,
            n_points=201
        )
        
        assert result['success']
        
        # Check stimulus changes at step
        t = result['t']
        stimulus = result['stimulus']
        idx_before = np.where(t < 50.0)[0]
        idx_after = np.where(t >= 50.0)[0]
        
        assert np.all(stimulus[idx_before] == 0.0)
        assert np.all(stimulus[idx_after] == 100.0)
    
    def test_simulate_with_custom_initial_state(self):
        """Test simulation with custom initial state."""
        circuit = TranscriptionCircuit()
        simulator = ODESimulator(circuit)
        
        # Custom initial state
        y0 = np.array([20.0, 15.0, 5.0, 2.0])
        
        result = simulator.simulate(
            t_span=(0, 50),
            stimulus=0.0,
            y0=y0,
            n_points=51
        )
        
        # Check initial state matches
        assert np.allclose(result['y'][:, 0], y0)
    
    def test_output_extraction(self):
        """Test output signal extraction."""
        circuit = TranscriptionCircuit()
        simulator = ODESimulator(circuit)
        
        result = simulator.simulate(
            t_span=(0, 100),
            stimulus=0.0,
            n_points=101
        )
        
        # Output should match V (first state variable)
        for i in range(len(result['t'])):
            expected_output = circuit.get_output(result['y'][:, i])
            assert abs(result['output'][i] - expected_output) < 1e-10


class TestODESimulatorAdvanced:
    """Test advanced simulation features."""
    
    def test_simulate_multiple_sequential(self):
        """Test multiple simulations with state carryover."""
        circuit = TranscriptionCircuit()
        simulator = ODESimulator(circuit)
        
        stimuli = [0.0, 100.0, 0.0]
        
        results = simulator.simulate_multiple(
            t_span=(0, 50),
            stimuli=stimuli,
            n_points=51,
            reset_between=False  # Carry state forward
        )
        
        assert len(results) == 3
        
        # Final state of simulation i should match initial state of i+1
        for i in range(len(results) - 1):
            final_state = results[i]['y'][:, -1]
            next_initial = results[i+1]['y'][:, 0]
            assert np.allclose(final_state, next_initial)
    
    def test_simulate_multiple_reset(self):
        """Test multiple simulations with state reset."""
        circuit = TranscriptionCircuit()
        simulator = ODESimulator(circuit)
        
        stimuli = [0.0, 100.0, 50.0]
        y0 = circuit.get_initial_state()
        
        results = simulator.simulate_multiple(
            t_span=(0, 50),
            stimuli=stimuli,
            y0=y0,
            n_points=51,
            reset_between=True  # Reset to y0 each time
        )
        
        assert len(results) == 3
        
        # All simulations should start from same initial state
        for result in results:
            assert np.allclose(result['y'][:, 0], y0)
    
    def test_find_steady_state(self):
        """Test steady state finding."""
        circuit = TranscriptionCircuit()
        simulator = ODESimulator(circuit)
        
        # Find steady state with no stimulus
        ss, converged = simulator.find_steady_state(
            stimulus=0.0,
            t_max=500.0,
            threshold=1e-5
        )
        
        assert ss.shape == (4,)
        # Convergence depends on dynamics, but should work for simple case
        
        # Check that derivatives are small at steady state
        dydt = circuit.get_derivatives(0, ss, 0.0)
        assert np.all(np.abs(dydt) < 0.1)


class TestODESimulatorIntegration:
    """Integration tests for realistic scenarios."""
    
    def test_response_to_step_input(self):
        """Test circuit response to step stimulus."""
        circuit = TranscriptionCircuit()
        simulator = ODESimulator(circuit)
        
        # Step from 0 to 100 at t=20
        stim = StimulusProtocol.step(
            step_time=20.0,
            baseline=0.0,
            amplitude=100.0
        )
        
        result = simulator.simulate(
            t_span=(0, 100),
            stimulus=stim,
            n_points=1001
        )
        
        t = result['t']
        output = result['output']
        
        # Output before step
        idx_before = np.where(t < 20.0)[0]
        output_before = output[idx_before]
        
        # Output after step (late time)
        idx_after = np.where(t > 80.0)[0]
        output_after = output[idx_after]
        
        # Output should increase after step
        assert np.mean(output_after) > np.mean(output_before)
    
    def test_learning_parameter_affects_output(self):
        """Test that learning parameter affects steady-state output."""
        circuit = TranscriptionCircuit()
        
        # Simulate with low H_tot
        circuit.update_params({'H_tot_min': 0.5, 'H_tot_max': 10.0})
        y0_low = circuit.get_initial_state()
        y0_low[3] = 0.5  # Low H_tot
        
        simulator = ODESimulator(circuit)
        result_low = simulator.simulate(
            t_span=(0, 500),
            stimulus=0.0,
            y0=y0_low,
            n_points=101
        )
        
        # Simulate with high H_tot
        y0_high = circuit.get_initial_state()
        y0_high[3] = 8.0  # High H_tot
        
        result_high = simulator.simulate(
            t_span=(0, 500),
            stimulus=0.0,
            y0=y0_high,
            n_points=101
        )
        
        # Higher H_tot should give higher steady-state output
        output_low_final = result_low['output'][-10:].mean()
        output_high_final = result_high['output'][-10:].mean()
        
        assert output_high_final > output_low_final
    
    def test_different_integration_methods(self):
        """Test that different methods give similar results."""
        circuit = TranscriptionCircuit()
        
        methods = ['RK45', 'RK23', 'LSODA']
        results = []
        
        for method in methods:
            simulator = ODESimulator(circuit, method=method)
            result = simulator.simulate(
                t_span=(0, 100),
                stimulus=50.0,
                n_points=101
            )
            results.append(result)
        
        # All methods should give similar final output
        final_outputs = [r['output'][-1] for r in results]
        
        # Check all outputs within 5% of each other
        mean_output = np.mean(final_outputs)
        for output in final_outputs:
            assert abs(output - mean_output) / mean_output < 0.05
