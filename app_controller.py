from gui.pharmacy_app import PharmacyApp

def start_main_app(root):
    for widget in root.winfo_children():
        widget.destroy()
    app = PharmacyApp(root)