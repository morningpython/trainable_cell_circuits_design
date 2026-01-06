"""
Tellurium/Antimony integration module for TCCDP.

This module provides functionality to:
- Load circuit models from Antimony language
- Convert between Antimony and Circuit objects
- Export circuits to SBML format
- Run simulations using Tellurium/RoadRunner
"""

from typing import Dict, Optional, Tuple, Union
from pathlib import Path
import logging

try:
    import tellurium as te
    from libsbml import readSBML, writeSBMLToFile, SBMLDocument
    TELLURIUM_AVAILABLE = True
except ImportError:
    TELLURIUM_AVAILABLE = False

import numpy as np
from numpy.typing import NDArray

from ..core.base_circuit import BaseCircuit


logger = logging.getLogger(__name__)


class AntimonyCircuit:
    """
    Wraps a Tellurium RoadRunner model for TCCDP compatibility.
    
    Bridges Tellurium's RoadRunner models with TCCDP's BaseCircuit interface.
    Allows using Antimony-defined models within the TCCDP training framework.
    """
    
    def __init__(self, antimony_string: str, model_name: str = "AntimonyModel"):
        """
        Initialize Antimony circuit from Antimony language string.
        
        Args:
            antimony_string: Antimony model definition
            model_name: Name for the model
        
        Raises:
            ImportError: If Tellurium is not installed
            RuntimeError: If Antimony model is invalid
        """
        if not TELLURIUM_AVAILABLE:
            raise ImportError(
                "Tellurium is required for Antimony integration. "
                "Install with: pip install tellurium libsbml"
            )
        
        self.model_name = model_name
        self.antimony_string = antimony_string
        
        try:
            # Load model using Tellurium
            self.roadrunner = te.loada(antimony_string)
            logger.info(f"Loaded Antimony model: {model_name}")
        except Exception as e:
            raise RuntimeError(f"Failed to load Antimony model: {e}")
    
    def get_initial_state(self) -> NDArray[np.float64]:
        """
        Get initial species concentrations.
        
        Returns:
            Initial state vector (species concentrations)
        """
        return np.array(self.roadrunner.getFloatingSpeciesConcentrations())
    
    def get_derivatives(
        self,
        t: float,
        state: NDArray[np.float64],
        stimulus: float
    ) -> NDArray[np.float64]:
        """
        Compute derivatives at given state (using RoadRunner).
        
        Args:
            t: Current time
            state: Current species concentrations
            stimulus: Input stimulus value
        
        Returns:
            Time derivatives of species
        """
        # Set state
        self.roadrunner.setFloatingSpeciesConcentrations(state)
        
        # Get derivatives
        return np.array(self.roadrunner.getRates())
    
    def simulate(
        self,
        t_span: Tuple[float, float],
        stimulus: float = 0.0,
        n_points: int = 100
    ) -> Dict[str, NDArray[np.float64]]:
        """
        Run deterministic simulation using RoadRunner.
        
        Args:
            t_span: Time interval (start, end)
            stimulus: Input stimulus (constant, multiplier for k_in)
            n_points: Number of time points
        
        Returns:
            Simulation results with keys: 't', 'y', 'output'
        """
        t_start, t_end = t_span
        
        # Set stimulus (multiplier for input rate k_in)
        original_k_in = None
        if "k_in" in self.roadrunner.getGlobalParameterIds():
            original_k_in = self.roadrunner.k_in
            self.roadrunner.k_in = original_k_in * stimulus if stimulus != 0 else original_k_in
        
        try:
            # Reset to initial conditions and simulate
            self.roadrunner.reset()
            results = self.roadrunner.simulate(t_start, t_end, n_points)
            
            # results is NamedArray with shape (n_points, n_species + 1)
            # First column is time, rest are species in order
            time_points = np.array(results[:, 0])
            species_data = np.array(results[:, 1:])
            
            # Return in standard format
            return {
                't': time_points,
                'y': species_data.T,  # Transpose to [species, time]
                'output': species_data[:, -1],  # Use last species as output
                'stimulus': np.full_like(time_points, stimulus),
                'success': True,
                'message': 'Simulation completed successfully'
            }
        finally:
            # Restore original parameter
            if original_k_in is not None and "k_in" in self.roadrunner.getGlobalParameterIds():
                self.roadrunner.k_in = original_k_in
    
    def get_model_info(self) -> Dict[str, any]:
        """
        Get information about the model.
        
        Returns:
            Dictionary with species names, parameters, reactions
        """
        return {
            'name': self.model_name,
            'species': list(self.roadrunner.getFloatingSpeciesIds()),
            'parameters': list(self.roadrunner.getGlobalParameterIds()),
            'reactions': list(self.roadrunner.getReactionIds()),
            'num_species': len(self.roadrunner.getFloatingSpeciesIds()),
            'num_parameters': len(self.roadrunner.getGlobalParameterIds()),
            'num_reactions': len(self.roadrunner.getReactionIds()),
        }
    
    def export_sbml(self, output_file: Union[str, Path]) -> bool:
        """
        Export model to SBML format.
        
        Args:
            output_file: Path to save SBML file
        
        Returns:
            True if successful
        """
        try:
            # Get SBML from RoadRunner
            sbml_str = self.roadrunner.getSBML()
            
            # Write to file
            with open(output_file, 'w') as f:
                f.write(sbml_str)
            
            logger.info(f"Exported SBML to {output_file}")
            return True
        except Exception as e:
            logger.error(f"Failed to export SBML: {e}")
            return False
    
    @staticmethod
    def load_sbml(sbml_file: Union[str, Path]) -> 'AntimonyCircuit':
        """
        Load circuit from SBML file.
        
        Args:
            sbml_file: Path to SBML file
        
        Returns:
            AntimonyCircuit instance
        """
        if not TELLURIUM_AVAILABLE:
            raise ImportError(
                "Tellurium is required for SBML loading. "
                "Install with: pip install tellurium libsbml"
            )
        
        try:
            # Load using Tellurium (correct API method)
            rr = te.loadSBMLModel(str(sbml_file))
            
            # Store original SBML for reconstruction
            with open(sbml_file, 'r') as f:
                sbml_content = f.read()
            
            # Create dummy Antimony string (SBML-loaded models don't have Antimony source)
            circuit = AntimonyCircuit.__new__(AntimonyCircuit)
            circuit.model_name = Path(sbml_file).stem
            circuit.antimony_string = f"// Loaded from SBML: {sbml_file}"
            circuit.roadrunner = rr
            
            logger.info(f"Loaded SBML model from {sbml_file}")
            return circuit
        except Exception as e:
            raise RuntimeError(f"Failed to load SBML file: {e}")


