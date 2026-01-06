"""
Unit tests for Training Monitor and Callbacks.
"""

import pytest
import numpy as np
from datetime import datetime
from pathlib import Path

from tccdp.training.monitor import (
    TrainingMetrics,
    TrainingHistory,
    ProgressBarCallback,
    HistoryCallback,
    VisualizationCallback,
    TrainingMonitor,
)


class TestTrainingMetrics:
    """Test TrainingMetrics dataclass."""
    
    def test_initialization(self):
        """Test creating a TrainingMetrics object."""
        metric = TrainingMetrics(
            epoch=0,
            loss=0.5,
            output=0.1,
            stimulus=1.0,
            learning_param=0.01
        )
        assert metric.epoch == 0
        assert metric.loss == 0.5
        assert metric.output == 0.1
        assert metric.stimulus == 1.0
        assert metric.learning_param == 0.01
        assert metric.timestamp is not None
    
    def test_default_timestamp(self):
        """Test that timestamp is auto-generated."""
        before = datetime.now()
        metric = TrainingMetrics(epoch=0, loss=0.5, output=0.1, stimulus=1.0)
        after = datetime.now()
        
        assert before <= metric.timestamp <= after


class TestTrainingHistory:
    """Test TrainingHistory tracking."""
    
    def test_initialization(self):
        """Test creating an empty TrainingHistory."""
        history = TrainingHistory()
        assert len(history.metrics) == 0
        assert history.start_time is None
        assert history.end_time is None
    
    def test_add_metric(self):
        """Test adding metrics to history."""
        history = TrainingHistory()
        metric = TrainingMetrics(epoch=0, loss=0.5, output=0.1, stimulus=1.0)
        
        history.add_metric(metric)
        assert len(history.metrics) == 1
        assert history.metrics[0] is metric
    
    def test_get_losses(self):
        """Test extracting loss values."""
        history = TrainingHistory()
        history.add_metric(TrainingMetrics(epoch=0, loss=0.5, output=0.1, stimulus=1.0))
        history.add_metric(TrainingMetrics(epoch=1, loss=0.3, output=0.2, stimulus=1.0))
        history.add_metric(TrainingMetrics(epoch=2, loss=0.1, output=0.3, stimulus=1.0))
        
        losses = history.get_losses()
        assert len(losses) == 3
        np.testing.assert_array_almost_equal(losses, [0.5, 0.3, 0.1])
    
    def test_get_outputs(self):
        """Test extracting output values."""
        history = TrainingHistory()
        history.add_metric(TrainingMetrics(epoch=0, loss=0.5, output=0.1, stimulus=1.0))
        history.add_metric(TrainingMetrics(epoch=1, loss=0.3, output=0.2, stimulus=1.0))
        
        outputs = history.get_outputs()
        np.testing.assert_array_almost_equal(outputs, [0.1, 0.2])
    
    def test_get_stimuli(self):
        """Test extracting stimulus values."""
        history = TrainingHistory()
        history.add_metric(TrainingMetrics(epoch=0, loss=0.5, output=0.1, stimulus=1.0))
        history.add_metric(TrainingMetrics(epoch=1, loss=0.3, output=0.2, stimulus=2.0))
        
        stimuli = history.get_stimuli()
        np.testing.assert_array_almost_equal(stimuli, [1.0, 2.0])
    
    def test_get_learning_params(self):
        """Test extracting learning parameter values."""
        history = TrainingHistory()
        history.add_metric(TrainingMetrics(epoch=0, loss=0.5, output=0.1, 
                                          stimulus=1.0, learning_param=0.01))
        history.add_metric(TrainingMetrics(epoch=1, loss=0.3, output=0.2, 
                                          stimulus=1.0, learning_param=0.015))
        
        params = history.get_learning_params()
        np.testing.assert_array_almost_equal(params, [0.01, 0.015])
    
    def test_get_epochs(self):
        """Test extracting epoch numbers."""
        history = TrainingHistory()
        for i in range(5):
            history.add_metric(TrainingMetrics(epoch=i, loss=0.5-i*0.1, 
                                              output=i*0.1, stimulus=1.0))
        
        epochs = history.get_epochs()
        np.testing.assert_array_equal(epochs, [0, 1, 2, 3, 4])
    
    def test_best_loss(self):
        """Test identifying best loss."""
        history = TrainingHistory()
        history.add_metric(TrainingMetrics(epoch=0, loss=0.5, output=0.1, stimulus=1.0))
        history.add_metric(TrainingMetrics(epoch=1, loss=0.2, output=0.2, stimulus=1.0))
        history.add_metric(TrainingMetrics(epoch=2, loss=0.3, output=0.3, stimulus=1.0))
        
        assert history.best_loss == 0.2
    
    def test_best_epoch(self):
        """Test identifying best epoch."""
        history = TrainingHistory()
        history.add_metric(TrainingMetrics(epoch=0, loss=0.5, output=0.1, stimulus=1.0))
        history.add_metric(TrainingMetrics(epoch=1, loss=0.2, output=0.2, stimulus=1.0))
        history.add_metric(TrainingMetrics(epoch=2, loss=0.3, output=0.3, stimulus=1.0))
        
        assert history.best_epoch == 1
    
    def test_duration_seconds(self):
        """Test calculating training duration."""
        history = TrainingHistory()
        history.start_time = datetime(2026, 1, 6, 10, 0, 0)
        history.end_time = datetime(2026, 1, 6, 10, 5, 30)
        
        assert history.duration_seconds == 330  # 5 minutes 30 seconds
    
    def test_summary(self):
        """Test summary statistics."""
        history = TrainingHistory()
        history.add_metric(TrainingMetrics(epoch=0, loss=1.0, output=0.1, stimulus=1.0))
        history.add_metric(TrainingMetrics(epoch=1, loss=0.5, output=0.2, stimulus=1.0))
        history.add_metric(TrainingMetrics(epoch=2, loss=0.1, output=0.3, stimulus=1.0))
        
        summary = history.summary()
        assert summary['total_epochs'] == 0
        assert summary['best_loss'] == 0.1
        assert summary['best_epoch'] == 2
        assert summary['initial_loss'] == 1.0
        assert summary['final_loss'] == 0.1


