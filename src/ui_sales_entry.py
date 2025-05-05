import customtkinter as ctk
from tkinter import ttk
from tkcalendar import DateEntry
import pandas as pd
import datetime
import os
from utils import get_products_df, SALES_CSV

def setup_sales_entry_tab(tab_frame, refresh_callback):
    products_df = get_products_df()

    # 商品情報（辞書に変換）
    product_info = products_df.set_index("商品名")[["商品ID", "単価", "カテゴリ名"]].to_dict(orient="index")

    def update_total(*args):
        name = product_var.get()
        info = product_info.get(name, {})
        try:
            quantity = int(quantity_entry.get())
            total = int(info.get("単価", 0)) * quantity
            total_label.configure(text=f"金額: {total} 円")
        except ValueError:
            total_label.configure(text="金額: - 円")

    def update_product_info(*args):
        name = product_var.get()
        info = product_info.get(name, {})
        unit_price_label.configure(text=f"単価: {info.get('単価', '-'):,} 円")
        category_label.configure(text=f"カテゴリ: {info.get('カテゴリ名', '-')}")
        update_total()

    def save_sales():
        name = product_var.get()
        info = product_info.get(name, {})
        if not info:
            print("⚠️ 商品情報が見つかりません")
            return

        try:
            sales_data = {
                "販売日": date_entry.get_date().strftime("%Y-%m-%d"),
                "顧客名": customer_entry.get().strip(),
                "商品ID": info["商品ID"],
                "数量": int(quantity_entry.get()),
                "金額": int(info["単価"]) * int(quantity_entry.get()),
                "更新日": datetime.date.today().strftime("%Y-%m-%d")
            }
        except Exception as e:
            print("❌ 入力エラー:", e)
            return

        try:
            df = pd.DataFrame([sales_data])
            if not os.path.exists(SALES_CSV):
                df.to_csv(SALES_CSV, index=False, encoding="utf-8-sig")
            else:
                df.to_csv(SALES_CSV, mode="a", index=False, header=False, encoding="utf-8-sig")

            print("✅ 保存完了:", sales_data)
            customer_entry.delete(0, "end")
            quantity_entry.delete(0, "end")
            total_label.configure(text="金額: - 円")

            # 売上一覧のフィルターをリセットしてから更新
            import ui_overview
            ui_overview.customer_filter_var.set("すべて")
            ui_overview.category_filter_var.set("すべて")
            ui_overview.start_date_widget.set_date(ui_overview.default_start_date)
            ui_overview.end_date_widget.set_date(ui_overview.default_end_date)

            refresh_callback()

        except Exception as e:
            print("❌ 保存エラー:", e)

    # --- UIパーツ ---
    form_frame = ctk.CTkFrame(tab_frame)
    form_frame.pack(padx=20, pady=20, fill="x")

    ctk.CTkLabel(form_frame, text="販売日").grid(row=0, column=0, sticky="w")
    date_entry = DateEntry(form_frame, date_pattern="yyyy-mm-dd")
    date_entry.set_date(datetime.date.today())
    date_entry.grid(row=0, column=1, pady=5)

    ctk.CTkLabel(form_frame, text="顧客名").grid(row=1, column=0, sticky="w")
    customer_entry = ctk.CTkEntry(form_frame)
    customer_entry.grid(row=1, column=1, pady=5)

    ctk.CTkLabel(form_frame, text="商品名").grid(row=2, column=0, sticky="w")
    product_names = products_df["商品名"].tolist()
    product_var = ctk.StringVar(value=product_names[0])
    product_menu = ctk.CTkOptionMenu(form_frame, variable=product_var, values=product_names)
    product_menu.grid(row=2, column=1, pady=5)

    ctk.CTkLabel(form_frame, text="数量").grid(row=3, column=0, sticky="w")
    quantity_entry = ctk.CTkEntry(form_frame)
    quantity_entry.grid(row=3, column=1, pady=5)

    unit_price_label = ctk.CTkLabel(form_frame, text="単価: - 円")
    category_label = ctk.CTkLabel(form_frame, text="カテゴリ: -")
    total_label = ctk.CTkLabel(form_frame, text="金額: - 円")
    unit_price_label.grid(row=4, column=0, columnspan=2, sticky="w", pady=5)
    category_label.grid(row=5, column=0, columnspan=2, sticky="w", pady=5)
    total_label.grid(row=6, column=0, columnspan=2, sticky="w", pady=5)

    save_button = ctk.CTkButton(form_frame, text="保存", command=save_sales)
    save_button.grid(row=7, column=0, columnspan=2, pady=10)

    # 初期反映
    product_var.trace_add("write", update_product_info)
    quantity_entry.bind("<KeyRelease>", update_total)
    update_product_info()
