# Veryl → LibreLane フロー

このプロジェクトは **Veryl** で書いた RTL を **SystemVerilog** に変換し、
**LibreLane**（sky130 PDK）で合成〜配置配線して、**面積・消費電力・遅延**を
比較するための構成です。

```
 RTL (Veryl)  ──veryl build──▶  SystemVerilog  ──librelane──▶  metrics.json  ──compare.py──▶  比較表
 src/*.veryl                       sv/*.sv          合成〜配置配線          area/power/timing
```

## 必要なもの

- **Veryl** — <https://veryl-lang.org/install/>
- **LibreLane** — <https://github.com/librelane/librelane>（Nix 推奨）
- **Icarus Verilog**（任意・機能検証用）
- Python 3（比較スクリプト。標準ライブラリのみ）

## ディレクトリ構成

```
.
├── Veryl.toml                     Veryl プロジェクト設定
├── src/*.veryl                    RTL
├── sv/*.sv                        生成される SystemVerilog（make sv）
├── librelane/<design>/config.json 設計ごとの LibreLane 設定
├── tb/*.sv                        機能検証テストベンチ（任意）
├── scripts/compare.py             metrics を集計して表を出力
├── docs/FLOW.md                   このドキュメント
└── Makefile
```

## 使い方

```bash
make sv        # Veryl → SystemVerilog
make check     # 機能検証（Icarus Verilog が必要）
make flow      # LibreLane フロー（全設計。1 設計あたり数分）
make compare   # 面積/電力/遅延の比較表を出力（results.csv も生成）
make list      # 検出された設計名を表示
```

LibreLane の起動方法が違う場合は上書きできます:

```bash
make flow LIBRELANE="nix run github:librelane/librelane --"
```

## 設計の追加

設計は `librelane/<name>/config.json` の存在から**自動検出**されます。追加は:

1. `src/<your_module>.veryl` に RTL を書く
2. `librelane/<name>/config.json` を作る（`DESIGN_NAME` は
   `<project.name>_<ModuleName>`。Veryl がモジュール名にプロジェクト名を
   前置するため）
3. `make flow` / `make compare` がそのまま新設計を拾います

## 結果の読み方と注意

- 指標の元データは `librelane/<design>/runs/<最新tag>/final/metrics.json`。
  `compare.py` がここを読み、面積・セル数・スラック・電力・fmax 目安を表にします。
- **合成ツール（Yosys+ABC）は組合せ算術を作り替える**ため、RTL の構造差が
  netlist で薄まることがあります。差を出す本命は **`CLOCK_PERIOD` を縮めて
  各設計の遅延限界を炙り出す**こと。ほかに `SYNTH_STRATEGY`、階層維持、
  ビット幅スイープが有効です。
- **SystemVerilog 対応**: Veryl の出力は合成可能な SV サブセットで、Yosys の
  ネイティブ `read_verilog -sv` で通ります（`interface`/`package` 等の高度な
  SV を使う場合のみ `config.json` に `USE_SLANG: true` を追加）。

## git-skel での更新

このプロジェクトはスケルトンから `git skel init` で作られています。
スケルトン側の改善（Makefile や compare.py など）は次で取り込めます:

```bash
git skel update
```

自分で書き換えたファイル（`Veryl.toml`、`src/`、`librelane/<design>/` など）を
更新で上書きされたくない場合は、**プロジェクト側の `.gitskelignore`** に
追加してください。
