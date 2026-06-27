#!/usr/bin/env python3
# ============================================================================
#  build_water_ref.py  —  TTT-WSP v5
#
#  Generates the isolated-H2O reference needed for a CORRECT adsorption energy:
#      dE_ads = E(slab+H2O) - E(slab) - E(H2O_gas)
#  The gas-phase H2O must be computed in the SAME pseudopotential / ecut as the
#  slab, in a large box at Gamma, with assume_isolated to remove image dipole
#  interaction. The earlier workflow never isolated this reference cleanly.
# ============================================================================
import numpy as np
from ase import Atoms
from ase.io import write

BOX   = 15.0     # cubic box edge (Ang); large enough to isolate the molecule
ROH   = 0.96
ANG   = np.radians(104.5) / 2
O  = np.array([BOX/2, BOX/2, BOX/2])
H1 = O + ROH * np.array([ np.sin(ANG), np.cos(ANG), 0.0])
H2 = O + ROH * np.array([-np.sin(ANG), np.cos(ANG), 0.0])
water = Atoms("OHH", positions=[O, H1, H2], cell=[BOX, BOX, BOX], pbc=True)

PSEUDO = {"O": "O.pbe-n-kjpaw_psl.1.0.0.UPF", "H": "H.pbe-kjpaw_psl.1.0.0.UPF"}

input_data = {
    "control": {"calculation": "relax", "prefix": "h2o_ref",
                "outdir": "./out", "pseudo_dir": "./pseudo",
                "tprnfor": True, "forc_conv_thr": 1.0e-3},
    "system":  {"ibrav": 0, "ecutwfc": 50.0, "ecutrho": 400.0,   # MATCH the slab
                "assume_isolated": "mt"},                         # Martyna-Tuckerman
    "electrons": {"conv_thr": 1.0e-7, "mixing_beta": 0.5},
    "ions": {"ion_dynamics": "bfgs"},
}
write("h2o_ref.in", water, format="espresso-in",
      input_data=input_data, pseudopotentials=PSEUDO, kpts=(1, 1, 1))
write("h2o_ref.xyz", water)
print("[water] wrote h2o_ref.in (15 A box, Gamma, Martyna-Tuckerman isolation)")
print("[water] IMPORTANT: ecutwfc/ecutrho here MUST equal the slab values.")
