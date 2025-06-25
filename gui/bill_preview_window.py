import tkinter as tk
from tkinter import ttk, messagebox, font, scrolledtext
from tkinter import filedialog
from pdf_generator import PDFGenerator

class BillPreviewWindow:
    def __init__(self, parent, bill_data):
        self.parent = parent
        self.bill_data = bill_data

        # Create a new top-level window
        self.window = tk.Toplevel(parent)
        self.window.title("Bill Preview")
        self.window.geometry("800x600")
        self.window.transient(parent)  # Set as transient to parent window
        self.window.grab_set()  # Make window modal

        # Set custom colors
        self.primary_color = "#6200ea"  # Deep purple
        self.secondary_color = "#03dac6"  # Teal
        self.bg_color = "#f5f5f5"  # Light gray
        self.text_color = "#212121"  # Dark gray

        # Create custom fonts
        self.title_font = font.Font(family="Segoe UI", size=16, weight="bold")
        self.header_font = font.Font(family="Segoe UI", size=12, weight="bold")
        self.normal_font = font.Font(family="Segoe UI", size=10)
        self.small_font = font.Font(family="Segoe UI", size=9)

        self.setup_bill_preview()

    def setup_bill_preview(self):
        # Configure window to be resizable and maximizable
        self.window.resizable(True, True)

        # Explicitly set window attributes to include maximize button
        # This works on Windows - different platforms may require different approaches
        if hasattr(self.window, 'attributes') and hasattr(self.window, 'state'):
            # For Windows
            self.window.attributes('-toolwindow', False)  # Ensure it's not a tool window
            self.window.state('normal')  # Set to normal state first

        # Set window title and icon
        self.window.title(f"Bill Preview - {self.bill_data['bill_id']}")

        # Main frame with padding
        main_frame = ttk.Frame(self.window, padding=20)
        main_frame.pack(fill="both", expand=True)

        # Create a canvas with scrollbar for scrolling
        canvas_frame = ttk.Frame(main_frame)
        canvas_frame.pack(fill="both", expand=True)

        # Create canvas
        canvas = tk.Canvas(canvas_frame)
        canvas.pack(side="left", fill="both", expand=True)

        # Add vertical scrollbar to canvas
        v_scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
        v_scrollbar.pack(side="right", fill="y")

        # Add horizontal scrollbar to canvas
        h_scrollbar = ttk.Scrollbar(canvas_frame, orient="horizontal", command=canvas.xview)
        h_scrollbar.pack(side="bottom", fill="x")

        # Configure the canvas
        canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        # Create a frame inside the canvas for the content
        content_frame = ttk.Frame(canvas, padding=10)
        canvas_window = canvas.create_window((0, 0), window=content_frame, anchor="nw")

        # Make the frame expand to the width of the canvas
        def configure_content_frame(event):
            canvas.itemconfig(canvas_window, width=event.width)

        canvas.bind('<Configure>', lambda event: [configure_content_frame(event),
                                                  canvas.configure(scrollregion=canvas.bbox("all"))])

        # Add mousewheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        # Bill header
        header_frame = ttk.Frame(content_frame)
        header_frame.pack(fill="x", pady=10)

        # Pharmacy name and logo
        pharmacy_label = ttk.Label(header_frame, text="Pharmacy Management System",
                                   font=self.title_font, foreground=self.primary_color)
        pharmacy_label.pack(side="left")

        # Bill title
        bill_title = ttk.Label(header_frame, text="INVOICE", font=self.title_font)
        bill_title.pack(side="right")

        # Separator
        separator = ttk.Separator(content_frame, orient="horizontal")
        separator.pack(fill="x", pady=10)

        # Bill info
        info_frame = ttk.Frame(content_frame)
        info_frame.pack(fill="x", pady=10)

        # Left side - Customer info
        customer_frame = ttk.LabelFrame(info_frame, text="Customer Information")
        customer_frame.pack(side="left", fill="x", expand=True, padx=(0, 10))

        customer_id_label = ttk.Label(customer_frame, text=f"Customer ID: {self.bill_data['customer_id']}")
        customer_id_label.pack(anchor="w", pady=2)

        customer_name_label = ttk.Label(customer_frame, text=f"Name: {self.bill_data['customer_name']}")
        customer_name_label.pack(anchor="w", pady=2)

        customer_contact_label = ttk.Label(customer_frame, text=f"Contact: {self.bill_data['customer_contact']}")
        customer_contact_label.pack(anchor="w", pady=2)

        customer_address_label = ttk.Label(customer_frame, text=f"Address: {self.bill_data['customer_address']}")
        customer_address_label.pack(anchor="w", pady=2)

        # Right side - Bill info
        bill_info_frame = ttk.LabelFrame(info_frame, text="Bill Information")
        bill_info_frame.pack(side="right", fill="x", expand=True)

        bill_id_label = ttk.Label(bill_info_frame, text=f"Bill No: {self.bill_data['bill_id']}")
        bill_id_label.pack(anchor="w", pady=2)

        bill_date_label = ttk.Label(bill_info_frame, text=f"Date: {self.bill_data['date']}")
        bill_date_label.pack(anchor="w", pady=2)

        # Items table
        items_frame = ttk.LabelFrame(content_frame, text="Items")
        items_frame.pack(fill="both", expand=True, pady=10)

        # Create table headers
        columns = ("S.No.",  "Medicine Name", "Quantity", "Price (₹)", "Amount (₹)")
        self.items_tree = ttk.Treeview(items_frame, columns=columns, show="headings", height=10)

        # Configure columns
        for col in columns:
            self.items_tree.heading(col, text=col)
            width = 150 if col == "Medicine Name" else 100
            self.items_tree.column(col, width=width, anchor="center")

        self.items_tree.pack(fill="both", expand=True, padx=5, pady=5)

        # Add scrollbar
        scrollbar = ttk.Scrollbar(items_frame, orient="vertical", command=self.items_tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.items_tree.configure(yscrollcommand=scrollbar.set)

        # Add items to the table
        for i, item in enumerate(self.bill_data['items'], 1):
            self.items_tree.insert("", "end", values=(
                i,
                
                item['medicine_name'],
                item['quantity'],
                item['price'],
                item['amount']
            ))

        # Totals
        totals_frame = ttk.Frame(content_frame)
        totals_frame.pack(fill="x", pady=10, anchor="e")

        # Create a grid for the totals
        totals_grid = ttk.Frame(totals_frame)
        totals_grid.pack(side="right")

        # Subtotal
        subtotal_label = ttk.Label(totals_grid, text="Subtotal:", font=self.normal_font)
        subtotal_label.grid(row=0, column=0, sticky="e", padx=5, pady=2)

        subtotal_value = ttk.Label(totals_grid, text=f"₹{self.bill_data['subtotal']}", font=self.normal_font)
        subtotal_value.grid(row=0, column=1, sticky="e", padx=5, pady=2)

        # Tax
        tax_label = ttk.Label(totals_grid, text="Tax (18%):", font=self.normal_font)
        tax_label.grid(row=1, column=0, sticky="e", padx=5, pady=2)

        tax_value = ttk.Label(totals_grid, text=f"₹{self.bill_data['tax']}", font=self.normal_font)
        tax_value.grid(row=1, column=1, sticky="e", padx=5, pady=2)

        # Separator
        separator = ttk.Separator(totals_grid, orient="horizontal")
        separator.grid(row=2, column=0, columnspan=2, sticky="ew", pady=5)

        # Total
        total_label = ttk.Label(totals_grid, text="Total:", font=self.header_font)
        total_label.grid(row=3, column=0, sticky="e", padx=5, pady=2)

        total_value = ttk.Label(totals_grid, text=f"₹{self.bill_data['total']}", font=self.header_font)
        total_value.grid(row=3, column=1, sticky="e", padx=5, pady=2)

        # Buttons directly below the totals
        button_frame = ttk.Frame(content_frame)
        button_frame.pack(fill="x", pady=15)

        save_btn = ttk.Button(button_frame, text="Save as PDF", command=self.save_as_pdf)
        save_btn.pack(side="right", padx=5)

        print_btn = ttk.Button(button_frame, text="Print", command=self.print_bill)
        print_btn.pack(side="right", padx=5)

        close_btn = ttk.Button(button_frame, text="Close", command=self.window.destroy)
        close_btn.pack(side="right", padx=5)

        # Footer
        footer_frame = ttk.Frame(content_frame)
        footer_frame.pack(fill="x", pady=10)

        thank_you_label = ttk.Label(footer_frame, text="Thank you !!!",
                                    font=self.header_font, foreground=self.primary_color)
        thank_you_label.pack(anchor="center", pady=5)

        terms_label = ttk.Label(footer_frame, text="Terms & Conditions Apply", font=self.small_font)
        terms_label.pack(anchor="center")

        # Clean up mousewheel binding when window is destroyed
        self.window.bind("<Destroy>", lambda e: canvas.unbind_all("<MouseWheel>"))

        # Set minimum size for the window
        self.window.update()
        self.window.minsize(800, 600)

        # Try to set the window to be maximizable using different approaches
        # This is platform-dependent, so we try multiple methods

        # Method 1: Using state (works on most platforms)
        try:
            self.window.state('zoomed')  # For Windows
        except:
            try:
                self.window.attributes('-zoomed', True)  # For some Unix systems
            except:
                pass

        # Method 2: Using geometry to set to screen size
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        self.window.geometry(f"{screen_width}x{screen_height}+0+0")

        # Method 3: For Tk 8.5+, try to use the zoomed state
        try:
            self.window.wm_state('zoomed')
        except:
            pass

    def save_as_pdf(self):
        """Save the current bill as a PDF file"""
        pdf_generator = PDFGenerator()

        # Ask user for save location
        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF Files", "*.pdf")],
            title="Save Bill As"
        )

        if file_path:
            success = pdf_generator.generate_bill_pdf(self.bill_data, file_path)
            if success:
                messagebox.showinfo("Success", f"Bill saved as PDF:\n{file_path}")
            else:
                messagebox.showerror("Error", "Failed to save PDF")

    def print_bill(self):
        # Placeholder for print functionality
        messagebox.showinfo("Print", "Printing functionality will be implemented here.")
        # In a real implementation, you would use a library like win32print or similar
        # to send the bill to a printer