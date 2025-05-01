import tkinter as tk
import datetime 
import customtkinter as ctk
from tkinter import ttk, filedialog, messagebox
from tkcalendar import DateEntry
import pandas as pd
import os

# --- フォント設定 ---
default_font = ("Arial", 14)
title_font = ("Arial", 18, "bold")
# --- スケーリング設定 ---
SCALING = 1.8  #

# --- グローバル変数 ---
original_df = None
joined_df = None
products_df = None
overview_table = None
overview_total_label = None
monthly_table = None
monthly_total_label = None
yearly_table = None
yearly_total_label = None
start_date_widget = None
end_date_widget = None
date_column_var = None
date_column_selector = None
sort_states = {}

# --- 商品マスター読み込み ---
def load_products_master():
    global products_df
    try:
        products_df = pd.read_csv('data/products.csv')
        categories_df = pd.read_csv('data/categories.csv')
        products_df = pd.merge(products_df, categories_df, on="カテゴリID", how="left")
    except Exception as e:
        products_df = None
        print(f"商品マスター読み込みエラー: {e}")

# --- ビューモード起動 ---
def launch_view_mode():
    global view_window

    view_window = ctk.CTk()
    view_window.title("売上ダッシュボード")
    view_window.geometry("1400x900")
    view_window.tk.call("tk", "scaling", SCALING)

    style = ttk.Style()
    style.theme_use('default')
    style.configure("Custom.Treeview", font=("Arial", 20), rowheight=100)
    style.configure("Custom.Treeview.Heading", font=("Arial", 15, "bold"))

    edit_button = ctk.CTkButton(view_window, text="編集モードへ", font=default_font, command=launch_edit_mode)
    edit_button.pack(side="top", anchor="ne", padx=10, pady=10)

    tabview = ctk.CTkTabview(view_window)
    tabview.pack(fill="both", expand=True, padx=10, pady=10)

    tab_overview = tabview.add("売上一覧")
    tab_monthly = tabview.add("月別売上")
    tab_yearly = tabview.add("年度別売上")

    setup_overview_tab(tab_overview)
    setup_monthly_tab(tab_monthly)
    setup_yearly_tab(tab_yearly)

    refresh_monthly_table()
    refresh_yearly_table()

    view_window.mainloop()

# --- 検索リセットボタン ---
def reset_date_filter():
    # 1. 顧客名・カテゴリを初期化（"すべて" に戻す）
    customer_filter_var.set("すべて")
    category_filter_var.set("すべて")

    # 2. 日付も初期化（今期開始日～今日）
    start_date_widget.set_date(default_start_date)
    end_date_widget.set_date(default_end_date)

    # 3. 表を更新（すべてのリセット状態を反映）
    refresh_overview_table()



