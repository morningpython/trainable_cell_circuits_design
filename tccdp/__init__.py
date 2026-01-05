"""
Trainable Cell Circuits Design Platform (TCCDP)

A Python framework for simulating and training molecular circuits
capable of learning without genetic modification.

Based on: "Molecular networks can learn without ... 2025 bioRxiv"
"""

__version__ = "0.1.0"
__author__ = "TCCDP Team"
__license__ = "MIT"

from tccdp.core.base_circuit import BaseCircuit
from tccdp.core.learning_rule import LearningRule

__all__ = [
    "BaseCircuit",
    "LearningRule",
    "__version__",
]
