# TTT-WSP v5 — 実行ランブック（ステップ1：収束テスト）

スラブ側を**実際に回し始める**ための手順。各ステップが何をしているかを解説しながら進む。
収束が出るまで物理（吸着エネルギー等）は議論しない、が大原則。

> サンドボックスで検証済み：`build_slab.py`/`gen_convergence.py` の構造生成、生成 QE 入力の
> pw.x によるパース（全 namelist と構造を正しく読み、欠けているのは擬ポテンシャルのみ）、
> `analyze_convergence.py` の判定ロジック。あとは手元で擬ポテンシャルを置けば走る。

---

## ステップ0 — 実行前チェック

```bash
python3 preflight.py
```

ASE・`pw.x`・擬ポテンシャル・入力の有無を点検する。`[XX]` が消えるまで先に進まない。
QE が 7.0 未満だと警告が出る（理由は下記§1の注を参照）。あなたの環境は v7.5 なのでそのまま。

---

## ステップ1 — 擬ポテンシャルを置く（いまの実際の入口）

収束テストは **Si と H の2つだけ**で足りる（undoped 不動態化スラブ）。
PAW-PBE（pslibrary 1.0.0 または SSSP efficiency PBE）の UPF を入手し `pseudo/` に置く。

```
pseudo/
  Si.pbe-n-kjpaw_psl.1.0.0.UPF
  H.pbe-kjpaw_psl.1.0.0.UPF
```

ファイル名は `build_slab.py`／`gen_convergence.py` の `PSEUDO` 辞書と**完全一致**させる
（違う名前の UPF を使うなら辞書側を書き換える）。本番では S・P・O も追加する。

> **QE<7.0 の注:** ASE は空の `&FCP`/`&RISM` namelist を書き出す。これは QE 7.x の機能で、
> 6.x はエラーにする。v7.5 なら無視してよい。古い QE しか無い場合は各 `.in` から
> この2つの空 namelist を削除する。

---

## ステップ2 — 収束入力を生成

```bash
python3 gen_convergence.py
```

最小の undoped スラブ（2×2 横・水なし・底面 H 不動態化・下3層固定）で、4つのスキャンを
`conv/{ecut,kpts,vacuum,layers}/` に生成する。各スキャンは注目パラメータだけを動かし、
他は妥当な暫定値（ecut 50/400・k点 4×4×1・真空10 Å・8層）に固定する。

---

## ステップ3 — 入力ファイルの読み方（解説）

`conv/ecut/ecut_50.in` を例に、各ブロックの意味:

```
&CONTROL
   calculation = 'scf'          # 収束テストは構造固定の一点計算（速い）
   tprnfor     = .true.         # 力も出力（後の relax 妥当性確認用）
   outdir      = './out'        # スクラッチ出力先（巨大→.gitignore 対象）
   pseudo_dir  = './pseudo'     # UPF の場所
   tefield = .true.             # ↓ 非対称スラブの双極子補正を有効化
   dipfield = .true.
/
&SYSTEM
   ibrav = 0                    # セルは CELL_PARAMETERS で明示
   ecutwfc = 50.0               # 波動関数カットオフ（このスキャンの主役）
   ecutrho = 400.0              # 電荷密度カットオフ＝8×ecutwfc（PAW の目安）
   occupations = 'smearing'     # ↓ ドープ／表面状態のための薄いスメアリング
   smearing = 'mv', degauss = 0.01   # Marzari-Vanderbilt cold smearing
   edir = 3                     # 双極子補正の方向（z）
   emaxpos = 0.831              # 鋸歯ポテンシャルを真空中央に（自動計算済み）
   eopreg = 0.05, eamp = 0.0    # 補正領域幅・外部電場ゼロ
   nat = 36, ntyp = 2           # 原子数・元素種数（自動）
/
&ELECTRONS
   conv_thr = 1e-06             # SCF 収束しきい値（Ry）
   mixing_beta = 0.3            # 電荷混合（スラブは小さめが安定）
/
ATOMIC_SPECIES ...             # 元素・質量・UPF 名
ATOMIC_POSITIONS angstrom ...  # 座標。末尾 "0 0 0" は固定原子（下層＋H）
K_POINTS automatic ...         # 面内サンプリング、面外は 1
```

要点は、**双極子補正・スメアリング・面内 k点・固定原子フラグ**が旧バルクモデルとの違い。

---

## ステップ4 — まず ecut スキャンを回す

```bash
cd conv/ecut
for f in *.in; do
  echo "running $f ..."
  pw.x -in $f > ${f%.in}.out
done
cd ../..
```

1本目（`ecut_40.out`）が出たら、最後まで走らせる前に**成功しているか**確認する:

```bash
grep -E "JOB DONE|convergence has been achieved|!    total energy" conv/ecut/ecut_40.out
```

- `convergence has been achieved` … SCF が収束した（正常）
- `!    total energy = ... Ry` … 最終エネルギー（この値を収束判定に使う）
- `JOB DONE.` … 正常終了

これらが出ていれば成功。出ていなければ §8 へ。

---

## ステップ5 — 残り3スキャンを回す

```bash
for d in conv/kpts conv/vacuum conv/layers; do
  (cd $d && for f in *.in; do pw.x -in $f > ${f%.in}.out; done)
done
```

2×2 セルの SCF なので各本は軽い（数十秒〜数分／本、設定とコア数による）。

---

## ステップ6 — 収束を判定

```bash
python3 analyze_convergence.py
```

各パラメータでエネルギーが止まる点を表で示し、収束した最小設定を提示する。判定基準:

| 量 | 指標 | 収束 |
|---|---|---|
| ecut | dE/atom | < 5 meV/atom |
| kpts | dE/atom | < 5 meV/atom |
| vacuum | dE(total) | < 3 meV |
| layers | 増分の二次差 | < 10 meV |

「NOT converged」が出たら、そのスキャン範囲を広げて回し直す。

---

## ステップ7 — 値を固定して最終確認

得られた `ecutwfc/ecutrho/kpts/VACUUM/NLAYERS` を `build_slab.py` 冒頭に書き込む。
最後に、選んだ設定で **layers=8 と 10 の ΔE_ads** を1点ずつ比べ、< ~50 meV で
安定していれば確定（バルク寄与が相殺する ΔE_ads の安定性が本当の収束指標）。

これで本番（undoped・Si+S・Si+S+P の ΔE_ads）に進める。

---

## ステップ8 — トラブルシューティング

| 症状 | 原因 | 対処 |
|---|---|---|
| `file ...UPF not found` | 擬ポテンシャル未配置／名前不一致 | `pseudo/` に置く・`PSEUDO` 辞書と名前を一致 |
| `Error ... &FCP/&RISM` | QE<7.0 | 空 `&FCP`/`&RISM` を削除、または 7.x へ |
| `convergence NOT achieved` | 混合が不安定 | `mixing_beta` を 0.1〜0.2 に下げる／`electron_maxstep` 増 |
| `S matrix not positive definite` 等 | スメアリング過小／格子近接 | `degauss` を 0.02 に・構造を `.xyz` で目視 |
| FFT/`ecutrho` 警告 | rho カットオフ不足 | `ecutrho` を 10×ecutwfc に |
| 異常に遅い | k点・ecut 過大 | 収束テストは 2×2 セルで十分、過剰設定を避ける |

座標の妥当性（水の食い込み・ドーパント位置・底面 H）は、走らせる前に必ず `.xyz` を
VESTA/OVITO/ASE GUI で目視する。旧版の非物理値の一因はこの目視の省略だった。

---

*ステップ1が緑になったら、その設定を土台に本番 ΔE_ads へ。*
