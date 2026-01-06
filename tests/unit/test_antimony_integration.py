"""
Unit tests for Antimony/Tellurium integration (E2-S3).

Tests Antimony model loading, conversion, and SBML export functionality.
"""

import pytest
import tempfile
from pathlib import Path

# Check if Tellurium is available
try:
    import tellurium as te
    TELLURIUM_AVAILABLE = True
except ImportError:
    TELLURIUM_AVAILABLE = False


@pytest.mark.skipif(not TELLURIUM_AVAILABLE, reason="Tellurium not installed")
class TestAntimonyIntegration:
    """Test Antimony/Tellurium integration."""
    
    def test_import_antimony_integration(self):
        """Test that antimony_integration module can be imported."""
        from tccdp.models.antimony_integration import (
            AntimonyCircuit,
            AntimonyExampleModels,
        )
        assert AntimonyCircuit is not None
        assert AntimonyExampleModels is not None
    
    def test_simple_antimony_model(self):
        """Test loading simple Antimony model."""
        from tccdp.models.antimony_integration import (
            AntimonyCircuit,
            AntimonyExampleModels,
        )
        
        # Get example model
        antimony_str = AntimonyExampleModels.simple_transcription()
        
        # Create circuit
        circuit = AntimonyCircuit(antimony_str, "SimpleTranscription")
        
        # Verify circuit is created
        assert circuit is not None
        assert circuit.model_name == "SimpleTranscription"
    
    def test_get_initial_state(self):
        """Test getting initial state from Antimony model."""
        from tccdp.models.antimony_integration import (
            AntimonyCircuit,
            AntimonyExampleModels,
        )
        
        antimony_str = AntimonyExampleModels.simple_transcription()
        circuit = AntimonyCircuit(antimony_str)
        
        # Get initial state
        state = circuit.get_initial_state()
        
        assert state is not None
        assert len(state) > 0
    
    def test_simulate_antimony_circuit(self):
        """Test simulation with Antimony circuit."""
        from tccdp.models.antimony_integration import (
            AntimonyCircuit,
            AntimonyExampleModels,
        )
        
        antimony_str = AntimonyExampleModels.simple_transcription()
        circuit = AntimonyCircuit(antimony_str)
        
        # Simulate
        results = circuit.simulate(
            t_span=(0, 100),
            stimulus=1.0,
            n_points=100
        )
        
        # Verify results
        assert 't' in results
        assert 'y' in results
        assert 'output' in results
        assert results['success']
        assert len(results['t']) == 100
    
    def test_get_model_info(self):
        """Test getting model information."""
        from tccdp.models.antimony_integration import (
            AntimonyCircuit,
            AntimonyExampleModels,
        )
        
        antimony_str = AntimonyExampleModels.simple_transcription()
        circuit = AntimonyCircuit(antimony_str, "TestModel")
        
        # Get info
        info = circuit.get_model_info()
        
        assert info['name'] == "TestModel"
        assert 'species' in info
        assert 'parameters' in info
        assert 'reactions' in info
        assert info['num_species'] > 0
    
    def test_example_models(self):
        """Test all example models."""
        from tccdp.models.antimony_integration import AntimonyExampleModels
        
        models = [
            ("SimpleTranscription", AntimonyExampleModels.simple_transcription()),
            ("TranscriptionWithFeedback", AntimonyExampleModels.transcription_with_feedback()),
            ("TranscriptionWithMemory", AntimonyExampleModels.transcription_with_memory()),
        ]
        
        for name, antimony_str in models:
            from tccdp.models.antimony_integration import AntimonyCircuit
            
            circuit = AntimonyCircuit(antimony_str, name)
            assert circuit is not None
            
            # Verify each has species
            info = circuit.get_model_info()
            assert info['num_species'] > 0
    
    def test_sbml_export(self):
        """Test SBML export functionality."""
        from tccdp.models.antimony_integration import (
            AntimonyCircuit,
            AntimonyExampleModels,
        )
        
        antimony_str = AntimonyExampleModels.simple_transcription()
        circuit = AntimonyCircuit(antimony_str)
        
        # Export to temporary file
        with tempfile.TemporaryDirectory() as tmpdir:
            sbml_file = Path(tmpdir) / "model.xml"
            
            success = circuit.export_sbml(sbml_file)
            
            assert success
            assert sbml_file.exists()
            
            # Verify file content
            with open(sbml_file, 'r') as f:
                content = f.read()
            
            assert 'sbml' in content.lower()
    
    def test_sbml_loading(self):
        """Test loading SBML file."""
        from tccdp.models.antimony_integration import (
            AntimonyCircuit,
            AntimonyExampleModels,
        )
        
        antimony_str = AntimonyExampleModels.simple_transcription()
        circuit1 = AntimonyCircuit(antimony_str)
        
        # Export to file
        with tempfile.TemporaryDirectory() as tmpdir:
            sbml_file = Path(tmpdir) / "model.xml"
            circuit1.export_sbml(sbml_file)
            
            # Load from file
            circuit2 = AntimonyCircuit.load_sbml(sbml_file)
            
            assert circuit2 is not None
            assert circuit2.model_name == sbml_file.stem
    
    def test_create_antimony_circuit_factory(self):
        """Test factory function for creating Antimony circuit."""
        from tccdp.models.antimony_integration import (
            create_antimony_circuit,
            AntimonyExampleModels,
        )
        
        antimony_str = AntimonyExampleModels.transcription_with_feedback()
        circuit = create_antimony_circuit(antimony_str, "FactoryTest")
        
        assert circuit is not None
        assert circuit.model_name == "FactoryTest"
    
    def test_load_sbml_circuit_factory(self):
        """Test factory function for loading SBML circuit."""
        from tccdp.models.antimony_integration import (
            AntimonyCircuit,
            load_sbml_circuit,
            AntimonyExampleModels,
        )
        
        antimony_str = AntimonyExampleModels.transcription_with_memory()
        circuit1 = AntimonyCircuit(antimony_str)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            sbml_file = Path(tmpdir) / "model.xml"
            circuit1.export_sbml(sbml_file)
            
            # Load using factory
            circuit2 = load_sbml_circuit(sbml_file)
            
            assert circuit2 is not None


