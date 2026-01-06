#!/usr/bin/env python3
"""Check ODESimulator API"""

from tccdp.circuits import TranscriptionCircuit
from tccdp.simulators import ODESimulator
import inspect

# Test basic API
circuit = TranscriptionCircuit()
simulator = ODESimulator(circuit=circuit)

# Check simulate method signature
sig = inspect.signature(simulator.simulate)
print('simulate() signature:')
params = list(sig.parameters.keys())
print(f'Parameters: {params}')

# Try simple simulation
try:
    results = simulator.simulate(t_span=(0, 50), stimulus=lambda t: 1.0, n_points=500)
    print('Simulation succeeded')
    rkeys = list(results.keys())
    print(f'Result keys: {rkeys}')
    olen = len(results['output'])
    print(f'Output length: {olen}')
except Exception as e:
    print(f'Error: {type(e).__name__}: {e}')
    import traceback
    traceback.print_exc()
