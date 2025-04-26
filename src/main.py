import tkinter as tk
import customtkinter as ctk
from tkinter import ttk, filedialog, messagebox
from tkcalendar import DateEntry
import pandas as pd
import os

# --- グローバル変数 ---
original_df = None
joined_df = None
products_df = None
overview_table = None
overview_total_label = None
overview_year_selector = None
monthly_table = None
monthly_total_label = None
monthly_year_selector = None

# --- 初期ウィンドウ非表示 (Linux対策) ---
dummy_root = tk.Tk()
dummy_root.withdraw()

# --- 商品マスター読み込み ---
def load_products_master():
    global products_df
    try:
        products_df = pd.read_csv('data/products.csv')
    except Exception as e:
        products_df = None
        print(f"商品マスター読み込みエラー: {e}")

# --- ビューモード起動 ---
def launch_view_mode():
    global view_window

    view_window = ctk.CTk()
    view_window.title("ビューモード - 売上ダッシュボード")
    view_window.geometry("1400x900")

    # 編集モードへボタン
    edit_button = ctk.CTkButton(view_window, text="編集モードへ", command=launch_edit_mode)
    edit_button.pack(side="top", anchor="ne", padx=10, pady=10)

    # タブビュー作成
    tabview = ctk.CTkTabview(view_window)
    tabview.pack(fill="both", expand=True, padx=10, pady=10)

    tab_overview = tabview.add("売上一覧")
    tab_monthly = tabview.add("月別売上")
    tab_yearly = tabview.add("年度別売上")

    setup_overview_tab(tab_overview)
    setup_monthly_tab(tab_monthly)
    setup_yearly_tab(tab_yearly)

    view_window.mainloop()

# --- 売上一覧タブ設定 ---
def setup_overview_tab(tab_frame):
    global overview_table, overview_total_label, overview_year_selector

    frame = ctk.CTkFrame(tab_frame)
    frame.pack(fill="both", expand=True, padx=10, pady=10)

    vsb = ttk.Scrollbar(frame, orient="vertical")
    hsb = ttk.Scrollbar(frame, orient="horizontal")

    overview_table = ttk.Treeview(frame, show="headings", yscrollcommand=vsb.set, xscrollcommand=hsb.set)
    vsb.config(command=overview_table.yview)
    hsb.config(command=overview_table.xview)

    overview_table.pack(fill="both", expand=True)
    vsb.pack(side="right", fill="y")
    hsb.pack(side="bottom", fill="x")

    # 年度選択ドロップダウン
    year_frame = ctk.CTkFrame(tab_frame)
    year_frame.pack(pady=5)

    ctk.CTkLabel(year_frame, text="年度選択").pack(side="left", padx=5)
    overview_year_selector = ctk.CTkOptionMenu(year_frame, values=["全体"], command=lambda _: refresh_overview_table())
    overview_year_selector.pack(side="left", padx=5)

    # 売上合計表示欄
    overview_total_label = ctk.CTkLabel(tab_frame, text="売上合計: 0 円", font=("Arial", 16))
    overview_total_label.pack(pady=5)

    refresh_overview_table()

# --- 売上一覧更新 ---
def refresh_overview_table():
    global products_df

    if products_df is None or not os.path.exists('data/sales.csv'):
        return

    sales_df = pd.read_csv('data/sales.csv')
    joined = pd.merge(sales_df, products_df, on="商品ID", how="left")
    joined['日付'] = pd.to_datetime(joined['日付'], errors='coerce')

    fiscal_years = sorted(list(set(joined['日付'].apply(lambda d: d.year if d.month >= 4 else d.year - 1).dropna())), reverse=True)
    if overview_year_selector.cget("values") == ("全体",):
        overview_year_selector.configure(values=["全体"] + [str(y) for y in fiscal_years])
        overview_year_selector.set(str(fiscal_years[0]))

    selected_year = overview_year_selector.get()

    if selected_year != "全体":
        selected_year = int(selected_year)
        joined = joined[(joined['日付'] >= f"{selected_year}-04-01") & (joined['日付'] <= f"{selected_year+1}-03-31")]

    overview_table.delete(*overview_table.get_children())
    columns = ["日付", "顧客名", "商品名", "数量", "金額", "登録日"]
    overview_table.configure(columns=columns)

    for col in columns:
        overview_table.heading(col, text=col)
        overview_table.column(col, width=150, anchor="center", stretch=False)

    for _, row in joined.iterrows():
        values = [row.get(col, "") for col in columns]
        overview_table.insert("", "end", values=values)

    total = joined['金額'].sum()
    overview_total_label.configure(text=f"売上合計: {int(total)} 円")

