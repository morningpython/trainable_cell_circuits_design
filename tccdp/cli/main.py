"""
Command-line interface for Trainable Cell Circuits Design Platform.

Provides CLI commands for training circuits, analyzing results,
and generating reports.
"""

import argparse
import sys
import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any

import numpy as np

from tccdp.circuits import TranscriptionCircuit
from tccdp.core.learning_rule import AutoregulationRule
from tccdp.simulators import ODESimulator
from tccdp.training import (
    create_pavlovian_protocol,
    create_sleep_wake_protocol,
    Trainer,
    TrainingMonitor,
    LearningCurveVisualizer,
)


# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_parser() -> argparse.ArgumentParser:
    """Create command-line argument parser.
    
    Returns:
        ArgumentParser configured with all subcommands
    """
    parser = argparse.ArgumentParser(
        description='Trainable Cell Circuits Design Platform CLI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Train with default Pavlovian protocol
  python -m tccdp.cli train --output-dir ./results

  # Train with custom parameters
  python -m tccdp.cli train --n-epochs 500 --learning-rate 0.02 --protocol sleep-wake

  # Generate visualization report
  python -m tccdp.cli visualize --history ./results/history.json --output-dir ./plots
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Train command
    train_parser = subparsers.add_parser(
        'train',
        help='Train a circuit with specified protocol'
    )
    train_parser.add_argument(
        '--protocol',
        choices=['pavlovian', 'sleep-wake'],
        default='pavlovian',
        help='Training protocol to use (default: pavlovian)'
    )
    train_parser.add_argument(
        '--n-epochs',
        type=int,
        default=100,
        help='Number of training epochs (default: 100)'
    )
    train_parser.add_argument(
        '--learning-rate',
        type=float,
        default=0.01,
        help='Learning rate (default: 0.01)'
    )
    train_parser.add_argument(
        '--dt',
        type=float,
        default=1.0,
        help='Time step for simulation (default: 1.0)'
    )
    train_parser.add_argument(
        '--seed',
        type=int,
        default=42,
        help='Random seed (default: 42)'
    )
    train_parser.add_argument(
        '--output-dir',
        type=str,
        default='./results',
        help='Output directory for results (default: ./results)'
    )
    train_parser.add_argument(
        '--verbose',
        action='store_true',
        help='Display progress bar and verbose output'
    )
    train_parser.set_defaults(func=train_command)
    
    # Info command
    info_parser = subparsers.add_parser(
        'info',
        help='Display system information and defaults'
    )
    info_parser.set_defaults(func=info_command)
    
    # Version command
    version_parser = subparsers.add_parser(
        'version',
        help='Show version information'
    )
    version_parser.set_defaults(func=version_command)
    
    return parser


def train_command(args: argparse.Namespace) -> int:
    """Execute training command.
    
    Args:
        args: Parsed command-line arguments
        
    Returns:
        Exit code (0 for success, non-zero for error)
    """
    try:
        logger.info('=' * 60)
        logger.info('TCCDP Training Command')
        logger.info('=' * 60)
        
        # Create output directory
        output_path = Path(args.output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        logger.info(f'Output directory: {output_path.absolute()}')
        
        # Initialize circuit
        logger.info('Initializing TranscriptionCircuit...')
        circuit = TranscriptionCircuit()
        
        # Initialize learning rule
        learning_rule = AutoregulationRule(learning_rate=args.learning_rate)
        logger.info(f'Learning rate: {args.learning_rate}')
        
        # Create protocol
        logger.info(f'Protocol: {args.protocol}')
        if args.protocol == 'pavlovian':
            protocol = create_pavlovian_protocol()
        else:
            protocol = create_sleep_wake_protocol()
        
        # Initialize simulator
        simulator = ODESimulator(circuit=circuit)
        
        # Create trainer
        trainer = Trainer(
            circuit=circuit,
            learning_rule=learning_rule,
            protocol=protocol,
            simulator=simulator,
            seed=args.seed
        )
        
        # Create monitor
        monitor = TrainingMonitor(
            n_epochs=args.n_epochs,
            save_dir=str(output_path),
            plot_interval=max(1, args.n_epochs // 20),
            verbose=args.verbose
        )
        
        # Simple target output function (50% of max)
        def target_output(phase, time_in_phase):
            if phase.stimulus > 0:
                return 0.5
            return 0.0
        
        # Train
        logger.info(f'Training for {args.n_epochs} epochs...')
        monitor.on_train_begin()
        
        history = trainer.train(
            n_epochs=args.n_epochs,
            dt=args.dt,
            target_output=target_output,
            callbacks=monitor.callbacks,  # Pass monitor's callbacks to trainer
            verbose=args.verbose
        )
        
        monitor.on_train_end()
        
        # Get summary
        summary = monitor.get_summary()
        
        # Save results
        logger.info('Saving results...')
        
        # Save training history
        history_file = output_path / 'training_history.json'
        with open(history_file, 'w') as f:
            json.dump({
                'epochs': [int(e) for e in monitor.history.get_epochs()],
                'losses': [float(l) for l in monitor.history.get_losses()],
                'outputs': [float(o) for o in monitor.history.get_outputs()],
                'stimuli': [float(s) for s in monitor.history.get_stimuli()],
            }, f, indent=2)
        logger.info(f'History saved to {history_file}')
        
        # Save summary
        summary_file = output_path / 'training_summary.json'
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        logger.info(f'Summary saved to {summary_file}')
        
        # Generate plots
        logger.info('Generating visualizations...')
        visualizer = LearningCurveVisualizer(figsize=(12, 9))
        visualizer.plot_learning_curves(
            monitor.history.get_epochs(),
            monitor.history.get_losses(),
            monitor.history.get_outputs(),
            monitor.history.get_stimuli(),
            monitor.history.get_learning_params(),
            save_path=str(output_path / 'learning_curves.png')
        )
        
        visualizer.plot_convergence_analysis(
            monitor.history.get_epochs(),
            monitor.history.get_losses(),
            window_size=max(1, args.n_epochs // 20),
            save_path=str(output_path / 'convergence.png')
        )
        
        # Print summary
        logger.info('=' * 60)
        logger.info('Training Complete!')
        logger.info('=' * 60)
        logger.info(f'Total Epochs: {summary["total_epochs"]}')
        logger.info(f'Initial Loss: {summary["initial_loss"]:.6f}')
        logger.info(f'Final Loss: {summary["final_loss"]:.6f}')
        logger.info(f'Best Loss: {summary["best_loss"]:.6f} (Epoch {summary["best_epoch"]})')
        logger.info(f'Improvement: {summary["loss_improvement"]:.2%}')
        logger.info(f'Duration: {summary["duration_seconds"]:.1f}s')
        logger.info('=' * 60)
        
        return 0
    
    except Exception as e:
        logger.error(f'Error during training: {e}', exc_info=True)
        return 1


def info_command(args: argparse.Namespace) -> int:
    """Display system information.
    
    Args:
        args: Parsed command-line arguments
        
    Returns:
        Exit code
    """
    print('TCCDP System Information')
    print('=' * 60)
    print(f'NumPy version: {np.__version__}')
    
    try:
        import matplotlib
        print(f'Matplotlib version: {matplotlib.__version__}')
        print('Visualization: Available')
    except ImportError:
        print('Visualization: Not available')
    
    try:
        import scipy
        print(f'SciPy version: {scipy.__version__}')
    except ImportError:
        print('SciPy: Not available')
    
    print()
    print('Available Protocols:')
    print('  - pavlovian: Classical conditioning (CS→CS+US→ITI)')
    print('  - sleep-wake: Sleep/wake cycling')
    print()
    print('Default Parameters:')
    print('  - Epochs: 100')
    print('  - Learning Rate: 0.01')
    print('  - Time Step: 1.0')
    print('  - Random Seed: 42')
    print('=' * 60)
    
    return 0


def version_command(args: argparse.Namespace) -> int:
    """Show version information.
    
    Args:
        args: Parsed command-line arguments
        
    Returns:
        Exit code
    """
    try:
        import tccdp
        version = getattr(tccdp, '__version__', 'unknown')
    except Exception:
        version = 'unknown'
    
    print(f'TCCDP Version: {version}')
    return 0


def main(argv: Optional[list] = None) -> int:
    """Main CLI entry point.
    
    Args:
        argv: Command-line arguments (default: sys.argv[1:])
        
    Returns:
        Exit code
    """
    parser = create_parser()
    args = parser.parse_args(argv)
    
    if not hasattr(args, 'func'):
        parser.print_help()
        return 0
    
    return args.func(args)


if __name__ == '__main__':
    sys.exit(main())
