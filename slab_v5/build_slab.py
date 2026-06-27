#!/usr/bin/env python3
# ============================================================================
#  build_slab.py  —  TTT-WSP v5  (slab-model rebuild)
#
#  Purpose
#  -------
#  Build a PHYSICALLY MEANINGFUL surface slab for studying H2O adsorption /
#  dissociation on S/P-doped sp3 lattices, replacing the earlier bulk-
#  interstitial model in which H2O was frozen inside a periodic bulk cell
#  (which produced non-physical adsorption energies of +4 to +17 eV).
#
#  What this script guarantees that the old workflow did NOT:
#    1. A real surface with a vacuum gap (so "adsorption" has meaning).
#    2. A passivated, fixed bottom (removes spurious dangling-bond states,
#       anchors the slab to the bulk; only the top surface does chemistry).
#    3. The dopant placed in the SURFACE region (where catalysis happens),
#       not buried at the cell center.
#    4. H2O placed above the active site and left FREE to relax.
#    5. A dipole correction set up for the asymmetric slab.
#
#  Output: a Quantum ESPRESSO pw.x input file (and an .xyz for inspection).
#
#  Requires: ase >= 3.22   (pip install ase)
#
#  Author scaffold for: kiki054-n / tttwsp
#  License: MIT
# ============================================================================
import numpy as np
from ase import Atoms
from ase.build import diamond100, diamond111
from ase.constraints import FixAtoms
from ase.io import write

# ----------------------------------------------------------------------------
# 1. USER PARAMETERS
# ----------------------------------------------------------------------------
FACE        = "100"      # "100" or "111"
NX, NY      = 3, 3       # in-plane supercell (lateral size; >=3 isolates dopant)
NLAYERS     = 8          # number of atomic layers (>=6; converge this!)
A_LAT       = 5.431      # Si lattice constant (Ang). Re-optimize for your pseudo.
VACUUM      = 8.0        # vacuum on EACH side (Ang). Total gap ~ 2*VACUUM.
N_FIXED     = 3          # bottom layers fixed to bulk geometry
SI_H        = 1.48       # Si-H passivation bond length (Ang)

# Dopants: list of (element, "top"|"sub") placed near the active site.
#   Si+S      -> [("S","top")]
#   Si+S+P    -> [("S","top"), ("P","top")]   (two adjacent surface sites)
#   undoped   -> []
DOPANTS     = [("S", "top"), ("P", "top")]

ADD_WATER   = True       # place a free H2O above the active site
O_HEIGHT    = 2.3        # initial O height above the surface (Ang); relaxed later

OUT_PREFIX  = "tttwsp_si_sp_h2o_100"   # output file stem

# Pseudopotential file names (pslibrary 1.0.0 PAW-PBE; confirm on your machine)
PSEUDO = {
    "Si": "Si.pbe-n-kjpaw_psl.1.0.0.UPF",
    "S":  "S.pbe-n-kjpaw_psl.1.0.0.UPF",
    "P":  "P.pbe-n-kjpaw_psl.1.0.0.UPF",
    "O":  "O.pbe-n-kjpaw_psl.1.0.0.UPF",
    "H":  "H.pbe-kjpaw_psl.1.0.0.UPF",
}

# ----------------------------------------------------------------------------
# 2. BUILD THE CLEAN SLAB
# ----------------------------------------------------------------------------
if FACE == "100":
    slab = diamond100("Si", (NX, NY, NLAYERS), a=A_LAT, vacuum=VACUUM,
                      orthogonal=True, periodic=True)
elif FACE == "111":
    slab = diamond111("Si", (NX, NY, NLAYERS), a=A_LAT, vacuum=VACUUM,
                      orthogonal=False, periodic=True)
else:
    raise ValueError("FACE must be '100' or '111'")

slab.center(vacuum=VACUUM, axis=2)

# ----------------------------------------------------------------------------
# 3. LAYER DETECTION (cluster atoms by z)
# ----------------------------------------------------------------------------
def detect_layers(atoms, tol=0.5):
    z = atoms.positions[:, 2]
    order = np.argsort(z)
    layers, current = [], [order[0]]
    for idx in order[1:]:
        if abs(z[idx] - z[current[-1]]) < tol:
            current.append(idx)
        else:
            layers.append(current); current = [idx]
    layers.append(current)
    return layers  # bottom -> top

layers = detect_layers(slab)
print(f"[build] {FACE} slab: {len(slab)} Si atoms in {len(layers)} layers")

# ----------------------------------------------------------------------------
# 4. PASSIVATE THE BOTTOM with H (sp3 dangling-bond completion)
# ----------------------------------------------------------------------------
def neighbors_above(atoms, i, cutoff=2.6):
    p = atoms.positions[i]
    dirs = []
    for j in range(len(atoms)):
        if j == i or atoms[j].symbol == "H":
            continue
        d = atoms.positions[j] - p
        if 0.1 < np.linalg.norm(d) < cutoff and d[2] > 0.2:
            dirs.append(d / np.linalg.norm(d))
    return dirs

def complete_sp3(up):
    if len(up) == 3:
        d = -(up[0] + up[1] + up[2]); return [d / np.linalg.norm(d)]
    if len(up) == 2:
        base = -0.5 * (up[0] + up[1])
        n = np.cross(up[0], up[1]); n /= np.linalg.norm(n)
        h = np.sqrt(2.0 / 3.0)
        return [base + h * n, base - h * n]
    return []

