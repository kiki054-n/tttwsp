# TriTetra Simulation Files — v3.1.4

## ファイル構成

| ファイル | 役割 |
|---|---|
| `tritetra_si_s_dope.in` | LAMMPSメイン入力スクリプト |
| `si_s.sw` | Stillinger-Weberポテンシャル（Si-S系） |
| `tritetra_analyze.py` | 結果解析・可視化スクリプト（Python） |

## 実行手順

### Step 1 — LAMMPSシミュレーション

```bash
lammps -in tritetra_si_s_dope.in > tritetra_thermo.log
```

**出力ファイル：**
- `tritetra_relaxed.xyz` — 緩和後の構造（OVITOで可視化可）
- `tritetra_bonds.txt` — 結合長データ
- `tritetra_displacement.dump` — 各原子の変位ベクトル

### Step 2 — Python解析

```bash
pip install numpy matplotlib pandas ase
python tritetra_analyze.py
```

**出力ファイル：**
- `tritetra_angles.csv` — S周辺の結合角と正四面体からの偏差
- `tritetra_distortion_map.png` — 歪みマップ（グラフ）

## 何を確認するか

このシミュレーションは以下を数値で検証します：

```
理想的なSiサイト:  v1 + v2 + v3 + v4 = 0  (完全なトリテトラ均衡)
Sドープサイト   :  v1 + v2 + v3 + v4 ≠ 0  (均衡の崩れ = トリガー効果)
```

`|v1+v2+v3+v4|` の値が大きいほど、局所的なベクトル均衡の崩れが大きく、
H₂O分解のトリガーとして機能する可能性が高いと解釈します。

## 必要環境

- LAMMPS（任意の最新版）
- Python 3.8以上
- numpy, matplotlib, pandas, ase