class AntimonyExampleModels:
    """
    Collection of example Antimony models for testing and learning.
    """
    
    @staticmethod
    def simple_transcription() -> str:
        """
        Simple transcription circuit (Strategy 1).
        
        Models:
        - Input stimulus V
        - Protein output H
        - High-pass filter for learning
        """
        return '''
model SimpleTranscription
  V -> V; k_in
  V -> ; k_dv * V
  -> H; beta_h * V
  H -> ; k_dh * H
  
  V = 0.0
  H = 0.0
  k_in = 0.1
  k_dv = 0.1
  k_dh = 0.01
  beta_h = 1.0
end
        '''
    
    @staticmethod
    def transcription_with_feedback() -> str:
        """
        Transcription circuit with autoregulation feedback.
        
        Models:
        - Negative feedback through binding
        - Learning via feedback strength adjustment
        """
        return '''
model TranscriptionWithFeedback
  V -> V; k_in
  V -> ; k_dv * V
  -> H; beta_h * V / (1 + k_h * H)
  H -> ; k_dh * H
  
  V = 0.0
  H = 0.0
  k_in = 0.1
  k_dv = 0.1
  k_dh = 0.01
  beta_h = 1.0
  k_h = 0.5
end
        '''
    
    @staticmethod
    def transcription_with_memory() -> str:
        """
        Transcription circuit with memory element (history-dependent).
        
        Models:
        - Long-lived protein M for memory
        - H responds to both V and M
        - Learning modifies M dynamics
        """
        return '''
model TranscriptionWithMemory
  V -> V; k_in
  V -> ; k_dv * V
  -> M; k_m * V
  M -> ; k_dm * M
  -> H; beta_h * V + alpha_h * M
  H -> ; k_dh * H
  
  V = 0.0
  M = 0.0
  H = 0.0
  k_in = 0.1
  k_dv = 0.1
  k_m = 0.2
  k_dm = 0.001
  k_dh = 0.01
  beta_h = 1.0
  alpha_h = 0.5
end
        '''


def create_antimony_circuit(antimony_string: str, name: str = "Circuit") -> BaseCircuit:
    """
    Factory function to create circuit from Antimony.
    
    Args:
        antimony_string: Antimony model definition
        name: Circuit name
    
    Returns:
        AntimonyCircuit instance (compatible with BaseCircuit interface)
    """
    return AntimonyCircuit(antimony_string, name)


def load_sbml_circuit(sbml_file: Union[str, Path]) -> BaseCircuit:
    """
    Load circuit from SBML file.
    
    Args:
        sbml_file: Path to SBML file
    
    Returns:
        AntimonyCircuit instance loaded from SBML
    """
    return AntimonyCircuit.load_sbml(sbml_file)
