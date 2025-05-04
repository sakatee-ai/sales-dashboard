
import tkinter as tk
import pandas as pd
from tkinter import ttk
from tkcalendar import DateEntry
import datetime
import customtkinter as ctk
from utils import SALES_CSV, CATEGORIES_CSV

overview_table = None
overview_total_label = None
start_date_widget = None
end_date_widget = None
customer_filter_var = None
category_filter_var = None
default_start_date = None
default_end_date = None

def refresh_overview_table(products_df):
    import os
    try:
        sales_df = pd.read_csv(SALES_CSV)
        joined = pd.merge(sales_df, products_df, on="商品ID", how="left")
        categories_df = pd.read_csv(CATEGORIES_CSV)
        joined = pd.merge(joined, categories_df, on="カテゴリID", how="left")
        joined["販売日"] = pd.to_datetime(joined["販売日"], errors="coerce")
    except Exception as e:
        print("読み込みエラー:", e)
        return

    start = start_date_widget.get_date()
    end = end_date_widget.get_date()
    joined = joined[(joined["販売日"] >= pd.to_datetime(start)) & (joined["販売日"] <= pd.to_datetime(end))]

    if customer_filter_var.get() != "すべて":
        joined = joined[joined["顧客名"] == customer_filter_var.get()]
    if category_filter_var.get() != "すべて":
        joined = joined[joined["カテゴリ名"] == category_filter_var.get()]

    overview_table.delete(*overview_table.get_children())
    columns = ["販売日", "顧客名", "カテゴリ名", "商品名", "数量", "金額", "更新日"]
    overview_table.configure(columns=columns)
    for col in columns:
        overview_table.heading(col, text=col)

    for _, row in joined.iterrows():
        values = [row.get(col, "") for col in columns]
        overview_table.insert("", "end", values=values)

    total = pd.to_numeric(joined["金額"], errors="coerce").sum()
    overview_total_label.configure(text=f"売上合計: {int(total)} 円")

def reset_filters(products_df):
    customer_filter_var.set("すべて")
    category_filter_var.set("すべて")
    start_date_widget.set_date(default_start_date)
    end_date_widget.set_date(default_end_date)
    refresh_overview_table(products_df)

def setup_overview_tab(tab_frame, products_df):
    global overview_table, overview_total_label
    global start_date_widget, end_date_widget
    global customer_filter_var, category_filter_var
    global default_start_date, default_end_date

    try:
        sales_df = pd.read_csv("data/sales.csv")
        sales_df["販売日"] = pd.to_datetime(sales_df["販売日"], errors="coerce")
        customer_list = ["すべて"] + sorted(sales_df["顧客名"].dropna().unique().tolist())
    except:
        customer_list = ["すべて"]

    try:
        categories_df = pd.read_csv("data/categories.csv")
        category_list = ["すべて"] + sorted(categories_df["カテゴリ名"].dropna().unique().tolist())
    except:
        category_list = ["すべて"]

    today = datetime.date.today()
    if today.month >= 4:
        default_start_date = datetime.date(today.year, 4, 1)
    else:
        default_start_date = datetime.date(today.year - 1, 4, 1)
    default_end_date = today

    filter_frame = ctk.CTkFrame(tab_frame)
    filter_frame.pack(fill="x", padx=10, pady=10)

    ctk.CTkLabel(filter_frame, text="期間（販売日）").pack(side="left", padx=5)

    start_date_widget = DateEntry(filter_frame, width=12, date_pattern='yyyy-mm-dd')
    start_date_widget.set_date(default_start_date)
    start_date_widget.pack(side="left", padx=5)

    end_date_widget = DateEntry(filter_frame, width=12, date_pattern='yyyy-mm-dd')
    end_date_widget.set_date(default_end_date)
    end_date_widget.pack(side="left", padx=5)

    ctk.CTkLabel(filter_frame, text="顧客名").pack(side="left", padx=5)
    customer_filter_var = tk.StringVar(value="すべて")
    customer_menu = ctk.CTkOptionMenu(filter_frame, variable=customer_filter_var, values=customer_list)
    customer_menu.pack(side="left", padx=5)

    ctk.CTkLabel(filter_frame, text="カテゴリ").pack(side="left", padx=5)
    category_filter_var = tk.StringVar(value="すべて")
    category_menu = ctk.CTkOptionMenu(filter_frame, variable=category_filter_var, values=category_list)
    category_menu.pack(side="left", padx=5)

    search_button = ctk.CTkButton(filter_frame, text="検索", command=lambda: refresh_overview_table(products_df))
    search_button.pack(side="right", padx=5)

    reset_button = ctk.CTkButton(filter_frame, text="リセット", command=lambda: reset_filters(products_df))
    reset_button.pack(side="right", padx=5)

    table_frame = ctk.CTkFrame(tab_frame)
    table_frame.pack(fill="both", expand=True, padx=10, pady=10)

    vsb = ttk.Scrollbar(table_frame, orient="vertical")
    hsb = ttk.Scrollbar(table_frame, orient="horizontal")

    overview_table = ttk.Treeview(table_frame, show="headings", yscrollcommand=vsb.set, xscrollcommand=hsb.set)
    vsb.config(command=overview_table.yview)
    hsb.config(command=overview_table.xview)
    overview_table.pack(fill="both", expand=True)
    vsb.pack(side="right", fill="y")
    hsb.pack(side="bottom", fill="x")

    overview_total_label = ctk.CTkLabel(tab_frame, text="売上合計: 0 円")
    overview_total_label.pack(pady=5)

    refresh_overview_table(products_df)
