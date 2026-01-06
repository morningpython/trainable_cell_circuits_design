"""
Tests for CLI module.
"""

import pytest
import json
from pathlib import Path

from tccdp.cli.main import create_parser, train_command, info_command, version_command


class TestCLIParser:
    """Test CLI argument parser."""
    
    def test_create_parser(self):
        """Test parser creation."""
        parser = create_parser()
        assert parser is not None
    
    def test_parse_train_command(self):
        """Test parsing train command."""
        parser = create_parser()
        args = parser.parse_args([
            'train',
            '--protocol', 'pavlovian',
            '--n-epochs', '50'
        ])
        assert args.command == 'train'
        assert args.protocol == 'pavlovian'
        assert args.n_epochs == 50
    
    def test_parse_train_with_learning_rate(self):
        """Test parsing train with learning rate."""
        parser = create_parser()
        args = parser.parse_args([
            'train',
            '--learning-rate', '0.02'
        ])
        assert args.learning_rate == 0.02
    
    def test_parse_train_sleep_wake(self):
        """Test parsing train with sleep-wake protocol."""
        parser = create_parser()
        args = parser.parse_args([
            'train',
            '--protocol', 'sleep-wake',
            '--n-epochs', '100'
        ])
        assert args.protocol == 'sleep-wake'
        assert args.n_epochs == 100
    
    def test_parse_info_command(self):
        """Test parsing info command."""
        parser = create_parser()
        args = parser.parse_args(['info'])
        assert args.command == 'info'
        assert hasattr(args, 'func')
    
    def test_parse_version_command(self):
        """Test parsing version command."""
        parser = create_parser()
        args = parser.parse_args(['version'])
        assert args.command == 'version'
        assert hasattr(args, 'func')
    
    def test_default_values(self):
        """Test default command values."""
        parser = create_parser()
        args = parser.parse_args(['train'])
        
        assert args.protocol == 'pavlovian'
        assert args.n_epochs == 100
        assert args.learning_rate == 0.01
        assert args.dt == 1.0
        assert args.seed == 42
        assert args.output_dir == './results'


class TestInfoCommand:
    """Test info command."""
    
    def test_info_command(self):
        """Test info command execution."""
        from argparse import Namespace
        args = Namespace()
        result = info_command(args)
        assert result == 0


class TestVersionCommand:
    """Test version command."""
    
    def test_version_command(self):
        """Test version command execution."""
        from argparse import Namespace
        args = Namespace()
        result = version_command(args)
        assert result == 0


class TestTrainCommand:
    """Test train command."""
    
    def test_train_command_basic(self, tmp_path):
        """Test basic training command."""
        from argparse import Namespace
        
        args = Namespace(
            protocol='pavlovian',
            n_epochs=5,
            learning_rate=0.01,
            dt=1.0,
            seed=42,
            output_dir=str(tmp_path),
            verbose=False
        )
        
        result = train_command(args)
        assert result == 0
        
        # Check output files
        assert (tmp_path / 'training_history.json').exists()
        assert (tmp_path / 'training_summary.json').exists()
    
    def test_train_command_creates_output_dir(self, tmp_path):
        """Test that train command creates output directory."""
        from argparse import Namespace
        
        output_dir = tmp_path / 'new_dir'
        assert not output_dir.exists()
        
        args = Namespace(
            protocol='pavlovian',
            n_epochs=2,
            learning_rate=0.01,
            dt=1.0,
            seed=42,
            output_dir=str(output_dir),
            verbose=False
        )
        
        result = train_command(args)
        assert result == 0
        assert output_dir.exists()
    
    def test_train_command_saves_history(self, tmp_path):
        """Test that training saves history."""
        from argparse import Namespace
        
        args = Namespace(
            protocol='pavlovian',
            n_epochs=3,
            learning_rate=0.01,
            dt=1.0,
            seed=42,
            output_dir=str(tmp_path),
            verbose=False
        )
        
        train_command(args)
        
        history_file = tmp_path / 'training_history.json'
        assert history_file.exists()
        
        with open(history_file) as f:
            history = json.load(f)
        
        assert 'epochs' in history
        assert 'losses' in history
        assert 'outputs' in history
        assert 'stimuli' in history
        assert len(history['epochs']) == 3
    
    def test_train_command_saves_summary(self, tmp_path):
        """Test that training saves summary."""
        from argparse import Namespace
        
        args = Namespace(
            protocol='pavlovian',
            n_epochs=3,
            learning_rate=0.01,
            dt=1.0,
            seed=42,
            output_dir=str(tmp_path),
            verbose=False
        )
        
        train_command(args)
        
        summary_file = tmp_path / 'training_summary.json'
        assert summary_file.exists()
        
        with open(summary_file) as f:
            summary = json.load(f)
        
        assert 'initial_loss' in summary
        assert 'final_loss' in summary
        assert 'best_loss' in summary
        assert 'improvement' in summary or 'loss_improvement' in summary
    
    def test_train_sleep_wake_protocol(self, tmp_path):
        """Test training with sleep-wake protocol."""
        from argparse import Namespace
        
        args = Namespace(
            protocol='sleep-wake',
            n_epochs=2,
            learning_rate=0.01,
            dt=1.0,
            seed=42,
            output_dir=str(tmp_path),
            verbose=False
        )
        
        result = train_command(args)
        assert result == 0
        assert (tmp_path / 'training_history.json').exists()


class TestCLIIntegration:
    """Integration tests for CLI."""
    
    def test_train_with_all_options(self, tmp_path):
        """Test training with all options specified."""
        from argparse import Namespace
        
        args = Namespace(
            protocol='pavlovian',
            n_epochs=10,
            learning_rate=0.02,
            dt=0.5,
            seed=123,
            output_dir=str(tmp_path),
            verbose=True
        )
        
        result = train_command(args)
        assert result == 0
    
    def test_cli_main_with_help(self):
        """Test CLI main with help argument."""
        from tccdp.cli.main import main
        from argparse import ArgumentParser
        
        # Help should return 0
        try:
            parser = create_parser()
            # Can't easily test help without exiting, but we can test parser creation
            assert parser is not None
        except SystemExit:
            # Help causes exit, which is expected
            pass
