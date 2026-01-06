"""
Transcription Circuit Implementation

This module implements the transcription-based learning circuit from the paper
"Learning by Modulation of Gene Expression in Gene Circuits" (Fig. 1a).

The circuit consists of:
- Gene G expressing protein V (output)
- High-pass filter H (temporal filtering)
- Feedback regulation via transcription factor C
- Total Hill coefficient H_tot (learning parameter)

Circuit Equations:
    dV/dt = k_L + k_H * H_tot^n / (K_D^n + H_tot^n) - γ_V * V
    dH_mon/dt = (V - H_mon) / τ_H
    dC/dt = k_C * S - γ_C * C
    dH_tot/dt = k_up * C * (H_mon - H_tot) - k_down * (H_tot - H_mon)

Where:
    V: Output protein concentration
    H_mon: Monomer high-pass filter state
    C: Transcription factor concentration
    H_tot: Total Hill coefficient (learning parameter)
    S: Stimulus signal
"""

from typing import Dict, List, Optional, Tuple
import numpy as np
from numpy.typing import NDArray

from ..core.base_circuit import BaseCircuit


class TranscriptionCircuit(BaseCircuit):
    """
    Transcription-based learning circuit with autoregulation.
    
    This circuit implements learning through modulation of the Hill coefficient
    in transcriptional regulation. The circuit learns to respond to stimuli
    through changes in H_tot, which controls the strength of positive feedback.
    
    State Variables:
        V: Output protein concentration [nM]
        H_mon: High-pass filter monomer state [nM]
        C: Transcription factor concentration [nM]
        H_tot: Total Hill coefficient (learning parameter) [dimensionless]
    
    Parameters:
        k_L: Basal transcription rate [nM/min]
        k_H: Maximum regulated transcription rate [nM/min]
        K_D: Dissociation constant [nM]
        n: Hill coefficient [dimensionless]
        γ_V: Protein degradation rate [1/min]
        τ_H: High-pass filter time constant [min]
        k_C: Transcription factor production rate [nM/min]
        γ_C: Transcription factor degradation rate [1/min]
        k_up: Learning rate (upregulation) [1/(nM*min)]
        k_down: Learning rate (downregulation) [1/min]
        H_tot_min: Minimum Hill coefficient [dimensionless]
        H_tot_max: Maximum Hill coefficient [dimensionless]
    
    Example:
        >>> circuit = TranscriptionCircuit()
        >>> state = circuit.get_initial_state()
        >>> t = 0.0
        >>> stimulus = 100.0  # nM
        >>> dydt = circuit.get_derivatives(t, state, stimulus)
        >>> output = circuit.get_output(state)
    """
    
    def get_default_params(self) -> Dict[str, float]:
        """
        Get default parameter values for the transcription circuit.
        
        Parameters are based on typical bacterial gene expression dynamics
        and the paper's supplementary information.
        
        Returns:
            Dictionary of parameter names and values
        """
        return {
            # Transcription parameters
            'k_L': 1.0,           # Basal transcription rate [nM/min]
            'k_H': 100.0,         # Maximum regulated transcription rate [nM/min]
            'K_D': 50.0,          # Dissociation constant [nM]
            'n': 2.0,             # Hill coefficient
            'γ_V': 0.1,           # Protein degradation rate [1/min]
            
            # High-pass filter parameters
            'τ_H': 50.0,          # Filter time constant [min]
            
            # Transcription factor parameters
            'k_C': 1.0,           # TF production rate [nM/min]
            'γ_C': 0.5,           # TF degradation rate [1/min]
            
            # Learning parameters
            'k_up': 0.01,         # Upregulation rate [1/(nM*min)]
            'k_down': 0.001,      # Downregulation rate [1/min]
            'H_tot_min': 0.1,     # Minimum Hill coefficient
            'H_tot_max': 10.0,    # Maximum Hill coefficient
        }
    
    def get_state_names(self) -> List[str]:
        """
        Get names of state variables.
        
        Returns:
            List of state variable names in order
        """
        return ['V', 'H_mon', 'C', 'H_tot']
    
    def get_initial_state(self) -> NDArray[np.float64]:
        """
        Get initial state vector.
        
        Initial conditions represent the circuit at steady state
        with no stimulus and baseline learning parameter.
        
        Returns:
            Initial state vector [V, H_mon, C, H_tot]
        """
        # Compute steady state V with no regulation
        k_L = self.params['k_L']
        γ_V = self.params['γ_V']
        V_ss = k_L / γ_V
        
        # H_mon starts at same value as V
        H_mon_0 = V_ss
        
        # C starts at zero (no stimulus)
        C_0 = 0.0
        
        # H_tot starts at minimum value
        H_tot_0 = self.params['H_tot_min']
        
        return np.array([V_ss, H_mon_0, C_0, H_tot_0], dtype=np.float64)
    
    def get_derivatives(
        self, 
        t: float, 
        y: NDArray[np.float64], 
        stimulus: float
    ) -> NDArray[np.float64]:
        """
        Compute time derivatives of state variables.
        
        Implements the ODE system for the transcription circuit:
            dV/dt = k_L + k_H * H_tot^n / (K_D^n + H_tot^n) - γ_V * V
            dH_mon/dt = (V - H_mon) / τ_H
            dC/dt = k_C * S - γ_C * C
            dH_tot/dt = k_up * C * (H_mon - H_tot) - k_down * (H_tot - H_mon)
        
        Args:
            t: Current time [min]
            y: State vector [V, H_mon, C, H_tot]
            stimulus: Stimulus signal [nM]
        
        Returns:
            Derivative vector [dV/dt, dH_mon/dt, dC/dt, dH_tot/dt]
        """
        # Unpack state variables
        V, H_mon, C, H_tot = y
        
        # Extract parameters
        k_L = self.params['k_L']
        k_H = self.params['k_H']
        K_D = self.params['K_D']
        n = self.params['n']
        γ_V = self.params['γ_V']
        τ_H = self.params['τ_H']
        k_C = self.params['k_C']
        γ_C = self.params['γ_C']
        k_up = self.params['k_up']
        k_down = self.params['k_down']
        H_tot_min = self.params['H_tot_min']
        H_tot_max = self.params['H_tot_max']
        
        # Compute Hill function for transcriptional activation
        H_tot_n = H_tot ** n
        K_D_n = K_D ** n
        hill_activation = H_tot_n / (K_D_n + H_tot_n)
        
        # dV/dt: Transcription (basal + regulated) - degradation
        dV_dt = k_L + k_H * hill_activation - γ_V * V
        
        # dH_mon/dt: High-pass filter dynamics
        dH_mon_dt = (V - H_mon) / τ_H
        
        # dC/dt: Transcription factor production and degradation
        dC_dt = k_C * stimulus - γ_C * C
        
        # dH_tot/dt: Learning dynamics
        error_signal = H_mon - H_tot
        dH_tot_dt = k_up * C * error_signal - k_down * error_signal
        
        # Clip H_tot derivatives to enforce bounds
        if H_tot <= H_tot_min and dH_tot_dt < 0:
            dH_tot_dt = 0.0
        elif H_tot >= H_tot_max and dH_tot_dt > 0:
            dH_tot_dt = 0.0
        
        return np.array([dV_dt, dH_mon_dt, dC_dt, dH_tot_dt], dtype=np.float64)
    
    def get_output(self, state: NDArray[np.float64]) -> float:
        """
        Extract output signal from state.
        
        The output is the protein concentration V, which is the
        reporter gene expression level.
        
        Args:
            state: State vector [V, H_mon, C, H_tot]
        
        Returns:
            Output signal (protein V concentration) [nM]
        """
        return float(state[0])
    
    def get_learning_parameter(self, state: NDArray[np.float64]) -> float:
        """
        Extract learning parameter from state.
        
        The learning parameter is H_tot, which controls the strength
        of positive feedback regulation.
        
        Args:
            state: State vector [V, H_mon, C, H_tot]
        
        Returns:
            Learning parameter (H_tot) [dimensionless]
        """
        return float(state[3])
    
    def set_learning_parameter(
        self, 
        state: NDArray[np.float64], 
        value: float
    ) -> NDArray[np.float64]:
        """
        Set learning parameter in state.
        
        Args:
            state: State vector [V, H_mon, C, H_tot]
            value: New value for H_tot
        
        Returns:
            Updated state vector with new H_tot value
        """
        new_state = state.copy()
        # Clip to valid range
        value = np.clip(value, self.params['H_tot_min'], self.params['H_tot_max'])
        new_state[3] = value
        return new_state
    
    def compute_hill_activation(self, H_tot: float) -> float:
        """
        Compute Hill activation function.
        
        This represents the strength of transcriptional activation
        as a function of the learning parameter H_tot.
        
        Args:
            H_tot: Total Hill coefficient
        
        Returns:
            Activation level [0, 1]
        """
        K_D = self.params['K_D']
        n = self.params['n']
        
        H_tot_n = H_tot ** n
        K_D_n = K_D ** n
        
        return H_tot_n / (K_D_n + H_tot_n)
    
    def __repr__(self) -> str:
        """String representation for debugging."""
        return (
            f"TranscriptionCircuit("
            f"k_H={self.params['k_H']:.1f}, "
            f"K_D={self.params['K_D']:.1f}, "
            f"n={self.params['n']:.1f}, "
            f"τ_H={self.params['τ_H']:.1f})"
        )
