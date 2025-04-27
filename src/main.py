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
yearly_table = None
yearly_total_label = None
start_date_widget = None
end_date_widget = None
date_column_var = None
date_column_selector = None
sort_states = {}

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

# --- 日付カラム自動検出関数（厳格版） ---
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

# --- ソート実行ロジック ---
def on_column_double_click(event):
    region = overview_table.identify("region", event.x, event.y)
    if region == "heading":
        col_id = overview_table.identify_column(event.x)
        col_index = int(col_id.replace("#", "")) - 1
        if col_index == 0:
            return
        column_name = overview_table["columns"][col_index]
        sort_overview_table_by_column(column_name)

def sort_overview_table_by_column(column_name):
    global overview_table, sort_states

    rows = [(overview_table.set(k, column_name), k) for k in overview_table.get_children("")]
    ascending = sort_states.get(column_name, True)

    try:
        rows.sort(key=lambda t: float(t[0].replace(',', '')), reverse=not ascending)
    except ValueError:
        rows.sort(reverse=not ascending)

    for index, (val, k) in enumerate(rows):
        overview_table.move(k, '', index)

    sort_states[column_name] = not ascending

# --- ビューモード起動 ---
def launch_view_mode():
    global view_window

    view_window = ctk.CTk()
    view_window.title("ビューモード - 売上ダッシュボード")
    view_window.geometry("1400x900")

    edit_button = ctk.CTkButton(view_window, text="編集モードへ", command=launch_edit_mode)
    edit_button.pack(side="top", anchor="ne", padx=10, pady=10)

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
    global start_date_widget, end_date_widget, date_column_var, date_column_selector

    control_frame = ctk.CTkFrame(tab_frame)
    control_frame.pack(fill="x", padx=10, pady=5)

    ctk.CTkLabel(control_frame, text="対象列").pack(side="left", padx=5)
    date_column_var = tk.StringVar()
    date_column_selector = ctk.CTkOptionMenu(control_frame, variable=date_column_var, values=["日付"])
    date_column_selector.pack(side="left", padx=5)

    ctk.CTkLabel(control_frame, text="開始日").pack(side="left", padx=5)
    start_date_widget = DateEntry(control_frame, width=12, background='darkblue', foreground='white', date_pattern='yyyy-mm-dd')
    start_date_widget.pack(side="left", padx=5)

    ctk.CTkLabel(control_frame, text="終了日").pack(side="left", padx=5)
    end_date_widget = DateEntry(control_frame, width=12, background='darkblue', foreground='white', date_pattern='yyyy-mm-dd')
    end_date_widget.pack(side="left", padx=5)

    search_button = ctk.CTkButton(control_frame, text="検索", command=apply_custom_filter)
    search_button.pack(side="left", padx=5)

    frame = ctk.CTkFrame(tab_frame)
    frame.pack(fill="both", expand=True, padx=10, pady=10)

    vsb = ttk.Scrollbar(frame, orient="vertical")
    hsb = ttk.Scrollbar(frame, orient="horizontal")

    overview_table = ttk.Treeview(frame, show="headings", yscrollcommand=vsb.set, xscrollcommand=hsb.set)
    vsb.config(command=overview_table.yview)
    hsb.config(command=overview_table.xview)

    overview_table.bind("<Double-1>", on_column_double_click)

    overview_table.pack(fill="both", expand=True)
    vsb.pack(side="right", fill="y")
    hsb.pack(side="bottom", fill="x")

    overview_total_label = ctk.CTkLabel(tab_frame, text="売上合計: 0 円", font=("Arial", 16))
    overview_total_label.pack(pady=5)

    refresh_overview_table()

# --- 月別売上タブ設定 ---
def setup_monthly_tab(tab_frame):
    global monthly_table, monthly_total_label

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

    monthly_total_label = ctk.CTkLabel(tab_frame, text="月別売上ビュー（データ未取得）", font=("Arial", 16))
    monthly_total_label.pack(pady=5)

# --- 年度別売上タブ設定 ---
def setup_yearly_tab(tab_frame):
    global yearly_table, yearly_total_label

    frame = ctk.CTkFrame(tab_frame)
    frame.pack(fill="both", expand=True, padx=10, pady=10)

    vsb = ttk.Scrollbar(frame, orient="vertical")
    hsb = ttk.Scrollbar(frame, orient="horizontal")

    yearly_table = ttk.Treeview(frame, show="headings", yscrollcommand=vsb.set, xscrollcommand=hsb.set)
    vsb.config(command=yearly_table.yview)
    hsb.config(command=yearly_table.xview)

    yearly_table.pack(fill="both", expand=True)
    vsb.pack(side="right", fill="y")
    hsb.pack(side="bottom", fill="x")

    yearly_total_label = ctk.CTkLabel(tab_frame, text="年度別売上ビュー（データ未取得）", font=("Arial", 16))
    yearly_total_label.pack(pady=5)

# --- カスタムフィルター検索 ---
def apply_custom_filter():
    start = start_date_widget.get_date()
    end = end_date_widget.get_date()
    refresh_overview_table(start, end)

# --- 売上一覧更新 ---
def refresh_overview_table(start_date=None, end_date=None):
    global products_df, date_column_selector

    if products_df is None or not os.path.exists('data/sales.csv'):
        return

    sales_df = pd.read_csv('data/sales.csv')
    joined = pd.merge(sales_df, products_df, on="商品ID", how="left")

    date_columns = detect_date_columns(joined)
    if date_columns:
        date_column_selector.configure(values=date_columns)
        date_column_var.set(date_columns[0])

    selected_date_column = date_column_var.get()

    if selected_date_column in joined.columns:
        joined[selected_date_column] = pd.to_datetime(joined[selected_date_column], errors='coerce')

    if start_date and end_date and selected_date_column in joined.columns:
        joined = joined[(joined[selected_date_column] >= pd.to_datetime(start_date)) &
                        (joined[selected_date_column] <= pd.to_datetime(end_date))]

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

# --- 編集モード起動(仮) ---
def launch_edit_mode():
    pass

# --- 起動 ---
if __name__ == "__main__":
    load_products_master()
    launch_view_mode()
