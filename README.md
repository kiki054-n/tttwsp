# TriTetra Water Splitting Project (TTT-WSP)

**A novel geometric framework for catalytic H₂O dissociation**  
**幾何学的触媒設計による水分解の新しいアプローチ**

[![License: CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC_BY--NC--SA_4.0-lightgrey.svg)](https://creativecommons.org/licenses/by-nc-sa/4.0/)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.19704117.svg)](https://doi.org/10.5281/zenodo.19704117)
[![Author](https://img.shields.io/badge/Author-川上真潔-f39c12?style=for-the-badge)](https://orcid.org/0009-0009-2972-6511)

[![Status](https://img.shields.io/badge/Status-Open%20Science-brightgreen)](.)
[![Version](https://img.shields.io/badge/Version-v4.0.0--public-blue)](.)
[![Lang](https://img.shields.io/badge/日本語-README__ja.md-blue)](./README_ja.md)

---

## 📖 概要 / Overview

本プロジェクトは、**TriTetra理論（TTT）** に基づく新しい水分解触媒メカニズムを提案し、DFT計算によってその有効性を検証します。

This project proposes and computationally validates a novel water-splitting catalyst mechanism grounded in the **TriTetra Theory (TTT)**.

**核心的な発見 / Key Findings:**

| 計算 | 結果 | 意義 |
|---|---|---|
| Si+S+P共ドープ（relax） | ΔΔE = **−4.46 eV** | S/P共ドープの相乗効果 |
| Si+S+P+H₂O吸着エネルギー | ΔE_ads = **−0.84 eV** | 自発的なH₂O吸着 |
| O-H解離活性化エネルギー | Ea = **0.282 eV** | Pt触媒（~0.8 eV）より低い |

---

## 🔷 TriTetra理論（TTT）

### 基本原理

sp³混成軌道を持つ結晶格子（Si・ダイヤモンド・cBN・SiC）は正四面体構造を基本単位とし、以下のベクトル均衡を満たします：

$$\vec{v}_1 + \vec{v}_2 + \vec{v}_3 + \vec{v}_4 = 0$$

**中心仮説:**
> 特定のドーパント（S・P）配置によりこのベクトル均衡が局所的に崩れると、隣接するH₂O分子のO-H結合解離エネルギーが変化する。

### DFT計算による検証結果

```
材料系              ΔΔE (eV)    TTT仮説との整合
─────────────────────────────────────────────
Si+S   (relax)     −1.67       ✅ 一致
Si+S+P (relax)     −4.46       ✅ 一致（最大効果）
SiC+P  (relax)     −0.31       ✅ 一致
SiC+S  (relax)     +1.55       ⚠️ 逆方向（要検討）
```

---

## 🌐 オープンサイエンスへの招待

本プロジェクトは**オープンサイエンス**として世界に公開しています。

### なぜ公開するのか

- 特許取得より、世界の研究者がこの手法を活用・発展させることに価値がある
- TTT理論の正しさを、より多くの研究者による追試で証明したい
- 「sp³格子 + S/Pドープ」という組み合わせの探索を世界規模で加速させたい

### あなたに試してほしいこと

本リポジトリのコードを使えば、**任意のsp³材料系でのH₂O吸着エネルギー変化**を計算できます。

| 基板 | ドーパント候補 | 期待される効果 |
|---|---|---|
| Si | S, P, Se, As | TTT効果の元素依存性 |
| SiC | P, N, Al | HER活性の最適化 |
| Diamond | B, N | 超安定触媒の可能性 |
| cBN | C, Si | 界面効果の検証 |
| GaN | Si, Mg | 光触媒との組み合わせ |

---

## ⚙️ 計算環境のセットアップ

詳細は [SETUP.md](./SETUP.md) を参照してください。

```bash
# 1. 仮想環境のセットアップ（WSL2/Linux）
mkdir -p ~/tttwsp/dft && cd ~/tttwsp/dft
python3 -m venv venv && source venv/bin/activate
pip install numpy matplotlib pandas ase

# 2. S添加Si+H₂O構造の生成
python3 build_structure.py

# 3. Quantum ESPRESSO入力ファイルの生成
python3 fix_input.py

# 4. DFT計算の実行
mkdir -p out && pw.x < tritetra_scf.in > tritetra_scf.out
```

---

## 📐 複合材料設計フレームワーク

詳細は [docs/COMPOSITE_MATERIAL_DESIGN.md](./docs/COMPOSITE_MATERIAL_DESIGN.md) を参照。

```
【推奨構造】TTT-SHC（Synergistic Hetero-Catalyst）

外部電解質（H₂O）
        ↕
S/P共ドープ CNT ネットワーク   ← HER/OER活性点
        ↕
SiO₂ナノドット                 ← アンカー層
        ↕
S/Pドープ SiC 中間層            ← バンドエンジニアリング
        ↕
cBN 薄膜                       ← 保護層
        ↕
Diamond コア                   ← 熱伝導・機械的基盤
```

---

## 📊 計算結果

全計算結果は [results/](./results/) フォルダに記録されています。

| Phase | 内容 | 主要結果 |
|---|---|---|
| Phase 1-2 | Si+S SCF計算 | ΔΔE = −0.09 eV |
| Phase 3 | Si+S relax計算 | **ΔΔE = −1.67 eV** |
| Phase 5 | SiC+S/P SCF | ΔΔE = −0.10〜−0.14 eV |
| Phase 6 | SiC+S/P relax | SiC+P: ΔΔE = −0.31 eV |
| Phase 7 | Si+S+P共ドープ | **ΔΔE = −4.46 eV** |
| Phase 8 | HER NEB計算 | **Ea = 0.282 eV** |
| Phase 9 | OER NEB計算 | Step1確認 |

---

## 🔬 シミュレーション計画

### 完了 ✅
- Si+S/P系のSCF・relax計算
- SiC+S/P系のSCF・relax計算
- Si+S+P共ドープ系のrelax計算
- HER O-H解離経路のNEB計算（Ea = 0.282 eV）
- OER Step 1のNEB計算

### 進行中・計画中 📋
- OER Step 2〜4のNEB計算
- フォノン解析（Phonopy）
- k点精密化（2×2×2）
- cBN/Diamond界面の正確な計算

---

## 🤝 コラボレーション

本プロジェクトへの参加を歓迎します。詳細は [CONTRIBUTING.md](./CONTRIBUTING.md) を参照してください。

特に以下の専門家を求めています：

- **計算化学者** — 他の材料系でのDFT計算
- **実験化学者** — Si+S+P触媒の実際の合成・評価
- **理論物理学者** — TTT理論の数理的形式化
- **電気化学者** — 水分解活性の電気化学的測定

**IssueまたはPull Requestでの貢献を歓迎します。**

---

## 📄 引用 / Citation

```
kiki054-n. (2026). TriTetra Water Splitting Project (TTT-WSP).
GitHub. https://github.com/kiki054-n/tttwsp
```

---

## 📜 ライセンス / License

MIT License — 自由に使用・改変・再配布できます。
詳細は [LICENSE](./LICENSE) を参照してください。

---

## 🙏 謝辞 / Acknowledgments

計算インフラ: [Quantum ESPRESSO](https://www.quantum-espresso.org/), [ASE](https://wiki.fysik.dtu.dk/ase/), [LAMMPS](https://www.lammps.org/)

---

*"The sphere whispers zero. The tetrahedron remembers it."*  
— TriTetra Project, v4.0.0-public