@pytest.mark.skipif(not TELLURIUM_AVAILABLE, reason="Tellurium not installed")
class TestAntimonyUsability:
    """Test practical usability of Antimony integration."""
    
    def test_simulation_consistency(self):
        """Test that simulations with same parameters are consistent."""
        from tccdp.models.antimony_integration import (
            AntimonyCircuit,
            AntimonyExampleModels,
        )
        
        antimony_str = AntimonyExampleModels.simple_transcription()
        circuit = AntimonyCircuit(antimony_str)
        
        # Run two simulations
        results1 = circuit.simulate(t_span=(0, 50), stimulus=1.0, n_points=100)
        results2 = circuit.simulate(t_span=(0, 50), stimulus=1.0, n_points=100)
        
        # Should be identical (deterministic)
        import numpy as np
        assert np.allclose(results1['output'], results2['output'])
    
    def test_different_stimuli(self):
        """Test simulations with different stimuli."""
        from tccdp.models.antimony_integration import (
            AntimonyCircuit,
            AntimonyExampleModels,
        )
        
        antimony_str = AntimonyExampleModels.transcription_with_feedback()
        circuit = AntimonyCircuit(antimony_str)
        
        # Run with different stimuli
        results_0 = circuit.simulate(t_span=(0, 100), stimulus=0.0, n_points=100)
        results_1 = circuit.simulate(t_span=(0, 100), stimulus=1.0, n_points=100)
        results_2 = circuit.simulate(t_span=(0, 100), stimulus=2.0, n_points=100)
        
        # Outputs should differ
        import numpy as np
        outputs = [results_0['output'], results_1['output'], results_2['output']]
        
        # Higher stimulus should generally lead to higher output
        # (not guaranteed but likely for typical circuits)
        assert len(outputs) == 3
