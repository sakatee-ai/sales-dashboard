import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv
import os
import pandas as pd

original_df = None  # フィルター元データ
filter_entries = []  # フィルターUI
sort_states = {}  # 各列のソート状態

# ツリー構築
def build_tree_from_directory(tree, parent, path):
    for entry in sorted(os.listdir(path)):
        full_path = os.path.join(path, entry)
        if os.path.isdir(full_path):
            node = tree.insert(parent, "end", text=entry, open=False, values=[full_path])
            build_tree_from_directory(tree, node, full_path)
        else:
            if entry.endswith(".csv"):
                tree.insert(parent, "end", text=entry, values=[full_path])

# 表表示処理
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

# 表描画処理
def display_table(df, table_widget):
    table_widget.delete(*table_widget.get_children())
    columns = ["選択"] + list(df.columns)
    table_widget["columns"] = columns
    table_widget["show"] = "headings"

    for col in columns:
        table_widget.heading(col, text=col)
        if col == "選択":
            table_widget.column(col, width=60, anchor="center", stretch=False)
        else:
            table_widget.column(col, width=150, anchor="center", stretch=False)

    for _, row in df.iterrows():
        values = ["☐"] + row.tolist()
        table_widget.insert("", "end", values=values)

# 保存処理
def save_table_to_csv(table, file_path):
    if not file_path:
        messagebox.showwarning("保存先未設定", "保存先ファイルパスがありません。")
        return
    try:
        with open(file_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            headers = table["columns"][1:]  # '選択'列を除く
            writer.writerow(headers)
            for row_id in table.get_children():
                values = table.item(row_id, "values")[1:]  # '選択'列を除く
                writer.writerow(values)
        messagebox.showinfo("保存完了", f"{file_path} に保存しました。")
    except Exception as e:
        messagebox.showerror("保存エラー", str(e))

# フィルター処理
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

# フィルター入力欄を更新
def update_filter_inputs(df):
    global filter_entries
    for widget in filter_entries:
        widget.destroy()
    filter_entries.clear()

    dummy_label = ttk.Label(filter_row, text="選択")
    dummy_label.grid(row=0, column=0, padx=2, pady=2)

    for i, col in enumerate(df.columns):
        values = ["すべて"] + sorted(df[col].dropna().astype(str).unique().tolist())
        var = tk.StringVar()
        combo = ttk.Combobox(filter_row, textvariable=var, values=values, state="readonly", width=16)
        combo.current(0)
        combo.grid(row=0, column=i+1, padx=2, pady=2)
        combo.bind("<<ComboboxSelected>>", lambda e: apply_filters(table))
        filter_entries.append(combo)

# ソート処理（ダブルクリック）
def on_column_double_click(event):
    region = table.identify("region", event.x, event.y)
    if region == "heading":
        col_id = table.identify_column(event.x)
        col_index = int(col_id.replace("#", "")) - 1
        if col_index == 0:
            return  # '選択'列は無視
        column = table["columns"][col_index]
        sort_table_by_column(column)

# ヘッダーテキストクリック（右端クリックでフィルター）
def on_column_click(event):
    region = table.identify("region", event.x, event.y)
    if region == "heading":
        col_id = table.identify_column(event.x)
        col_index = int(col_id.replace("#", "")) - 1
        if col_index == 0:
            return
        col_name = table["columns"][col_index]
        col_width = table.column(col_name, option="width")
        if event.x > table.bbox("", col_id)[0] + col_width - 20:
            show_filter_popup(col_name, event.x_root, event.y_root)

# フィルターポップアップ（未実装）
def show_filter_popup(col_name, x, y):
    popup = tk.Toplevel()
    popup.geometry(f"150x200+{x}+{y}")
    popup.title(f"{col_name} フィルター")
    label = tk.Label(popup, text=f"[{col_name}]の候補をここに出す", anchor="w")
    label.pack(fill="both", expand=True, padx=5, pady=5)

# テーブルソート
def sort_table_by_column(column):
    global original_df, sort_states
    if original_df is None or original_df.empty:
        return
    ascending = sort_states.get(column, True)
    sort_states[column] = not ascending
    sorted_df = original_df.sort_values(by=column, ascending=ascending)
    display_table(sorted_df, table)

# 保存ボタン群の追加
def add_save_buttons(parent_frame, table, get_current_path, set_current_path):
    button_frame = ttk.Frame(parent_frame)
    button_frame.pack(fill="x", padx=10, pady=5)

    def save():
        path = get_current_path()
        if not path:
            messagebox.showwarning("保存できません", "ファイルが開かれていません。")
            return
        save_table_to_csv(table, path)

    def save_as():
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSVファイル", "*.csv")],
            title="名前をつけて保存"
        )
        if path:
            set_current_path(path)
            save_table_to_csv(table, path)

    ttk.Button(button_frame, text="保存", command=save).pack(side="left", padx=5)
    ttk.Button(button_frame, text="名前をつけて保存", command=save_as).pack(side="left", padx=5)

# UI本体
def create_ui():
    global filter_row, table

    window = tk.Tk()
    window.title("CSV表ビューア")
    window.geometry("1100x740")

    style = ttk.Style()
    style.configure("Treeview", font=("Arial", 11), rowheight=25)

    paned = ttk.PanedWindow(window, orient=tk.HORIZONTAL)
    paned.pack(fill="both", expand=True)

    frame_left = ttk.Frame(paned, width=250)
    frame_left.pack_propagate(False)
    tree = ttk.Treeview(frame_left)
    tree.pack(fill="both", expand=True)
    tree.column("#0", width=220)
    paned.add(frame_left)

    root_path = "data"
    if os.path.exists(root_path):
        root_node = tree.insert("", "end", text=os.path.basename(root_path), open=True, values=[root_path])
        build_tree_from_directory(tree, root_node, root_path)
    else:
        messagebox.showwarning("フォルダなし", f"{root_path} が存在しません")

    frame_right = ttk.Frame(paned)
    filter_row = ttk.Frame(frame_right)
    filter_row.pack(fill="x", padx=10, pady=3)

    vsb = ttk.Scrollbar(frame_right, orient="vertical")
    hsb = ttk.Scrollbar(frame_right, orient="horizontal")

    table = ttk.Treeview(
        frame_right,
        show="headings",
        yscrollcommand=vsb.set,
        xscrollcommand=hsb.set
    )
    vsb.config(command=table.yview)
    hsb.config(command=table.xview)

    table.pack(fill="both", expand=True)
    vsb.pack(side="right", fill="y")
    hsb.pack(side="bottom", fill="x")
    table.bind("<Double-1>", on_column_double_click)
    table.bind("<Button-1>", on_column_click)
    paned.add(frame_right)

    current_file_path = {"path": None}

    def on_tree_select_wrapper(event):
        selected_item = tree.focus()
        file_path = tree.item(selected_item, "values")[0] if tree.item(selected_item, "values") else ""
        current_file_path["path"] = file_path
        on_item_click(event, tree, table)

    tree.bind("<<TreeviewSelect>>", on_tree_select_wrapper)

    add_save_buttons(window, table,
                     get_current_path=lambda: current_file_path["path"],
                     set_current_path=lambda path: current_file_path.update({"path": path}))

    window.mainloop()

if __name__ == "__main__":
    create_ui()
