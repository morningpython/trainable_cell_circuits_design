"""Unit tests for BaseCircuit abstract class."""

import pytest
import numpy as np
from tccdp.core.base_circuit import BaseCircuit


class DummyCircuit(BaseCircuit):
    """Concrete implementation for testing."""
    
    def get_default_params(self):
        return {"k1": 0.1, "k2": 0.5}
    
    def get_state_names(self):
        return ["X", "Y"]
    
    def get_initial_state(self):
        return np.array([1.0, 0.0])
    
    def get_derivatives(self, t, y, stimulus):
        return np.array([-self.params["k1"] * y[0], self.params["k2"] * y[0]])
    
    def get_output(self, state):
        return state[1]


class TestBaseCircuit:
    """Test suite for BaseCircuit."""
    
    def test_initialization_with_defaults(self):
        """Test circuit initializes with default parameters."""
        circuit = DummyCircuit()
        
        assert circuit.n_states == 2
        assert len(circuit.state_names) == 2
        assert "k1" in circuit.params
        assert "k2" in circuit.params
    
    def test_initialization_with_custom_params(self):
        """Test circuit initializes with custom parameters."""
        custom_params = {"k1": 0.2, "k2": 1.0}
        circuit = DummyCircuit(params=custom_params)
        
        assert circuit.params["k1"] == 0.2
        assert circuit.params["k2"] == 1.0
    
    def test_get_state_names(self):
        """Test state names are correct."""
        circuit = DummyCircuit()
        names = circuit.get_state_names()
        
        assert names == ["X", "Y"]
        assert circuit.state_names == names
    
    def test_get_initial_state(self):
        """Test initial state is correct."""
        circuit = DummyCircuit()
        state = circuit.get_initial_state()
        
        assert len(state) == 2
        assert state[0] == 1.0
        assert state[1] == 0.0
    
    def test_get_derivatives(self):
        """Test derivative computation."""
        circuit = DummyCircuit()
        t = 0.0
        y = np.array([1.0, 0.5])
        stimulus = 1.0
        
        dydt = circuit.get_derivatives(t, y, stimulus)
        
        assert len(dydt) == 2
        assert dydt[0] == -0.1 * 1.0  # -k1 * y[0]
        assert dydt[1] == 0.5 * 1.0   # k2 * y[0]
    
    def test_get_output(self):
        """Test output extraction."""
        circuit = DummyCircuit()
        state = np.array([1.0, 2.0])
        
        output = circuit.get_output(state)
        
        assert output == 2.0
    
    def test_update_params(self):
        """Test parameter updating."""
        circuit = DummyCircuit()
        
        circuit.update_params({"k1": 0.3})
        
        assert circuit.params["k1"] == 0.3
        assert circuit.params["k2"] == 0.5  # Unchanged
    
    def test_update_params_invalid_key(self):
        """Test updating with invalid parameter raises error."""
        circuit = DummyCircuit()
        
        with pytest.raises(KeyError):
            circuit.update_params({"invalid": 1.0})
    
    def test_get_param(self):
        """Test getting individual parameter."""
        circuit = DummyCircuit()
        
        k1 = circuit.get_param("k1")
        
        assert k1 == 0.1
    
    def test_get_param_invalid(self):
        """Test getting invalid parameter raises error."""
        circuit = DummyCircuit()
        
        with pytest.raises(KeyError):
            circuit.get_param("invalid")
    
    def test_propensities_not_implemented(self):
        """Test stochastic methods raise NotImplementedError by default."""
        circuit = DummyCircuit()
        state = np.array([100, 50])
        
        with pytest.raises(NotImplementedError):
            circuit.get_propensities(state, 1.0)
    
    def test_stoichiometry_not_implemented(self):
        """Test stoichiometry raises NotImplementedError by default."""
        circuit = DummyCircuit()
        
        with pytest.raises(NotImplementedError):
            circuit.get_stoichiometry()
    
    def test_repr(self):
        """Test string representation."""
        circuit = DummyCircuit()
        
        repr_str = repr(circuit)
        
        assert "DummyCircuit" in repr_str
        assert "n_states=2" in repr_str
        assert "params=2" in repr_str
    
    def test_str(self):
        """Test human-readable string."""
        circuit = DummyCircuit()
        
        str_repr = str(circuit)
        
        assert "DummyCircuit" in str_repr
        assert "k1" in str_repr or "k2" in str_repr
