#!/usr/bin/env python3
# ============================================================================
#  preflight.py  —  TTT-WSP v5
#  Run this BEFORE launching any pw.x job. It checks the four things that
#  cause 90% of "it won't run" failures: ASE, pw.x, pseudopotentials, inputs.
# ============================================================================
import os, shutil, subprocess, sys, glob

ok = True
def check(label, good, hint=""):
    global ok
    print(f"  [{'OK ' if good else 'XX '}] {label}")
    if not good:
        ok = False
        if hint: print(f"         -> {hint}")

print("=" * 60)
print(" TTT-WSP v5 preflight")
print("=" * 60)

# 1. ASE
try:
    import ase
    check(f"ASE importable (v{ase.__version__})", True)
except Exception:
    check("ASE importable", False, "pip install ase")

# 2. pw.x on PATH
pw = shutil.which("pw.x")
check(f"pw.x on PATH ({pw})", pw is not None,
      "conda install -c conda-forge qe   (or load your QE module)")

# 3. QE version (warn if < 7.0: ASE writes &FCP/&RISM namelists)
if pw:
    try:
        import re
        out = subprocess.run([pw], input="", capture_output=True, text=True,
                             timeout=20).stdout
        m = re.search(r"PWSCF v\.(\d+)\.(\d+)", out)
        ver = f"{m.group(1)}.{m.group(2)}" if m else "?"
        old = bool(m) and int(m.group(1)) < 7
        check(f"QE version {ver}", not old,
              "QE < 7.0 may reject empty &FCP/&RISM namelists ASE emits; "
              "delete those two empty namelists from each .in, or upgrade to 7.x")
    except Exception:
        print("  [?? ] could not read pw.x version")

# 4. pseudopotentials (convergence step needs only Si + H)
PDIR = "./pseudo"
need_conv = ["Si.pbe-n-kjpaw_psl.1.0.0.UPF", "H.pbe-kjpaw_psl.1.0.0.UPF"]
need_full = ["S.pbe-n-kjpaw_psl.1.0.0.UPF", "P.pbe-n-kjpaw_psl.1.0.0.UPF",
             "O.pbe-n-kjpaw_psl.1.0.0.UPF"]
have = set(os.path.basename(p) for p in glob.glob(os.path.join(PDIR, "*.UPF")))
for f in need_conv:
    check(f"pseudo (convergence): {f}", f in have,
          f"place it in {PDIR}/ (SSSP / pslibrary PAW-PBE)")
for f in need_full:
    present = f in have
    print(f"  [{'OK ' if present else '.. '}] pseudo (production): {f}"
          f"{'' if present else '   (needed later, not for convergence)'}")

# 5. convergence inputs generated?
n = len(glob.glob("conv/*/*.in"))
check(f"convergence inputs present ({n} files under conv/)", n >= 17,
      "python3 gen_convergence.py")

print("-" * 60)
print(" READY to run." if ok else " NOT ready — fix the [XX] items above.")
sys.exit(0 if ok else 1)
