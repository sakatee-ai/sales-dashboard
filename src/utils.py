import os
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PRODUCTS_CSV = os.path.join(BASE_DIR, "data", "products.csv")
CATEGORIES_CSV = os.path.join(BASE_DIR, "data", "categories.csv")
SALES_CSV = os.path.join(BASE_DIR, "data", "sales.csv")

def load_products_master():
    try:
        products_df = pd.read_csv(PRODUCTS_CSV)
        categories_df = pd.read_csv(CATEGORIES_CSV)
        products_df = pd.merge(products_df, categories_df, on="カテゴリID", how="left")
        return products_df
    except Exception as e:
        print(f"商品マスター読み込みエラー: {e}")
        return None

def detect_date_columns(df):
    date_columns = []
    for col in df.columns:
        try:
            parsed = pd.to_datetime(df[col], errors='coerce', format='%Y-%m-%d')
            if parsed.notna().sum() / len(parsed) > 0.8:
                date_columns.append(col)
        except Exception:
            continue
    return date_columns
