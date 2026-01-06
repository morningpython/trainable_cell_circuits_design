import tellurium as te
import numpy as np

# Test correct Antimony syntax
ant_code = """
model test
  V -> H; k * V
  V = 1.0
  H = 0.0
  k = 0.1
end
"""

rr = te.loada(ant_code)
print("RoadRunner loaded successfully")

# Check API
print("\nChecking simulate() API:")
result = rr.simulate(0, 100, 100)
print(f"Result type: {type(result)}")
print(f"Result shape: {result.shape}")
print(f"Columns: {result.dtype.names if hasattr(result, 'dtype') else 'N/A'}")

# Check first few rows
print(f"\nFirst row: {result[0]}")
print(f"Result[0,0] (time): {result[0,0]}")

# Check SBML methods
print("\nChecking Tellurium SBML methods:")
print("Available methods with 'sbml' or 'SBML':")
methods = [m for m in dir(te) if 'sbml' in m.lower()]
print(methods)

# Check RoadRunner for SBML writing
print("\nChecking RoadRunner SBML methods:")
rr_methods = [m for m in dir(rr) if 'sbml' in m.lower() or 'write' in m.lower()]
print(rr_methods)

# Check model attributes
print("\nChecking RoadRunner model info:")
print(f"Species: {rr.species}")
print(f"Reactions: {rr.reactions}")
