
# Sakatees CSV アプリ（売上ダッシュボード）

## 🎯 概要
このアプリは、CSV形式の売上データ・商品マスタ・カテゴリ情報をもとに、

- 売上一覧の自動集計  
- 月別・年度別の売上推移をグラフで可視化  
- 商品・カテゴリごとの分析も視野に入れた構成  

などを行う、**ローカル完結型の売上ダッシュボードツール**です。

Python（Tkinter + CustomTkinter）で構築されており、  
Excelでは扱いづらい中規模データも軽快に管理できます。

## 🧱 構成（ディレクトリ）

```
.
├── main.py                # メインアプリ起動スクリプト
├── ui_monthly.py         # 月別売上タブ
├── ui_overview.py        # 売上一覧・集計表示
├── ui_category_edit.py   # カテゴリ編集タブ
├── ui_sales_entry.py     # 売上登録フォームタブ
├── utils.py              # データ読み込みユーティリティ
├── venv/                 # 仮想環境（除外対象）
├── data/
│   ├── sales.csv         # 売上データ
│   ├── products.csv      # 商品マスタ
│   └── categories.csv    # カテゴリマスタ
├── output/               # 出力フォルダ（保存CSVなど）
├── requirements.txt      # 必要パッケージ一覧
└── .gitignore
```

## 🚀 セットアップ手順

### 1. 仮想環境の作成（初回のみ）
```bash
python -m venv venv
```

### 2. 仮想環境の有効化（Windows PowerShell）
```bash
venv\Scripts\Activate.ps1
```

### 3. 必要パッケージのインストール
```bash
pip install -r requirements.txt
```

## 🖥 アプリの起動
```bash
python main.py
```

## 📌 機能一覧

- ✅ CSV読み込み＆売上一覧表示（フィルター・合計付き）
- ✅ 月別売上ビュー
- ✅ カテゴリ編集（即反映）
- ✅ 売上登録フォーム（商品マスタ連携・自動計算）
- ✅ CSV出力ボタン（filtered_sales_YYYYMMDD.csv）
- ⏳ グラフ表示（今後の強化予定）

## 🛠 開発メモ（進捗ログ）

- 2025/5/5 Ver.1.0 正式完成（ローカル運用レベルまで実装）
- 2025/5/1 `.venv → venv` へ切替＆GitHub構成をクリーンに整理

## 📄 ライセンス
MITライセンス予定（個人・業務利用OK）

## 🙋‍♂️ 作者
Sakatees Japan  
https://sakatees-ai.jp（※準備中）

---

© Sakatees Japan
