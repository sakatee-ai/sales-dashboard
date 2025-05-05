import customtkinter as ctk
from tkinter import ttk
import pandas as pd
from utils import CATEGORIES_CSV
import tkinter as tk
from utils import reload_products_df
from ui_overview import refresh_overview_table


category_table = None

def setup_category_tab(tab_frame, products_df):
    global category_table

    frame = ctk.CTkFrame(tab_frame)
    frame.pack(fill="both", expand=True, padx=10, pady=10)

    category_table = ttk.Treeview(frame, columns=["カテゴリID", "カテゴリ名"], show="headings", selectmode="browse")
    category_table.heading("カテゴリID", text="カテゴリID")
    category_table.heading("カテゴリ名", text="カテゴリ名")

    # 🌟 見やすい幅＋中央寄せ
    category_table.column("カテゴリID", width=120, anchor="center", stretch=False)
    category_table.column("カテゴリ名", width=250, anchor="center", stretch=False)

    vsb = ttk.Scrollbar(frame, orient="vertical", command=category_table.yview)
    category_table.configure(yscrollcommand=vsb.set)
    vsb.pack(side="right", fill="y")
    category_table.pack(fill="both", expand=True)

    load_categories()

    # 🌟 編集用エントリボックスを1つ使い回し
    editor = tk.Entry(frame)
    editor.place_forget()

    def on_double_click(event):
        item_id = category_table.identify_row(event.y)
        column = category_table.identify_column(event.x)
        if not item_id or column != "#2":  # 「カテゴリ名」列だけ編集許可
            return

        x, y, width, height = category_table.bbox(item_id, column)
        value = category_table.set(item_id, column)

        editor.place(x=x, y=y, width=width, height=height)
        editor.delete(0, tk.END)
        editor.insert(0, value)
        editor.focus()

        def save_edit(event):
            new_value = editor.get()
            category_table.set(item_id, column, new_value)
            editor.place_forget()

        editor.bind("<Return>", save_edit)
        editor.bind("<FocusOut>", lambda e: editor.place_forget())

    category_table.bind("<Double-1>", on_double_click)

    # 保存ボタン
    save_button = ctk.CTkButton(tab_frame, text="保存", command=save_categories)
    save_button.pack(pady=5)
def load_categories():
    category_table.delete(*category_table.get_children())
    try:
        df = pd.read_csv(CATEGORIES_CSV)
        for _, row in df.iterrows():
            category_table.insert("", "end", values=[row["カテゴリID"], row["カテゴリ名"]])
    except Exception as e:
        print("カテゴリ読み込みエラー:", e)

def save_categories():
    try:
        rows = []
        for child in category_table.get_children():
            values = category_table.item(child)["values"]
            rows.append(values)
        df = pd.DataFrame(rows, columns=["カテゴリID", "カテゴリ名"])
        df.to_csv(CATEGORIES_CSV, index=False, encoding="utf-8-sig")
        print("カテゴリ保存完了")
        reload_products_df()
        refresh_overview_table()

        # 🌟 再読み込み＋反映
        reload_products_df()
        refresh_overview_table()

    except Exception as e:
        print("カテゴリ保存エラー:", e)