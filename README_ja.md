# TriTetra 水分解プロジェクト（TTT-WSP）

**幾何学的触媒設計による水分解の新しいアプローチ**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Status](https://img.shields.io/badge/Status-Open%20Science-brightgreen)](.)
[![English](https://img.shields.io/badge/English-README.md-blue)](./README.md)

---

## 概要

本プロジェクトは、**TriTetra理論（TTT）** に基づく新しい水分解触媒メカニズムを提案し、DFT計算によって検証します。世界の研究者と共にこの手法を発展させることを目的として、オープンサイエンスとして公開しています。

---

## 核心的な発見

| 計算 | 結果 | 意義 |
|---|---|---|
| Si+S+P共ドープ relax計算 | ΔΔE = **−4.46 eV** | S/P共ドープの相乗効果 |
| H₂O吸着エネルギー | ΔE_ads = **−0.84 eV** | 自発的なH₂O吸着 |
| O-H解離活性化エネルギー | Ea = **0.282 eV** | Pt触媒（~0.8 eV）より低い |

---

## TriTetra理論（TTT）とは

sp³混成軌道を持つ結晶格子（Si・ダイヤモンド・cBN・SiC）は正四面体構造を基本単位とし、以下のベクトル均衡を満たします：

$$\vec{v}_1 + \vec{v}_2 + \vec{v}_3 + \vec{v}_4 = 0$$

**中心仮説:**
特定のドーパント（S・P）配置によりこの均衡が局所的に崩れると、隣接するH₂O分子のO-H結合解離エネルギーが変化する。

この仮説をDFT計算（Quantum ESPRESSO）で検証した結果、**複数の材料系でTTT仮説と一致する方向の変化**を確認しました。

---

## なぜ公開するのか

特許取得より、**世界の研究者がこの手法を活用・発展させること**に価値があると考えます。

- TTT理論の正しさを、より多くの研究者による追試で証明したい
- 「sp³格子 + S/Pドープ」という材料探索を世界規模で加速させたい
- オープンサイエンスとして、再現性・透明性を確保したい

---

## あなたに試してほしいこと

本リポジトリのコードを使えば、**任意のsp³材料系でのH₂O吸着エネルギー変化**を計算できます。

| 基板 | ドーパント候補 | 期待される効果 |
|---|---|---|
| Si | S, P, Se, As | TTT効果の元素依存性 |
| SiC | P, N, Al | HER活性の最適化 |
| Diamond | B, N | 超安定触媒の可能性 |
| cBN | C, Si | 界面効果の検証 |
| GaN | Si, Mg | 光触媒との組み合わせ |

---

## 計算結果一覧

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

## クイックスタート

```bash
# 環境セットアップ（詳細はSETUP.md）
mkdir -p ~/tttwsp/dft && cd ~/tttwsp/dft
python3 -m venv venv && source venv/bin/activate
pip install numpy matplotlib pandas ase

# 構造生成
python3 build_structure.py

# DFT計算
mkdir -p out && pw.x < tritetra_scf.in > tritetra_scf.out
```

---

## コラボレーション

以下の専門家の参加を歓迎します：

- **計算化学者** — 他の材料系でのDFT計算
- **実験化学者** — Si+S+P触媒の実際の合成・評価
- **理論物理学者** — TTT理論の数理的形式化
- **電気化学者** — 水分解活性の電気化学的測定

Issueからお気軽にご連絡ください。

---

## 引用

```
kiki054-n. (2026). TriTetra Water Splitting Project (TTT-WSP).
GitHub. https://github.com/kiki054-n/tttwsp
```

---

## ライセンス

MIT License — 自由に使用・改変・再配布できます。

---

*"The sphere whispers zero. The tetrahedron remembers it."*  
— TriTetra Project, v4.0.0-public
