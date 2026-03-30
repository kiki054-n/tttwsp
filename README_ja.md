# TriTetra 水分解プロジェクト（TTT-WSP）

**幾何学的触媒制御による水分解のための新理論フレームワーク**

[![Status](https://img.shields.io/badge/Status-特許出願準備中-red)](.)
[![License](https://img.shields.io/badge/License-All%20Rights%20Reserved-darkred)](.)
[![Version](https://img.shields.io/badge/Version-v3.2.0--private-grey)](.)

---

> ⚠️ **本リポジトリは特許出願準備中のため非公開です。**
> 内容の無断転載・複製・使用を禁じます。
> 詳細は [PATENT_NOTICE.md](./PATENT_NOTICE.md) を参照してください。

---

## 概要

本プロジェクトは、**TriTetra理論（TTT）** に基づく新しい水分解触媒メカニズムの研究・開発を目的とします。

TTT理論の核心は、sp³混成軌道を持つ結晶格子の**幾何学的ベクトル均衡**を能動的に制御することで、H₂Oの解離に必要なエネルギー障壁を低減させるというアプローチです。

---

## 背景と課題

水の電気分解による水素製造は再生可能エネルギーの文脈で注目を集めていますが、**過電圧（overpotential）** の問題が実用化の障壁となっています。

| 従来技術の課題 | 内容 |
|---|---|
| 過電圧 | 理論値1.23Vに対し実際は1.8〜2.0V以上必要 |
| 触媒コスト | 白金族（Pt, Ir, Ru）が必要 |
| 耐久性 | 酸性・アルカリ環境での長期安定性が低い |

本研究は、電気化学的アプローチとは根本的に異なる原理——**結晶格子の幾何学的構造制御**——からこの問題にアプローチします。

---

## TriTetra理論（TTT）

### 基本原理：ベクトル均衡

正四面体（tetrahedron）は、球の無限ベクトルの総和がゼロとなる性質を、最小頂点数で近似する唯一の多面体です。

$$\vec{v}_1 + \vec{v}_2 + \vec{v}_3 + \vec{v}_4 = 0$$

sp³混成軌道を持つ結晶（Si・ダイヤモンド・cBNなど）はすべてこの正四面体構造を基本単位とします。

### 中心仮説

> 特定のドーパント配置により局所的なベクトル均衡が崩れると、隣接するH₂O分子のO-H結合解離エネルギーが変化する。

この仮説はDFT（密度汎関数理論）計算によって検証可能であり、本プロジェクトの主要な計算ターゲットです。

### メカニズムの概略

```
[sp³結晶格子の完全なベクトル均衡状態]
            ↓
[特定ドーパントによる局所的均衡崩壊]
            ↓
[幾何学的非対称性の伝播]
            ↓
[H₂OのO-H結合解離エネルギーの変化]
            ↓
[低エネルギーでの水分解の実現（検証中）]
```

---

## 着目する材料系

| 役割 | 材料 | 理由 |
|---|---|---|
| 基板格子 | Si、ダイヤモンド、cBN | 完全なsp³四面体構造を持つ |
| ドーパント | （出願書類に記載） | 局所的な幾何学的非対称性を導入 |
| 導波構造 | カーボンナノチューブ（CNT） | エネルギーの方向的伝達 |

---

## シミュレーション計画

### Phase 1：DFT計算（実施中）

- ドーパント導入前後の電子密度分布の比較
- H₂O吸着エネルギー（ΔE_ads）の計算
- O-H結合解離経路のNEB解析

**使用ソフトウェア:** Quantum ESPRESSO / VASP

**現在の状態:** 入力ファイル生成完了、計算実行中

### Phase 2：フォノン解析（計画中）

- ドーパント周辺の局所振動モードの特定
- H₂OのO-Hストレッチモード（~3600 cm⁻¹）との結合の検証

**使用ソフトウェア:** Phonopy

### Phase 3：分子動力学MD（計画中）

- ReaxFF力場によるH₂O解離イベントの統計的観測
- ドーパント濃度依存性の評価

**使用ソフトウェア:** LAMMPS

---

## ディレクトリ構成

```
tttwsp/
├── README.md                  # 英語版README
├── README_ja.md               # 本ファイル（日本語版）
├── PATENT_NOTICE.md           # 特許権利表示
├── SETUP.md                   # 環境構築ガイド
├── simulations/
│   └── dft/
│       ├── build_structure.py # 構造生成スクリプト（ASEベース）
│       ├── make_qe_input.py   # QE入力ファイル生成スクリプト
│       ├── tritetra_system.xyz # 生成された構造ファイル（可視化用）
│       ├── tritetra_system.cif # 生成された構造ファイル（QE用）
│       ├── tritetra.in        # Quantum ESPRESSO入力ファイル
│       ├── pseudo/            # 擬ポテンシャルファイル
│       └── out/               # 計算結果出力先
├── analysis/
│   └── tritetra_analyze.py    # 結果解析スクリプト
└── LICENSE
```

---

## 特許出願の状況

| 項目 | 内容 |
|---|---|
| 出願状況 | 出願準備中（Pre-filing） |
| 対象国・地域 | 日本 / PCT（国際出願） |
| 出願期限 | 2026年9月14日（新規性喪失の例外 期限） |
| 技術分類（予定） | C25B 1/04, C01B 3/04, B01J 27/00 |

---

## 公開ロードマップ

```
[現在] Privateリポジトリ（出願準備中）
    ↓
[出願後] 理論概要・シミュレーション設計をPublic公開
    ↓
[審査中] 計算結果・解析スクリプトを段階的に公開
    ↓
[権利確定後] フル公開・オープンサイエンスへ移行
```

---

## 環境構築

詳細は [SETUP.md](./SETUP.md) を参照してください。

**クイックスタート（WSL2 / Linux）:**

```bash
# 仮想環境のセットアップ
mkdir -p ~/tttwsp/dft && cd ~/tttwsp/dft
python3 -m venv venv && source venv/bin/activate
pip install numpy matplotlib pandas ase

# 構造生成
python3 build_structure.py

# DFT計算
mkdir -p out && pw.x < tritetra.in > tritetra.out
```

---

## 共同研究・連絡

本研究への参加・共同研究に関心をお持ちの方は、Issueまたは直接連絡ください。

**現時点でのNDA（秘密保持契約）の締結を条件に、詳細を共有できます。**

---

## ライセンス

Copyright © 2026 kiki054-n. All Rights Reserved.

特許出願完了まで、本リポジトリのすべての内容について、いかなる形式での複製・使用・改変・配布も禁止します。

---

*"The sphere whispers zero. The tetrahedron remembers it."*
— TriTetra Project, v3.2.0-private
