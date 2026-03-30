# TriTetra Water Splitting Project (TTT-WSP)

**A novel geometric framework for catalytic H₂O dissociation**
**水分解触媒素子のための幾何学的新理論フレームワーク**

[![Status](https://img.shields.io/badge/Status-Pre--Patent%20%2F%20Private-red)](.)
[![License](https://img.shields.io/badge/License-All%20Rights%20Reserved-darkred)](.)
[![Version](https://img.shields.io/badge/Version-v3.2.0--private-grey)](.)
[![Lang](https://img.shields.io/badge/日本語-README__ja.md-blue)](./README_ja.md)

---

> ⚠️ **This repository is private pending patent application.**
> Unauthorized reproduction or use of any content is prohibited.
> See [PATENT_NOTICE.md](./PATENT_NOTICE.md) for details.

📖 **日本語版はこちら → [README_ja.md](./README_ja.md)**

---

## Overview

This project researches and develops a novel catalytic water-splitting mechanism grounded in the **TriTetra Theory (TTT)**.

The central insight of TTT is that actively controlling the **geometric vector equilibrium** of sp³-hybridized crystal lattices may reduce the energy barrier required for H₂O dissociation.

---

## Background

Electrolytic hydrogen production faces the persistent challenge of **overpotential**. This research proposes a distinct approach based on the geometric properties of crystal lattices, rather than purely electrochemical methods.

| Challenge | Detail |
|---|---|
| Overpotential | Practical voltage (1.8–2.0V) far exceeds theoretical minimum (1.23V) |
| Catalyst cost | Platinum-group metals (Pt, Ir, Ru) required |
| Durability | Poor long-term stability in acidic/alkaline environments |

---

## TriTetra Theory (TTT)

### Core Principle: Vector Equilibrium

The regular tetrahedron is the minimum-vertex polyhedron that approximates the zero-sum vector property of a sphere:

$$\vec{v}_1 + \vec{v}_2 + \vec{v}_3 + \vec{v}_4 = 0$$

All sp³-hybridized crystals (Si, diamond, cBN) share this tetrahedral bonding geometry as their fundamental unit.

### Central Hypothesis

> A specific dopant configuration that locally disrupts vector equilibrium will measurably alter the O–H bond dissociation energy of proximate H₂O molecules.

This hypothesis is verifiable via DFT (Density Functional Theory) calculation — the primary computational target of this project.

### Mechanism

```
[Perfect sp³ lattice: vector equilibrium maintained]
            ↓
[Dopant introduced: local equilibrium disrupted]
            ↓
[Geometric asymmetry propagates through lattice]
            ↓
[O–H bond dissociation energy of H₂O modified]
            ↓
[Low-energy water splitting (under investigation)]
```

---

## Material Systems of Interest

| Role | Material | Rationale |
|---|---|---|
| Base lattice | Si, Diamond, cBN | Perfect sp³ tetrahedral network |
| Dopant | (reserved for patent filing) | Introduces local geometric asymmetry |
| Waveguide | Carbon nanotube (CNT) | Directed energy propagation |

---

## Simulation Roadmap

### Phase 1: DFT Calculation — 🔄 In Progress

- Electronic structure comparison: undoped vs. doped supercell
- H₂O adsorption energy: ΔE_ads = E(slab+H₂O) − E(slab) − E(H₂O)
- O–H bond dissociation pathway via NEB method

**Software:** Quantum ESPRESSO
**Status:** Input files generated, calculation running

### Phase 2: Phonon Analysis — 📋 Planned

- Local vibrational modes around dopant site
- Coupling with H₂O O–H stretch mode (~3600 cm⁻¹)

**Software:** Phonopy + Quantum ESPRESSO

### Phase 3: Molecular Dynamics — 📋 Planned

- H₂O dissociation event statistics via ReaxFF
- Dopant concentration dependence

**Software:** LAMMPS

---

## Repository Structure

```
tttwsp/
├── README.md                  # This file (English)
├── README_ja.md               # Japanese version
├── PATENT_NOTICE.md           # Patent rights notice
├── SETUP.md                   # Environment setup guide
├── simulations/
│   └── dft/
│       ├── build_structure.py # Structure builder (ASE-based)
│       ├── make_qe_input.py   # QE input file generator
│       ├── tritetra_system.xyz # Generated structure (visualization)
│       ├── tritetra_system.cif # Generated structure (QE input)
│       ├── tritetra.in        # Quantum ESPRESSO input file
│       ├── pseudo/            # Pseudopotential files (UPF)
│       └── out/               # Calculation output directory
├── analysis/
│   └── tritetra_analyze.py    # Post-processing analysis script
└── LICENSE
```

---

## Quick Start

See [SETUP.md](./SETUP.md) for the full setup guide.

```bash
# Setup virtual environment (WSL2 / Linux)
mkdir -p ~/tttwsp/dft && cd ~/tttwsp/dft
python3 -m venv venv && source venv/bin/activate
pip install numpy matplotlib pandas ase

# Generate structure
python3 build_structure.py

# Run DFT calculation
mkdir -p out && pw.x < tritetra.in > tritetra.out
```

---

## Patent Status

| Item | Detail |
|---|---|
| Filing status | Pre-filing (preparation in progress) |
| Target regions | Japan / PCT (international) |
| Filing deadline | September 14, 2026 |
| Anticipated IPC | C25B 1/04, C01B 3/04, B01J 27/00 |

---

## Disclosure Roadmap

```
[Now]          Private repository (pre-filing)
    ↓
[After filing] Theory overview + simulation design → Public
    ↓
[Under review] Calculation results → staged release
    ↓
[After grant]  Full open science release
```

---

## Collaboration

For collaboration inquiries, please open an Issue or contact directly.
**An NDA is required before sharing technical details.**

---

## License

Copyright © 2026 kiki054-n. All Rights Reserved.

Until patent filing is complete, all content in this repository is proprietary.
Reproduction, use, modification, or distribution in any form is prohibited.

---

*"The sphere whispers zero. The tetrahedron remembers it."*
— TriTetra Project, v3.2.0-private
