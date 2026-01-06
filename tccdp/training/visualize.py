"""
Advanced visualization tools for training results and circuit analysis.

Provides high-level plotting utilities for analyzing circuit behavior
and training dynamics.
"""

from typing import Optional, List, Tuple, Dict, Any
import logging
from pathlib import Path

import numpy as np
from numpy.typing import NDArray

try:
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    from matplotlib.gridspec import GridSpec
    import matplotlib
    matplotlib.use('Agg')  # Use non-interactive backend
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

logger = logging.getLogger(__name__)


class LearningCurveVisualizer:
    """Visualize training learning curves and metrics.
    
    Creates publication-quality plots showing training progress,
    including loss curves, output dynamics, and learning parameter evolution.
    """
    
    def __init__(self, figsize: Tuple[int, int] = (14, 10), dpi: int = 150):
        """Initialize visualizer.
        
        Args:
            figsize: Figure size in inches
            dpi: Dots per inch for saved figures
        """
        self.figsize = figsize
        self.dpi = dpi
    
    def plot_learning_curves(
        self,
        epochs: NDArray[np.int_],
        losses: NDArray[np.float64],
        outputs: NDArray[np.float64],
        stimuli: NDArray[np.float64],
        learning_params: Optional[NDArray[np.float64]] = None,
        title: str = 'Training Progress',
        save_path: Optional[str] = None,
        show_grid: bool = True
    ) -> Optional[Any]:
        """Create comprehensive learning curve visualization.
        
        Args:
            epochs: Array of epoch numbers
            losses: Array of loss values per epoch
            outputs: Array of mean outputs per epoch
            stimuli: Array of mean stimuli per epoch
            learning_params: Array of learning parameters per epoch (optional)
            title: Plot title
            save_path: Path to save figure (None to skip saving)
            show_grid: Whether to show grid
            
        Returns:
            Figure object if HAS_MATPLOTLIB, else None
        """
        if not HAS_MATPLOTLIB:
            logger.warning('Matplotlib not available for visualization')
            return None
        
        # Determine layout based on learning_params
        n_plots = 4 if learning_params is not None else 3
        
        fig, axes = plt.subplots(2, 2, figsize=self.figsize, dpi=self.dpi)
        fig.suptitle(title, fontsize=16, fontweight='bold')
        
        # Plot 1: Loss (main metric)
        ax = axes[0, 0]
        ax.plot(epochs, losses, 'b-', linewidth=2.5, label='Loss')
        ax.fill_between(epochs, losses, alpha=0.2, color='blue')
        ax.set_xlabel('Epoch', fontsize=11)
        ax.set_ylabel('Loss (MSE)', fontsize=11)
        ax.set_title('Training Loss', fontsize=12, fontweight='bold')
        if show_grid:
            ax.grid(True, alpha=0.3, linestyle='--')
        ax.set_yscale('log')
        
        # Add best loss annotation
        best_idx = np.argmin(losses)
        ax.plot(epochs[best_idx], losses[best_idx], 'r*', markersize=15, 
               label=f'Best: {losses[best_idx]:.4f}')
        ax.legend(loc='best')
        
        # Plot 2: Circuit Output
        ax = axes[0, 1]
        ax.plot(epochs, outputs, 'g-', linewidth=2.5, label='Mean Output')
        ax.fill_between(epochs, outputs, alpha=0.2, color='green')
        ax.set_xlabel('Epoch', fontsize=11)
        ax.set_ylabel('Output', fontsize=11)
        ax.set_title('Circuit Output Response', fontsize=12, fontweight='bold')
        if show_grid:
            ax.grid(True, alpha=0.3, linestyle='--')
        
        # Add final value annotation
        ax.text(0.98, 0.05, f'Final: {outputs[-1]:.4f}', 
               transform=ax.transAxes, ha='right', va='bottom',
               bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        # Plot 3: Stimulus Profile
        ax = axes[1, 0]
        ax.plot(epochs, stimuli, 'r-', linewidth=2.5, label='Mean Stimulus')
        ax.fill_between(epochs, stimuli, alpha=0.2, color='red')
        ax.set_xlabel('Epoch', fontsize=11)
        ax.set_ylabel('Stimulus', fontsize=11)
        ax.set_title('Input Stimulus Profile', fontsize=12, fontweight='bold')
        if show_grid:
            ax.grid(True, alpha=0.3, linestyle='--')
        
        # Plot 4: Learning Parameter (if provided)
        ax = axes[1, 1]
        if learning_params is not None:
            ax.plot(epochs, learning_params, 'purple', linewidth=2.5, 
                   label='Learning Parameter')
            ax.fill_between(epochs, learning_params, alpha=0.2, color='purple')
            ax.set_ylabel('H_tot', fontsize=11)
            ax.set_title('Learning Parameter Evolution', fontsize=12, fontweight='bold')
            if show_grid:
                ax.grid(True, alpha=0.3, linestyle='--')
        else:
            # Summary statistics text
            ax.axis('off')
            summary_text = self._create_summary_text(epochs, losses, outputs)
            ax.text(0.1, 0.9, summary_text, transform=ax.transAxes, 
                   fontsize=11, verticalalignment='top', family='monospace',
                   bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.7))
        
        ax.set_xlabel('Epoch', fontsize=11)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=self.dpi, bbox_inches='tight')
            logger.info(f'Saved learning curves to {save_path}')
        
        return fig
    
    @staticmethod
    def _create_summary_text(epochs: NDArray, losses: NDArray, 
                             outputs: NDArray) -> str:
        """Create summary statistics text.
        
        Args:
            epochs: Epoch array
            losses: Loss array
            outputs: Output array
            
        Returns:
            Formatted summary text
        """
        best_idx = np.argmin(losses)
        improvement = (losses[0] - losses[-1]) / max(losses[0], 1e-10)
        
        text = 'SUMMARY STATISTICS\n'
        text += '=' * 25 + '\n'
        text += f'Total Epochs: {len(epochs)}\n'
        text += f'Initial Loss: {losses[0]:.4f}\n'
        text += f'Final Loss: {losses[-1]:.4f}\n'
        text += f'Best Loss: {losses[best_idx]:.4f}\n'
        text += f'Best Epoch: {epochs[best_idx]}\n'
        text += f'Improvement: {improvement:.2%}\n'
        text += '-' * 25 + '\n'
        text += f'Mean Output: {np.mean(outputs):.4f}\n'
        text += f'Std Output: {np.std(outputs):.4f}\n'
        
        return text
    
    def plot_loss_comparison(
        self,
        loss_dict: Dict[str, NDArray[np.float64]],
        epochs: Optional[NDArray[np.int_]] = None,
        title: str = 'Loss Comparison',
        save_path: Optional[str] = None,
        log_scale: bool = True
    ) -> Optional[Any]:
        """Compare multiple loss curves.
        
        Args:
            loss_dict: Dictionary mapping labels to loss arrays
            epochs: Epoch numbers (if None, use indices)
            title: Plot title
            save_path: Path to save figure
            log_scale: Whether to use log scale for y-axis
            
        Returns:
            Figure object if HAS_MATPLOTLIB, else None
        """
        if not HAS_MATPLOTLIB:
            logger.warning('Matplotlib not available')
            return None
        
        fig, ax = plt.subplots(figsize=(10, 6), dpi=self.dpi)
        
        colors = plt.cm.tab10(np.linspace(0, 1, len(loss_dict)))
        
        for (label, losses), color in zip(loss_dict.items(), colors):
            x = epochs if epochs is not None else np.arange(len(losses))
            ax.plot(x, losses, marker='o', linewidth=2, label=label, color=color)
        
        ax.set_xlabel('Epoch', fontsize=12)
        ax.set_ylabel('Loss (MSE)', fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        if log_scale:
            ax.set_yscale('log')
        ax.grid(True, alpha=0.3, linestyle='--')
        ax.legend(loc='best', fontsize=10)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=self.dpi, bbox_inches='tight')
            logger.info(f'Saved comparison plot to {save_path}')
        
        return fig
    
    def plot_convergence_analysis(
        self,
        epochs: NDArray[np.int_],
        losses: NDArray[np.float64],
        window_size: int = 10,
        save_path: Optional[str] = None
    ) -> Optional[Any]:
        """Analyze convergence with moving average and variance.
        
        Args:
            epochs: Array of epoch numbers
            losses: Array of loss values
            window_size: Window size for moving average
            save_path: Path to save figure
            
        Returns:
            Figure object if HAS_MATPLOTLIB, else None
        """
        if not HAS_MATPLOTLIB:
            logger.warning('Matplotlib not available')
            return None
        
        # Calculate moving average and std
        ma = np.convolve(losses, np.ones(window_size)/window_size, mode='valid')
        ma_epochs = epochs[window_size-1:]
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5), dpi=self.dpi)
        
        # Plot 1: Loss with moving average
        ax1.plot(epochs, losses, 'b-', alpha=0.5, label='Raw Loss', linewidth=1.5)
        ax1.plot(ma_epochs, ma, 'r-', label=f'MA (window={window_size})', 
                linewidth=2.5)
        ax1.set_xlabel('Epoch', fontsize=11)
        ax1.set_ylabel('Loss (MSE)', fontsize=11)
        ax1.set_title('Loss Convergence', fontsize=12, fontweight='bold')
        ax1.set_yscale('log')
        ax1.grid(True, alpha=0.3)
        ax1.legend()
        
        # Plot 2: Convergence rate (negative gradient)
        loss_grad = np.gradient(losses)
        ax2.plot(epochs[1:], loss_grad[1:], 'g-', linewidth=2)
        ax2.fill_between(epochs[1:], loss_grad[1:], alpha=0.3, color='green')
        ax2.axhline(y=0, color='k', linestyle='--', alpha=0.3)
        ax2.set_xlabel('Epoch', fontsize=11)
        ax2.set_ylabel('Loss Gradient (dL/dE)', fontsize=11)
        ax2.set_title('Convergence Rate', fontsize=12, fontweight='bold')
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=self.dpi, bbox_inches='tight')
            logger.info(f'Saved convergence analysis to {save_path}')
        
        return fig


