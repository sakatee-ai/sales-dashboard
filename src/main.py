import tkinter as tk
from tkinter import ttk

def create_treeview(window):
    style = ttk.Style()
    style.configure("Treeview", font=("Arial", 12), rowheight=25)

    tree = ttk.Treeview(window)
    tree.pack(fill="both", expand=True)

    tree.column("#0", width=200)  # ツリーの幅広げる

    folder1 = tree.insert("", "end", text="フォルダA", open=True)
    tree.insert(folder1, "end", text="file1.csv")
    tree.insert(folder1, "end", text="file2.csv")

    folder2 = tree.insert("", "end", text="フォルダB", open=True)
    tree.insert(folder2, "end", text="file3.csv")

    return tree

def main():
    window = tk.Tk()
    window.title("CSVアプリ - ツリービュー改")
    window.geometry("400x300")

    create_treeview(window)

    window.mainloop()

if __name__ == "__main__":
    main()
