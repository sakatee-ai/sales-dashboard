import customtkinter as ctk
from ui_overview import setup_overview_tab
from ui_monthly import setup_monthly_tab
from utils import load_products_master

def launch_view_mode(products_df):
    view_window = ctk.CTk()
    view_window.title("売上ダッシュボード")
    view_window.geometry("1400x900")
    view_window.tk.call("tk", "scaling", 1.8)

    tabview = ctk.CTkTabview(view_window)
    tabview.pack(fill="both", expand=True, padx=10, pady=10)

    tab_overview = tabview.add("売上一覧")
    tab_monthly = tabview.add("月別売上")

    setup_overview_tab(tab_overview, products_df)
    setup_monthly_tab(tab_monthly, products_df)

    view_window.mainloop()

if __name__ == "__main__":
    products_df = load_products_master()
    if products_df is not None:
        launch_view_mode(products_df)
