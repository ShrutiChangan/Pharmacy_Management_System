import tkinter as tk
from gui.pharmacy_app import PharmacyApp
from gui.login_ui import LoginPage

def start_main_app(root):
    for widget in root.winfo_children():
        widget.destroy()
    app = PharmacyApp(root)


if __name__ == "__main__":
    root = tk.Tk()
    login = LoginPage(root, lambda: start_main_app(root))
    root.mainloop()