class CircuitDynamicsVisualizer:
    """Visualize circuit state variables and dynamics.
    
    Creates plots showing how circuit states evolve during training
    and how they respond to stimuli.
    """
    
    def __init__(self, figsize: Tuple[int, int] = (14, 8), dpi: int = 150):
        """Initialize visualizer.
        
        Args:
            figsize: Figure size in inches
            dpi: Dots per inch for saved figures
        """
        self.figsize = figsize
        self.dpi = dpi
    
    def plot_state_evolution(
        self,
        state_names: List[str],
        state_trajectories: Dict[str, NDArray[np.float64]],
        time_points: Optional[NDArray[np.float64]] = None,
        title: str = 'State Variable Evolution',
        save_path: Optional[str] = None
    ) -> Optional[Any]:
        """Plot evolution of circuit state variables.
        
        Args:
            state_names: Names of state variables
            state_trajectories: Dict mapping state names to trajectories
            time_points: Time points for x-axis (optional)
            title: Plot title
            save_path: Path to save figure
            
        Returns:
            Figure object if HAS_MATPLOTLIB, else None
        """
        if not HAS_MATPLOTLIB:
            logger.warning('Matplotlib not available')
            return None
        
        n_states = len(state_names)
        n_cols = min(2, n_states)
        n_rows = (n_states + n_cols - 1) // n_cols
        
        fig, axes = plt.subplots(n_rows, n_cols, figsize=self.figsize, dpi=self.dpi)
        if n_states == 1:
            axes = [axes]
        else:
            axes = axes.flatten()
        
        fig.suptitle(title, fontsize=14, fontweight='bold')
        
        colors = ['blue', 'green', 'red', 'purple', 'orange', 'brown']
        
        for idx, state_name in enumerate(state_names):
            ax = axes[idx]
            trajectory = state_trajectories.get(state_name, np.array([]))
            
            if len(trajectory) > 0:
                x = time_points if time_points is not None else np.arange(len(trajectory))
                color = colors[idx % len(colors)]
                ax.plot(x, trajectory, color=color, linewidth=2)
                ax.fill_between(x, trajectory, alpha=0.2, color=color)
                
                ax.set_ylabel(state_name, fontsize=11, fontweight='bold')
                ax.set_xlabel('Time' if time_points is not None else 'Step', fontsize=10)
                ax.grid(True, alpha=0.3)
                
                # Add statistics
                stats_text = f'Mean: {np.mean(trajectory):.4f}\n'
                stats_text += f'Min: {np.min(trajectory):.4f}\n'
                stats_text += f'Max: {np.max(trajectory):.4f}'
                ax.text(0.98, 0.97, stats_text, transform=ax.transAxes,
                       ha='right', va='top', fontsize=9, family='monospace',
                       bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        # Hide unused axes
        for idx in range(n_states, len(axes)):
            axes[idx].axis('off')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=self.dpi, bbox_inches='tight')
            logger.info(f'Saved state evolution plot to {save_path}')
        
        return fig
    
    def plot_phase_portrait(
        self,
        state_x: NDArray[np.float64],
        state_y: NDArray[np.float64],
        xlabel: str = 'State X',
        ylabel: str = 'State Y',
        title: str = 'Phase Portrait',
        color_by: Optional[NDArray[np.float64]] = None,
        save_path: Optional[str] = None
    ) -> Optional[Any]:
        """Plot 2D phase portrait of circuit dynamics.
        
        Args:
            state_x: X-axis state variable
            state_y: Y-axis state variable
            xlabel: Label for x-axis
            ylabel: Label for y-axis
            title: Plot title
            color_by: Optional array to color trajectory by
            save_path: Path to save figure
            
        Returns:
            Figure object if HAS_MATPLOTLIB, else None
        """
        if not HAS_MATPLOTLIB:
            logger.warning('Matplotlib not available')
            return None
        
        fig, ax = plt.subplots(figsize=(8, 8), dpi=self.dpi)
        
        if color_by is not None:
            scatter = ax.scatter(state_x, state_y, c=color_by, cmap='viridis',
                               s=20, alpha=0.6)
            cbar = plt.colorbar(scatter, ax=ax)
            cbar.set_label('Epoch', fontsize=10)
            ax.plot(state_x, state_y, 'k-', alpha=0.1, linewidth=0.5)
        else:
            ax.plot(state_x, state_y, 'b-', linewidth=2, alpha=0.7)
            ax.plot(state_x[0], state_y[0], 'go', markersize=10, label='Start')
            ax.plot(state_x[-1], state_y[-1], 'r*', markersize=15, label='End')
            ax.legend()
        
        ax.set_xlabel(xlabel, fontsize=12)
        ax.set_ylabel(ylabel, fontsize=12)
        ax.set_title(title, fontsize=13, fontweight='bold')
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=self.dpi, bbox_inches='tight')
            logger.info(f'Saved phase portrait to {save_path}')
        
        return fig