# --- 売上一覧タブ設定 ---
def setup_overview_tab(tab_frame):
    import datetime

    global overview_table, overview_total_label
    global start_date_widget, end_date_widget, date_column_var, date_column_selector
    global customer_filter_var, category_filter_var
    global default_start_date, default_end_date

    # --- 顧客・カテゴリの値をCSVから読み込み ---
    try:
        sales_df = pd.read_csv('data/sales.csv')
        sales_df["販売日"] = pd.to_datetime(sales_df["販売日"], errors='coerce')
        customer_list = ["すべて"] + sorted(sales_df["顧客名"].dropna().unique().tolist())
    except:
        customer_list = ["すべて"]

    try:
        categories_df = pd.read_csv('data/categories.csv')
        category_list = ["すべて"] + sorted(categories_df["カテゴリ名"].dropna().unique().tolist())
    except:
        category_list = ["すべて"]

    # --- フィルター行 ---
    control_frame = ctk.CTkFrame(tab_frame)
    control_frame.pack(fill="x", padx=30, pady=5)

    # --- 今日の日付＆今期の開始日 ---
    today = datetime.date.today()
    if today.month >= 4:
        default_start_date = datetime.date(today.year, 4, 1)
    else:
        default_start_date = datetime.date(today.year - 1, 4, 1)
    default_end_date = today

    # --- 「期間（販売日）」ラベル ---
    ctk.CTkLabel(control_frame, text="期間（販売日）", font=default_font).pack(side="left", padx=5)

    # 開始日
    start_date_widget = DateEntry(control_frame, width=int(9 * SCALING), background='darkblue', foreground='white', date_pattern='yyyy-mm-dd')
    start_date_widget.set_date(default_start_date)
    start_date_widget.pack(side="left", padx=5)

    # 終了日
    end_date_widget = DateEntry(control_frame, width=int(9 * SCALING), background='darkblue', foreground='white', date_pattern='yyyy-mm-dd')
    end_date_widget.set_date(default_end_date)
    end_date_widget.pack(side="left", padx=5)

    # 顧客フィルター
    ctk.CTkLabel(control_frame, text="顧客名", font=default_font).pack(side="left", padx=5)
    customer_filter_var = tk.StringVar(value="すべて")
    customer_filter_selector = ctk.CTkOptionMenu(control_frame, variable=customer_filter_var, values=customer_list)
    customer_filter_selector.pack(side="left", padx=5)

    # カテゴリフィルター
    ctk.CTkLabel(control_frame, text="カテゴリ", font=default_font).pack(side="left", padx=5)
    category_filter_var = tk.StringVar(value="すべて")
    category_filter_selector = ctk.CTkOptionMenu(control_frame, variable=category_filter_var, values=category_list)
    category_filter_selector.pack(side="left", padx=5)

    # 検索・リセットボタン
    button_frame = ctk.CTkFrame(control_frame)
    button_frame.pack(side="right", padx=10)

    search_button = ctk.CTkButton(button_frame, text="検索", font=default_font, command=apply_custom_filter)
    search_button.pack(side="left", padx=5)

    reset_button = ctk.CTkButton(button_frame, text="リセット", font=default_font, command=reset_date_filter)
    reset_button.pack(side="left", padx=5)

    # --- 表エリア ---
    table_frame = ctk.CTkFrame(tab_frame)
    table_frame.pack(fill="both", expand=True, padx=10, pady=10)

    vsb = ttk.Scrollbar(table_frame, orient="vertical")
    hsb = ttk.Scrollbar(table_frame, orient="horizontal")

    overview_table = ttk.Treeview(
        table_frame, show="headings", style="Custom.Treeview",
        yscrollcommand=vsb.set, xscrollcommand=hsb.set
    )
    vsb.config(command=overview_table.yview)
    hsb.config(command=overview_table.xview)

    overview_table.pack(fill="both", expand=True)
    vsb.pack(side="right", fill="y")
    hsb.pack(side="bottom", fill="x")

    overview_total_label = ctk.CTkLabel(tab_frame, text="売上合計: 0 円", font=title_font)
    overview_total_label.pack(pady=5)

    refresh_overview_table()


# --- 月別売上タブ設定 ---
def setup_monthly_tab(tab_frame):
    global monthly_table, monthly_total_label

    frame = ctk.CTkFrame(tab_frame)
    frame.pack(fill="both", expand=True, padx=10, pady=10)

    vsb = ttk.Scrollbar(frame, orient="vertical")
    hsb = ttk.Scrollbar(frame, orient="horizontal")

    monthly_table = ttk.Treeview(frame, show="headings", style="Custom.Treeview", yscrollcommand=vsb.set, xscrollcommand=hsb.set)
    vsb.config(command=monthly_table.yview)
    hsb.config(command=monthly_table.xview)

    monthly_table.pack(fill="both", expand=True)
    vsb.pack(side="right", fill="y")
    hsb.pack(side="bottom", fill="x")

    monthly_total_label = ctk.CTkLabel(tab_frame, text="月別売上ビュー", font=title_font)
    monthly_total_label.pack(pady=5)

