import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import ttk, messagebox, font, scrolledtext
import random
import os 
import tempfile
from pdf_generator import PDFGenerator
from database.connection import DatabaseConnection
from repositories.medicine_repository import MedicineRepository
from repositories.customer_repository import CustomerRepository
from repositories.supplier_repository import SupplierRepository
from repositories.billing_repository import BillingRepository
from gui.login_ui import LoginPage
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkcalendar import DateEntry
import datetime
from main import start_main_app
from gui.bill_preview_window import BillPreviewWindow

class PharmacyApp:
    def __init__(self, root):
        self.root = root 
        self.root.title("Pharmacy Management System")
        self.root.geometry("1100x700")

        # Database connection
        self.db = DatabaseConnection()
        self.medicine_repo = MedicineRepository(self.db)
        self.supplier_repo = SupplierRepository(self.db)
        self.customer_repo = CustomerRepository(self.db)
        self.billing_repo = BillingRepository(self.db)

        # Set custom colors
        self.primary_color = "#6200ea"  # Deep purple
        self.secondary_color = "#03dac6"  # Teal
        self.bg_color = "#f5f5f5"  # Light gray
        self.text_color = "#212121"  # Dark gray
        self.accent_color = "#bb86fc"  # Light purple

        self.root.configure(bg=self.bg_color)

        # Create custom fonts
        self.title_font = font.Font(family="Segoe UI", size=18, weight="bold")
        self.header_font = font.Font(family="Segoe UI", size=14, weight="bold")
        self.normal_font = font.Font(family="Segoe UI", size=10)
        self.button_font = font.Font(family="Segoe UI", size=10, weight="bold")

        # Set custom style
        self.style = ttk.Style()
        self.style.theme_use("clam")

        # Configure colors and styles
        self.style.configure("TFrame", background=self.bg_color)
        self.style.configure("TLabelframe", background=self.bg_color)
        self.style.configure("TLabelframe.Label", background=self.bg_color, foreground=self.primary_color,
                             font=self.header_font)

        # Configure notebook style
        self.style.configure("TNotebook", background=self.bg_color, tabmargins=[2, 5, 2, 0])
        self.style.configure("TNotebook.Tab", background="#e0e0e0", foreground=self.text_color,
                             padding=[15, 8], font=self.normal_font)
        self.style.map("TNotebook.Tab",
                       background=[("selected", self.primary_color)],
                       foreground=[("selected", "#ffffff")])

        # Configure button style
        self.style.configure("TButton", background=self.primary_color, foreground="#ffffff",
                             padding=8, font=self.button_font)
        self.style.map("TButton",
                       background=[("active", self.accent_color)],
                       foreground=[("active", "#ffffff")])

        # Secondary button style
        self.style.configure("Secondary.TButton", background=self.secondary_color, foreground="#ffffff")
        self.style.map("Secondary.TButton",
                       background=[("active", "#018786")],
                       foreground=[("active", "#ffffff")])

        # Configure label style
        self.style.configure("TLabel", background=self.bg_color, foreground=self.text_color, font=self.normal_font)
        self.style.configure("Header.TLabel", background=self.bg_color, foreground=self.primary_color,
                             font=self.header_font)
        self.style.configure("Title.TLabel", background=self.bg_color, foreground=self.primary_color,
                             font=self.title_font)

        # Configure entry style
        self.style.configure("TEntry", font=self.normal_font, fieldbackground="#ffffff")

        # Configure treeview style
        self.style.configure("Treeview",
                             background="#ffffff",
                             foreground=self.text_color,
                             rowheight=25,
                             fieldbackground="#ffffff",
                             font=self.normal_font)
        self.style.configure("Treeview.Heading",
                             background=self.primary_color,
                             foreground="#ffffff",
                             font=self.button_font)
        self.style.map("Treeview", background=[("selected", self.accent_color)], foreground=[("selected", "#ffffff")])

        # Create header with gradient effect
        self.header_frame = tk.Frame(root, bg=self.primary_color, height=70)
        self.header_frame.pack(fill="x")

        # Create gradient effect (simulated with multiple frames)
        for i in range(3):
            gradient = tk.Frame(self.header_frame, bg=self.get_gradient_color(i), height=3)
            gradient.pack(fill="x")

        header_label = tk.Label(self.header_frame, text="Pharmacy Management System",
                                font=self.title_font, bg=self.primary_color, fg="#ffffff")
        header_label.pack(side="left", padx=20, pady=10)

        # Current date display
        current_date = datetime.datetime.now().strftime("%d %b, %Y")
        date_label = tk.Label(self.header_frame, text=f"Date: {current_date}",
                              font=self.normal_font, bg=self.primary_color, fg="#ffffff")
        date_label.pack(side="right", padx=20, pady=15)

        # Logout button
        logout_btn = tk.Button(self.header_frame, text="Logout",
                               font=self.normal_font, bg="#ff5252", fg="#ffffff",
                               command=self.logout)
        logout_btn.pack(side="right", padx=10, pady=15)

        # Create notebook (tabs)
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True, padx=20, pady=15)

        # Create tabs
        self.home_tab = ttk.Frame(self.notebook)
        self.medicines_tab = ttk.Frame(self.notebook)
        self.suppliers_tab = ttk.Frame(self.notebook)
        self.billing_tab = ttk.Frame(self.notebook)
        self.billing_history_tab = ttk.Frame(self.notebook)
        self.reports_tab = ttk.Frame(self.notebook)
        self.stock_alerts_tab = ttk.Frame(self.notebook)
        
        self.notebook.add(self.home_tab, text="Home")
        self.notebook.add(self.medicines_tab, text="Medicines")
        self.notebook.add(self.suppliers_tab, text="Suppliers")
        self.notebook.add(self.billing_tab, text="Billing")
        self.notebook.add(self.billing_history_tab, text="Billing History")
        self.notebook.add(self.reports_tab, text="Reports")
        self.notebook.add(self.stock_alerts_tab, text="Stock Alerts")
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_change)

        # Setup each tab
        self.setup_home_tab()
        self.setup_medicines_tab()
        self.setup_suppliers_tab()
        self.setup_billing_tab()
        self.setup_billing_history_tab()
        self.setup_reports_tab()
        self.setup_stock_alerts_tab()

        # Create footer
        footer_frame = tk.Frame(root, bg=self.primary_color, height=25)
        footer_frame.pack(fill="x", side="bottom")

        footer_label = tk.Label(footer_frame, text="© 2025 Pharmacy Management",
                                font=("Segoe UI", 8), bg=self.primary_color, fg="#ffffff")
        footer_label.pack(side="right", padx=10, pady=3)

    def logout(self):
        self.db.close()
        self.root.destroy()
        root = tk.Tk()
        login = LoginPage(root, lambda: start_main_app(root))
        root.mainloop()

    def get_gradient_color(self, index):
        # Create a gradient effect
        colors = ["#7c4dff", "#651fff", "#6200ea"]
        return colors[index % len(colors)]

    def setup_home_tab(self):
        # Home tab with buttons to navigate to other tabs
        home_frame = ttk.Frame(self.home_tab)
        home_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Welcome banner with gradient background
        banner_frame = tk.Frame(home_frame, bg=self.primary_color, height=120, bd=0, relief="flat")
        banner_frame.pack(fill="x", pady=20)

        welcome_label = tk.Label(banner_frame, text="Welcome to Pharmacy Management System",
                                 font=("Segoe UI", 22, "bold"), bg=self.primary_color, fg="#ffffff")
        welcome_label.pack(pady=40)

        instruction_label = ttk.Label(home_frame, text="Please select an option below:",
                                      style="Header.TLabel")
        instruction_label.pack(pady=20)

        # Create button frame with card-like appearance
        button_frame = tk.Frame(home_frame, bg=self.bg_color)
        button_frame.pack(pady=20)

        # Create grid of buttons with card-like appearance
        buttons = [
            ("Medicines", lambda: self.notebook.select(1), "Manage your medicine inventory"),
            ("Suppliers", lambda: self.notebook.select(2), "Manage supplier details"),
            ("Billing", lambda: self.notebook.select(3), "Create new bills"),
            ("Billing History", lambda: self.notebook.select(4), "View past transactions"),
            ("Reports", lambda: self.notebook.select(5), "View data analysis reports"),
            ("Stock Alerts" , lambda: self.notebook.select(6), "View Low stock items")
        ]

        # Arrange buttons in a grid (3 in first row, 3 in second row)
        for i, (text, command, description) in enumerate(buttons):
            row = i // 3
            col = i % 3

            # Create card-like frame
            card = tk.Frame(button_frame, bg="#ffffff", bd=0, relief="flat", padx=10, pady=10)
            card.grid(row=row, column=col, padx=15, pady=15)

            # Add shadow effect (simulated with frames)
            shadow = tk.Frame(button_frame, bg="#dddddd", height=120, width=220)
            shadow.grid(row=row, column=col, padx=15, pady=15)
            shadow.lower(card)

            # Button title
            title = tk.Label(card, text=text, font=("Segoe UI", 14, "bold"), bg="#ffffff", fg=self.primary_color)
            title.pack(pady=5)

            # Button description
            desc = tk.Label(card, text=description, font=("Segoe UI", 9), bg="#ffffff", fg=self.text_color,
                            wraplength=180)
            desc.pack(pady=5)

            # Button
            btn = ttk.Button(card, text="Open", command=command, width=15)
            btn.pack(pady=10)

            # Make the entire card clickable
            card.bind("<Button-1>", lambda e, cmd=command: cmd())
            title.bind("<Button-1>", lambda e, cmd=command: cmd())
            desc.bind("<Button-1>", lambda e, cmd=command: cmd())

    def setup_medicines_tab(self):
        # Create a notebook for medicine operations
        medicine_notebook = ttk.Notebook(self.medicines_tab)
        medicine_notebook.pack(fill="both", expand=True, padx=20, pady=10)

        # Create tabs for Add/Update Medicine and Search Medicine
        add_medicine_tab = ttk.Frame(medicine_notebook)
        search_medicine_tab = ttk.Frame(medicine_notebook)

        medicine_notebook.add(add_medicine_tab, text="Add/Update Medicine")
        medicine_notebook.add(search_medicine_tab, text="Search Medicine")

        # Setup Add/Update Medicine tab
        medicine_frame = ttk.LabelFrame(add_medicine_tab, text="Medicine Details")
        medicine_frame.pack(fill="both", expand=False, padx=20, pady=10)

        fields = [
            ("Medicine ID:", 0, 0),
            ("Medicine Name:", 1, 0),
            ("Description:", 2, 0),
            ("Supplier Name:", 3, 0),
            ("Price (₹):", 0, 2),
            ("Quantity:", 1, 2),
            ("Expiry Date:", 2, 2),
            ("Location in Store:", 3, 2)
        ]

        self.medicine_entries = {}

        for label_text, row, col in fields:
            label = ttk.Label(medicine_frame, text=label_text)
            label.grid(row=row, column=col, padx=10, pady=5, sticky="w")

            if label_text == "Expiry Date:":
                entry = DateEntry(medicine_frame, width=20, background=self.primary_color,
                                  foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd',
                                  font=self.normal_font)
            elif label_text == "Supplier Name:":
                supplier_names = self.medicine_repo.get_supplier_names()
                entry = ttk.Combobox(medicine_frame, width=23, values=supplier_names)
            elif label_text == "Medicine ID:":
                entry = ttk.Entry(medicine_frame, width=25, state='normal')  # Initially editable
            else:
                entry = ttk.Entry(medicine_frame, width=25)

            entry.grid(row=row, column=col + 1, padx=10, pady=5, sticky="w")
            self.medicine_entries[label_text.replace(":", "")] = entry

        # Generate medicine ID button - moved after entries are created
        generate_id_btn = ttk.Button(medicine_frame, text="Generate ID", command=self.generate_medicine_id)
        generate_id_btn.grid(row=0, column=1, padx=(200, 0), pady=5, sticky="w")

        # Now generate the initial ID after all entries are created
        self.generate_medicine_id()

        # Add buttons
        button_frame = ttk.Frame(medicine_frame)
        button_frame.grid(row=4, column=0, columnspan=4, padx=10, pady=10)

        save_btn = ttk.Button(button_frame, text="Save Medicine", command=self.save_medicine)
        save_btn.pack(side="left", padx=10)

        update_btn = ttk.Button(button_frame, text="Update Medicine", command=self.update_medicine)
        update_btn.pack(side="left", padx=10)

        clear_btn = ttk.Button(button_frame, text="Clear", command=self.clear_medicine_form)
        clear_btn.pack(side="left", padx=10)

        # Load medicine button
        load_frame = ttk.Frame(medicine_frame)
        load_frame.grid(row=5, column=0, columnspan=4, padx=10, pady=10, sticky="w")

        load_label = ttk.Label(load_frame, text="Load Medicine by ID:")
        load_label.pack(side="left", padx=5)

        self.load_id_entry = ttk.Entry(load_frame, width=15)
        self.load_id_entry.pack(side="left", padx=5)

        load_btn = ttk.Button(load_frame, text="Load", command=self.load_medicine)
        load_btn.pack(side="left", padx=5)

        # Setup Search Medicine tab with scrollable content
        # Create a canvas with scrollbar for the search tab
        search_canvas = tk.Canvas(search_medicine_tab)
        search_canvas.pack(side="left", fill="both", expand=True)

        # Add a scrollbar to the canvas
        search_scrollbar = ttk.Scrollbar(search_medicine_tab, orient="vertical", command=search_canvas.yview)
        search_scrollbar.pack(side="right", fill="y")

        # Configure the canvas
        search_canvas.configure(yscrollcommand=search_scrollbar.set)
        search_canvas.bind('<Configure>', lambda e: search_canvas.configure(scrollregion=search_canvas.bbox("all")))

        # Create a frame inside the canvas for the content
        search_medicine_frame = ttk.Frame(search_canvas)
        search_canvas_window = search_canvas.create_window((0, 0), window=search_medicine_frame, anchor="nw")

        # Make the frame expand to the width of the canvas
        def configure_search_frame(event):
            search_canvas.itemconfig(search_canvas_window, width=event.width)

        search_canvas.bind('<Configure>', lambda event: [configure_search_frame(event),
                                                         search_canvas.configure(
                                                             scrollregion=search_canvas.bbox("all"))])

        # Add mousewheel scrolling
        def _on_mousewheel(event):
            search_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        search_canvas.bind_all("<MouseWheel>", _on_mousewheel)

        # Search options (now inside the scrollable frame)
        search_frame = ttk.LabelFrame(search_medicine_frame, text="Search Medicine")
        search_frame.pack(fill="x", padx=10, pady=10)

        # Search by options
        search_by_label = ttk.Label(search_frame, text="Search By:")
        search_by_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        self.search_by_var = tk.StringVar()
        search_by_combo = ttk.Combobox(search_frame, textvariable=self.search_by_var, width=15)
        search_by_combo['values'] = ('ID', 'Name', 'Supplier', 'Location')
        search_by_combo.current(0)
        search_by_combo.grid(row=0, column=1, padx=10, pady=10, sticky="w")

        # Search term
        search_term_label = ttk.Label(search_frame, text="Search Term:")
        search_term_label.grid(row=0, column=2, padx=10, pady=10, sticky="w")

        self.search_term_entry = ttk.Entry(search_frame, width=25)
        self.search_term_entry.grid(row=0, column=3, padx=10, pady=10, sticky="w")

        # Search button
        search_btn = ttk.Button(search_frame, text="Search", command=self.search_medicines)
        search_btn.grid(row=0, column=4, padx=10, pady=10)

        # Reset button
        reset_btn = ttk.Button(search_frame, text="Reset", command=self.reset_medicine_search)
        reset_btn.grid(row=0, column=5, padx=10, pady=10)

        # Results table
        results_frame = ttk.LabelFrame(search_medicine_frame, text="Search Results")
        results_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Create treeview for medicine results
        columns = ("ID", "Name", "Supplier", "Price (₹)", "Quantity", "Expiry Date", "Location")
        self.medicine_tree = ttk.Treeview(results_frame, columns=columns, show="headings", height=10)

        # Configure columns
        for col in columns:
            self.medicine_tree.heading(col, text=col)
            width = 150 if col == "Name" or col == "Supplier" else 100
            self.medicine_tree.column(col, width=width, anchor="center")

        self.medicine_tree.pack(fill="both", expand=True, padx=10, pady=10)

        # Add scrollbar for the treeview
        tree_scrollbar = ttk.Scrollbar(results_frame, orient="vertical", command=self.medicine_tree.yview)
        tree_scrollbar.pack(side="right", fill="y")
        self.medicine_tree.configure(yscrollcommand=tree_scrollbar.set)

        # Action buttons
        action_frame = ttk.Frame(search_medicine_frame)
        action_frame.pack(fill="x", padx=10, pady=10)

        edit_btn = ttk.Button(action_frame, text="Edit Selected", command=self.edit_selected_medicine)
        edit_btn.pack(side="left", padx=5)

        delete_btn = ttk.Button(action_frame, text="Delete Selected", command=self.delete_selected_medicine)
        delete_btn.pack(side="left", padx=5)

        # Clean up mousewheel binding when window is destroyed
        search_medicine_tab.bind("<Destroy>", lambda e: search_canvas.unbind_all("<MouseWheel>"))

        # Load initial medicines
        self.load_medicines()
    def generate_medicine_id(self):
        # Generate a unique medicine ID
        medicine_id = f"MED{random.randint(1000, 9999)}"
        current_state = self.medicine_entries["Medicine ID"]['state']
        self.medicine_entries["Medicine ID"].config(state='normal')
        self.medicine_entries["Medicine ID"].delete(0, tk.END)
        self.medicine_entries["Medicine ID"].insert(0, medicine_id)
        self.medicine_entries["Medicine ID"].config(state=current_state)

    def save_medicine(self):
        # Get data from form
        medicine_data = {
            'medicine_id': self.medicine_entries["Medicine ID"].get(),
            'name': self.medicine_entries["Medicine Name"].get(),
            'description': self.medicine_entries["Description"].get(),
            'supplier_name': self.medicine_entries["Supplier Name"].get(),
            'price': self.medicine_entries["Price (₹)"].get().replace('₹', ''),
            'quantity': self.medicine_entries["Quantity"].get(),
            'expiry_date': self.medicine_entries["Expiry Date"].get(),
            'location': self.medicine_entries["Location in Store"].get()
        }

        # Validate data
        if not medicine_data['medicine_id'] or not medicine_data['name'] or not medicine_data['supplier_name']:
            messagebox.showerror("Error", "Medicine ID, Name, and Supplier are required fields")
            return

        # Add medicine to database
        success = self.medicine_repo.add_medicine(medicine_data)

        if success:
            messagebox.showinfo("Success", "Medicine added successfully")
            self.clear_medicine_form()
            self.load_medicines()

    def update_medicine(self):
        # Get data from form
        medicine_data = {
            'medicine_id': self.medicine_entries["Medicine ID"].get(),
            'name': self.medicine_entries["Medicine Name"].get(),
            'description': self.medicine_entries["Description"].get(),
            'supplier_name': self.medicine_entries["Supplier Name"].get(),
            'price': self.medicine_entries["Price (₹)"].get().replace('₹', ''),
            'quantity': self.medicine_entries["Quantity"].get(),
            'expiry_date': self.medicine_entries["Expiry Date"].get(),
            'location': self.medicine_entries["Location in Store"].get()
        }

        # Validate data
        if not medicine_data['medicine_id'] or not medicine_data['name'] or not medicine_data['supplier_name']:
            messagebox.showerror("Error", "Medicine ID, Name, and Supplier are required fields")
            return

        # Update medicine in database
        success = self.medicine_repo.update_medicine(medicine_data)

        if success:
            messagebox.showinfo("Success", "Medicine updated successfully")
            self.load_medicines()

    def clear_medicine_form(self, keep_id_state=False):
        # Clear all entry fields
        for field_name, entry in self.medicine_entries.items():
            if field_name == "Medicine ID":
                current_state = entry['state']
                entry.config(state='normal')
                entry.delete(0, tk.END)
                if keep_id_state:
                    entry.config(state=current_state)
                else:
                    entry.config(state='normal')  # Make editable for new entries
            elif hasattr(entry, 'delete'):
                entry.delete(0, tk.END)
            elif hasattr(entry, 'set'):
                entry.set('')

        # Generate a new medicine ID if we're not keeping state
        if not keep_id_state:
            self.generate_medicine_id()

    def load_medicine(self):
        medicine_id = self.load_id_entry.get()

        if not medicine_id:
            messagebox.showerror("Error", "Please enter a Medicine ID")
            return

        # Get medicine from database
        medicine = self.medicine_repo.get_medicine_by_id(medicine_id)

        if medicine:
            # Clear form but keep Medicine ID field state
            self.clear_medicine_form(keep_id_state=True)

            # Fill form with medicine data
            self.medicine_entries["Medicine ID"].config(state='normal')
            self.medicine_entries["Medicine ID"].delete(0, tk.END)
            self.medicine_entries["Medicine ID"].insert(0, medicine['medicine_id'])
            self.medicine_entries["Medicine ID"].config(state='readonly')  # Make it read-only

            # Fill other fields normally
            self.medicine_entries["Medicine Name"].insert(0, medicine['name'])
            self.medicine_entries["Description"].insert(0, medicine['description'] or "")
            self.medicine_entries["Supplier Name"].set(medicine['supplier_name'])
            self.medicine_entries["Price (₹)"].insert(0, str(medicine['price']))
            self.medicine_entries["Quantity"].insert(0, str(medicine['quantity']))

            if medicine['expiry_date']:
                self.medicine_entries["Expiry Date"].set_date(medicine['expiry_date'])

            self.medicine_entries["Location in Store"].insert(0, medicine['location'] or "")
        else:
            messagebox.showerror("Error", f"Medicine with ID {medicine_id} not found")

    def load_medicines(self):
        # Clear treeview
        for item in self.medicine_tree.get_children():
            self.medicine_tree.delete(item)

        # Get all medicines from database
        medicines = self.medicine_repo.get_all_medicines()

        # Add medicines to treeview
        for medicine in medicines:
            self.medicine_tree.insert("", "end", values=(
                medicine["medicine_id"],
                medicine['name'],
                medicine['supplier_name'],
                f"₹{medicine['price']}",
                medicine['quantity'],
                medicine['expiry_date'].strftime('%Y-%m-%d') if medicine['expiry_date'] else "",
                medicine['location']
            ))

    def search_medicines(self):
        search_by = self.search_by_var.get()
        search_term = self.search_term_entry.get()

        if not search_term:
            messagebox.showerror("Error", "Please enter a search term")
            return

        # Clear treeview
        for item in self.medicine_tree.get_children():
            self.medicine_tree.delete(item)

        # Search medicines in database
        medicines = self.medicine_repo.search_medicines(search_by, search_term)

        if not medicines:
            messagebox.showinfo("Info", "No medicines found matching your search")
            return

        # Add medicines to treeview
        for medicine in medicines:
            self.medicine_tree.insert("", "end", values=(
                medicine["medicine_id"],
                medicine['name'],
                medicine['supplier_name'],
                f"₹{medicine['price']}",
                medicine['quantity'],
                medicine['expiry_date'].strftime('%Y-%m-%d') if medicine['expiry_date'] else "",
                medicine['location']
            ))

    def reset_medicine_search(self):
        self.search_term_entry.delete(0, tk.END)
        self.load_medicines()

    def edit_selected_medicine(self):
        selected_item = self.medicine_tree.selection()

        if not selected_item:
            messagebox.showerror("Error", "Please select a medicine to edit")
            return

        # Get medicine ID from selected item
        medicine_id = self.medicine_tree.item(selected_item[0], 'values')[0]

        # Load medicine into form
        self.load_id_entry.delete(0, tk.END)
        self.load_id_entry.insert(0, medicine_id)
        self.load_medicine()

        # Switch to Add/Update tab
        self.notebook.select(1)  # Select Medicines tab
        medicine_notebook = self.medicines_tab.winfo_children()[0]
        medicine_notebook.select(0)  # Select Add/Update tab

    def delete_selected_medicine(self):
        selected_item = self.medicine_tree.selection()

        if not selected_item:
            messagebox.showerror("Error", "Please select a medicine to delete")
            return

        # Get medicine ID from selected item
        medicine_id = self.medicine_tree.item(selected_item[0], 'values')[0]

        # Confirm deletion
        confirm = messagebox.askyesno("Confirm", f"Are you sure you want to delete medicine {medicine_id}?")

        if confirm:
            # Delete medicine from database
            success = self.medicine_repo.delete_medicine(medicine_id)

            if success:
                messagebox.showinfo("Success", "Medicine deleted successfully")
                self.load_medicines()

    def setup_suppliers_tab(self):
        # Create a notebook for supplier operations
        supplier_notebook = ttk.Notebook(self.suppliers_tab)
        supplier_notebook.pack(fill="both", expand=True, padx=20, pady=10)

        # Create tabs for Add Supplier, Search Supplier, and Supply Records
        add_supplier_tab = ttk.Frame(supplier_notebook)
        search_supplier_tab = ttk.Frame(supplier_notebook)
        supply_records_tab = ttk.Frame(supplier_notebook)

        supplier_notebook.add(add_supplier_tab, text="Add Supplier")
        supplier_notebook.add(search_supplier_tab, text="Search Supplier")
        supplier_notebook.add(supply_records_tab, text="Supply Records")

        # Setup Add Supplier tab
        supplier_frame = ttk.LabelFrame(add_supplier_tab, text="Supplier Details")
        supplier_frame.pack(fill="both", expand=False, padx=20, pady=10)

        # Create entry fields for basic supplier info
        basic_fields = [
            ("Supplier ID:", 0, 0),
            ("Supplier Name:", 1, 0),
            ("Contact No:", 2, 0),
            ("Email ID:", 3, 0),
            ("Address:", 4, 0)
        ]

        self.supplier_entries = {}

        for label_text, row, col in basic_fields:
            label = ttk.Label(supplier_frame, text=label_text)
            label.grid(row=row, column=col, padx=10, pady=10, sticky="w")

            entry = ttk.Entry(supplier_frame, width=30)
            entry.grid(row=row, column=col + 1, padx=10, pady=10, sticky="w")
            self.supplier_entries[label_text.replace(":", "")] = entry

        # Generate supplier ID button
        generate_id_btn = ttk.Button(supplier_frame, text="Generate ID", command=self.generate_supplier_id)
        generate_id_btn.grid(row=0, column=1, padx=(250, 0), pady=10, sticky="w")

        # Create a separator
        separator = ttk.Separator(supplier_frame, orient="vertical")
        separator.grid(row=0, column=2, rowspan=6, padx=20, sticky="ns")

        # Create entry fields for supply details
        supply_fields = [
            ("Medicine Supplied:", 0, 3),
            ("Quantity Supplied:", 1, 3),
            ("Amount Paid (₹):", 2, 3),
        ]

        self.supply_entries = {}

        for label_text, row, col in supply_fields:
            label = ttk.Label(supplier_frame, text=label_text)
            label.grid(row=row, column=col, padx=10, pady=10, sticky="w")

            if label_text == "Medicine Supplied:":
                # Get all medicines for dropdown
                medicines = self.medicine_repo.get_all_medicines()
                medicine_names = [medicine['name'] for medicine in medicines]

                entry = ttk.Combobox(supplier_frame, width=23, values=medicine_names)
            else:
                entry = ttk.Entry(supplier_frame, width=25)

            entry.grid(row=row, column=col + 1, padx=10, pady=10, sticky="w")
            self.supply_entries[label_text.replace(":", "")] = entry

        # Add date picker for supply date
        date_label = ttk.Label(supplier_frame, text="Supply Date:")
        date_label.grid(row=3, column=3, padx=10, pady=10, sticky="w")

        self.supply_date = DateEntry(supplier_frame, width=20, background=self.primary_color,
                                     foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd',
                                     font=self.normal_font)
        self.supply_date.grid(row=3, column=4, padx=10, pady=10, sticky="w")

        # Add buttons
        save_btn = ttk.Button(supplier_frame, text="Save Supplier", command=self.save_supplier)
        save_btn.grid(row=5, column=0, padx=10, pady=10, sticky="w")

        add_supply_btn = ttk.Button(supplier_frame, text="Add Supply Record", command=self.add_supply_record)
        add_supply_btn.grid(row=4, column=4, padx=10, pady=10, sticky="e")

        # Setup Search Supplier tab with scrolling capability
        # Create a canvas for scrolling
        search_canvas = tk.Canvas(search_supplier_tab)
        search_canvas.pack(side="left", fill="both", expand=True)

        # Add a scrollbar to the canvas
        search_scrollbar = ttk.Scrollbar(search_supplier_tab, orient="vertical", command=search_canvas.yview)
        search_scrollbar.pack(side="right", fill="y")

        # Configure the canvas
        search_canvas.configure(yscrollcommand=search_scrollbar.set)
        search_canvas.bind('<Configure>', lambda e: search_canvas.configure(scrollregion=search_canvas.bbox("all")))

        # Create a frame inside the canvas for the content
        search_supplier_frame = ttk.Frame(search_canvas)
        search_canvas_window = search_canvas.create_window((0, 0), window=search_supplier_frame, anchor="nw")

        # Make the frame expand to the width of the canvas
        def configure_search_frame(event):
            search_canvas.itemconfig(search_canvas_window, width=event.width)

        search_canvas.bind('<Configure>', lambda event: [configure_search_frame(event),
                                                         search_canvas.configure(
                                                             scrollregion=search_canvas.bbox("all"))])

        # Add mousewheel scrolling
        def _on_mousewheel(event):
            search_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        search_canvas.bind_all("<MouseWheel>", _on_mousewheel)

        # Search options
        search_options_frame = ttk.LabelFrame(search_supplier_frame, text="Search Options")
        search_options_frame.pack(fill="x", padx=10, pady=10)

        # Search by options
        search_by_label = ttk.Label(search_options_frame, text="Search By:")
        search_by_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        self.supplier_search_by_var = tk.StringVar()
        search_by_combo = ttk.Combobox(search_options_frame, textvariable=self.supplier_search_by_var, width=15)
        search_by_combo['values'] = ('ID', 'Name', 'Contact No')
        search_by_combo.current(0)
        search_by_combo.grid(row=0, column=1, padx=10, pady=10, sticky="w")

        # Search term
        search_term_label = ttk.Label(search_options_frame, text="Search Term:")
        search_term_label.grid(row=0, column=2, padx=10, pady=10, sticky="w")

        self.supplier_search_term_entry = ttk.Entry(search_options_frame, width=25)
        self.supplier_search_term_entry.grid(row=0, column=3, padx=10, pady=10, sticky="w")

        # Search button
        search_btn = ttk.Button(search_options_frame, text="Search", command=self.search_suppliers)
        search_btn.grid(row=0, column=4, padx=10, pady=10)

        # Reset button
        reset_btn = ttk.Button(search_options_frame, text="Reset", command=self.reset_supplier_search)
        reset_btn.grid(row=0, column=5, padx=10, pady=10)

        # Results table
        results_frame = ttk.LabelFrame(search_supplier_frame, text="Search Results")
        results_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Create treeview for supplier results
        columns = ("ID", "Name", "Contact No", "Email", "Address")
        self.supplier_search_tree = ttk.Treeview(results_frame, columns=columns, show="headings", height=10)

        # Configure columns
        for col in columns:
            self.supplier_search_tree.heading(col, text=col)
            width = 200 if col == "Address" else 120
            self.supplier_search_tree.column(col, width=width, anchor="center")

        self.supplier_search_tree.pack(fill="both", expand=True, padx=10, pady=10)

        # Add scrollbar for the treeview
        tree_scrollbar = ttk.Scrollbar(results_frame, orient="vertical", command=self.supplier_search_tree.yview)
        tree_scrollbar.pack(side="right", fill="y")
        self.supplier_search_tree.configure(yscrollcommand=tree_scrollbar.set)

        # Action buttons
        action_frame = ttk.Frame(search_supplier_frame)
        action_frame.pack(fill="x", padx=10, pady=10)

        edit_btn = ttk.Button(action_frame, text="Edit Selected", command=self.edit_selected_supplier)
        edit_btn.pack(side="left", padx=5)

        delete_btn = ttk.Button(action_frame, text="Delete Selected", command=self.delete_selected_supplier)
        delete_btn.pack(side="left", padx=5)

        view_supplies_btn = ttk.Button(action_frame, text="View Supply History", command=self.view_supplier_supplies)
        view_supplies_btn.pack(side="left", padx=5)

        # Setup Supply Records tab
        supply_records_frame = ttk.Frame(supply_records_tab)
        supply_records_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Search options
        supply_search_frame = ttk.LabelFrame(supply_records_frame, text="Search Options")
        supply_search_frame.pack(fill="x", padx=10, pady=10)

        # Supplier selection
        supplier_label = ttk.Label(supply_search_frame, text="Supplier:")
        supplier_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        # Get all suppliers for dropdown
        suppliers = self.supplier_repo.get_all_suppliers()
        supplier_options = ["All Suppliers"] + [supplier['name'] for supplier in suppliers]

        self.supplier_combo = ttk.Combobox(supply_search_frame, width=25)
        self.supplier_combo['values'] = supplier_options
        self.supplier_combo.current(0)
        self.supplier_combo.grid(row=0, column=1, padx=10, pady=10, sticky="w")

        # Date range
        date_label = ttk.Label(supply_search_frame, text="Date Range:")
        date_label.grid(row=0, column=2, padx=10, pady=10, sticky="w")

        date_frame = ttk.Frame(supply_search_frame)
        date_frame.grid(row=0, column=3, padx=10, pady=10, sticky="w")

        from_label = ttk.Label(date_frame, text="From:")
        from_label.pack(side="left", padx=5)

        self.from_date_supply = DateEntry(date_frame, width=12, background=self.primary_color,
                                          foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd',
                                          font=self.normal_font)
        self.from_date_supply.pack(side="left", padx=5)

        to_label = ttk.Label(date_frame, text="To:")
        to_label.pack(side="left", padx=5)

        self.to_date_supply = DateEntry(date_frame, width=12, background=self.primary_color,
                                        foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd',
                                        font=self.normal_font)
        self.to_date_supply.pack(side="left", padx=5)

        # Search button
        search_btn = ttk.Button(supply_search_frame, text="Search", command=self.search_supplies)
        search_btn.grid(row=0, column=4, padx=10, pady=10)

        # Results table
        supply_results_frame = ttk.LabelFrame(supply_records_frame, text="Supply Records")
        supply_results_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Create treeview for supply records
        columns = ("Supplier ID", "Supplier", "Medicine", "Quantity", "Amount Paid (₹)", "Supply Date")
        self.supply_tree = ttk.Treeview(supply_results_frame, columns=columns, show="headings", height=10)

        # Configure columns
        for col in columns:
            self.supply_tree.heading(col, text=col)
            width = 150 if col == "Supplier" or col == "Medicine" else 120
            self.supply_tree.column(col, width=width, anchor="center")

        self.supply_tree.pack(fill="both", expand=True, padx=10, pady=10)

        # Add scrollbar
        scrollbar = ttk.Scrollbar(supply_results_frame, orient="vertical", command=self.supply_tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.supply_tree.configure(yscrollcommand=scrollbar.set)

        # Load suppliers and supplies
        self.load_suppliers()
        self.load_supplies()

    def generate_supplier_id(self):
        # Generate a unique supplier ID
        supplier_id = f"SUP{random.randint(1000, 9999)}"
        self.supplier_entries["Supplier ID"].delete(0, tk.END)
        self.supplier_entries["Supplier ID"].insert(0, supplier_id)

    def save_supplier(self):
        # Get data from form
        supplier_data = {
            'supplier_id': self.supplier_entries["Supplier ID"].get(),
            'name': self.supplier_entries["Supplier Name"].get(),
            'contact': self.supplier_entries["Contact No"].get(),
            'email': self.supplier_entries["Email ID"].get(),
            'address': self.supplier_entries["Address"].get()
        }

        # Validate data
        if not supplier_data['supplier_id'] or not supplier_data['name'] or not supplier_data['contact']:
            messagebox.showerror("Error", "Supplier ID, Name, and Contact are required fields")
            return

        # Add supplier to database
        success = self.supplier_repo.add_supplier(supplier_data)

        if success:
            # Refresh the supplier list in medicine repository
            self.medicine_repo.load_suppliers()

            # Update the supplier dropdown in the medicine tab
            supplier_names = self.medicine_repo.get_supplier_names()
            self.medicine_entries["Supplier Name"]['values'] = supplier_names

            # Also update the supplier combo in the supply records tab if needed
            self.supplier_combo['values'] = ["All Suppliers"] + supplier_names

            messagebox.showinfo("Success", "Supplier added successfully")
            self.clear_supplier_form()
            self.load_suppliers()

    def add_supply_record(self):
        # Get supplier ID
        supplier_id = self.supplier_entries["Supplier ID"].get()

        if not supplier_id:
            messagebox.showerror("Error", "Please enter a Supplier ID")
            return

        # Check if supplier exists
        supplier = self.supplier_repo.get_supplier_by_id(supplier_id)

        if not supplier:
            messagebox.showerror("Error", f"Supplier with ID {supplier_id} not found")
            return

        # Get medicine name
        medicine_name = self.supply_entries["Medicine Supplied"].get()

        if not medicine_name:
            messagebox.showerror("Error", "Please select a medicine")
            return

        # Get medicine ID
        medicines = self.medicine_repo.get_all_medicines()
        medicine_id = None

        for medicine in medicines:
            if medicine['name'] == medicine_name:
                medicine_id = medicine['medicine_id']
                break

        if not medicine_id:
            messagebox.showerror("Error", f"Medicine {medicine_name} not found")
            return

        # Get other supply data
        quantity = self.supply_entries["Quantity Supplied"].get()
        amount = self.supply_entries["Amount Paid (₹)"].get().replace('₹', '')
        supply_date = self.supply_date.get_date()

        # Validate data
        if not quantity or not amount:
            messagebox.showerror("Error", "Quantity and Amount are required fields")
            return

        try:
            quantity = int(quantity)
            amount = float(amount)
        except ValueError:
            messagebox.showerror("Error", "Quantity must be an integer and Amount must be a number")
            return

        # Create supply record
        supply_data = {
            'supplier_id': supplier_id,
            'medicine_id': medicine_id,
            'quantity': quantity,
            'amount': amount,
            'supply_date': supply_date
        }

        # Add supply record to database
        success = self.supplier_repo.add_supply_record(supply_data)

        if success:
            messagebox.showinfo("Success", "Supply record added successfully")
            self.clear_supply_form()
            self.load_supplies()

    def clear_supplier_form(self):
        # Clear all entry fields
        for entry in self.supplier_entries.values():
            entry.delete(0, tk.END)

        # Generate a new supplier ID
        self.generate_supplier_id()

    def clear_supply_form(self):
        # Clear supply entry fields
        for entry in self.supply_entries.values():
            if hasattr(entry, 'delete'):
                entry.delete(0, tk.END)
            elif hasattr(entry, 'set'):
                entry.set('')

        # Reset supply date to today
        self.supply_date.set_date(datetime.datetime.now())

    def load_suppliers(self):
        # Clear treeview
        for item in self.supplier_search_tree.get_children():
            self.supplier_search_tree.delete(item)

        # Get all suppliers from database
        suppliers = self.supplier_repo.get_all_suppliers()

        # Add suppliers to treeview
        for supplier in suppliers:
            self.supplier_search_tree.insert("", "end", values=(
                supplier['supplier_id'],
                supplier['name'],
                supplier['contact'],
                supplier['email'],
                supplier['address']
            ))

    def search_suppliers(self):
        search_by = self.supplier_search_by_var.get()
        search_term = self.supplier_search_term_entry.get()

        if not search_term:
            messagebox.showerror("Error", "Please enter a search term")
            return

        # Clear treeview
        for item in self.supplier_search_tree.get_children():
            self.supplier_search_tree.delete(item)

        # Search suppliers in database
        suppliers = self.supplier_repo.search_suppliers(search_by, search_term)

        # Add suppliers to treeview
        for supplier in suppliers:
            self.supplier_search_tree.insert("", "end", values=(
                supplier['supplier_id'],
                supplier['name'],
                supplier['contact'],
                supplier['email'],
                supplier['address']
            ))

    def reset_supplier_search(self):
        self.supplier_search_term_entry.delete(0, tk.END)
        self.load_suppliers()

    def edit_selected_supplier(self):
        selected_item = self.supplier_search_tree.selection()

        if not selected_item:
            messagebox.showerror("Error", "Please select a supplier to edit")
            return

        # Get supplier ID from selected item
        supplier_id = self.supplier_search_tree.item(selected_item[0], 'values')[0]

        # Get supplier from database
        supplier = self.supplier_repo.get_supplier_by_id(supplier_id)

        if supplier:
            # Clear form
            self.clear_supplier_form()

            # Fill form with supplier data
            self.supplier_entries["Supplier ID"].insert(0, supplier['supplier_id'])
            self.supplier_entries["Supplier Name"].insert(0, supplier['name'])
            self.supplier_entries["Contact No"].insert(0, supplier['contact'])
            self.supplier_entries["Email ID"].insert(0, supplier['email'] or "")
            self.supplier_entries["Address"].insert(0, supplier['address'] or "")

            # Switch to Add Supplier tab
            self.notebook.select(2)  # Select Suppliers tab
            supplier_notebook = self.suppliers_tab.winfo_children()[0]
            supplier_notebook.select(0)  # Select Add Supplier tab
        else:
            messagebox.showerror("Error", f"Supplier with ID {supplier_id} not found")

    def delete_selected_supplier(self):
        selected_item = self.supplier_search_tree.selection()

        if not selected_item:
            messagebox.showerror("Error", "Please select a supplier to delete")
            return

        # Get supplier ID from selected item
        supplier_id = self.supplier_search_tree.item(selected_item[0], 'values')[0]

        # Confirm deletion
        confirm = messagebox.askyesno("Confirm", f"Are you sure you want to delete supplier {supplier_id}?")

        if confirm:
            # Delete supplier from database
            success = self.supplier_repo.delete_supplier(supplier_id)

            if success:
                messagebox.showinfo("Success", "Supplier deleted successfully")
                self.load_suppliers()

    def view_supplier_supplies(self):
        selected_item = self.supplier_search_tree.selection()

        if not selected_item:
            messagebox.showerror("Error", "Please select a supplier to view supplies")
            return

        # Get supplier ID from selected item
        supplier_id = self.supplier_search_tree.item(selected_item[0], 'values')[0]
        supplier_name = self.supplier_search_tree.item(selected_item[0], 'values')[1]

        # Switch to Supply Records tab
        self.notebook.select(2)  # Select Suppliers tab
        supplier_notebook = self.suppliers_tab.winfo_children()[0]
        supplier_notebook.select(2)  # Select Supply Records tab

        # Set supplier in dropdown
        self.supplier_combo.set(supplier_name)

        # Search supplies
        self.search_supplies()

    def load_supplies(self):
        # Clear treeview
        for item in self.supply_tree.get_children():
            self.supply_tree.delete(item)

        # Get all supplies from database
        supplies = self.supplier_repo.get_supply_records()

        # Add supplies to treeview
        for supply in supplies:
            self.supply_tree.insert("", "end", values=(
                supply['supplier_id'],
                supply['supplier_name'],
                supply['medicine_name'],
                supply['quantity'],
                f"₹{supply['amount']}",
                supply['supply_date'].strftime('%Y-%m-%d')
            ))

    def search_supplies(self):
        supplier_name = self.supplier_combo.get()
        from_date = self.from_date_supply.get_date()
        to_date = self.to_date_supply.get_date()

        # Get supplier ID from name
        supplier_id = None
        if supplier_name != "All Suppliers":
            suppliers = self.supplier_repo.get_all_suppliers()
            for supplier in suppliers:
                if supplier['name'] == supplier_name:
                    supplier_id = supplier['supplier_id']
                    break

        # Clear treeview
        for item in self.supply_tree.get_children():
            self.supply_tree.delete(item)

        # Search supplies in database
        supplies = self.supplier_repo.get_supply_records(supplier_id, from_date, to_date)

        # Add supplies to treeview
        for supply in supplies:
            self.supply_tree.insert("", "end", values=(
                supply['supplier_id'],
                supply['supplier_name'],
                supply['medicine_name'],
                supply['quantity'],
                f"₹{supply['amount']}",
                supply['supply_date'].strftime('%Y-%m-%d')
            ))

    def setup_billing_tab(self):
        # Create a main frame with scrollbar for billing tab
        container = ttk.Frame(self.billing_tab)
        container.pack(fill="both", expand=True)

        # Add a canvas for scrolling
        canvas = tk.Canvas(container)
        canvas.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollbar.pack(side="right", fill="y")

        canvas.configure(yscrollcommand=scrollbar.set)

        # Create an inner frame for content inside the canvas
        billing_frame = ttk.Frame(canvas)
        canvas_window = canvas.create_window((0, 0), window=billing_frame, anchor="nw")

        # Configure scrolling behavior
        billing_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        # Section 1: Customer Details
        customer_frame = ttk.LabelFrame(billing_frame, text="Customer Details")
        customer_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        # Customer search section
        search_frame = ttk.Frame(customer_frame)
        search_frame.pack(fill="x", padx=10, pady=5)

        search_label = ttk.Label(search_frame, text="Search Customer:")
        search_label.pack(side="left", padx=5)

        self.customer_search_entry = ttk.Entry(search_frame, width=20)
        self.customer_search_entry.pack(side="left", padx=5)

        search_btn = ttk.Button(search_frame, text="Search", command=self.search_customer_for_bill)
        search_btn.pack(side="left", padx=5)

        # Customer fields section
        fields_frame = ttk.Frame(customer_frame)
        fields_frame.pack(fill="x", padx=10, pady=5)

        customer_fields = [
            ("Customer ID:", 0, 0),
            ("Customer Name:", 0, 2),
            ("Contact No:", 1, 0),
            ("Email:", 1, 2),
            ("Address:", 2, 0)
        ]

        self.customer_bill_entries = {}

        for label_text, row, col in customer_fields:
            label = ttk.Label(fields_frame, text=label_text)
            label.grid(row=row, column=col, padx=10, pady=5, sticky="w")

            if label_text == "Address:":
                entry = ttk.Entry(fields_frame, width=50)
                entry.grid(row=row, column=col+1, columnspan=3, padx=10, pady=5, sticky="w")
            else:
                entry = ttk.Entry(fields_frame, width=20)
                entry.grid(row=row, column=col+1, padx=10, pady=5, sticky="w")

            self.customer_bill_entries[label_text.replace(":", "")] = entry

        # Buttons for customer actions
        generate_id_btn = ttk.Button(fields_frame, text="Generate ID", command=self.generate_customer_id)
        generate_id_btn.grid(row=0, column=1, padx=(200, 0), pady=5, sticky="w")

        new_customer_btn = ttk.Button(fields_frame, text="Add as New Customer", command=self.add_new_customer)
        new_customer_btn.grid(row=3, column=0, padx=10, pady=5, sticky="w")

        clear_customer_btn = ttk.Button(fields_frame, text="Clear", command=self.clear_customer_form)
        clear_customer_btn.grid(row=3, column=2, padx=10, pady=5, sticky="w")

        # Section 2: Bill Creation
        bill_frame = ttk.LabelFrame(billing_frame, text="Create Bill")
        bill_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        # Medicine details treeview section
        medicine_frame = ttk.LabelFrame(bill_frame, text="Medicine Details")
        medicine_frame.pack(fill="both", expand=True, padx=10, pady=10)

        columns = ("Medicine ID", "Medicine Name", "Quantity", "Price (₹)", "Amount (₹)")
        self.billing_tree = ttk.Treeview(medicine_frame, columns=columns, show="headings", height=6)

        for col in columns:
            self.billing_tree.heading(col, text=col)
            width = 150 if col == "Medicine Name" else 100
            self.billing_tree.column(col, width=width, anchor="center")

        self.billing_tree.pack(fill="both", expand=True, padx=10, pady=10)

        # Add medicine section
        add_med_frame = ttk.LabelFrame(bill_frame, text="Add Medicine to Bill")
        add_med_frame.pack(fill="x", padx=10, pady=10)

        search_row = ttk.Frame(add_med_frame)
        search_row.pack(fill="x", padx=5, pady=5)

        med_search_label = ttk.Label(search_row, text="Search Medicine:")
        med_search_label.pack(side="left", padx=5)

        self.med_search_entry = ttk.Entry(search_row, width=20)
        self.med_search_entry.pack(side="left", padx=5)

        med_search_btn = ttk.Button(search_row, text="Search", command=self.search_medicine_for_bill)
        med_search_btn.pack(side="left", padx=5)

        selection_row = ttk.Frame(add_med_frame)
        selection_row.pack(fill="x", padx=5, pady=5)

        med_label = ttk.Label(selection_row, text="Medicine:")
        med_label.pack(side="left", padx=5)

        medicines = self.medicine_repo.get_all_medicines()
        medicine_names = [medicine['name'] for medicine in medicines]

        self.med_combo = ttk.Combobox(selection_row, width=20, font=self.normal_font, values=medicine_names)
        self.med_combo.pack(side="left", padx=5)

        qty_label = ttk.Label(selection_row, text="Quantity:")
        qty_label.pack(side="left", padx=5)

        self.qty_entry = ttk.Entry(selection_row, width=10)
        self.qty_entry.pack(side="left", padx=5)

        button_row = ttk.Frame(add_med_frame)
        button_row.pack(fill="x", padx=5, pady=10)

        # Adjusted the size of the Add Medicine button
        add_btn = ttk.Button(button_row, text="Add Medicine", command=self.add_medicine_to_bill)
        add_btn.pack(side="left", padx=10)

        remove_btn = ttk.Button(button_row, text="Remove Selected", command=self.remove_medicine_from_bill)
        remove_btn.pack(side="left", padx=10)

        # Billing summary section
        total_frame = ttk.LabelFrame(bill_frame, text="Billing Summary")
        total_frame.pack(fill="x", padx=10, pady=10)

        subtotal_label = ttk.Label(total_frame, text="Subtotal:")
        subtotal_label.grid(row=0, column=0, padx=5, pady=5, sticky="e")

        self.subtotal_amount = ttk.Label(total_frame, text="₹0.00")
        self.subtotal_amount.grid(row=0, column=1, padx=5, pady=5, sticky="e")

        tax_label = ttk.Label(total_frame, text="Tax (18%):")
        tax_label.grid(row=1, column=0, padx=5, pady=5, sticky="e")

        self.tax_amount = ttk.Label(total_frame, text="₹0.00")
        self.tax_amount.grid(row=1, column=1, padx=5, pady=5, sticky="e")

        total_label = ttk.Label(total_frame, text="Total Amount:")
        total_label.grid(row=2, column=0, padx=5, pady=5, sticky="e")

        self.total_amount = ttk.Label(total_frame, text="₹0.00")
        self.total_amount.grid(row=2, column=1, padx=5, pady=5, sticky="e")

        button_frame = ttk.Frame(bill_frame)
        button_frame.pack(fill="x", padx=10, pady=10)

        clear_bill_btn = ttk.Button(button_frame, text="Clear Bill", command=self.clear_bill)
        clear_bill_btn.pack(side="left", padx=10)

        generate_btn = ttk.Button(button_frame, text="Generate Bill", command=self.generate_bill)
        generate_btn.pack(side="left", padx=10)
        self.bill_items = []

        def configure_content_frame(event):
            canvas.itemconfig(canvas_window, width=event.width)

        canvas.bind('<Configure>', lambda event: [configure_content_frame(event),
                                                  canvas.configure(scrollregion=canvas.bbox("all"))])

        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        billing_frame.bind("<Enter>", lambda e: canvas.bind_all("<MouseWheel>", _on_mousewheel))
        billing_frame.bind("<Leave>", lambda e: canvas.unbind_all("<MouseWheel>"))
    
    def generate_customer_id(self):
        # Generate a unique customer ID
        customer_id = f"CUST{random.randint(1000, 9999)}"
        self.customer_bill_entries["Customer ID"].delete(0, tk.END)
        self.customer_bill_entries["Customer ID"].insert(0, customer_id)
    
    def search_customer_for_bill(self):
        search_term = self.customer_search_entry.get()
        
        if not search_term:
            messagebox.showerror("Error", "Please enter a search term")
            return
        
        # Search customers in database
        customers = self.customer_repo.search_customers(search_term)
        
        if not customers:
            messagebox.showinfo("Info", "No customers found")
            return
        
        # If only one customer found, fill the form
        if len(customers) == 1:
            self.fill_customer_form(customers[0])
        else:
            # Create a selection dialog
            self.create_customer_selection_dialog(customers)
    
    def create_customer_selection_dialog(self, customers):
        # Create a new top-level window
        selection_window = tk.Toplevel(self.root)
        selection_window.title("Select Customer")
        selection_window.geometry("600x400")
        selection_window.transient(self.root)  # Set as transient to parent window
        selection_window.grab_set()  # Make window modal
        
        # Create a frame for the treeview
        frame = ttk.Frame(selection_window, padding=10)
        frame.pack(fill="both", expand=True)
        
        # Create treeview for customers
        columns = ("ID", "Name", "Contact", "Email", "Address")
        customer_tree = ttk.Treeview(frame, columns=columns, show="headings", height=10)
        
        # Configure columns
        for col in columns:
            customer_tree.heading(col, text=col)
            width = 200 if col == "Address" else 100
            customer_tree.column(col, width=width, anchor="center")
        
        customer_tree.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=customer_tree.yview)
        scrollbar.pack(side="right", fill="y")
        customer_tree.configure(yscrollcommand=scrollbar.set)
        
        # Add customers to treeview
        for customer in customers:
            customer_tree.insert("", "end", values=(
                customer['customer_id'],
                customer['name'],
                customer['contact'],
                customer['email'],
                customer['address']
            ))
        
        # Add select button
        select_btn = ttk.Button(frame, text="Select", command=lambda: self.select_customer(customer_tree, customers, selection_window))
        select_btn.pack(pady=10)
    
    def select_customer(self, tree, customers, window):
        selected_item = tree.selection()
        
        if not selected_item:
            messagebox.showerror("Error", "Please select a customer")
            return
        
        # Get customer ID from selected item
        customer_id = tree.item(selected_item[0], 'values')[0]
        
        # Find customer in list
        selected_customer = None
        for customer in customers:
            if customer['customer_id'] == customer_id:
                selected_customer = customer
                break
        
        if selected_customer:
            # Fill customer form
            self.fill_customer_form(selected_customer)
            
            # Close selection window
            window.destroy()
    
    def fill_customer_form(self, customer):
        # Clear form
        self.clear_customer_form()
        
        # Fill form with customer data
        self.customer_bill_entries["Customer ID"].insert(0, customer['customer_id'])
        self.customer_bill_entries["Customer Name"].insert(0, customer['name'])
        self.customer_bill_entries["Contact No"].insert(0, customer['contact'])
        self.customer_bill_entries["Email"].insert(0, customer['email'] or "")
        self.customer_bill_entries["Address"].insert(0, customer['address'] or "")
    
    def clear_customer_form(self):
        # Clear all entry fields
        for entry in self.customer_bill_entries.values():
            entry.delete(0, tk.END)
        
    def add_new_customer(self):
        # Get data from form
        customer_data = {
            'customer_id': self.customer_bill_entries["Customer ID"].get(),
            'name': self.customer_bill_entries["Customer Name"].get(),
            'contact': self.customer_bill_entries["Contact No"].get(),
            'email': self.customer_bill_entries["Email"].get(),
            'address': self.customer_bill_entries["Address"].get()
        }
        
        # Validate data
        if not customer_data['customer_id'] or not customer_data['name'] or not customer_data['contact']:
            messagebox.showerror("Error", "Customer ID, Name, and Contact are required fields")
            return
        
        # Add customer to database
        success = self.customer_repo.add_customer(customer_data)
        
        if success:
            messagebox.showinfo("Success", "Customer added successfully")
    
    def search_medicine_for_bill(self):
        search_term = self.med_search_entry.get()
        
        if not search_term:
            messagebox.showerror("Error", "Please enter a search term")
            return
        
        # Search medicines in database
        medicines = self.medicine_repo.search_medicines("Name", search_term)
        
        if not medicines:
            messagebox.showinfo("Info", "No medicines found")
            return
        
        # Update medicine dropdown
        medicine_names = [medicine['name'] for medicine in medicines]
        self.med_combo['values'] = medicine_names
        
        # If only one medicine found, select it
        if len(medicines) == 1:
            self.med_combo.set(medicines[0]['name'])
    
    def add_medicine_to_bill(self):
        medicine_name = self.med_combo.get()
        quantity = self.qty_entry.get()
        
        if not medicine_name:
            messagebox.showerror("Error", "Please select a medicine")
            return
        
        if not quantity:
            messagebox.showerror("Error", "Please enter a quantity")
            return
        
        try:
            quantity = int(quantity)
            if quantity <= 0:
                raise ValueError("Quantity must be positive")
        except ValueError:
            messagebox.showerror("Error", "Quantity must be a positive integer")
            return
        
        # Get medicine from database
        medicines = self.medicine_repo.search_medicines("Name", medicine_name)
        
        if not medicines:
            messagebox.showerror("Error", f"Medicine {medicine_name} not found")
            return
        
        medicine = medicines[0]
        
        # Check if quantity is available
        if quantity > int(medicine['quantity']):
            messagebox.showerror("Error", f"Only {medicine['quantity']} units of {medicine_name} available")
            return
        
        # Calculate amount
        price = float(medicine['price'])
        amount = price * quantity
        
        # Add to treeview
        self.billing_tree.insert("", "end", values=(
            medicine['medicine_id'],
            medicine['name'],
            quantity,
            f"₹{price:.2f}",
            f"₹{amount:.2f}"
        ))
        
        # Add to bill items
        self.bill_items.append({
            'medicine_id': medicine['medicine_id'],
            'medicine_name': medicine['name'],
            'quantity': quantity,
            'price': f"{price:.2f}",
            'amount': f"{amount:.2f}"
        })
        
        # Update totals
        self.update_bill_totals()
        
        # Clear medicine selection
        self.med_combo.set("")
        self.qty_entry.delete(0, tk.END)
    
    def remove_medicine_from_bill(self):
        selected_item = self.billing_tree.selection()
        
        if not selected_item:
            messagebox.showerror("Error", "Please select a medicine to remove")
            return
        
        # Get medicine ID from selected item
        medicine_id = self.billing_tree.item(selected_item[0], 'values')[0]
        
        # Remove from bill items
        self.bill_items = [item for item in self.bill_items if item['medicine_id'] != medicine_id]
        
        # Remove from treeview
        self.billing_tree.delete(selected_item)
        
        # Update totals
        self.update_bill_totals()
    
    def update_bill_totals(self):
        # Calculate subtotal
        subtotal = sum(float(item['amount']) for item in self.bill_items)
        
        # Calculate tax (18%)
        tax = subtotal * 0.18
        
        # Calculate total
        total = subtotal + tax
        
        # Update labels
        self.subtotal_amount.config(text=f"₹{subtotal:.2f}")
        self.tax_amount.config(text=f"₹{tax:.2f}")
        self.total_amount.config(text=f"₹{total:.2f}")
    
    def clear_bill(self):
        # Clear customer form
        self.clear_customer_form()
        
        # Clear medicine treeview
        for item in self.billing_tree.get_children():
            self.billing_tree.delete(item)
        
        # Clear bill items
        self.bill_items = []
        
        # Reset totals
        self.subtotal_amount.config(text="₹0.00")
        self.tax_amount.config(text="₹0.00")
        self.total_amount.config(text="₹0.00")
        self.customer_search_entry.delete(0, tk.END)
        self.med_search_entry.delete(0, tk.END)


    def generate_bill(self):
        # Check if customer is selected
        customer_id = self.customer_bill_entries["Customer ID"].get()
        
        if not customer_id:
            messagebox.showerror("Error", "Please select or add a customer")
            return
        
        # Check if there are items in the bill
        if not self.bill_items:
            messagebox.showerror("Error", "Please add at least one medicine to the bill")
            return
        
        # Generate bill ID
        bill_id = f"BILL-{random.randint(1000, 9999)}"
        
        # Get customer details
        customer_name = self.customer_bill_entries["Customer Name"].get()
        customer_contact = self.customer_bill_entries["Contact No"].get()
        customer_address = self.customer_bill_entries["Address"].get()
        
        # Get current date
        current_date = datetime.datetime.now().strftime("%Y-%m-%d")
        
        # Calculate totals
        subtotal = sum(float(item['amount']) for item in self.bill_items)
        tax = subtotal * 0.18
        total = subtotal + tax
        
        # Format currency values
        subtotal_formatted = f"{subtotal:.2f}"
        tax_formatted = f"{tax:.2f}"
        total_formatted = f"{total:.2f}"
        
        # Create bill data
        bill_data = {
            'bill_id': bill_id,
            'customer_id': customer_id,
            'customer_name': customer_name,
            'customer_contact': customer_contact,
            'customer_address': customer_address,
            'date': current_date,
            'items': self.bill_items,
            'subtotal': subtotal_formatted,
            'tax': tax_formatted,
            'total': total_formatted
        }
        
        # Save bill to database
        success = self.billing_repo.create_bill(bill_data)
        
        if success:
            # Show bill preview
            bill_preview = BillPreviewWindow(self.root, bill_data)
            
            # Clear bill form for next bill
            self.clear_bill()
            
            # Refresh medicines (quantities have changed)
            self.load_medicines()

    def setup_billing_history_tab(self):
        # Create a frame for billing history
        history_frame = ttk.Frame(self.billing_history_tab)
        history_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Add search functionality
        search_frame = ttk.LabelFrame(history_frame, text="Search Options")
        search_frame.pack(fill="x", padx=10, pady=10)

        # Search by options
        search_by_label = ttk.Label(search_frame, text="Search By:")
        search_by_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        self.bill_search_by_var = tk.StringVar()
        search_by_combo = ttk.Combobox(search_frame, textvariable=self.bill_search_by_var, width=15)
        search_by_combo['values'] = ('Bill ID', 'Customer Name', 'Customer ID', 'Date')
        search_by_combo.current(0)
        search_by_combo.grid(row=0, column=1, padx=10, pady=10, sticky="w")

        # Search term
        search_term_label = ttk.Label(search_frame, text="Search Term:")
        search_term_label.grid(row=0, column=2, padx=10, pady=10, sticky="w")

        self.bill_search_entry = ttk.Entry(search_frame, width=25)
        self.bill_search_entry.grid(row=0, column=3, padx=10, pady=10, sticky="w")

        # Search button
        search_btn = ttk.Button(search_frame, text="Search", command=self.search_bills)
        search_btn.grid(row=0, column=4, padx=10, pady=10)

        # Add date range filter
        date_frame = ttk.Frame(search_frame)
        date_frame.grid(row=1, column=0, columnspan=5, padx=10, pady=10, sticky="w")

        date_range_label = ttk.Label(date_frame, text="Date Range:")
        date_range_label.pack(side="left", padx=5)

        from_label = ttk.Label(date_frame, text="From:")
        from_label.pack(side="left", padx=5)

        self.from_date = DateEntry(date_frame, width=12, background=self.primary_color,
                                   foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd',
                                   font=self.normal_font)
        self.from_date.pack(side="left", padx=5)

        to_label = ttk.Label(date_frame, text="To:")
        to_label.pack(side="left", padx=5)

        self.to_date = DateEntry(date_frame, width=12, background=self.primary_color,
                                 foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd',
                                 font=self.normal_font)
        self.to_date.pack(side="left", padx=5)

        filter_btn = ttk.Button(date_frame, text="Filter", command=self.filter_bills_by_date)
        filter_btn.pack(side="left", padx=5)

        # Create treeview for billing history
        results_frame = ttk.LabelFrame(history_frame, text="Billing History")
        results_frame.pack(fill="both", expand=True, padx=10, pady=10)

        columns = ("Bill ID", "Customer ID", "Customer Name", "Medicines", "Amount (₹)", "Date")
        self.history_tree = ttk.Treeview(results_frame, columns=columns, show="headings", height=15)

        # Configure columns
        for col in columns:
            self.history_tree.heading(col, text=col)
            if col == "Customer Name":
                width = 150
            elif col == "Medicines":
                width = 250  # Wider column for medicines list
            else:
                width = 120
            self.history_tree.column(col, width=width, anchor="center")

        self.history_tree.pack(fill="both", expand=True, padx=10, pady=10)

        # Add scrollbar
        scrollbar = ttk.Scrollbar(results_frame, orient="vertical", command=self.history_tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.history_tree.configure(yscrollcommand=scrollbar.set)

        # Action buttons
        action_frame = ttk.Frame(history_frame)
        action_frame.pack(fill="x", padx=10, pady=10)

        view_btn = ttk.Button(action_frame, text="View Bill Details", command=self.view_bill_details)
        view_btn.pack(side="left", padx=5)

        print_btn = ttk.Button(action_frame, text="Print Bill", command=self.print_bill)
        print_btn.pack(side="left", padx=5)

        # Load bills
        self.load_bills()

        # Add this to refresh whenever the tab is selected
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)

    def on_tab_changed(self, event):
        if self.notebook.index("current") == 4:  # Billing History tab is index 4
            self.load_bills()

    def load_bills(self):
        # Clear treeview
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)

        # Get all bills from database
        bills = self.billing_repo.get_all_bills()

        # Add bills to treeview
        for bill in bills:
            self.history_tree.insert("", "end", values=(
                bill['bill_id'],
                bill['customer_id'],
                bill['customer_name'],
                bill.get('medicines', 'N/A'),  # Added medicines column
                f"₹{bill['total']}",
                bill['bill_date'].strftime('%Y-%m-%d')
            ))

    def search_bills(self):
        search_by = self.bill_search_by_var.get()
        search_term = self.bill_search_entry.get()

        if not search_term:
            messagebox.showerror("Error", "Please enter a search term")
            return

        # Clear treeview
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)

        # Search bills in database
        bills = self.billing_repo.search_bills(search_by, search_term)

        # Add bills to treeview
        for bill in bills:
            self.history_tree.insert("", "end", values=(
                bill['bill_id'],
                bill['customer_id'],
                bill['customer_name'],
                bill.get('medicines', 'N/A'),  # Added medicines column
                f"₹{bill['total']}",
                bill['bill_date'].strftime('%Y-%m-%d')
            ))

    def filter_bills_by_date(self):
        from_date = self.from_date.get_date()
        to_date = self.to_date.get_date()

        # Clear treeview
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)

        # Filter bills in database
        bills = self.billing_repo.filter_bills_by_date(from_date, to_date)

        # Add bills to treeview
        for bill in bills:
            self.history_tree.insert("", "end", values=(
                bill['bill_id'],
                bill['customer_id'],
                bill['customer_name'],
                bill.get('medicines', 'N/A'),  # Added medicines column
                f"₹{bill['total']}",
                bill['bill_date'].strftime('%Y-%m-%d')
            ))

    def view_bill_details(self):
        selected_item = self.history_tree.selection()

        if not selected_item:
            messagebox.showerror("Error", "Please select a bill to view")
            return

        # Get bill ID from selected item
        bill_id = self.history_tree.item(selected_item[0], 'values')[0]

        # Get bill details from database
        bill_data = self.billing_repo.get_bill_details(bill_id)

        if bill_data:
            # Show bill preview
            bill_preview = BillPreviewWindow(self.root, bill_data)
        else:
            messagebox.showerror("Error", f"Bill with ID {bill_id} not found")
    
    def print_bill(self):
        selected_item = self.history_tree.selection()

        if not selected_item:
            messagebox.showerror("Error", "Please select a bill to print")
            return

        # Get bill ID from selected item
        bill_id = self.history_tree.item(selected_item[0], 'values')[0]

        # Get bill details from database
        bill_data = self.billing_repo.get_bill_details(bill_id)

        if bill_data:
            # Generate PDF
            pdf_generator = PDFGenerator()

            # Create a temporary file
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
                temp_path = temp_file.name

            success = pdf_generator.generate_bill_pdf(bill_data, temp_path)

            if success:
                # Open PDF with default viewer
                os.startfile(temp_path)
            else:
                messagebox.showerror("Error", "Failed to generate PDF")
        else:
            messagebox.showerror("Error", f"Bill with ID {bill_id} not found")

    def setup_reports_tab(self):
        report_frame = ttk.LabelFrame(self.reports_tab, text="Sales Analysis")
        report_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Button to generate sales chart
        generate_btn = ttk.Button(report_frame, text="View Monthly Sales Chart", command=self.show_sales_chart)
        generate_btn.pack(pady=10)
        
        bestseller_btn = ttk.Button(report_frame, text="View Best Sellers", command=self.show_best_sellers)
        bestseller_btn.pack(pady=10)


    # Frame to hold the chart
        self.chart_frame = ttk.Frame(report_frame)
        self.chart_frame.pack(fill="both", expand=True)

    def show_sales_chart(self):
        # Clear previous chart if any
        for widget in self.chart_frame.winfo_children():
            widget.destroy()

        # Get sales data
        bills = self.billing_repo.get_all_bills()

        if not bills:
            messagebox.showinfo("Info", "No billing data available for chart.")
            return

        # Create DataFrame
        df = pd.DataFrame(bills)
        df['bill_date'] = pd.to_datetime(df['bill_date'])
        df['month'] = df['bill_date'].dt.to_period('M').astype(str)
        df['total'] = pd.to_numeric(df['total'])

        monthly_sales = df.groupby('month')['total'].sum().reset_index()

        # Plot chart
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.bar(monthly_sales['month'], monthly_sales['total'], color="#00eab7")
        ax.set_title("Monthly Sales Report", fontsize=14)
        ax.set_xlabel("Month")
        ax.set_ylabel("Total Sales (₹)")
        ax.grid(True)

        # Embed in Tkinter
        canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def show_best_sellers(self):
        """Displays the top 10 best-selling medicines in the reports section."""

        # Clear previous content in the chart frame
        for widget in self.chart_frame.winfo_children():
            widget.destroy()

        # Fetch billing and medicine data
        bill_items = self.billing_repo.get_all_bill_items()
        medicines = self.medicine_repo.get_all_medicines()

        if not bill_items or not medicines:
            messagebox.showinfo("Info", "No billing data available.")
            return

        # Convert to DataFrames
        items_df = pd.DataFrame(bill_items)
        meds_df = pd.DataFrame(medicines)

        # Sanitize bill items (remove invalid rows)
        items_df = items_df[items_df['quantity'] != 'quantity']  # Remove header-like rows if accidentally inserted
        items_df['quantity'] = pd.to_numeric(items_df['quantity'], errors='coerce')
        items_df.dropna(subset=['quantity'], inplace=True)
        items_df['quantity'] = items_df['quantity'].astype(int)

        # Standardize ID format for merging
        items_df['medicine_id'] = items_df['medicine_id'].astype(str)
        meds_df['medicine_id'] = meds_df['medicine_id'].astype(str)

        # Aggregate total quantity sold per medicine
        best_sellers = (
            items_df.groupby('medicine_id')['quantity']
            .sum()
            .reset_index()
            .sort_values(by='quantity', ascending=False)
            .head(10)
        )

        # Merge to get medicine names
        best_sellers = best_sellers.merge(
            meds_df[['medicine_id', 'name']],
            on='medicine_id',
            how='left'
        )
        
        # Display in a TreeView
        tree = ttk.Treeview(
            self.chart_frame,
            columns=("Name", "Total Sold"),
            show="headings",
            height=10
        )
        tree.heading("Name", text="Medicine Name")
        tree.heading("Total Sold", text="Total Quantity Sold")
        tree.column("Name", anchor="w", width=200)
        tree.column("Total Sold", anchor="center", width=150)

        for _, row in best_sellers.iterrows():
            name = row['name'] if pd.notnull(row['name']) else "Unknown"
            quantity = row['quantity']
            tree.insert("", "end", values=(name, quantity))

        tree.pack(fill="both", expand=True, padx=10, pady=10)

        
    def setup_stock_alerts_tab(self):
        alert_frame = ttk.LabelFrame(self.stock_alerts_tab, text="Low Stock Medicines (Below 10)")
        alert_frame.pack(fill="both", expand=True, padx=20, pady=20)

        self.stock_tree = ttk.Treeview(alert_frame, columns=("ID", "Name", "Quantity", "Expiry", "Location"), show="headings")
        for col in self.stock_tree["columns"]:
            self.stock_tree.heading(col, text=col)
            self.stock_tree.column(col, anchor="center")
        self.stock_tree.pack(fill="both", expand=True, padx=10, pady=10)

        refresh_btn = ttk.Button(alert_frame, text="Load", command=self.load_low_stock_medicines)
        refresh_btn.pack(pady=10)

        #self.load_low_stock_medicines()

    def on_tab_change(self, event):
        selected_tab = event.widget.select()
        tab_text = event.widget.tab(selected_tab, "text")

        if tab_text == "Stock Alerts":
            self.load_low_stock_medicines()
   
    def load_low_stock_medicines(self):
        # Clear table
        for item in self.stock_tree.get_children():
            self.stock_tree.delete(item)

        medicines = self.medicine_repo.get_all_medicines()

        if not medicines:
            messagebox.showinfo("Info", "No medicine data available.")
            return

        df = pd.DataFrame(medicines)
        df['quantity'] = pd.to_numeric(df['quantity'])
        low_stock_df = df[df['quantity'] < 10]

        for _, row in low_stock_df.iterrows():
            self.stock_tree.insert("", "end", values=(
                row['medicine_id'],
                row['name'],
                row['quantity'],
                row['expiry_date'].strftime('%Y-%m-%d') if pd.notnull(row['expiry_date']) else "N/A",
                row['location']
            ))
