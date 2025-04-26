import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import csv
import os
import pandas as pd

# Treeviewスタイルをダークテーマに
style = ttk.Style()
style.theme_use("clam")
style.configure("Treeview",
    background="#333333",
    foreground="white",
    rowheight=25,
    fieldbackground="#333333",
    bordercolor="#444444",
    borderwidth=1)
style.configure("Treeview.Heading",
    background="#444444",
    foreground="white",
    bordercolor="#444444",
    borderwidth=1)

original_df = None
filter_entries = []
sort_states = {}

# ディレクトリツリーを構築
def build_tree_from_directory(tree, parent, path):
    for entry in sorted(os.listdir(path)):
        full_path = os.path.join(path, entry)
        if os.path.isdir(full_path):
            node = tree.insert(parent, "end", text=entry, open=False, values=[full_path])
            build_tree_from_directory(tree, node, full_path)
        elif entry.endswith(".csv"):
            tree.insert(parent, "end", text=entry, values=[full_path])

# CSV選択時の処理
def on_item_click(event, tree, table_widget):
    global original_df
    selected_item = tree.focus()
    full_path = tree.item(selected_item, "values")[0] if tree.item(selected_item, "values") else ""

    if full_path.endswith(".csv") and os.path.isfile(full_path):
        try:
            df = pd.read_csv(full_path)
            original_df = df.copy()
            if not df.empty:
                update_filter_inputs(df)
                display_table(df, table_widget)
        except Exception as e:
            messagebox.showerror("エラー", f"読み込み失敗: {e}")

# テーブル表示
def display_table(df, table_widget):
    table_widget.delete(*table_widget.get_children())
    columns = ["選択"] + list(df.columns)
    table_widget.configure(columns=columns, show="headings")

    for col in columns:
        table_widget.heading(col, text=col)
        table_widget.column(col, width=100 if col == "選択" else 150, anchor="center", stretch=False)

    for _, row in df.iterrows():
        values = ["☐"] + row.tolist()
        table_widget.insert("", "end", values=values)

# CSV保存
def save_table_to_csv(table, file_path):
    if not file_path:
        messagebox.showwarning("保存できません", "ファイルが開かれていません。")
        return
    try:
        with open(file_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            headers = table["columns"][1:]
            writer.writerow(headers)
            for row_id in table.get_children():
                values = table.item(row_id, "values")[1:]
                writer.writerow(values)
        messagebox.showinfo("保存完了", f"{file_path} に保存しました。")
    except Exception as e:
        messagebox.showerror("保存エラー", str(e))

# フィルター適用
def apply_filters(table_widget):
    global original_df, filter_entries
    if original_df is None:
        return
    df_filtered = original_df.copy()
    for col, widget in zip(original_df.columns, filter_entries):
        val = widget.get().strip()
        if val and val != "すべて":
            df_filtered = df_filtered[df_filtered[col].astype(str).str.contains(val, na=False)]
    display_table(df_filtered, table_widget)

# フィルター欄更新
def update_filter_inputs(df):
    global filter_entries
    for widget in filter_entries:
        widget.destroy()
    filter_entries.clear()

    dummy_label = ctk.CTkLabel(filter_row, text="選択")
    dummy_label.grid(row=0, column=0, padx=2, pady=2)

    for i, col in enumerate(df.columns):
        values = ["すべて"] + sorted(df[col].dropna().astype(str).unique())
        var = ctk.StringVar()  # 修正ポイント！！！！
        combo = ctk.CTkOptionMenu(filter_row, variable=var, values=values, command=lambda e: apply_filters(table))
        combo.grid(row=0, column=i+1, padx=2, pady=2)
        filter_entries.append(combo)

# カラムダブルクリック時のソート
def on_column_double_click(event):
    region = table.identify("region", event.x, event.y)
    if region == "heading":
        col_id = table.identify_column(event.x)
        col_index = int(col_id.replace("#", "")) - 1
        if col_index == 0:
            return
        column = table["columns"][col_index]
        sort_table_by_column(column)

# カラム名でソート
def sort_table_by_column(column):
    global original_df, sort_states
    if original_df is None or original_df.empty:
        return
    ascending = sort_states.get(column, True)
    sort_states[column] = not ascending
    sorted_df = original_df.sort_values(by=column, ascending=ascending)
    display_table(sorted_df, table)

# 保存ボタン
def add_save_buttons(parent_frame, table, get_current_path, set_current_path):
    button_frame = ctk.CTkFrame(parent_frame)
    button_frame.pack(fill="x", padx=10, pady=5)

    ctk.CTkButton(button_frame, text="保存", command=lambda: save_table_to_csv(table, get_current_path())).pack(side="left", padx=5)
    ctk.CTkButton(button_frame, text="名前をつけて保存", command=lambda: save_as_dialog(table, set_current_path)).pack(side="left", padx=5)

# 名前を付けて保存
def save_as_dialog(table, set_current_path):
    path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSVファイル", "*.csv")])
    if path:
        set_current_path(path)
        save_table_to_csv(table, path)

# メインUI作成
def create_ui():
    global filter_row, table

    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    window = ctk.CTk()
    window.title("CSV表ビューア")
    window.geometry("1200x800")

    main_frame = ctk.CTkFrame(window)
    main_frame.pack(fill="both", expand=True)

    left_frame = ctk.CTkFrame(main_frame, width=250)
    left_frame.pack(side="left", fill="y")

    right_frame = ctk.CTkFrame(main_frame)
    right_frame.pack(side="left", fill="both", expand=True)

    tree = ttk.Treeview(left_frame)
    tree.pack(fill="both", expand=True)
    tree.column("#0", width=220)

    root_path = "data"
    if os.path.exists(root_path):
        root_node = tree.insert("", "end", text=os.path.basename(root_path), open=True, values=[root_path])
        build_tree_from_directory(tree, root_node, root_path)
    else:
        messagebox.showwarning("フォルダなし", f"{root_path} が存在しません")

    filter_row = ctk.CTkFrame(right_frame)
    filter_row.pack(fill="x", padx=10, pady=3)

    vsb = ttk.Scrollbar(right_frame, orient="vertical")
    hsb = ttk.Scrollbar(right_frame, orient="horizontal")

    global table
    table = ttk.Treeview(right_frame, show="headings", yscrollcommand=vsb.set, xscrollcommand=hsb.set)
    vsb.config(command=table.yview)
    hsb.config(command=table.xview)

    table.pack(fill="both", expand=True)
    vsb.pack(side="right", fill="y")
    hsb.pack(side="bottom", fill="x")
    table.bind("<Double-1>", on_column_double_click)

    global current_file_path
    current_file_path = {"path": None}

    def on_tree_select_wrapper(event):
        selected_item = tree.focus()
        file_path = tree.item(selected_item, "values")[0] if tree.item(selected_item, "values") else ""
        current_file_path["path"] = file_path
        on_item_click(event, tree, table)

    tree.bind("<<TreeviewSelect>>", on_tree_select_wrapper)

    add_save_buttons(right_frame, table, lambda: current_file_path["path"], lambda p: current_file_path.update({"path": p}))

    window.mainloop()

if __name__ == "__main__":
    create_ui()
