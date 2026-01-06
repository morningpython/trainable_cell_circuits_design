"""
Training monitoring and visualization utilities.

Provides tools for tracking training progress, logging metrics,
and generating performance visualizations.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
import logging
from datetime import datetime

import numpy as np
from numpy.typing import NDArray

try:
    from tqdm import tqdm
    HAS_TQDM = True
except ImportError:
    HAS_TQDM = False

try:
    import matplotlib.pyplot as plt
    import matplotlib
    matplotlib.use('Agg')  # Use non-interactive backend
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False


# Setup logging
logger = logging.getLogger(__name__)


@dataclass
class TrainingMetrics:
    """Container for training metrics at a single epoch.
    
    Attributes:
        epoch: Epoch number
        loss: Training loss at this epoch
        output: Mean circuit output
        stimulus: Mean stimulus value
        learning_param: Learning parameter value
        timestamp: When this epoch was recorded
    """
    epoch: int
    loss: float
    output: float
    stimulus: float
    learning_param: Optional[float] = None
    timestamp: Optional[datetime] = None

    def __post_init__(self):
        """Initialize timestamp if not provided."""
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class TrainingHistory:
    """Complete training history with metrics tracking.
    
    Attributes:
        metrics: List of TrainingMetrics objects
        start_time: Training start time
        end_time: Training end time
        total_epochs: Total epochs trained
    """
    metrics: List[TrainingMetrics] = field(default_factory=list)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    total_epochs: int = 0
    
    def add_metric(self, metric: TrainingMetrics) -> None:
        """Add a training metric to history.
        
        Args:
            metric: TrainingMetrics object to add
        """
        self.metrics.append(metric)
    
    def get_losses(self) -> NDArray[np.float64]:
        """Get array of all loss values.
        
        Returns:
            1D array of losses
        """
        return np.array([m.loss for m in self.metrics])
    
    def get_outputs(self) -> NDArray[np.float64]:
        """Get array of all output values.
        
        Returns:
            1D array of outputs
        """
        return np.array([m.output for m in self.metrics])
    
    def get_stimuli(self) -> NDArray[np.float64]:
        """Get array of all stimulus values.
        
        Returns:
            1D array of stimuli
        """
        return np.array([m.stimulus for m in self.metrics])
    
    def get_learning_params(self) -> NDArray[np.float64]:
        """Get array of all learning parameter values.
        
        Returns:
            1D array of learning parameters
        """
        return np.array([
            m.learning_param if m.learning_param is not None else 0.0
            for m in self.metrics
        ])
    
    def get_epochs(self) -> NDArray[np.int_]:
        """Get array of all epoch numbers.
        
        Returns:
            1D array of epoch numbers
        """
        return np.array([m.epoch for m in self.metrics])
    
    @property
    def duration_seconds(self) -> float:
        """Get total training duration in seconds.
        
        Returns:
            Duration in seconds, or 0 if not completed
        """
        if self.start_time is None or self.end_time is None:
            return 0.0
        return (self.end_time - self.start_time).total_seconds()
    
    @property
    def best_loss(self) -> Optional[float]:
        """Get best (minimum) loss value.
        
        Returns:
            Best loss or None if no metrics
        """
        if not self.metrics:
            return None
        return min(m.loss for m in self.metrics)
    
    @property
    def best_epoch(self) -> Optional[int]:
        """Get epoch with best loss.
        
        Returns:
            Epoch number with best loss or None if no metrics
        """
        if not self.metrics:
            return None
        best_idx = np.argmin(self.get_losses())
        return self.metrics[best_idx].epoch
    
    def summary(self) -> Dict[str, Any]:
        """Get summary statistics of training.
        
        Returns:
            Dictionary with summary metrics
        """
        if not self.metrics:
            return {}
        
        losses = self.get_losses()
        
        return {
            'total_epochs': self.total_epochs,
            'duration_seconds': self.duration_seconds,
            'initial_loss': losses[0],
            'final_loss': losses[-1],
            'best_loss': self.best_loss,
            'best_epoch': self.best_epoch,
            'loss_improvement': (losses[0] - losses[-1]) / max(losses[0], 1e-10),
            'mean_loss': float(np.mean(losses)),
            'std_loss': float(np.std(losses)),
        }


class MonitoringCallback(ABC):
    """Abstract base class for monitoring callbacks.
    
    Subclasses implement specific monitoring behaviors like
    logging, visualization, or early stopping.
    """
    
    @abstractmethod
    def on_epoch_begin(self, epoch: int, logs: Optional[Dict] = None) -> None:
        """Called at beginning of each epoch.
        
        Args:
            epoch: Current epoch number
            logs: Dictionary of metrics
        """
        pass
    
    @abstractmethod
    def on_epoch_end(self, epoch: int, logs: Optional[Dict] = None) -> None:
        """Called at end of each epoch.
        
        Args:
            epoch: Current epoch number
            logs: Dictionary of metrics
        """
        pass
    
    def on_train_begin(self) -> None:
        """Called at beginning of training."""
        pass
    
    def on_train_end(self) -> None:
        """Called at end of training."""
        pass


class ProgressBarCallback(MonitoringCallback):
    """Callback that displays training progress with tqdm.
    
    Shows a progress bar with current metrics.
    """
    
    def __init__(self, n_epochs: int, verbose: bool = True):
        """Initialize progress bar callback.
        
        Args:
            n_epochs: Total number of epochs
            verbose: Whether to display progress
        """
        self.n_epochs = n_epochs
        self.verbose = verbose
        self.pbar: Optional[Any] = None
        self.epoch = 0
    
    def on_train_begin(self) -> None:
        """Initialize progress bar at training start."""
        if HAS_TQDM and self.verbose:
            self.pbar = tqdm(total=self.n_epochs, desc='Training', unit='epoch')
    
    def on_epoch_begin(self, epoch: int, logs: Optional[Dict] = None) -> None:
        """Called at epoch start."""
        self.epoch = epoch
    
    def on_epoch_end(self, epoch: int, logs: Optional[Dict] = None) -> None:
        """Update progress bar with metrics.
        
        Args:
            epoch: Current epoch number
            logs: Dictionary with 'loss' and other metrics
        """
        if self.pbar is None:
            return
        
        logs = logs or {}
        loss = logs.get('loss', 0.0)
        desc = f'Training (loss={loss:.4f})'
        self.pbar.update(1)
        self.pbar.set_description(desc)
    
    def on_train_end(self) -> None:
        """Close progress bar at training end."""
        if self.pbar is not None:
            self.pbar.close()


class HistoryCallback(MonitoringCallback):
    """Callback that records training history.
    
    Stores all metrics from training for later analysis.
    """
    
    def __init__(self):
        """Initialize history callback."""
        self.history = TrainingHistory()
    
    def on_train_begin(self) -> None:
        """Initialize history at training start."""
        self.history.start_time = datetime.now()
    
    def on_epoch_begin(self, epoch: int, logs: Optional[Dict] = None) -> None:
        """Called at epoch start."""
        pass
    
    def on_epoch_end(self, epoch: int, logs: Optional[Dict] = None) -> None:
        """Record metrics at epoch end.
        
        Args:
            epoch: Current epoch number
            logs: Dictionary with metrics
        """
        logs = logs or {}
        
        metric = TrainingMetrics(
            epoch=epoch,
            loss=logs.get('loss', 0.0),
            output=logs.get('output', 0.0),
            stimulus=logs.get('stimulus', 0.0),
            learning_param=logs.get('learning_param', None),
            timestamp=datetime.now()
        )
        self.history.add_metric(metric)
    
    def on_train_end(self) -> None:
        """Finalize history at training end."""
        self.history.end_time = datetime.now()


class VisualizationCallback(MonitoringCallback):
    """Callback that generates training visualizations.
    
    Saves plots at specified intervals during training.
    """
    
    def __init__(
        self,
        save_dir: Optional[str] = None,
        plot_interval: int = 10,
        verbose: bool = False
    ):
        """Initialize visualization callback.
        
        Args:
            save_dir: Directory to save plots (default: current directory)
            plot_interval: Generate plot every N epochs
            verbose: Whether to print progress
        """
        self.save_dir = save_dir or '.'
        self.plot_interval = plot_interval
        self.verbose = verbose
        self.history = TrainingHistory()
    
    def on_epoch_begin(self, epoch: int, logs: Optional[Dict] = None) -> None:
        """Called at epoch start."""
        pass
    
    def on_epoch_end(self, epoch: int, logs: Optional[Dict] = None) -> None:
        """Record metrics and optionally generate plots.
        
        Args:
            epoch: Current epoch number
            logs: Dictionary with metrics
        """
        logs = logs or {}
        
        metric = TrainingMetrics(
            epoch=epoch,
            loss=logs.get('loss', 0.0),
            output=logs.get('output', 0.0),
            stimulus=logs.get('stimulus', 0.0),
            learning_param=logs.get('learning_param', None),
        )
        self.history.add_metric(metric)
        
        # Generate plot at intervals
        if (epoch + 1) % self.plot_interval == 0:
            if HAS_MATPLOTLIB:
                self._generate_plot(epoch + 1)
    
    def _generate_plot(self, epoch: int) -> None:
        """Generate and save training visualization.
        
        Args:
            epoch: Current epoch number
        """
        if not HAS_MATPLOTLIB:
            logger.warning('Matplotlib not available for visualization')
            return
        
        try:
            fig, axes = plt.subplots(2, 2, figsize=(12, 8))
            fig.suptitle(f'Training Progress - Epoch {epoch}', fontsize=14)
            
            epochs = self.history.get_epochs()
            losses = self.history.get_losses()
            outputs = self.history.get_outputs()
            stimuli = self.history.get_stimuli()
            
            # Loss plot
            axes[0, 0].plot(epochs, losses, 'b-', linewidth=2)
            axes[0, 0].set_xlabel('Epoch')
            axes[0, 0].set_ylabel('Loss')
            axes[0, 0].set_title('Training Loss')
            axes[0, 0].grid(True, alpha=0.3)
            
            # Output plot
            axes[0, 1].plot(epochs, outputs, 'g-', linewidth=2)
            axes[0, 1].set_xlabel('Epoch')
            axes[0, 1].set_ylabel('Output')
            axes[0, 1].set_title('Circuit Output')
            axes[0, 1].grid(True, alpha=0.3)
            
            # Stimulus plot
            axes[1, 0].plot(epochs, stimuli, 'r-', linewidth=2)
            axes[1, 0].set_xlabel('Epoch')
            axes[1, 0].set_ylabel('Stimulus')
            axes[1, 0].set_title('Mean Stimulus')
            axes[1, 0].grid(True, alpha=0.3)
            
            # Summary statistics
            summary = self.history.summary()
            axes[1, 1].axis('off')
            summary_text = '\n'.join([
                f'{k}: {v:.4f}' if isinstance(v, float) else f'{k}: {v}'
                for k, v in summary.items()
            ])
            axes[1, 1].text(0.1, 0.5, summary_text, fontsize=10, family='monospace',
                          verticalalignment='center')
            
            plt.tight_layout()
            
            # Save figure
            filename = f'{self.save_dir}/training_epoch_{epoch:04d}.png'
            plt.savefig(filename, dpi=100, bbox_inches='tight')
            plt.close()
            
            if self.verbose:
                logger.info(f'Saved visualization to {filename}')
        
        except Exception as e:
            logger.error(f'Error generating visualization: {e}')


class TrainingMonitor:
    """Unified training monitor combining history and visualization.
    
    Manages all monitoring aspects of training including logging,
    progress tracking, and metrics visualization.
    """
    
    def __init__(
        self,
        n_epochs: int,
        save_dir: Optional[str] = None,
        plot_interval: int = 10,
        verbose: bool = True
    ):
        """Initialize training monitor.
        
        Args:
            n_epochs: Total number of epochs to train
            save_dir: Directory to save results
            plot_interval: Generate plots every N epochs
            verbose: Whether to display progress information
        """
        self.n_epochs = n_epochs
        self.callbacks: List[MonitoringCallback] = []
        
        # Add progress bar callback
        if verbose:
            self.callbacks.append(ProgressBarCallback(n_epochs, verbose=True))
        
        # Always add history callback
        self.history_callback = HistoryCallback()
        self.callbacks.append(self.history_callback)
        
        # Add visualization callback
        self.callbacks.append(
            VisualizationCallback(
                save_dir=save_dir,
                plot_interval=plot_interval,
                verbose=verbose
            )
        )
    
    @property
    def history(self) -> TrainingHistory:
        """Get training history.
        
        Returns:
            TrainingHistory object with all metrics
        """
        return self.history_callback.history
    
    def on_train_begin(self) -> None:
        """Notify all callbacks of training start."""
        for callback in self.callbacks:
            callback.on_train_begin()
    
    def on_train_end(self) -> None:
        """Notify all callbacks of training end."""
        for callback in self.callbacks:
            callback.on_train_end()
    
    def on_epoch_begin(self, epoch: int, logs: Optional[Dict] = None) -> None:
        """Notify all callbacks of epoch start.
        
        Args:
            epoch: Current epoch number
            logs: Dictionary of metrics
        """
        for callback in self.callbacks:
            callback.on_epoch_begin(epoch, logs)
    
    def on_epoch_end(self, epoch: int, logs: Optional[Dict] = None) -> None:
        """Notify all callbacks of epoch end.
        
        Args:
            epoch: Current epoch number
            logs: Dictionary of metrics
        """
        for callback in self.callbacks:
            callback.on_epoch_end(epoch, logs)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get training summary statistics.
        
        Returns:
            Dictionary with summary metrics
        """
        return self.history.summary()
