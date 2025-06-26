import tkinter as tk
from tkinter import messagebox
from tkinter import ttk, messagebox, font, scrolledtext
from database.connection import DatabaseConnection
from repositories.user_repository import UserRepository

class LoginPage:
    def __init__(self, root, on_login_success):
        self.root = root
        self.on_login_success = on_login_success
        self.root.title("Pharmacy Management - Login")
        self.root.geometry("500x400")

        # Database connection
        self.db = DatabaseConnection()
        self.user_repo = UserRepository(self.db)

        # Set custom colors
        self.primary_color = "#6200ea"  # Deep purple
        self.secondary_color = "#03dac6"  # Teal
        self.bg_color = "#f5f5f5"  # Light gray
        self.text_color = "#212121"  # Dark gray

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
        self.style.configure("TLabel", background=self.bg_color, foreground=self.text_color, font=self.normal_font)
        self.style.configure("Header.TLabel", background=self.bg_color, foreground=self.primary_color,
                             font=self.header_font)
        self.style.configure("Title.TLabel", background=self.bg_color, foreground=self.primary_color,
                             font=self.title_font)

        # Configure button style
        self.style.configure("TButton", background=self.primary_color, foreground="#ffffff",
                             padding=8, font=self.button_font)
        self.style.map("TButton",
                       background=[("active", "#7c4dff")],
                       foreground=[("active", "#ffffff")])

        # Configure entry style
        self.style.configure("TEntry", font=self.normal_font, fieldbackground="#ffffff")

        self.setup_login_ui()

    def setup_login_ui(self):
        
        # Create header with gradient effect
        self.header_frame = tk.Frame(self.root, bg=self.primary_color, height=70)
        self.header_frame.pack(fill="x")

        # Create gradient effect (simulated with multiple frames)
        for i in range(3):
            gradient = tk.Frame(self.header_frame, bg=self.get_gradient_color(i), height=3)
            gradient.pack(fill="x")

        header_label = tk.Label(self.header_frame, text="Pharmacy Management System",
                                font=self.title_font, bg=self.primary_color, fg="#ffffff")
        header_label.pack(side="left", padx=20, pady=10)

        # Main container to center the login form
        main_container = ttk.Frame(self.root)
        main_container.pack(fill="both", expand=True)

        # Configure grid weights to center the form
        main_container.columnconfigure(0, weight=1)
        main_container.columnconfigure(2, weight=1)
        main_container.rowconfigure(0, weight=1)
        main_container.rowconfigure(2, weight=1)

        # Login frame - placed in the center cell of the grid
        login_frame = ttk.Frame(main_container, padding=20)
        login_frame.grid(row=1, column=1, sticky="nsew")

        # Login title
        login_title = ttk.Label(login_frame, text="Login", style="Title.TLabel")
        login_title.pack(pady=20)

        # Username
        username_label = ttk.Label(login_frame, text="Username:")
        username_label.pack(fill="x", pady=(10, 5))

        # Fixed width entry that won't stretch excessively
        username_container = ttk.Frame(login_frame)
        username_container.pack(fill="x", pady=5)
        username_container.columnconfigure(0, weight=1)
        username_container.columnconfigure(2, weight=1)

        self.username_entry = ttk.Entry(username_container, width=30)
        self.username_entry.grid(row=0, column=1)

        # Password
        password_label = ttk.Label(login_frame, text="Password:")
        password_label.pack(fill="x", pady=(10, 5))

        # Fixed width entry that won't stretch excessively
        password_container = ttk.Frame(login_frame)
        password_container.pack(fill="x", pady=5)
        password_container.columnconfigure(0, weight=1)
        password_container.columnconfigure(2, weight=1)

        self.password_entry = ttk.Entry(password_container, width=30, show="*")
        self.password_entry.grid(row=0, column=1)

        # Login button
        login_btn = ttk.Button(login_frame, text="Login", command=self.login)
        login_btn.pack(pady=20)

        # Bind Enter key to login
        self.root.bind('<Return>', lambda event: self.login())

        # Set focus to username entry
        self.username_entry.focus_set()

        # Create footer
        footer_frame = tk.Frame(self.root, bg=self.primary_color, height=25)
        footer_frame.pack(fill="x", side="bottom")

        footer_label = tk.Label(footer_frame, text="© 2025 Pharmacy Management",
                                font=("Segoe UI", 8), bg=self.primary_color, fg="#ffffff")
        footer_label.pack(side="right", padx=10, pady=3)

    def get_gradient_color(self, index):
        # Create a gradient effect
        colors = ["#7c4dff", "#651fff", "#6200ea"]
        return colors[index % len(colors)]

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        # Authenticate user
        user = self.user_repo.authenticate(username, password)

        if user:
            self.on_login_success()
            self.root.unbind('<Return>') 
        else:
            messagebox.showerror("Login Failed", "Invalid username or password")