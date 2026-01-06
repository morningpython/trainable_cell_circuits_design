"""Unit tests for HighPassFilter."""

import pytest
import numpy as np
from tccdp.core.high_pass_filter import HighPassFilter, AdaptiveHighPassFilter


class TestHighPassFilter:
    """Test suite for HighPassFilter."""
    
    def test_initialization(self):
        """Test filter initializes correctly."""
        hpf = HighPassFilter(tau=50.0)
        
        assert hpf.tau == 50.0
        assert hpf.state == 0.0
    
    def test_initialization_with_state(self):
        """Test filter initializes with custom state."""
        hpf = HighPassFilter(tau=30.0, initial_state=1.5)
        
        assert hpf.tau == 30.0
        assert hpf.state == 1.5
    
    def test_initialization_invalid_tau(self):
        """Test initialization with invalid tau raises error."""
        with pytest.raises(ValueError):
            HighPassFilter(tau=0.0)
        
        with pytest.raises(ValueError):
            HighPassFilter(tau=-10.0)
    
    def test_derivative(self):
        """Test derivative computation."""
        hpf = HighPassFilter(tau=50.0)
        hpf.state = 0.5
        
        dH_dt = hpf.derivative(input_signal=1.0)
        
        expected = (1.0 - 0.5) / 50.0
        assert dH_dt == pytest.approx(expected)
    
    def test_output(self):
        """Test output computation."""
        hpf = HighPassFilter(tau=50.0)
        hpf.state = 0.3
        
        output = hpf.output(input_signal=1.0)
        
        assert output == pytest.approx(0.7)
    
    def test_update(self):
        """Test state update."""
        hpf = HighPassFilter(tau=50.0)
        dt = 0.1
        
        output = hpf.update(input_signal=1.0, dt=dt)
        
        # State should increase from 0 toward 1
        assert hpf.state > 0
        assert hpf.state < 1.0
        assert output == pytest.approx(1.0 - hpf.state)
    
    def test_reset(self):
        """Test filter reset."""
        hpf = HighPassFilter(tau=50.0)
        hpf.state = 5.0
        
        hpf.reset()
        
        assert hpf.state == 0.0
    
    def test_reset_with_value(self):
        """Test filter reset with custom value."""
        hpf = HighPassFilter(tau=50.0)
        
        hpf.reset(state=2.5)
        
        assert hpf.state == 2.5
    
    def test_cutoff_frequency(self):
        """Test cutoff frequency calculation."""
        hpf = HighPassFilter(tau=50.0)
        
        f_c = hpf.cutoff_frequency()
        
        expected = 1.0 / (2.0 * np.pi * 50.0)
        assert f_c == pytest.approx(expected)
    
    def test_step_response(self):
        """Test step response simulation."""
        hpf = HighPassFilter(tau=50.0)
        
        time, output = hpf.step_response(duration=100.0, dt=1.0, step_height=1.0)
        
        # Output should start at 1 (full step) and decay toward 0
        assert output[0] == pytest.approx(1.0, abs=0.1)
        assert output[-1] < 0.2  # Decaying (was 1.0, now much smaller)
        assert output[-1] < output[0]  # Must be decreasing
        assert len(time) == len(output)
    
    def test_frequency_response(self):
        """Test frequency response calculation."""
        hpf = HighPassFilter(tau=50.0)
        frequencies = np.logspace(-3, 0, 10)  # 0.001 to 1 Hz
        
        magnitude, phase = hpf.frequency_response(frequencies)
        
        assert len(magnitude) == len(frequencies)
        assert len(phase) == len(frequencies)
        # At high frequencies, magnitude should approach 0 dB
        assert magnitude[-1] > magnitude[0]
    
    def test_dc_blocking(self):
        """Test that DC (constant) signals are blocked."""
        hpf = HighPassFilter(tau=10.0)
        
        # Apply constant input for long time
        for _ in range(1000):
            output = hpf.update(input_signal=1.0, dt=0.1)
        
        # Output should be near zero (DC blocked)
        assert abs(output) < 0.01
    
    def test_ac_passing(self):
        """Test that AC (changing) signals pass through."""
        hpf = HighPassFilter(tau=10.0)
        
        # Reset and apply step
        hpf.reset()
        output_initial = hpf.output(input_signal=1.0)
        
        # Immediately after step, output should be significant
        assert abs(output_initial) > 0.9
    
    def test_repr(self):
        """Test string representation."""
        hpf = HighPassFilter(tau=50.0)
        hpf.state = 1.5
        
        repr_str = repr(hpf)
        
        assert "HighPassFilter" in repr_str
        assert "50" in repr_str
        assert "1.5" in repr_str
    
    def test_str(self):
        """Test human-readable string."""
        hpf = HighPassFilter(tau=50.0)
        
        str_repr = str(hpf)
        
        assert "HighPassFilter" in str_repr
        assert "τ=" in str_repr or "tau=" in str_repr.lower()


class TestAdaptiveHighPassFilter:
    """Test suite for AdaptiveHighPassFilter."""
    
    def test_initialization(self):
        """Test adaptive filter initializes correctly."""
        ahpf = AdaptiveHighPassFilter(tau=50.0, min_tau=1.0, max_tau=1000.0)
        
        assert ahpf.tau == 50.0
        assert ahpf.min_tau == 1.0
        assert ahpf.max_tau == 1000.0
    
    def test_set_tau(self):
        """Test setting tau."""
        ahpf = AdaptiveHighPassFilter(tau=50.0, min_tau=1.0, max_tau=1000.0)
        
        ahpf.set_tau(100.0)
        
        assert ahpf.tau == 100.0
    
    def test_set_tau_clipping_min(self):
        """Test tau is clipped to minimum."""
        ahpf = AdaptiveHighPassFilter(tau=50.0, min_tau=1.0, max_tau=1000.0)
        
        ahpf.set_tau(0.5)
        
        assert ahpf.tau == 1.0
    
    def test_set_tau_clipping_max(self):
        """Test tau is clipped to maximum."""
        ahpf = AdaptiveHighPassFilter(tau=50.0, min_tau=1.0, max_tau=1000.0)
        
        ahpf.set_tau(2000.0)
        
        assert ahpf.tau == 1000.0
    
    def test_update_tau(self):
        """Test updating tau by delta."""
        ahpf = AdaptiveHighPassFilter(tau=50.0, min_tau=1.0, max_tau=1000.0)
        
        ahpf.update_tau(25.0)
        
        assert ahpf.tau == 75.0
    
    def test_update_tau_with_clipping(self):
        """Test tau update respects bounds."""
        ahpf = AdaptiveHighPassFilter(tau=50.0, min_tau=1.0, max_tau=1000.0)
        
        ahpf.update_tau(2000.0)
        
        assert ahpf.tau == 1000.0
