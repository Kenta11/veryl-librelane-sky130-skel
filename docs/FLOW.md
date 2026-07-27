# Veryl → LibreLane フロー

このプロジェクトは **Veryl** で書いた設計を **SystemVerilog** に変換し、
**LibreLane**（sky130 PDK）で合成〜配置配線（P&R）して、その設計の
**面積・消費電力・遅延**を確認するための構成です。

```
 設計 (Veryl)  ──veryl build──▶  SystemVerilog  ──librelane──▶  metrics.json  ──report.py──▶  面積/電力/遅延
 src/*.veryl                       sv/*.sv          合成〜P&R
```

1 スケルトン = 1 設計です。複数を比較したい場合は、設計ごとにこのスケルトンから
別プロジェクトを作り、それぞれの `make report` の結果を比べてください。

## 必要なもの

- **Veryl** — <https://veryl-lang.org/install/>（機能検証は Veryl 組み込みの
  ネイティブシミュレータを使うので、外部シミュレータは不要）
- **LibreLane** — <https://github.com/librelane/librelane>（Nix 推奨）
- Python 3（レポートスクリプト。標準ライブラリのみ）

## ディレクトリ構成

```
.
├── Veryl.toml               Veryl プロジェクト設定（sources = ["src", "tb"]）
├── src/*.veryl              設計（トップは1つ。複数ファイルに分割可）
├── tb/*.veryl              テストベンチ（#[test] モジュール）
├── sv/*.sv                 生成される SystemVerilog（make sv）
├── librelane/config.json   LibreLane / sky130 設定
├── scripts/report.py       metrics から面積/電力/遅延を表示
├── docs/FLOW.md            このドキュメント
└── Makefile
```

設計は複数の `.veryl` ファイルに分けて構いません（`src/` 全体がコンパイル対象）。
テストベンチは `tb/` に置き、`#[test(...)]` を付けます。テストモジュールは生成 SV
では `` `ifdef `` で囲まれるため、**合成（LibreLane）には混入しません**。

## 使い方

```bash
make check     # 機能検証（veryl test / ネイティブシミュレータ。外部ツール不要）
make sv        # Veryl → SystemVerilog
make pnr       # LibreLane フロー（合成〜配置配線。数分）
make report    # 最新ランの面積/電力/遅延を表示
```

LibreLane の起動方法が違う場合は上書きできます:

```bash
make pnr LIBRELANE="nix run github:librelane/librelane --"
```

## 自分の設計に置き換える

1. `src/` を自分の設計に差し替える（トップモジュールは1つ、複数ファイル可）
2. `tb/` のテストベンチを設計に合わせて更新する
3. `librelane/config.json` の `DESIGN_NAME` をトップに合わせる
   （`<project.name>_<ModuleName>`。Veryl がモジュール名にプロジェクト名を前置。
   例: project `example` / module `Adder` → `example_Adder`）
4. 必要に応じて `CLOCK_PERIOD` など `config.json` を調整
5. `make check` → `make pnr` → `make report`

## 結果の読み方と注意

- 指標の元データは `librelane/runs/<最新tag>/final/metrics.json`。
  `report.py` がここを読み、面積・セル数・スラック・電力・fmax 目安を表示します。
- **遅延を追い込むなら `CLOCK_PERIOD` のスイープ**が基本です。周期を縮めて
  タイミングが成立する下限を探すと、その設計の実力（fmax）が見えます。
  ほかに `SYNTH_STRATEGY`（面積優先/遅延優先）も効きます。
- **SystemVerilog 対応**: Veryl の出力は合成可能な SV サブセットで、Yosys の
  ネイティブ `read_verilog -sv` で通ります（`interface`/`package` 等の高度な
  SV を使う場合のみ `config.json` に `USE_SLANG: true` を追加）。

## git-skel での更新

このプロジェクトはスケルトンから `git skel init` で作られています。
スケルトン側の改善（Makefile や report.py など）は次で取り込めます:

```bash
git skel update
```

自分で書き換えたファイル（`Veryl.toml`、`src/`、`tb/`、`librelane/config.json`
など）を更新で上書きされたくない場合は、**プロジェクト側の `.gitskelignore`** に
追加してください。