H_added = []
for i in layers[0]:                       # bottom layer
    dangling = complete_sp3(neighbors_above(slab, i))
    for d in dangling:
        if d[2] < 0:                      # keep only downward-pointing caps
            H_added.append(slab.positions[i] + SI_H * d)
for hp in H_added:
    slab += Atoms("H", positions=[hp])
print(f"[build] passivated bottom with {len(H_added)} H atoms")

# ----------------------------------------------------------------------------
# 5. FIX THE BOTTOM N_FIXED LAYERS (+ their H)
# ----------------------------------------------------------------------------
fixed_idx = []
for L in layers[:N_FIXED]:
    fixed_idx += L
# also fix the passivating H (they belong to the fixed bulk region)
for i in range(len(slab)):
    if slab[i].symbol == "H":
        fixed_idx.append(i)
slab.set_constraint(FixAtoms(indices=sorted(set(fixed_idx))))
print(f"[build] fixed {len(set(fixed_idx))} atoms (bottom {N_FIXED} layers + cap H)")

# ----------------------------------------------------------------------------
# 6. PLACE DOPANT(S) IN THE TOP SURFACE REGION
# ----------------------------------------------------------------------------
top_layer = layers[-1]
xy_center = slab.cell.array[:2, :2].sum(axis=0)[:2] / 2.0  # cell xy center
def nearest_top_atom(exclude=()):
    best, bestd = None, 1e9
    for i in top_layer:
        if i in exclude:
            continue
        d = np.linalg.norm(slab.positions[i, :2] - xy_center)
        if d < bestd:
            best, bestd = i, d
    return best

active_site = None
used = []
for (elem, where) in DOPANTS:
    i = nearest_top_atom(exclude=used)
    slab[i].symbol = elem
    used.append(i)
    if active_site is None:
        active_site = i
    print(f"[build] doped: {elem} at top-layer index {i}, pos={np.round(slab.positions[i],3)}")

if active_site is None:                    # undoped reference: use central top atom
    active_site = nearest_top_atom()

# ----------------------------------------------------------------------------
# 7. ADD A FREE H2O ABOVE THE ACTIVE SITE
# ----------------------------------------------------------------------------
if ADD_WATER:
    site = slab.positions[active_site].copy()
    ztop = slab.positions[[i for L in layers for i in L], 2].max()
    O = np.array([site[0], site[1], ztop + O_HEIGHT])
    # water geometry: O-H = 0.96 Ang, H-O-H = 104.5 deg, H atoms tilted upward
    roh, half = 0.96, np.radians(104.5) / 2
    H1 = O + roh * np.array([ np.sin(half), 0.0, np.cos(half)])
    H2 = O + roh * np.array([-np.sin(half), 0.0, np.cos(half)])
    slab += Atoms("OHH", positions=[O, H1, H2])
    print(f"[build] added free H2O, O at {np.round(O,3)} (z+{O_HEIGHT} above surface)")

# ----------------------------------------------------------------------------
# 8. DIPOLE-CORRECTION PLACEMENT (sawtooth in the middle of the vacuum)
# ----------------------------------------------------------------------------
cz = slab.cell.array[2, 2]
zmax = slab.positions[:, 2].max()
emaxpos = min(0.99, (zmax + VACUUM * 0.5) / cz)   # fractional z, inside vacuum
print(f"[build] dipole sawtooth emaxpos = {emaxpos:.3f} (fractional z)")

# ----------------------------------------------------------------------------
# 9. WRITE QE INPUT + xyz
# ----------------------------------------------------------------------------
input_data = {
    "control": {
        "calculation": "relax",
        "restart_mode": "from_scratch",
        "prefix": OUT_PREFIX,
        "outdir": "./out",
        "pseudo_dir": "./pseudo",
        "tprnfor": True, "tstress": False,
        "forc_conv_thr": 1.0e-3,
        "nstep": 200,
        "tefield": True, "dipfield": True,      # dipole correction ON
    },
    "system": {
        "ibrav": 0,
        "ecutwfc": 50.0,                         # CONVERGE THIS (scan 40-70)
        "ecutrho": 400.0,                        # ~8x ecutwfc for PAW
        "occupations": "smearing",
        "smearing": "mv", "degauss": 0.01,       # cold smearing for doped slab
        "edir": 3, "emaxpos": float(round(emaxpos, 3)), "eopreg": 0.05, "eamp": 0.0,
    },
    "electrons": {
        "conv_thr": 1.0e-6,
        "mixing_beta": 0.3,                      # lower for slabs (stability)
        "electron_maxstep": 200,
    },
    "ions": {"ion_dynamics": "bfgs"},
}

kpts = (4, 4, 1) if (NX, NY) == (1, 1) else (max(2, 8 // NX), max(2, 8 // NY), 1)
print(f"[build] k-points = {kpts}  (CONVERGE THIS; never use Gamma-only)")

write(f"{OUT_PREFIX}.in", slab, format="espresso-in",
      input_data=input_data, pseudopotentials=PSEUDO, kpts=kpts)
write(f"{OUT_PREFIX}.xyz", slab)

from collections import Counter
print(f"[build] composition: {dict(Counter(slab.get_chemical_symbols()))}")
print(f"[build] wrote {OUT_PREFIX}.in  and  {OUT_PREFIX}.xyz")
print("[build] DONE.")
