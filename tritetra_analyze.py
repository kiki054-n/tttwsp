"""
tritetra_analyze.py
TriTetra Water Splitting Project — v3.1.4

LAMMPSシミュレーション結果の解析スクリプト
- S周辺の結合長を抽出
- 正四面体からの角度偏差（v4崩れの定量化）を計算
- 変位マップをCSV出力

Requirements:
    pip install numpy matplotlib pandas ase
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from ase.io import read

# ════════════════════════════════════════════════════════════
# 1. 緩和後の構造を読み込む
# ════════════════════════════════════════════════════════════
print("=" * 50)
print(" TriTetra v3.1.4 — Post-processing")
print("=" * 50)

atoms = read("tritetra_relaxed.xyz")
positions = atoms.get_positions()
symbols   = atoms.get_chemical_symbols()

# S原子のインデックスを特定
s_indices = [i for i, s in enumerate(symbols) if s == "S"]
print(f"\nS dopant atoms: {len(s_indices)} found")
for idx in s_indices:
    print(f"  Index {idx}: position = {positions[idx].round(4)} Å")

# ════════════════════════════════════════════════════════════
# 2. S周辺の最近接Si原子を特定（第一近接）
# ════════════════════════════════════════════════════════════
CUTOFF = 3.0  # Å — Si-S結合の最大距離

results = []

for s_idx in s_indices:
    s_pos = positions[s_idx]
    neighbors = []

    for i, (pos, sym) in enumerate(zip(positions, symbols)):
        if i == s_idx:
            continue
        dist = np.linalg.norm(pos - s_pos)
        if dist < CUTOFF:
            neighbors.append({"index": i, "symbol": sym, "dist": dist, "pos": pos})

    neighbors.sort(key=lambda x: x["dist"])
    print(f"\n  S (index {s_idx}) — nearest neighbors:")
    for n in neighbors[:6]:
        print(f"    {n['symbol']}[{n['index']}]  dist = {n['dist']:.4f} Å")

    # ── 結合角の計算（トリテトラ均衡: 理想値 = 109.47°）─────
    ideal_angle = 109.4712  # 正四面体の結合角
    angles = []

    nn = neighbors[:4]  # 第一近接4原子
    for i in range(len(nn)):
        for j in range(i+1, len(nn)):
            v1 = nn[i]["pos"] - s_pos
            v2 = nn[j]["pos"] - s_pos
            cos_a = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
            cos_a = np.clip(cos_a, -1.0, 1.0)
            angle = np.degrees(np.arccos(cos_a))
            deviation = angle - ideal_angle
            angles.append({
                "pair": f"{nn[i]['symbol']}[{nn[i]['index']}]-S-{nn[j]['symbol']}[{nn[j]['index']}]",
                "angle_deg": round(angle, 4),
                "deviation_deg": round(deviation, 4)
            })

    print(f"\n  Bond angles around S (ideal = {ideal_angle:.2f}°):")
    for a in angles:
        flag = "  ← DISTORTED" if abs(a["deviation_deg"]) > 2.0 else ""
        print(f"    {a['pair']:40s}  {a['angle_deg']:7.3f}°  (Δ = {a['deviation_deg']:+.3f}°){flag}")

    results.append({"s_index": s_idx, "neighbors": neighbors[:4], "angles": angles})

# ════════════════════════════════════════════════════════════
# 3. TriTetraベクトル均衡の検証
#    v1 + v2 + v3 + v4 = 0 からの偏差を計算
# ════════════════════════════════════════════════════════════
print("\n" + "=" * 50)
print(" TriTetra Vector Equilibrium Check")
print(" Ideal: v1 + v2 + v3 + v4 = 0")
print("=" * 50)

for r in results:
    nn = r["neighbors"][:4]
    if len(nn) < 4:
        print("  Warning: fewer than 4 neighbors found")
        continue

    s_pos = positions[r["s_index"]]
    vectors = [n["pos"] - s_pos for n in nn]
    v_sum = np.sum(vectors, axis=0)
    v_sum_norm = np.linalg.norm(v_sum)

    print(f"\n  S index {r['s_index']}:")
    for i, (v, n) in enumerate(zip(vectors, nn)):
        print(f"    v{i+1} ({n['symbol']}[{n['index']}]): {v.round(4)}")
    print(f"\n  v1+v2+v3+v4 = {v_sum.round(6)}")
    print(f"  |v1+v2+v3+v4| = {v_sum_norm:.6f} Å")

    if v_sum_norm < 0.1:
        print("  ✅ Near-perfect equilibrium (|sum| < 0.1 Å)")
    elif v_sum_norm < 0.5:
        print("  ⚠️  Mild disruption detected")
    else:
        print(f"  🔴 Significant v4 DISRUPTION: {v_sum_norm:.4f} Å")
        print(f"     → TriTetra equilibrium broken at S site")

# ════════════════════════════════════════════════════════════
# 4. 結果をCSVに保存
# ════════════════════════════════════════════════════════════
rows = []
for r in results:
    for a in r["angles"]:
        rows.append({
            "S_index": r["s_index"],
            "bond_pair": a["pair"],
            "angle_deg": a["angle_deg"],
            "deviation_from_tetrahedral": a["deviation_deg"]
        })

df = pd.DataFrame(rows)
df.to_csv("tritetra_angles.csv", index=False)
print("\n✅ Saved: tritetra_angles.csv")

# ════════════════════════════════════════════════════════════
# 5. 角度偏差のプロット
# ════════════════════════════════════════════════════════════
if not df.empty:
    fig, ax = plt.subplots(figsize=(10, 5))
    colors = ["red" if abs(d) > 2.0 else "steelblue"
              for d in df["deviation_from_tetrahedral"]]
    ax.bar(range(len(df)), df["deviation_from_tetrahedral"], color=colors)
    ax.axhline(0, color="black", linewidth=0.8, linestyle="--")
    ax.axhline(2.0,  color="red", linewidth=0.5, linestyle=":")
    ax.axhline(-2.0, color="red", linewidth=0.5, linestyle=":")
    ax.set_xticks(range(len(df)))
    ax.set_xticklabels(df["bond_pair"], rotation=45, ha="right", fontsize=8)
    ax.set_ylabel("Deviation from 109.47° (degrees)")
    ax.set_title("TriTetra v3.1.4 — Bond Angle Distortion around S dopant\n"
                 "v₁+v₂+v₃+v₄=0 equilibrium disruption map")
    plt.tight_layout()
    plt.savefig("tritetra_distortion_map.png", dpi=150)
    print("✅ Saved: tritetra_distortion_map.png")
    plt.show()

print("\n" + "=" * 50)
print(" Analysis complete — TriTetra v3.1.4")
print("=" * 50)
