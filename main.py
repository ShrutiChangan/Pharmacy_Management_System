import tkinter as tk
from gui.login_ui import LoginPage
from app_controller import start_main_app



if __name__ == "__main__":
    root = tk.Tk()
    login = LoginPage(root, lambda: start_main_app(root))
    root.mainloop()