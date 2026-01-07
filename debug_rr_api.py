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

# Check how to access/check parameters
print("\nChecking parameter access:")
print(f"rr.k = {rr.k}")
print(f"rr['k'] = {rr['k']}")

# Try hasattr
print(f"\nhasattr(rr, 'k') = {hasattr(rr, 'k')}")

# Try getattr
print(f"getattr(rr, 'k', None) = {getattr(rr, 'k', None)}")

# Check attribute names
print("\nAll attributes starting with lowercase (likely variables):")
attrs = [attr for attr in dir(rr) if not attr.startswith('_') and attr[0].islower()]
print(attrs[:20])  # First 20

# Check if we can get a list of parameters
print("\nChecking model structure:")
print(f"rr.getFloatingSpeciesIds() = {rr.getFloatingSpeciesIds()}")
print(f"rr.getBoundarySpeciesIds() = {rr.getBoundarySpeciesIds()}")
print(f"rr.getGlobalParameterIds() = {rr.getGlobalParameterIds()}")

# Check reaction info
print(f"\nrr.getNumReactions() = {rr.getNumReactions()}")
print(f"rr.getReactionIds() = {rr.getReactionIds()}")

# Try accessing parameter as attribute
print(f"\nrr.k = {rr.k}")
try:
    rr.k = 0.2
    print(f"After rr.k = 0.2: rr.k = {rr.k}")
except Exception as e:
    print(f"Cannot set k: {e}")

# Try resetting
print(f"\nBefore reset: rr.V = {rr.V}, rr.H = {rr.H}")
rr.reset()
print(f"After reset: rr.V = {rr.V}, rr.H = {rr.H}")
