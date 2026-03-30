# 環境構築ガイド / Environment Setup Guide

TriTetra Water Splitting Project — シミュレーション環境のセットアップ手順

---

## 動作環境 / Requirements

| 項目 | 内容 |
|---|---|
| OS | Windows 10/11（WSL2経由）、Linux、macOS |
| Python | 3.10以上 |
| 必須ツール | Quantum ESPRESSO 7.x、ASE 3.x |
| 推奨メモリ | 8GB以上 |

---

## Step 1：WSL2のインストール（Windowsのみ）

PowerShellを**管理者として**開いて実行：

```powershell
wsl --install
```

再起動後、Ubuntuが自動起動します。

### Ubuntuユーザーの設定

```
Enter new UNIX username: （小文字英字で入力、例: tttwsp）
New password: （入力中は画面に表示されない）
Retype new password: （同じパスワードをもう一度）
```

`passwd: password updated successfully` と表示されれば完了。

---

## Step 2：Ubuntuのパッケージ更新

```bash
sudo apt update && sudo apt upgrade -y
```

---

## Step 3：Quantum ESPRESSOのインストール

```bash
sudo apt install -y quantum-espresso python3-full python3-venv
```

インストール確認：

```bash
pw.x --version
```

バージョン情報が表示されればOK。

---

## Step 4：Python仮想環境のセットアップ

```bash
# 作業ディレクトリの作成
mkdir -p ~/tttwsp/dft && cd ~/tttwsp/dft

# 仮想環境の作成と有効化
python3 -m venv venv
source venv/bin/activate
```

プロンプトが `(venv)` で始まれば有効化成功。

```bash
# ライブラリのインストール
pip install numpy matplotlib pandas ase
```

> **毎回Ubuntuを開いたときに必要な操作:**
> ```bash
> cd ~/tttwsp/dft && source venv/bin/activate
> ```

---

## Step 5：擬ポテンシャルのダウンロード

```bash
mkdir -p pseudo && cd pseudo

wget https://pseudopotentials.quantum-espresso.org/upf_files/Si.pbe-n-kjpaw_psl.1.0.0.UPF
wget https://pseudopotentials.quantum-espresso.org/upf_files/S.pbe-n-kjpaw_psl.1.0.0.UPF
wget https://pseudopotentials.quantum-espresso.org/upf_files/O.pbe-n-kjpaw_psl.1.0.0.UPF
wget https://pseudopotentials.quantum-espresso.org/upf_files/H.pbe-kjpaw_psl.1.0.0.UPF

cd ..
```

---

## Step 6：構造ファイルの生成

```bash
python3 build_structure.py
```

正常終了時の出力例：

```
Siスーパーセル: 54原子
Sドーパント配置: index=33, 位置=[9.504 6.789 9.504] Å
最終系: 57原子
  Si=53, S=1, O=1, H=2
✅ 出力完了:
  tritetra_system.xyz  — 可視化用
  tritetra_system.cif  — QE入力用
```

---

## Step 7：DFT計算の実行

```bash
mkdir -p out
pw.x < tritetra.in > tritetra.out
```

完了確認：

```bash
tail -5 tritetra.out
```

最終行に `JOB DONE.` が表示されれば成功。

---

## トラブルシューティング

### `externally-managed-environment` エラー
→ 仮想環境を使用してください（Step 4参照）。`pip install` に `--break-system-packages` は使用しないこと。

### `ModuleNotFoundError: No module named 'numpy'`
→ 仮想環境が有効化されていません。`source venv/bin/activate` を実行してください。

### `pw.x: command not found`
→ `sudo apt install -y quantum-espresso` を再実行してください。

---

*最終更新: 2026-03-30*
