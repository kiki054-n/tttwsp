#!/usr/bin/env python3
# ============================================================================
#  analyze_convergence.py  —  TTT-WSP v5  (Step 1 readout)
#
#  Reads the .out files produced by the convergence scans and reports, for
#  each parameter, where the total energy stops changing. Prints the minimal
#  CONVERGED setting to lock in for all production runs.
#
#  Metrics / tolerances:
#    ecut    : dE per atom vs previous           -> converged < 5 meV/atom
#    kpts    : dE per atom vs previous           -> converged < 5 meV/atom
#    vacuum  : dE (total)   vs previous          -> converged < 3 meV
#    layers  : incremental dE per 2 added layers -> converged < 5 meV
# ============================================================================
import os, re, glob

RY2EV, RY2MEV = 13.605693122994, 13605.693122994
TOL = {"ecut": 5.0, "kpts": 5.0, "vacuum": 3.0, "layers": 10.0}  # meV(/atom)

def final_energy_ry(path):
    e = None
    with open(path) as f:
        for line in f:
            if "!" in line and "total energy" in line:
                m = re.search(r"=\s*(-?\d+\.\d+)", line)
                if m: e = float(m.group(1))
    return e

def natoms(path):
    with open(path) as f:
        for line in f:
            if "number of atoms/cell" in line:
                return int(re.search(r"=\s*(\d+)", line).group(1))
    return None

def scan(folder, key):
    rows = []
    for out in glob.glob(os.path.join(folder, "*.out")):
        x = int(re.search(r"_(\d+)\.out$", out).group(1))
        E = final_energy_ry(out)
        if E is None:
            print(f"  [warn] {out}: not converged / no energy"); continue
        rows.append((x, E * RY2EV, natoms(out)))
    return sorted(rows)

def report_per_atom(rows, label, unit):
    print(f"\n### {label} convergence")
    print(f"  {unit:>8s}  {'E/atom (eV)':>13s}  {'dE/atom (meV)':>14s}  status")
    prev, recommended = None, None
    for x, E, n in rows:
        epa = E / n
        if prev is None:
            print(f"  {x:8d}  {epa:13.6f}  {'--':>14s}")
        else:
            d = (epa - prev) * 1000.0
            tol = TOL["ecut"] if "ecut" in label.lower() else TOL["kpts"]
            mark = "converged" if abs(d) < tol else ""
            if abs(d) < tol and recommended is None:
                recommended = x
            print(f"  {x:8d}  {epa:13.6f}  {d:14.2f}  {mark}")
        prev = epa
    if recommended:
        print(f"  -> use {label.split()[0]} = {recommended} "
              f"(first within {tol:.0f} meV/atom)")
    else:
        print(f"  -> NOT converged in tested range; extend the scan")

def report_total(rows, label):
    print(f"\n### {label} convergence")
    print(f"  {'value':>8s}  {'E_total (eV)':>14s}  {'dE (meV)':>10s}  status")
    prev, recommended = None, None
    for x, E, n in rows:
        if prev is None:
            print(f"  {x:8d}  {E:14.5f}  {'--':>10s}")
        else:
            d = (E - prev) * 1000.0
            mark = "converged" if abs(d) < TOL["vacuum"] else ""
            if abs(d) < TOL["vacuum"] and recommended is None:
                recommended = x
            print(f"  {x:8d}  {E:14.5f}  {d:10.2f}  {mark}")
        prev = E
    if recommended:
        print(f"  -> use vacuum = {recommended} Ang (first within "
              f"{TOL['vacuum']:.0f} meV)")
    else:
        print("  -> NOT converged; extend the scan")

def report_layers(rows):
    print(f"\n### layers convergence (incremental energy per +2 layers)")
    print(f"  {'layers':>8s}  {'E_total (eV)':>14s}  {'E/atom (eV)':>13s}  "
          f"{'d(incr) (meV)':>14s}  status")
    prev_inc, prev_E, prev_n, recommended = None, None, None, None
    for x, E, n in rows:
        epa = E / n
        if prev_E is None:
            print(f"  {x:8d}  {E:14.5f}  {epa:13.6f}  {'--':>14s}")
        else:
            inc = (E - prev_E) / ((n - prev_n) / 4.0)  # energy per added layer*~
            if prev_inc is not None:
                d = (inc - prev_inc) * 1000.0
                mark = "converged" if abs(d) < TOL["layers"] else ""
                if abs(d) < TOL["layers"] and recommended is None:
                    recommended = x
                print(f"  {x:8d}  {E:14.5f}  {epa:13.6f}  {d:14.2f}  {mark}")
            else:
                print(f"  {x:8d}  {E:14.5f}  {epa:13.6f}  {'--':>14s}")
            prev_inc = inc
        prev_E, prev_n = E, n
    if recommended:
        print(f"  -> use layers = {recommended} (incremental energy stable "
              f"< {TOL['layers']:.0f} meV)")
    else:
        print("  -> increment not yet flat; add more layers")

if __name__ == "__main__":
    print("=" * 64)
    print(" TTT-WSP v5 — Step 1 convergence readout")
    print("=" * 64)
    if (r := scan("conv/ecut", "ecut")):     report_per_atom(r, "ecut (Ry)", "ecutwfc")
    if (r := scan("conv/kpts", "kpts")):     report_per_atom(r, "kpts (NxNx1)", "N")
    if (r := scan("conv/vacuum", "vacuum")): report_total(r, "vacuum (Ang)")
    if (r := scan("conv/layers", "layers")): report_layers(r)
    print("\nLock the four converged values into build_slab.py before any "
          "production run. Re-confirm once with a single dE_ads at the chosen "
          "settings.")