class TestProgressBarCallback:
    """Test ProgressBarCallback."""
    
    def test_initialization(self):
        """Test creating a ProgressBarCallback."""
        callback = ProgressBarCallback(n_epochs=100, verbose=False)
        assert callback.n_epochs == 100
        assert not callback.verbose
    
    def test_progress_bar_verbose_false(self):
        """Test callback with verbose=False."""
        callback = ProgressBarCallback(n_epochs=10, verbose=False)
        callback.on_train_begin()
        
        for epoch in range(10):
            callback.on_epoch_begin(epoch)
            callback.on_epoch_end(epoch, {'loss': 0.5})
        
        callback.on_train_end()
        # Should not crash and pbar should be None
        assert callback.pbar is None


class TestHistoryCallback:
    """Test HistoryCallback."""
    
    def test_records_metrics(self):
        """Test that callback records training metrics."""
        callback = HistoryCallback()
        callback.on_train_begin()
        
        for epoch in range(5):
            callback.on_epoch_end(epoch, {
                'loss': 0.5 - epoch*0.1,
                'output': epoch*0.1,
                'stimulus': 1.0
            })
        
        callback.on_train_end()
        
        assert len(callback.history.metrics) == 5
        assert callback.history.best_loss == pytest.approx(0.1, abs=1e-9)
        assert callback.history.start_time is not None
        assert callback.history.end_time is not None
    
    def test_history_summary(self):
        """Test history summary from callback."""
        callback = HistoryCallback()
        callback.on_train_begin()
        
        for epoch in range(3):
            callback.on_epoch_end(epoch, {
                'loss': 0.5 - epoch*0.2,
                'output': epoch*0.1,
                'stimulus': 1.0
            })
        
        callback.on_train_end()
        summary = callback.history.summary()
        
        assert summary['best_loss'] == pytest.approx(0.1, abs=1e-9)
        assert summary['initial_loss'] == pytest.approx(0.5, abs=1e-9)


class TestVisualizationCallback:
    """Test VisualizationCallback."""
    
    def test_initialization(self, tmp_path):
        """Test creating a VisualizationCallback."""
        callback = VisualizationCallback(save_dir=str(tmp_path), plot_interval=2)
        assert callback.save_dir == str(tmp_path)
        assert callback.plot_interval == 2
    
    def test_records_metrics(self):
        """Test that callback records metrics."""
        callback = VisualizationCallback(plot_interval=10, verbose=False)
        callback.on_epoch_begin(0)
        
        for epoch in range(5):
            callback.on_epoch_end(epoch, {
                'loss': 0.5 - epoch*0.1,
                'output': epoch*0.1,
                'stimulus': 1.0
            })
        
        assert len(callback.history.metrics) == 5


class TestTrainingMonitor:
    """Test unified TrainingMonitor."""
    
    def test_initialization(self, tmp_path):
        """Test creating a TrainingMonitor."""
        monitor = TrainingMonitor(
            n_epochs=100,
            save_dir=str(tmp_path),
            plot_interval=20,
            verbose=False
        )
        
        assert monitor.n_epochs == 100
        assert len(monitor.callbacks) >= 2  # At least history and visualization
    
    def test_monitor_full_training_cycle(self, tmp_path):
        """Test monitor through full training cycle."""
        monitor = TrainingMonitor(
            n_epochs=10,
            save_dir=str(tmp_path),
            plot_interval=5,
            verbose=False
        )
        
        monitor.on_train_begin()
        
        for epoch in range(10):
            monitor.on_epoch_begin(epoch)
            monitor.on_epoch_end(epoch, {
                'loss': 0.5 - epoch*0.04,
                'output': epoch*0.1,
                'stimulus': 1.0,
                'learning_param': 0.01
            })
        
        monitor.on_train_end()
        
        # Check that history was recorded
        assert len(monitor.history.metrics) == 10
        summary = monitor.get_summary()
        assert 'best_loss' in summary
        assert summary['best_loss'] < 0.15  # 9*0.04 = 0.36, min at epoch 9
    
    def test_monitor_summary(self):
        """Test monitor summary statistics."""
        monitor = TrainingMonitor(n_epochs=5, verbose=False)
        monitor.on_train_begin()
        
        for epoch in range(5):
            monitor.on_epoch_end(epoch, {
                'loss': 1.0 - epoch*0.2,
                'output': epoch*0.05,
                'stimulus': 1.0
            })
        
        monitor.on_train_end()
        summary = monitor.get_summary()
        
        assert summary['total_epochs'] == 0
        assert summary['best_loss'] == pytest.approx(0.2, abs=1e-9)
        assert summary['initial_loss'] == pytest.approx(1.0, abs=1e-9)
        assert summary['final_loss'] == pytest.approx(0.2, abs=1e-9)