# --- 年度別売上タブ設定 ---
def setup_yearly_tab(tab_frame):
    global yearly_table, yearly_total_label

    frame = ctk.CTkFrame(tab_frame)
    frame.pack(fill="both", expand=True, padx=10, pady=10)

    vsb = ttk.Scrollbar(frame, orient="vertical")
    hsb = ttk.Scrollbar(frame, orient="horizontal")

    yearly_table = ttk.Treeview(frame, show="headings", style="Custom.Treeview", yscrollcommand=vsb.set, xscrollcommand=hsb.set)
    vsb.config(command=yearly_table.yview)
    hsb.config(command=yearly_table.xview)

    yearly_table.pack(fill="both", expand=True)
    vsb.pack(side="right", fill="y")
    hsb.pack(side="bottom", fill="x")

    yearly_total_label = ctk.CTkLabel(tab_frame, text="年度別売上ビュー", font=title_font)
    yearly_total_label.pack(pady=5)

# --- データ更新 ---
def refresh_overview_table(start_date=None, end_date=None):
    if products_df is None or not os.path.exists('data/sales.csv'):
        return

    sales_df = pd.read_csv('data/sales.csv')
    joined = pd.merge(sales_df, products_df, on="商品ID", how="left")

    selected_date_column = "販売日"

    if selected_date_column in joined.columns:
        joined[selected_date_column] = pd.to_datetime(joined[selected_date_column], errors='coerce')

    # --- 日付で絞り込み ---
    if start_date and end_date and selected_date_column in joined.columns:
        joined = joined[(joined[selected_date_column] >= pd.to_datetime(start_date)) &
                        (joined[selected_date_column] <= pd.to_datetime(end_date))]

    # --- 顧客名フィルター ---
    selected_customer = customer_filter_var.get()
    if selected_customer != "すべて":
        joined = joined[joined["顧客名"] == selected_customer]

    # --- カテゴリ名フィルター ---
    selected_category = category_filter_var.get()
    if selected_category != "すべて":
        joined = joined[joined["カテゴリ名"] == selected_category]

    # --- 表更新 ---
    overview_table.delete(*overview_table.get_children())
    columns = ["販売日", "顧客名", "カテゴリ名", "商品名", "数量", "金額", "更新日"]
    overview_table.configure(columns=columns)

    for col in columns:
        overview_table.heading(col, text=col)

    for _, row in joined.iterrows():
        values = []
        for col in columns:
            val = row.get(col, "")
            if isinstance(val, pd.Timestamp):
                val = val.strftime("%Y-%m-%d")
            values.append(val)
        overview_table.insert("", "end", values=values)

    overview_table.update_idletasks()

    def get_visual_length(text):
        return sum(2 if ord(c) > 127 else 1 for c in str(text))

    custom_widths = {
        "販売日": 130 * SCALING,
        "更新日": 160 * SCALING,
        "商品名": 250 * SCALING,
        "顧客名": 200 * SCALING,
        "カテゴリ名": 150 * SCALING,
    }

    for col in columns:
        max_visual_len = max(
            [get_visual_length(overview_table.set(item, col)) for item in overview_table.get_children()] + [len(col)]
        )
        auto_width = max(max_visual_len * 7 * SCALING, 100 * SCALING)
        width_px = custom_widths.get(col, min(auto_width, 350 * SCALING))
        overview_table.column(col, width=int(width_px), anchor="center", stretch=False)

    joined["金額"] = pd.to_numeric(joined["金額"], errors='coerce')
    total = joined["金額"].sum()
    overview_total_label.configure(text=f"売上合計: {int(total)} 円")


def refresh_monthly_table():
    if products_df is None or not os.path.exists('data/sales.csv'):
        return

    sales_df = pd.read_csv('data/sales.csv')
    joined = pd.merge(sales_df, products_df, on="商品ID", how="left")
    date_col = detect_date_columns(joined)[0]

    joined[date_col] = pd.to_datetime(joined[date_col], errors='coerce')
    joined['年月'] = joined[date_col].dt.to_period('M')
    monthly_summary = joined.groupby('年月')['金額'].sum().reset_index()
    monthly_summary['年月'] = monthly_summary['年月'].astype(str)

    monthly_table.delete(*monthly_table.get_children())
    monthly_table.configure(columns=["年月", "売上合計"])

    for col in ["年月", "売上合計"]:
        monthly_table.heading(col, text=col)
        monthly_table.column(col, width=200, anchor="center", stretch=False)

    for _, row in monthly_summary.iterrows():
        monthly_table.insert("", "end", values=[row["年月"], int(row["金額"])])

    monthly_total_label.configure(text=f"月別売上合計: {int(monthly_summary['金額'].sum())} 円")

