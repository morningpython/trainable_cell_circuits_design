"""
Unit tests for TranscriptionCircuit class.
"""

import numpy as np
import pytest

from tccdp.circuits.transcription_circuit import TranscriptionCircuit


class TestTranscriptionCircuitInitialization:
    """Test circuit initialization and configuration."""
    
    def test_default_initialization(self):
        """Test initialization with default parameters."""
        circuit = TranscriptionCircuit()
        
        # Check that default parameters are set
        assert 'k_L' in circuit.params
        assert 'k_H' in circuit.params
        assert 'K_D' in circuit.params
        assert 'τ_H' in circuit.params
        
        # Check parameter types
        assert isinstance(circuit.params['k_L'], (int, float))
        assert isinstance(circuit.params['k_H'], (int, float))
        
    def test_custom_parameters(self):
        """Test initialization with custom parameters."""
        custom_params = {
            'k_L': 2.0,
            'k_H': 200.0,
            'K_D': 100.0,
            'τ_H': 100.0,
        }
        circuit = TranscriptionCircuit(params=custom_params)
        
        assert circuit.params['k_L'] == 2.0
        assert circuit.params['k_H'] == 200.0
        assert circuit.params['K_D'] == 100.0
        assert circuit.params['τ_H'] == 100.0
    
    def test_state_names(self):
        """Test state variable names."""
        circuit = TranscriptionCircuit()
        names = circuit.get_state_names()
        
        assert names == ['V', 'H_mon', 'C', 'H_tot']
        assert len(names) == 4
    
    def test_initial_state_shape(self):
        """Test initial state vector shape."""
        circuit = TranscriptionCircuit()
        state = circuit.get_initial_state()
        
        assert state.shape == (4,)
        assert state.dtype == np.float64
    
    def test_initial_state_values(self):
        """Test initial state values are reasonable."""
        circuit = TranscriptionCircuit()
        state = circuit.get_initial_state()
        
        V, H_mon, C, H_tot = state
        
        # V should be at basal steady state
        expected_V = circuit.params['k_L'] / circuit.params['γ_V']
        assert abs(V - expected_V) < 1e-10
        
        # H_mon should equal V initially
        assert abs(H_mon - V) < 1e-10
        
        # C should be zero (no stimulus)
        assert C == 0.0
        
        # H_tot should be at minimum
        assert H_tot == circuit.params['H_tot_min']


class TestTranscriptionCircuitDynamics:
    """Test circuit dynamics and ODE system."""
    
    def test_derivatives_shape(self):
        """Test derivative vector shape."""
        circuit = TranscriptionCircuit()
        state = circuit.get_initial_state()
        t = 0.0
        stimulus = 0.0
        
        dydt = circuit.get_derivatives(t, state, stimulus)
        
        assert dydt.shape == (4,)
        assert dydt.dtype == np.float64
    
    def test_derivatives_no_stimulus(self):
        """Test derivatives with no stimulus."""
        circuit = TranscriptionCircuit()
        state = circuit.get_initial_state()
        t = 0.0
        stimulus = 0.0
        
        dydt = circuit.get_derivatives(t, state, stimulus)
        dV_dt, dH_mon_dt, dC_dt, dH_tot_dt = dydt
        
        # At initial steady state with no stimulus:
        # dV/dt should be near zero (basal balance)
        assert abs(dV_dt) < 1.0
        
        # dH_mon/dt should be zero (H_mon = V)
        assert abs(dH_mon_dt) < 1e-10
        
        # dC/dt should be zero (no stimulus, C=0)
        assert dC_dt == 0.0
        
        # dH_tot/dt should be zero (no error signal)
        assert abs(dH_tot_dt) < 1e-10
    
    def test_derivatives_with_stimulus(self):
        """Test derivatives with stimulus."""
        circuit = TranscriptionCircuit()
        state = circuit.get_initial_state()
        t = 0.0
        stimulus = 100.0  # Strong stimulus
        
        dydt = circuit.get_derivatives(t, state, stimulus)
        dV_dt, dH_mon_dt, dC_dt, dH_tot_dt = dydt
        
        # With stimulus, C should increase
        assert dC_dt > 0
        
        # Other derivatives should be computable
        assert np.isfinite(dV_dt)
        assert np.isfinite(dH_mon_dt)
        assert np.isfinite(dH_tot_dt)
    
    def test_hill_activation_bounds(self):
        """Test Hill activation function stays in [0, 1]."""
        circuit = TranscriptionCircuit()
        
        # Test at various H_tot values
        for H_tot in [0.1, 1.0, 5.0, 10.0, 100.0]:
            activation = circuit.compute_hill_activation(H_tot)
            assert 0.0 <= activation <= 1.0
    
    def test_hill_activation_monotonic(self):
        """Test Hill activation increases with H_tot."""
        circuit = TranscriptionCircuit()
        
        H_tot_values = np.linspace(0.1, 10.0, 20)
        activations = [circuit.compute_hill_activation(h) for h in H_tot_values]
        
        # Should be monotonically increasing
        for i in range(len(activations) - 1):
            assert activations[i+1] >= activations[i]
    
    def test_htot_clipping_lower_bound(self):
        """Test H_tot doesn't go below minimum."""
        circuit = TranscriptionCircuit()
        state = circuit.get_initial_state()
        
        # Set H_tot to minimum and create negative error signal
        state[3] = circuit.params['H_tot_min']
        state[1] = state[0] - 10.0  # H_mon < H_tot
        state[2] = 10.0  # Some C
        
        dydt = circuit.get_derivatives(0.0, state, 0.0)
        dH_tot_dt = dydt[3]
        
        # Should be clipped to zero (not decrease)
        assert dH_tot_dt >= -1e-10
    
    def test_htot_clipping_upper_bound(self):
        """Test H_tot doesn't go above maximum."""
        circuit = TranscriptionCircuit()
        state = circuit.get_initial_state()
        
        # Set H_tot to maximum and create positive error signal
        state[3] = circuit.params['H_tot_max']
        state[1] = state[0] + 10.0  # H_mon > H_tot
        state[2] = 10.0  # Some C
        
        dydt = circuit.get_derivatives(0.0, state, 0.0)
        dH_tot_dt = dydt[3]
        
        # Should be clipped to zero (not increase)
        assert dH_tot_dt <= 1e-10


