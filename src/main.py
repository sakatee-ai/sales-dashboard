import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv
import os

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
    selected_item = tree.focus()
    full_path = tree.item(selected_item, "values")[0] if tree.item(selected_item, "values") else ""

    if full_path.endswith(".csv") and os.path.isfile(full_path):
        try:
            with open(full_path, newline="", encoding="utf-8") as f:
                reader = csv.reader(f)
                rows = list(reader)
                if not rows:
                    return

                table_widget.delete(*table_widget.get_children())
                table_widget["columns"] = []
                headers = rows[0]
                table_widget["columns"] = headers
                table_widget["show"] = "headings"

                for i, col in enumerate(headers):
                    table_widget.heading(col, text=col)
                    table_widget.column(col, width=200, anchor="center", stretch=False)

                for row in rows[1:]:
                    table_widget.insert("", "end", values=row)

        except Exception as e:
            messagebox.showerror("エラー", f"読み込み失敗: {e}")

# 編集フォーム
def add_edit_form(parent_frame, table):
    form_frame = ttk.LabelFrame(parent_frame, text="編集フォーム")
    form_frame.pack(fill="x", padx=10, pady=5)

    entry_vars = []
    entry_widgets = []

    def update_form_with_values(values):
        for widget in entry_widgets:
            widget.destroy()
        entry_vars.clear()
        entry_widgets.clear()

        for i, value in enumerate(values):
            var = tk.StringVar(value=value)
            entry = ttk.Entry(form_frame, textvariable=var, width=20)
            entry.grid(row=0, column=i, padx=5, pady=2)
            entry_vars.append(var)
            entry_widgets.append(entry)

    def on_row_select(event):
        selected = table.focus()
        if not selected:
            return
        values = table.item(selected, "values")
        update_form_with_values(values)

    def on_update():
        selected = table.focus()
        if not selected:
            messagebox.showwarning("選択なし", "編集する行を選んでください。")
            return
        new_values = [var.get() for var in entry_vars]
        table.item(selected, values=new_values)

    update_button = ttk.Button(form_frame, text="更新", command=on_update)
    update_button.grid(row=1, column=0, columnspan=10, pady=5)

    table.bind("<<TreeviewSelect>>", on_row_select)

    return update_form_with_values

# 保存処理

def save_table_to_csv(table, file_path):
    if not file_path:
        messagebox.showwarning("保存先未設定", "保存先ファイルパスがありません。")
        return
    try:
        with open(file_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            headers = table["columns"]
            writer.writerow(headers)
            for row_id in table.get_children():
                values = table.item(row_id, "values")
                writer.writerow(values)
        messagebox.showinfo("保存完了", f"{file_path} に保存しました。")
    except Exception as e:
        messagebox.showerror("保存エラー", str(e))

def refresh_tree(tree, root_path):
    tree.delete(*tree.get_children())
    if os.path.exists(root_path):
        root_node = tree.insert("", "end", text=os.path.basename(root_path), open=True, values=[root_path])
        build_tree_from_directory(tree, root_node, root_path)

def add_save_buttons(parent_frame, table, tree, root_path, get_current_path, set_current_path):
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
            refresh_tree(tree, root_path)

    ttk.Button(button_frame, text="保存", command=save).pack(side="left", padx=5)
    ttk.Button(button_frame, text="名前をつけて保存", command=save_as).pack(side="left", padx=5)

# UI本体

def create_ui():
    window = tk.Tk()
    window.title("CSV表ビューア")
    window.geometry("900x600")

    style = ttk.Style()
    style.configure("Treeview", font=("Arial", 11), rowheight=25)

    paned = ttk.PanedWindow(window, orient=tk.HORIZONTAL)
    paned.pack(fill="both", expand=True)

    # 左側：ツリービュー
    frame_left = ttk.Frame(paned, width=250)
    frame_left.pack_propagate(False)
    tree = ttk.Treeview(frame_left)
    tree.pack(fill="both", expand=True)
    tree.column("#0", width=220)
    paned.add(frame_left)

    # フォルダ構成読み込み
    root_path = "data"
    if os.path.exists(root_path):
        root_node = tree.insert("", "end", text=os.path.basename(root_path), open=True, values=[root_path])
        build_tree_from_directory(tree, root_node, root_path)
    else:
        messagebox.showwarning("フォルダなし", f"{root_path} が存在しません")

    # 右側：表＋スクロール
    frame_right = ttk.Frame(paned)
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

    table.grid(row=0, column=0, sticky="nsew")
    vsb.grid(row=0, column=1, sticky="ns")
    hsb.grid(row=1, column=0, sticky="ew")
    frame_right.rowconfigure(0, weight=1)
    frame_right.columnconfigure(0, weight=1)

    paned.add(frame_right)

    # ファイルパス管理用
    current_file_path = {"path": None}

    # 編集フォーム作成（戻り値でEntry更新関数を取得）
    update_form_with_values = add_edit_form(window, table)

    # 保存ボタン群
    add_save_buttons(window, table, tree, root_path,
                     get_current_path=lambda: current_file_path["path"],
                     set_current_path=lambda path: current_file_path.update({"path": path}))

    # ツリービュー選択時の処理
    def on_tree_select_wrapper(event):
        selected_item = tree.focus()
        file_path = tree.item(selected_item, "values")[0] if tree.item(selected_item, "values") else ""
        current_file_path["path"] = file_path
        on_item_click(event, tree, table)

        # 自動的に1行目を選んでフォームに反映
        first_row = table.get_children()
        if first_row:
            values = table.item(first_row[0], "values")
            update_form_with_values(values)

    tree.bind("<<TreeviewSelect>>", on_tree_select_wrapper)

    window.mainloop()

if __name__ == "__main__":
    create_ui()