# --- 月別売上タブ設定 ---
def setup_monthly_tab(tab_frame):
    global monthly_table, monthly_total_label, monthly_year_selector

    frame = ctk.CTkFrame(tab_frame)
    frame.pack(fill="both", expand=True, padx=10, pady=10)

    vsb = ttk.Scrollbar(frame, orient="vertical")
    hsb = ttk.Scrollbar(frame, orient="horizontal")

    monthly_table = ttk.Treeview(frame, show="headings", yscrollcommand=vsb.set, xscrollcommand=hsb.set)
    vsb.config(command=monthly_table.yview)
    hsb.config(command=monthly_table.xview)

    monthly_table.pack(fill="both", expand=True)
    vsb.pack(side="right", fill="y")
    hsb.pack(side="bottom", fill="x")

    # 年度選択ドロップダウン
    year_frame = ctk.CTkFrame(tab_frame)
    year_frame.pack(pady=5)

    ctk.CTkLabel(year_frame, text="年度選択").pack(side="left", padx=5)
    monthly_year_selector = ctk.CTkOptionMenu(year_frame, values=["全体"], command=lambda _: refresh_monthly_table())
    monthly_year_selector.pack(side="left", padx=5)

    # 売上合計表示欄
    monthly_total_label = ctk.CTkLabel(tab_frame, text="売上合計: 0 円", font=("Arial", 16))
    monthly_total_label.pack(pady=5)

    refresh_monthly_table()

# --- 月別売上更新 ---
def refresh_monthly_table():
    global products_df

    if products_df is None or not os.path.exists('data/sales.csv'):
        return

    sales_df = pd.read_csv('data/sales.csv')
    joined = pd.merge(sales_df, products_df, on="商品ID", how="left")
    joined['日付'] = pd.to_datetime(joined['日付'], errors='coerce')

    fiscal_years = sorted(list(set(joined['日付'].apply(lambda d: d.year if d.month >= 4 else d.year - 1).dropna())), reverse=True)
    if monthly_year_selector.cget("values") == ("全体",):
        monthly_year_selector.configure(values=["全体"] + [str(y) for y in fiscal_years])
        monthly_year_selector.set(str(fiscal_years[0]))

    selected_year = monthly_year_selector.get()

    if selected_year != "全体":
        selected_year = int(selected_year)
        joined = joined[(joined['日付'] >= f"{selected_year}-04-01") & (joined['日付'] <= f"{selected_year+1}-03-31")]

    joined['年月'] = joined['日付'].dt.to_period('M')
    grouped = joined.groupby('年月')['金額'].sum().reset_index()

    monthly_table.delete(*monthly_table.get_children())
    monthly_table.configure(columns=["年月", "売上合計"])

    for col in ["年月", "売上合計"]:
        monthly_table.heading(col, text=col)
        monthly_table.column(col, width=150, anchor="center", stretch=False)

    for _, row in grouped.iterrows():
        monthly_table.insert("", "end", values=[row['年月'], int(row['金額'])])

    total = grouped['金額'].sum()
    monthly_total_label.configure(text=f"売上合計: {int(total)} 円")

# --- 年度別売上タブ設定 (仮) ---
def setup_yearly_tab(tab_frame):
    label = ctk.CTkLabel(tab_frame, text="年度別売上集計は後で作成予定", font=("Arial", 16))
    label.pack(pady=20)

# --- 編集モード起動 (簡易版) ---
def launch_edit_mode():
    pass

# --- 起動 ---
if __name__ == "__main__":
    load_products_master()
    launch_view_mode()
