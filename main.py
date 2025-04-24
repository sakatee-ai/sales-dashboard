# src/main.py

import pandas as pd
import os

# CSVファイルのパス（今は固定パス、後で選択式にしてもOK）
csv_path = os.path.join("..", "data", "sample.csv")

# CSVを読み込んで表示
try:
    df = pd.read_csv(csv_path)
    print("📄 読み込んだCSVファイルの中身：")
    print(df.head())  # 最初の5行だけ表示
except FileNotFoundError:
    print("❌ ファイルが見つかりませんでした。data/sample.csv があるか確認してね。")