class TestTranscriptionCircuitOutput:
    """Test circuit output and learning parameter access."""
    
    def test_get_output(self):
        """Test output extraction from state."""
        circuit = TranscriptionCircuit()
        state = np.array([50.0, 45.0, 2.0, 1.5])
        
        output = circuit.get_output(state)
        
        assert output == 50.0
        assert isinstance(output, float)
    
    def test_get_learning_parameter(self):
        """Test learning parameter extraction."""
        circuit = TranscriptionCircuit()
        state = np.array([50.0, 45.0, 2.0, 1.5])
        
        H_tot = circuit.get_learning_parameter(state)
        
        assert H_tot == 1.5
        assert isinstance(H_tot, float)
    
    def test_set_learning_parameter(self):
        """Test learning parameter modification."""
        circuit = TranscriptionCircuit()
        state = circuit.get_initial_state()
        
        new_state = circuit.set_learning_parameter(state, 5.0)
        
        assert new_state[3] == 5.0
        # Other state variables unchanged
        assert new_state[0] == state[0]
        assert new_state[1] == state[1]
        assert new_state[2] == state[2]
    
    def test_set_learning_parameter_clipping(self):
        """Test learning parameter clips to valid range."""
        circuit = TranscriptionCircuit()
        state = circuit.get_initial_state()
        
        # Try to set below minimum
        new_state = circuit.set_learning_parameter(state, -1.0)
        assert new_state[3] == circuit.params['H_tot_min']
        
        # Try to set above maximum
        new_state = circuit.set_learning_parameter(state, 100.0)
        assert new_state[3] == circuit.params['H_tot_max']


class TestTranscriptionCircuitParameterUpdate:
    """Test parameter update functionality."""
    
    def test_update_params(self):
        """Test parameter updates."""
        circuit = TranscriptionCircuit()
        original_kH = circuit.params['k_H']
        
        circuit.update_params({'k_H': 200.0})
        
        assert circuit.params['k_H'] == 200.0
        assert circuit.params['k_H'] != original_kH
    
    def test_get_param(self):
        """Test parameter retrieval."""
        circuit = TranscriptionCircuit()
        
        k_H = circuit.get_param('k_H')
        assert k_H == circuit.params['k_H']
        
        # Test that missing parameter raises KeyError
        with pytest.raises(KeyError):
            circuit.get_param('nonexistent')


class TestTranscriptionCircuitIntegration:
    """Integration tests for circuit behavior."""
    
    def test_steady_state_no_stimulus(self):
        """Test circuit reaches steady state with no stimulus."""
        circuit = TranscriptionCircuit()
        state = circuit.get_initial_state()
        
        # Simulate for long time with no stimulus
        t = 0.0
        dt = 0.1
        stimulus = 0.0
        
        for _ in range(1000):
            dydt = circuit.get_derivatives(t, state, stimulus)
            state = state + dydt * dt
            t += dt
        
        # Check derivatives are near zero (steady state)
        dydt_final = circuit.get_derivatives(t, state, stimulus)
        assert np.all(np.abs(dydt_final) < 0.1)
    
    def test_output_increases_with_htot(self):
        """Test that output increases when H_tot increases."""
        circuit = TranscriptionCircuit()
        state = circuit.get_initial_state()
        
        # Measure output at low H_tot
        state = circuit.set_learning_parameter(state, 0.5)
        # Let circuit reach steady state
        for _ in range(500):
            dydt = circuit.get_derivatives(0.0, state, 0.0)
            state = state + dydt * 0.1
        output_low = circuit.get_output(state)
        
        # Reset and measure output at high H_tot
        state = circuit.get_initial_state()
        state = circuit.set_learning_parameter(state, 8.0)
        # Let circuit reach steady state
        for _ in range(500):
            dydt = circuit.get_derivatives(0.0, state, 0.0)
            state = state + dydt * 0.1
        output_high = circuit.get_output(state)
        
        # Higher H_tot should give higher steady-state output
        assert output_high > output_low
    
    def test_repr(self):
        """Test string representation."""
        circuit = TranscriptionCircuit()
        repr_str = repr(circuit)
        
        assert 'TranscriptionCircuit' in repr_str
        assert 'k_H' in repr_str
        assert 'K_D' in repr_str
