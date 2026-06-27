# TTT-WSP v5 — スラブモデル DFT プロトコル

S/P ドープ sp³ 格子上の **H₂O 吸着・解離** を、物理的に意味のある形で評価するための手順書。
旧バージョン（v3〜v4）の **バルク間隙モデル**——周期バルクセル内に H₂O を固定して
SCF した——を置き換える。旧モデルは「表面」が存在せず、吸着エネルギーとして
+4〜+17 eV という非物理値を生んでいた。本プロトコルはその根を断つ。

---

## 0. 旧モデルの問題と本プロトコルの対応

| 旧モデルの問題 | 影響した主張 | 本プロトコルでの修正 |
|---|---|---|
| バルク中心にドーパント＋水を固定（表面なし） | 触媒の枠組み全体 | 真空層付きスラブ、表面にドーパント、水は表面で**緩和** |
| ΔE_ads = +4〜+17 eV（非物理） | ΔE_ads=−0.84「自発吸着」 | 正しい参照（孤立水）＋緩和で物理的な ΔE_ads |
| ΔΔE がアーティファクトの差 | ΔΔE=−4.46「相乗効果」 | 両項が物理量になって初めて差に意味 |
| Γ点のみ・ecut 30 Ry | 全数値の精度 | k点・ecut・真空・層厚の**収束テストを必須化** |
| 単調増加 NEB（逆障壁0、鞍点なし） | Ea=0.282「Pt 超え」 | 生成系を真の極小として取り直す（フェーズ2、後述） |
| `.in`/`.out` 未公開 | Data Availability の記述 | 完了した入力・出力を repo に commit |

---

## 1. 必要ファイル

```
build_slab.py          スラブ構築（真空・不動態化・固定・ドープ・水配置・QE入力出力）
build_water_ref.py     孤立 H₂O 参照（吸着エネルギーの分母）
compute_adsorption.py  .out を集計して ΔE_ads と ΔΔE を計算（非物理値を自動警告）
pseudo/                擬ポテンシャル（pslibrary 1.0.0 PAW-PBE 等）を置く
```

依存: `pip install ase`、Quantum ESPRESSO v7.x（`pw.x`、後で `neb.x`）。

---

## 2. ステップ0 — 格子定数と擬ポテンシャルの確認

数値の前提を固定する。使用する擬ポテンシャルで **Si バルクの格子定数を最適化**し、
`build_slab.py` の `A_LAT` に反映する（PBE は実験値 5.431 Å よりやや大きめに出やすい）。
擬ポテンシャル名（`PSEUDO` 辞書）が `pseudo/` の実ファイルと一致しているか確認。

---

## 3. ステップ1 — 収束テスト（**最重要・先にやる**）

旧版の信頼性問題はここに集約される。**収束を確認する前に物理を議論しない。**
最も小さい系（undoped、`DOPANTS=[]`、`ADD_WATER=False`、`NX=NY=2`）で順に走らせ、
全エネルギーが目標許容内に収まる最小設定を決める。

| パラメータ | スキャン範囲 | 目標許容 |
|---|---|---|
| `ecutwfc` | 40, 50, 60, 70 Ry（`ecutrho = 8×`） | エネルギー差 < 5 meV/atom |
| k点 | 2×2×1, 4×4×1, 6×6×1 | 表面エネルギー差 < 5 meV/Å² |
| `VACUUM` | 6, 8, 10, 12 Å | エネルギー差 < 5 meV |
| `NLAYERS` | 6, 8, 10, 12（下層固定） | 表面エネルギー収束 |

S は浅い擬ポテンシャルだと 30 Ry では不足しがちなので、ecut は特に丁寧に。
決めた `ecutwfc/ecutrho/kpts/VACUUM/NLAYERS` を以降すべての系で**共通**に使う。

このステップは2本のスクリプトで自動化してある:

```bash
python3 gen_convergence.py       # conv/{ecut,kpts,vacuum,layers}/*.in を生成
# 各 .in を pw.x で実行（例）
for d in conv/ecut conv/kpts conv/vacuum conv/layers; do
  (cd $d && for f in *.in; do pw.x -in $f > ${f%.in}.out; done)
done
python3 analyze_convergence.py   # 収束した最小設定を表で提示
```

判定基準は ecut・kpts が dE/atom < 5 meV、vacuum が dE < 3 meV、layers が
増分（傾き）の二次差 < 10 meV。**最終確認**として、選んだ設定で layers=8 と 10 の
ΔE_ads を1点ずつ比べ、< ~50 meV で安定していれば確定（バルク寄与が相殺する
ΔE_ads の安定性が、層厚・真空の本当の収束指標）。