def save_training_report(
    output_dir: str,
    epochs: NDArray[np.int_],
    losses: NDArray[np.float64],
    outputs: NDArray[np.float64],
    stimuli: NDArray[np.float64],
    learning_params: Optional[NDArray[np.float64]] = None,
    state_trajectories: Optional[Dict[str, NDArray]] = None,
    state_names: Optional[List[str]] = None
) -> None:
    """Generate comprehensive training report with all visualizations.
    
    Args:
        output_dir: Directory to save report files
        epochs: Array of epoch numbers
        losses: Array of loss values
        outputs: Array of output values
        stimuli: Array of stimulus values
        learning_params: Learning parameter values (optional)
        state_trajectories: Dict of state trajectories (optional)
        state_names: Names of state variables (optional)
    """
    if not HAS_MATPLOTLIB:
        logger.warning('Matplotlib not available, skipping report generation')
        return
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Generate learning curves
    lcv = LearningCurveVisualizer()
    lcv.plot_learning_curves(
        epochs, losses, outputs, stimuli, learning_params,
        save_path=str(output_path / 'learning_curves.png')
    )
    
    # Generate convergence analysis
    lcv.plot_convergence_analysis(
        epochs, losses, window_size=max(1, len(epochs)//20),
        save_path=str(output_path / 'convergence_analysis.png')
    )
    
    # Generate state evolution if available
    if state_trajectories and state_names:
        cdv = CircuitDynamicsVisualizer()
        cdv.plot_state_evolution(
            state_names, state_trajectories,
            save_path=str(output_path / 'state_evolution.png')
        )
    
    logger.info(f'Training report saved to {output_dir}')
