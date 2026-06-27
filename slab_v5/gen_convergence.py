#!/usr/bin/env python3
# ============================================================================
#  gen_convergence.py  —  TTT-WSP v5  (Step 1: convergence tests)
#
#  Generates QE scf inputs that scan the four numerical parameters on the
#  SMALLEST system (undoped, passivated, no water, 2x2 lateral). Run these
#  BEFORE any physics is discussed. The goal is to find the minimal settings
#  at which the total energy stops changing.
#
#  Held-fixed values during each scan (iterate once if a scan moves the
#  optimum a lot):  ecutwfc=50/ecutrho=400,  kpts=4x4x1,  vacuum=10,  layers=8
#
#  Output tree:
#     conv/ecut/    ecut_40.in ecut_50.in ecut_60.in ecut_70.in
#     conv/kpts/    kpts_2.in  kpts_4.in  kpts_6.in  kpts_8.in
#     conv/vacuum/  vac_6.in   vac_8.in   vac_10.in  vac_12.in  vac_14.in
#     conv/layers/  lay_6.in   lay_8.in   lay_10.in  lay_12.in
#
#  Requires: ase
# ============================================================================
import os, numpy as np
from ase import Atoms
from ase.build import diamond100
from ase.constraints import FixAtoms
from ase.io import write

A_LAT, SI_H, NXY = 5.431, 1.48, 2          # small lateral cell for speed
PSEUDO = {"Si": "Si.pbe-n-kjpaw_psl.1.0.0.UPF", "H": "H.pbe-kjpaw_psl.1.0.0.UPF"}

# --- verified helpers (identical geometry to build_slab.py) -----------------
def detect_layers(atoms, tol=0.5):
    z = atoms.positions[:, 2]; order = np.argsort(z)
    layers, cur = [], [order[0]]
    for idx in order[1:]:
        if abs(z[idx] - z[cur[-1]]) < tol: cur.append(idx)
        else: layers.append(cur); cur = [idx]
    layers.append(cur); return layers

def neighbors_above(atoms, i, cutoff=2.6):
    p = atoms.positions[i]; dirs = []
    for j in range(len(atoms)):
        if j == i or atoms[j].symbol == "H": continue
        d = atoms.positions[j] - p
        if 0.1 < np.linalg.norm(d) < cutoff and d[2] > 0.2:
            dirs.append(d / np.linalg.norm(d))
    return dirs

def complete_sp3(up):
    if len(up) == 3:
        d = -(up[0] + up[1] + up[2]); return [d / np.linalg.norm(d)]
    if len(up) == 2:
        base = -0.5 * (up[0] + up[1]); n = np.cross(up[0], up[1]); n /= np.linalg.norm(n)
        h = np.sqrt(2.0 / 3.0); return [base + h * n, base - h * n]
    return []

def build_undoped_slab(nlayers, vacuum):
    slab = diamond100("Si", (NXY, NXY, nlayers), a=A_LAT, vacuum=vacuum,
                      orthogonal=True, periodic=True)
    slab.center(vacuum=vacuum, axis=2)
    layers = detect_layers(slab)
    Hpos = []
    for i in layers[0]:
        for d in complete_sp3(neighbors_above(slab, i)):
            if d[2] < 0: Hpos.append(slab.positions[i] + SI_H * d)
    for hp in Hpos: slab += Atoms("H", positions=[hp])
    fixed = [i for L in layers[:3] for i in L] + \
            [i for i in range(len(slab)) if slab[i].symbol == "H"]
    slab.set_constraint(FixAtoms(indices=sorted(set(fixed))))
    return slab, vacuum

def emaxpos_of(slab, vacuum):
    cz = slab.cell.array[2, 2]; zmax = slab.positions[:, 2].max()
    return float(round(min(0.99, (zmax + vacuum * 0.5) / cz), 3))

def make_input(ecutwfc, ecutrho, kpts, vacuum, nlayers):
    slab, vac = build_undoped_slab(nlayers, vacuum)
    idata = {
        "control": {"calculation": "scf", "prefix": "conv", "outdir": "./out",
                    "pseudo_dir": "./pseudo", "tprnfor": True,
                    "tefield": True, "dipfield": True},
        "system": {"ibrav": 0, "ecutwfc": ecutwfc, "ecutrho": ecutrho,
                   "occupations": "smearing", "smearing": "mv", "degauss": 0.01,
                   "edir": 3, "emaxpos": emaxpos_of(slab, vac),
                   "eopreg": 0.05, "eamp": 0.0},
        "electrons": {"conv_thr": 1.0e-6, "mixing_beta": 0.3,
                      "electron_maxstep": 200},
    }
    return slab, idata

def emit(path, slab, idata, kpts):
    write(path, slab, format="espresso-in", input_data=idata,
          pseudopotentials=PSEUDO, kpts=kpts)

# --- the four scans ---------------------------------------------------------
if __name__ == "__main__":
    base = dict(ecutwfc=50.0, ecutrho=400.0, kpts=(4, 4, 1),
                vacuum=10.0, nlayers=8)
    for d in ["conv/ecut", "conv/kpts", "conv/vacuum", "conv/layers"]:
        os.makedirs(d, exist_ok=True)

    # ecut scan (ecutrho = 8x)
    for e in [40, 50, 60, 70]:
        s, idata = make_input(float(e), float(8 * e), base["kpts"],
                              base["vacuum"], base["nlayers"])
        emit(f"conv/ecut/ecut_{e}.in", s, idata, base["kpts"])

    # k-point scan
    for k in [2, 4, 6, 8]:
        s, idata = make_input(base["ecutwfc"], base["ecutrho"], (k, k, 1),
                              base["vacuum"], base["nlayers"])
        emit(f"conv/kpts/kpts_{k}.in", s, idata, (k, k, 1))

    # vacuum scan
    for v in [6, 8, 10, 12, 14]:
        s, idata = make_input(base["ecutwfc"], base["ecutrho"], base["kpts"],
                              float(v), base["nlayers"])
        emit(f"conv/vacuum/vac_{v}.in", s, idata, base["kpts"])

    # layer scan
    for n in [6, 8, 10, 12]:
        s, idata = make_input(base["ecutwfc"], base["ecutrho"], base["kpts"],
                              base["vacuum"], n)
        emit(f"conv/layers/lay_{n}.in", s, idata, base["kpts"])

    print("[conv] generated scans under conv/{ecut,kpts,vacuum,layers}/")
    print("[conv] run each, e.g.:")
    print("       cd conv/ecut && for f in *.in; do pw.x -in $f > ${f%.in}.out; done")
    print("[conv] then: python3 analyze_convergence.py")