---

## 4. ステップ2 — 構造構築

吸着エネルギー1点につき、同一設定で **3 つ**の計算が要る:

1. **slab+H₂O**：`ADD_WATER=True`
2. **bare slab**：`ADD_WATER=False`（同じドープ・同じセル）
3. **孤立 H₂O**：`build_water_ref.py`（全系で 1 回でよい）

比較する系（例）:

```bash
# undoped 参照
#   build_slab.py: DOPANTS=[], ADD_WATER=True  -> si_pure_h2o.in
#                  DOPANTS=[], ADD_WATER=False -> si_pure.in
# Si+S
#   DOPANTS=[("S","top")], ADD_WATER=True/False
# Si+S+P（隣接2サイト）
#   DOPANTS=[("S","top"),("P","top")], ADD_WATER=True/False
python3 build_water_ref.py
```

`*.xyz` を必ず可視化し（VESTA/OVITO/ASE GUI）、**水が格子に食い込んでいない**こと、
ドーパントが表面層にあること、底面が H で閉じていることを目視確認する。
旧版の非物理値は、この目視を省いたことが一因。

---

## 5. ステップ3 — 計算実行

```bash
mkdir -p out
for f in si_pure si_pure_h2o si_s si_s_h2o si_sp tttwsp_si_sp_h2o_100 h2o_ref; do
    mpirun -np 16 pw.x -in ${f}.in > ${f}.out
done
```

緩和が収束（`bfgs converged` / `Final energy`）したことを各 `.out` で確認。
ジョブ管理は系ごとにディレクトリを分けると `prefix` 衝突を避けられる。

---

## 6. ステップ4 — 吸着エネルギーと TTT 効果

```bash
python3 compute_adsorption.py
```

$$\Delta E_{ads} = E(\text{slab+H}_2\text{O}) - E(\text{slab}) - E(\text{H}_2\text{O, gas})$$
$$\Delta\Delta E = \Delta E_{ads}(\text{doped}) - \Delta E_{ads}(\text{pure})$$

**判定ゲート:** 物理的な水の吸着は概ね −0.1〜−1.0 eV。スクリプトは
`|ΔE_ads| > 2 eV` を `UNPHYSICAL` と警告する。警告が出たら ΔΔE は読まない——
両親項が物理量になって初めて、その差に意味が生まれる。ここが旧版との決定的な違い。

---

## 7. ステップ5 — 幾何記述子の相関（因果ではなく相関として）

各ドープ配置で、ドーパント周りの $|\sum_{i}\vec{v}_i|$（四面体均衡からのずれ）を
緩和後構造から計算し、ΔΔE と**散布図**にする。相関があれば TTT 仮説を支持する
状況証拠になるが、「均衡の崩れが ΔΔE を *引き起こす*」とは主張しない
（電子的効果との切り分けには PDOS・電荷密度差が要る）。preprint 5.1 の
hedge はこの線で正しい。

---

## 8. フェーズ2（別途）— NEB の作り直し

Ea を語るには、まず **生成系（FS）が本物のエネルギー極小**であることを確かめる。
旧 NEB は IS→終端まで単調増加で、climbing image が終端・逆障壁0＝鞍点を挟めていない。

1. FS 候補（H が表面サイトに解離吸着した構造）を**単独で relax** し、極小か確認。
2. IS と FS の両端を固定して NEB（7〜9 image）。プロファイルが
   IS→TS(中間で最大)→FS と**山型**になることを必須条件にする。
3. 比較表は速度論量（表面解離障壁）のみで揃え、各文献値に出典を付す。
   気相 O–H 結合解離エネルギー（~5.1 eV）は別物なので同じ列に置かない。
4. 「Pt より低い」は、上記が満たされ、同一手法での Pt(111) 基準が取れるまで保留。

---

## 9. 公開（Data Availability の修正）

収束した最終設定の `.in` と、対応する `.out`（または抜粋）、`*.xyz` を
repo に commit する。これで preprint の「全入力ファイルを公開」が初めて真になる。
旧 `tritetra_si_s_dope.in`（LAMMPS SW トイモデル）は `legacy/` に移し、
DFT 本体と混同されないよう README で明確に分離する。

---

*TTT-WSP v5 slab protocol — 構造の妥当性を、主張の前に。*
