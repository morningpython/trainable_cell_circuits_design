"""Base abstract class for all trainable molecular circuits."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import numpy.typing as npt


class BaseCircuit(ABC):
    """Abstract base class for trainable molecular circuits.
    
    All circuit implementations (Transcription, Protein Modification, Metabolic)
    inherit from this class and implement the required abstract methods.
    
    Attributes:
        params: Dictionary of circuit parameters (rates, constants, etc.)
        state_names: List of state variable names
        n_states: Number of state variables
    """
    
    def __init__(self, params: Optional[Dict[str, float]] = None) -> None:
        """Initialize the circuit with parameters.
        
        Args:
            params: Circuit-specific parameters. If None, uses default parameters.
        """
        self.params = params if params is not None else self.get_default_params()
        self.state_names = self.get_state_names()
        self.n_states = len(self.state_names)
    
    @abstractmethod
    def get_default_params(self) -> Dict[str, float]:
        """Get default parameters for this circuit.
        
        Returns:
            Dictionary of parameter names and their default values
        """
        pass
    
    @abstractmethod
    def get_state_names(self) -> List[str]:
        """Get names of state variables.
        
        Returns:
            List of state variable names (e.g., ['V', 'Hmon', 'C', 'Htot'])
        """
        pass
    
    @abstractmethod
    def get_initial_state(self) -> npt.NDArray[np.float64]:
        """Get initial state for the circuit.
        
        Returns:
            Array of initial values for each state variable
        """
        pass
    
    @abstractmethod
    def get_derivatives(
        self,
        t: float,
        y: npt.NDArray[np.float64],
        stimulus: float
    ) -> npt.NDArray[np.float64]:
        """Compute time derivatives for ODE-based simulation.
        
        Args:
            t: Current time
            y: Current state vector
            stimulus: External stimulus value (0 or 1 for binary, or continuous)
        
        Returns:
            Array of derivatives dy/dt for each state variable
        """
        pass
    
    @abstractmethod
    def get_output(self, state: npt.NDArray[np.float64]) -> float:
        """Extract output signal from current state.
        
        Args:
            state: Current state vector
        
        Returns:
            Scalar output value (typically the reporter concentration)
        """
        pass
    
    def get_propensities(
        self,
        state: npt.NDArray[np.float64],
        stimulus: float
    ) -> npt.NDArray[np.float64]:
        """Compute propensities for stochastic (Gillespie) simulation.
        
        This method is optional and only needed for circuits that support
        stochastic simulation. Default implementation raises NotImplementedError.
        
        Args:
            state: Current state vector (molecule counts, not concentrations)
            stimulus: External stimulus value
        
        Returns:
            Array of reaction propensities
        
        Raises:
            NotImplementedError: If stochastic simulation is not supported
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} does not support stochastic simulation"
        )
    
    def get_stoichiometry(self) -> npt.NDArray[np.int32]:
        """Get stoichiometry matrix for stochastic simulation.
        
        Returns:
            Matrix where rows are species and columns are reactions
        
        Raises:
            NotImplementedError: If stochastic simulation is not supported
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} does not support stochastic simulation"
        )
    
    def update_params(self, new_params: Dict[str, float]) -> None:
        """Update circuit parameters.
        
        Args:
            new_params: Dictionary of parameters to update
        
        Raises:
            KeyError: If parameter name is not valid
        """
        for key, value in new_params.items():
            if key not in self.params:
                raise KeyError(f"Invalid parameter: {key}")
            self.params[key] = value
    
    def get_param(self, name: str) -> float:
        """Get value of a specific parameter.
        
        Args:
            name: Parameter name
        
        Returns:
            Parameter value
        
        Raises:
            KeyError: If parameter name does not exist
        """
        if name not in self.params:
            raise KeyError(f"Parameter '{name}' not found")
        return self.params[name]
    
    def __repr__(self) -> str:
        """String representation of the circuit."""
        return (
            f"{self.__class__.__name__}("
            f"n_states={self.n_states}, "
            f"params={len(self.params)})"
        )
    
    def __str__(self) -> str:
        """Human-readable string representation."""
        params_str = ", ".join(f"{k}={v:.3g}" for k, v in list(self.params.items())[:3])
        if len(self.params) > 3:
            params_str += ", ..."
        return f"{self.__class__.__name__}({params_str})"
