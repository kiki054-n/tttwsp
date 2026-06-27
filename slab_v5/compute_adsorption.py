#!/usr/bin/env python3
# ============================================================================
#  compute_adsorption.py  —  TTT-WSP v5
#
#  Computes adsorption energies and the TTT effect (ddE) from pw.x .out files.
#
#      dE_ads(system) = E(slab+H2O) - E(slab) - E(H2O_gas)
#      ddE            = dE_ads(doped) - dE_ads(pure)
#
#  Reads the LAST converged total energy ("!  total energy") from each .out,
#  so it works for both scf and relax runs.
#
#  Sanity gate: a physical H2O adsorption energy is roughly -0.1 to -1.0 eV.
#  Any |dE_ads| > ~2 eV almost certainly means a bad initial geometry or an
#  unrelaxed clash -- the script flags it instead of reporting it as science.
# ============================================================================
import sys, re

RY2EV = 13.605693122994

def final_energy_ry(path):
    """Return the last '!  total energy' value (Ry) from a pw.x output."""
    e = None
    with open(path) as f:
        for line in f:
            if "!" in line and "total energy" in line:
                m = re.search(r"=\s*(-?\d+\.\d+)", line)
                if m:
                    e = float(m.group(1))
    if e is None:
        raise RuntimeError(f"no converged total energy found in {path}")
    return e

def e_ads_eV(slab_h2o_out, slab_out, water_out):
    E_sh = final_energy_ry(slab_h2o_out)
    E_s  = final_energy_ry(slab_out)
    E_w  = final_energy_ry(water_out)
    return (E_sh - E_s - E_w) * RY2EV

def flag(dE):
    a = abs(dE)
    if a > 2.0:
        return "  <<< UNPHYSICAL: bad geometry / unrelaxed clash, NOT adsorption"
    if dE > 0.0:
        return "  (positive: H2O does not bind in this configuration)"
    return "  (negative: bound)"

if __name__ == "__main__":
    # Edit these to point at your finished .out files -------------------------
    WATER = "h2o_ref.out"
    jobs = {
        # label:        (slab+H2O .out,            bare slab .out)
        "Si (pure)":    ("si_pure_h2o.out",        "si_pure.out"),
        "Si+S":         ("si_s_h2o.out",           "si_s.out"),
        "Si+S+P":       ("tttwsp_si_sp_h2o_100.out","si_sp.out"),
    }
    # ------------------------------------------------------------------------
    print(f"{'system':14s} {'dE_ads (eV)':>12s}   note")
    print("-" * 70)
    results = {}
    for label, (sh, s) in jobs.items():
        try:
            dE = e_ads_eV(sh, s, WATER)
            results[label] = dE
            print(f"{label:14s} {dE:12.3f} {flag(dE)}")
        except Exception as ex:
            print(f"{label:14s} {'--':>12s}   [skipped: {ex}]")

    if "Si (pure)" in results:
        print("\nTTT effect  ddE = dE_ads(doped) - dE_ads(pure):")
        base = results["Si (pure)"]
        for label, dE in results.items():
            if label == "Si (pure)":
                continue
            ddE = dE - base
            print(f"  {label:12s} ddE = {ddE:+.3f} eV")
        print("\nReminder: ddE is only meaningful if BOTH dE_ads values above are "
              "physical (no UNPHYSICAL flags). A clean ddE built from two "
              "unphysical dE_ads is a difference of artifacts.")