def refresh_yearly_table():
    if products_df is None or not os.path.exists('data/sales.csv'):
        return

    sales_df = pd.read_csv('data/sales.csv')
    joined = pd.merge(sales_df, products_df, on="商品ID", how="left")
    date_col = detect_date_columns(joined)[0]

    joined[date_col] = pd.to_datetime(joined[date_col], errors='coerce')
    joined['年度'] = joined[date_col].dt.year
    yearly_summary = joined.groupby('年度')['金額'].sum().reset_index()

    yearly_table.delete(*yearly_table.get_children())
    yearly_table.configure(columns=["年度", "売上合計"])

    for col in ["年度", "売上合計"]:
        yearly_table.heading(col, text=col)
        yearly_table.column(col, width=200, anchor="center", stretch=False)

    for _, row in yearly_summary.iterrows():
        yearly_table.insert("", "end", values=[row["年度"], int(row["金額"])])

    yearly_total_label.configure(text=f"年度別売上合計: {int(yearly_summary['金額'].sum())} 円")

# --- 販売日カラム自動検出 ---
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

# --- カスタムフィルター検索 ---
def apply_custom_filter():
    start = start_date_widget.get_date()
    end = end_date_widget.get_date()
    refresh_overview_table(start, end)

# --- 編集モード（選択行編集）---
def launch_edit_mode():
    selected_item = overview_table.focus()
    if not selected_item:
        messagebox.showwarning("警告", "編集する行を選択してください。")
        return

    selected_values = overview_table.item(selected_item, "values")
    if not selected_values:
        return

    edit_window = ctk.CTkToplevel()
    edit_window.title("データ編集")
    edit_window.geometry("500x500")

    labels = ["販売日", "顧客名", "カテゴリ名", "商品名", "数量", "金額", "更新日"]
    entry_vars = []

    def update_price(*_):
        try:
            商品名 = entry_vars[3].get()
            数量 = int(entry_vars[4].get())
            product_row = products_df[products_df["商品名"] == 商品名]
            単価 = int(product_row["単価"].values[0])
            entry_vars[5].set(str(数量 * 単価))  # 金額に代入
        except:
            pass  # 落ちないようにする

    for idx, label in enumerate(labels):
        frame = ctk.CTkFrame(edit_window)
        frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(frame, text=label, width=120, anchor="w", font=default_font).pack(side="left")

        var = tk.StringVar(value=selected_values[idx])
        state = "disabled" if label == "更新日" else "normal"
        entry = ctk.CTkEntry(frame, textvariable=var, font=default_font, state=state)
        entry.pack(side="left", fill="x", expand=True)
        entry_vars.append(var)

        if label == "数量":
            var.trace_add("write", update_price)

    def save_changes():
        # 更新日を今日の日付に自動設定
        today_str = datetime.date.today().strftime("%Y-%m-%d")
        entry_vars[6].set(today_str)

        new_values = [var.get() for var in entry_vars]
        overview_table.item(selected_item, values=new_values)

        # 合計再計算
        all_values = [overview_table.item(cid)["values"] for cid in overview_table.get_children()]
        df = pd.DataFrame(all_values, columns=["販売日", "顧客名", "カテゴリ名", "商品名", "数量", "金額", "更新日"])
        df["金額"] = pd.to_numeric(df["金額"], errors="coerce")
        overview_total_label.configure(text=f"売上合計: {int(df['金額'].sum())} 円")

        edit_window.destroy()

    save_button = ctk.CTkButton(edit_window, text="保存", font=default_font, command=save_changes)
    save_button.pack(pady=20)



# --- 起動 ---
if __name__ == "__main__":
    load_products_master()
    launch_view_mode()
