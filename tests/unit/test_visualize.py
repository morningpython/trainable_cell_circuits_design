"""
Tests for visualization module.
"""

import pytest
import numpy as np
from pathlib import Path

from tccdp.training.visualize import (
    LearningCurveVisualizer,
    CircuitDynamicsVisualizer,
    save_training_report,
)


class TestLearningCurveVisualizer:
    """Test LearningCurveVisualizer."""
    
    @pytest.fixture
    def visualizer(self):
        """Create a visualizer instance."""
        return LearningCurveVisualizer()
    
    @pytest.fixture
    def training_data(self):
        """Create sample training data."""
        epochs = np.arange(100)
        losses = 1.0 * np.exp(-epochs / 30) + 0.01 * np.random.randn(100)
        outputs = 0.5 * (1 - np.exp(-epochs / 50))
        stimuli = np.ones(100)
        learning_params = 0.5 * (1 - np.exp(-epochs / 40))
        
        return epochs, losses, outputs, stimuli, learning_params
    
    def test_initialization(self, visualizer):
        """Test creating a visualizer."""
        assert visualizer.figsize == (14, 10)
        assert visualizer.dpi == 150
    
    def test_create_summary_text(self, training_data):
        """Test summary text generation."""
        epochs, losses, outputs, stimuli, learning_params = training_data
        
        text = LearningCurveVisualizer._create_summary_text(epochs, losses, outputs)
        
        assert 'SUMMARY STATISTICS' in text
        assert 'Total Epochs:' in text
        assert 'Initial Loss:' in text
        assert 'Final Loss:' in text
        assert 'Best Loss:' in text
        assert 'Improvement:' in text
    
    def test_plot_learning_curves_no_matplotlib(self, visualizer, training_data, 
                                                monkeypatch):
        """Test plot with matplotlib disabled."""
        import tccdp.training.visualize as viz_module
        monkeypatch.setattr(viz_module, 'HAS_MATPLOTLIB', False)
        
        epochs, losses, outputs, stimuli, _ = training_data
        result = visualizer.plot_learning_curves(
            epochs, losses, outputs, stimuli
        )
        
        assert result is None


class TestCircuitDynamicsVisualizer:
    """Test CircuitDynamicsVisualizer."""
    
    @pytest.fixture
    def visualizer(self):
        """Create a visualizer instance."""
        return CircuitDynamicsVisualizer()
    
    @pytest.fixture
    def state_data(self):
        """Create sample state data."""
        time = np.linspace(0, 10, 100)
        state_v = 70 + 20 * np.sin(time)
        state_h = 0.5 + 0.2 * np.cos(2*time)
        state_c = 0.1 * time
        
        return {
            'V': state_v,
            'H': state_h,
            'C': state_c,
        }, ['V', 'H', 'C'], time
    
    def test_initialization(self, visualizer):
        """Test creating a visualizer."""
        assert visualizer.figsize == (14, 8)
        assert visualizer.dpi == 150
    
    def test_plot_state_evolution_no_matplotlib(self, visualizer, state_data,
                                                monkeypatch):
        """Test plotting with matplotlib disabled."""
        import tccdp.training.visualize as viz_module
        monkeypatch.setattr(viz_module, 'HAS_MATPLOTLIB', False)
        
        trajectories, names, time = state_data
        result = visualizer.plot_state_evolution(names, trajectories, time)
        
        assert result is None


class TestSaveTrainingReport:
    """Test training report generation."""
    
    @pytest.fixture
    def training_data(self):
        """Create sample training data."""
        epochs = np.arange(50)
        losses = 1.0 * np.exp(-epochs / 15)
        outputs = 0.5 * (1 - np.exp(-epochs / 25))
        stimuli = np.ones(50)
        learning_params = 0.5 * (1 - np.exp(-epochs / 20))
        
        return epochs, losses, outputs, stimuli, learning_params
    
    def test_save_training_report_no_matplotlib(self, tmp_path, training_data,
                                                monkeypatch):
        """Test report generation with matplotlib disabled."""
        import tccdp.training.visualize as viz_module
        monkeypatch.setattr(viz_module, 'HAS_MATPLOTLIB', False)
        
        epochs, losses, outputs, stimuli, learning_params = training_data
        
        # Should not raise error even without matplotlib
        save_training_report(
            str(tmp_path),
            epochs, losses, outputs, stimuli, learning_params
        )
    
    def test_save_training_report_creates_directory(self, tmp_path, training_data):
        """Test that report creates output directory."""
        epochs, losses, outputs, stimuli, learning_params = training_data
        
        report_dir = tmp_path / 'report'
        assert not report_dir.exists()
        
        save_training_report(
            str(report_dir),
            epochs, losses, outputs, stimuli, learning_params
        )
        
        assert report_dir.exists()


class TestVisualizationIntegration:
    """Integration tests for visualization module."""
    
    def test_learning_curve_with_full_data(self):
        """Test learning curve with full dataset."""
        epochs = np.arange(100)
        losses = np.exp(-epochs/30)
        outputs = 1 - np.exp(-epochs/50)
        stimuli = np.ones(100)
        learning_params = 1 - np.exp(-epochs/40)
        
        visualizer = LearningCurveVisualizer(figsize=(10, 8))
        
        # Test without saving
        fig = visualizer.plot_learning_curves(
            epochs, losses, outputs, stimuli, learning_params
        )
        
        if fig is not None:
            assert hasattr(fig, 'axes')
            assert len(fig.axes) > 0


class TestLossComparison:
    """Test loss comparison visualization."""
    
    def test_plot_loss_comparison(self):
        """Test comparing multiple loss curves."""
        epochs = np.arange(50)
        loss_dict = {
            'Model A': 1.0 * np.exp(-epochs/20),
            'Model B': 1.5 * np.exp(-epochs/15),
            'Model C': 0.8 * np.exp(-epochs/25),
        }
        
        visualizer = LearningCurveVisualizer()
        fig = visualizer.plot_loss_comparison(
            loss_dict, epochs=epochs, log_scale=True
        )
        
        if fig is not None:
            assert hasattr(fig, 'axes')
            assert len(fig.axes) > 0
    
    def test_plot_convergence_analysis(self):
        """Test convergence analysis."""
        epochs = np.arange(100)
        losses = np.exp(-epochs/30) + 0.01*np.random.randn(100)
        
        visualizer = LearningCurveVisualizer()
        fig = visualizer.plot_convergence_analysis(
            epochs, losses, window_size=10
        )
        
        if fig is not None:
            assert hasattr(fig, 'axes')
            assert len(fig.axes) == 2


class TestPhasePortrait:
    """Test phase portrait visualization."""
    
    def test_plot_phase_portrait_basic(self):
        """Test basic phase portrait."""
        t = np.linspace(0, 4*np.pi, 200)
        x = np.cos(t)
        y = np.sin(t)
        
        visualizer = CircuitDynamicsVisualizer()
        fig = visualizer.plot_phase_portrait(x, y)
        
        if fig is not None:
            assert hasattr(fig, 'axes')
    
    def test_plot_phase_portrait_with_color(self):
        """Test phase portrait with color mapping."""
        t = np.linspace(0, 4*np.pi, 200)
        x = np.cos(t)
        y = np.sin(t)
        epochs = np.arange(200)
        
        visualizer = CircuitDynamicsVisualizer()
        fig = visualizer.plot_phase_portrait(
            x, y, color_by=epochs
        )
        
        if fig is not None:
            assert hasattr(fig, 'axes')
