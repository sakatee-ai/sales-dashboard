from datetime import datetime
import os
import pandas as pd

# ===== 読み込み部分（ここは既にあるよね） =====
csv_path = os.path.join(os.path.dirname(__file__), "..", "data", "sample.csv")
csv_path = os.path.abspath(csv_path)
df = pd.read_csv(csv_path)

# ===== 加工（例：30歳以上） =====
df_filtered = df[df["年齢"] >= 30]

# ===== 出力パス構築 =====
now = datetime.now()
month_folder = now.strftime("%Y%m")         # 例：202504
timestamp = now.strftime("%Y%m%d_%H%M")      # 例：20250424_1830
filename = f"sample_filtered_{timestamp}.csv"

# 月別フォルダに出力
output_dir = os.path.join(os.path.dirname(__file__), "..", "output", month_folder)
os.makedirs(output_dir, exist_ok=True)

output_path = os.path.join(output_dir, filename)
df_filtered.to_csv(output_path, index=False, encoding="utf-8-sig")

print(f"✅ 月別フォルダに保存しました: {output_path}")
