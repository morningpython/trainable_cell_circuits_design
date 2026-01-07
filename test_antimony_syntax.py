#!/usr/bin/env python3
"""Test Tellurium Antimony syntax - without parameter declarations"""

import tellurium as te

# Test simple model without parameter declarations
ant = '''
model test
  V -> V; 0.1
  V -> ; 0.1 * V
  -> H; 1.0 * V
  H -> ; 0.01 * H
  
  V = 0.0
  H = 0.0
end
'''

try:
    r = te.loada(ant)
    print("Model 1 loaded successfully!")
    print("Species:", r.getFloatingSpeciesIds())
    r.simulate(0, 100, 100)
    print("Simulation successful!")
except Exception as e:
    print(f"Error: {e}")

# Test with named parameters in reactions
ant2 = '''
model test2
  V -> V; k_in
  V -> ; k_dv * V
  -> H; beta_h * V
  H -> ; k_dh * H
  
  V = 0.0
  H = 0.0
  k_in = 0.1
  k_dv = 0.1
  k_dh = 0.01
  beta_h = 1.0
end
'''

try:
    r = te.loada(ant2)
    print("\nModel 2 loaded successfully!")
    print("Species:", r.getFloatingSpeciesIds())
    print("Parameters:", r.getGlobalParameterIds())
except Exception as e:
    print(f"\nError in model 2: {e}")

# Test with compartment
ant3 = '''
model test3
  compartment cell = 1.0
  species V in cell, H in cell
  
  V -> V; 0.1
  V -> ; 0.1 * V
  -> H; 1.0 * V
  H -> ; 0.01 * H
  
  V = 0.0
  H = 0.0
end
'''

try:
    r = te.loada(ant3)
    print("\nModel 3 loaded successfully!")
    print("Species:", r.getFloatingSpeciesIds())
except Exception as e:
    print(f"\nError in model 3: {e}")
