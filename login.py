import tkinter as tk
from tkinter import ttk, messagebox
import database
from admin_panel import create_admin_panel

def create_login_window(parent=None):
    """Create login window with working input fields."""
    login_window = tk.Toplevel(parent)
    login_window.title("Nova Movies - Login")
    login_window.configure(bg='#080808')
    
    # Set larger window size
    window_width = 500
    window_height = 600
    screen_width = login_window.winfo_screenwidth()
    screen_height = login_window.winfo_screenheight()
    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2
    login_window.geometry(f'{window_width}x{window_height}+{x}+{y}')
    
    # Create main container
    main_frame = tk.Frame(login_window, bg='#080808')
    main_frame.pack(expand=True, fill='both', padx=50, pady=30)
    
    # Create frames for login and register forms
    login_frame = tk.Frame(main_frame, bg='#080808')
    register_frame = tk.Frame(main_frame, bg='#080808')
    
    # Variables to store entry widgets
    entries = {
        'login': {},
        'register': {}
    }

    def show_login_form():
        register_frame.pack_forget()
        login_frame.pack(expand=True, fill='both')
        login_window.geometry(f'{window_width}x{450}+{x}+{y}')  # Smaller height for login
        
    def show_register_form():
        login_frame.pack_forget()
        register_frame.pack(expand=True, fill='both')
        login_window.geometry(f'{window_width}x{window_height}+{x}+{y}')  # Full height for register

    def handle_login():
        username = entries['login']['username'].get().strip()
        password = entries['login']['password'].get().strip()
        
        if not username or not password:
            messagebox.showerror("Error", "Please fill in all fields")
            return
            
        user = database.check_login(username, password)
        if user:
            login_window.logged_in_user = user
            login_window.destroy()
        else:
            messagebox.showerror("Error", "Invalid username or password")

    def handle_register():
        name = entries['register']['name'].get().strip()
        username = entries['register']['username'].get().strip()
        password = entries['register']['password'].get().strip()
        confirm_password = entries['register']['confirm_password'].get().strip()
        phone = entries['register']['phone'].get().strip()
        
        # Validation
        if not all([name, username, password, confirm_password, phone]):
            messagebox.showerror("Error", "Please fill in all fields")
            return
            
        if password != confirm_password:
            messagebox.showerror("Error", "Passwords do not match")
            return
            
        if not phone.isdigit() or len(phone) != 10:
            messagebox.showerror("Error", "Please enter a valid 10-digit phone number")
            return
        
        # Try to register
        if database.register_user(name, username, password, phone):
            messagebox.showinfo("Success", "Registration successful! Please login.")
            show_login_form()
        else:
            messagebox.showerror("Error", "Username already exists")

    # Create login form
    tk.Label(login_frame, text="LOGIN", font="Helvetica 24 bold", 
            bg='#080808', fg='#ff3b3b').pack(pady=30)
    
    # Username
    tk.Label(login_frame, text="Username", bg='#080808', 
            fg='white', font="Helvetica 12").pack(pady=(0,5))
    entries['login']['username'] = tk.Entry(login_frame, font="Helvetica 12", width=30)
    entries['login']['username'].pack(pady=(0,15))
    
    # Password
    tk.Label(login_frame, text="Password", bg='#080808', 
            fg='white', font="Helvetica 12").pack(pady=(0,5))
    entries['login']['password'] = tk.Entry(login_frame, show="*", font="Helvetica 12", width=30)
    entries['login']['password'].pack(pady=(0,20))
    
    # Login button
    login_btn = tk.Button(login_frame, text="LOGIN", 
                         font="Helvetica 12 bold",
                         bg='#ff3b3b', fg='white',
                         width=25, height=2,
                         command=handle_login)
    login_btn.pack(pady=20)
    
    # Register link
    register_link = tk.Label(login_frame, text="Don't have an account? Register",
                           font="Helvetica 10", bg='#080808', fg='#ff3b3b',
                           cursor="hand2")
    register_link.pack(pady=20)
    register_link.bind("<Button-1>", lambda e: show_register_form())

    # Create register form
    tk.Label(register_frame, text="REGISTER", font="Helvetica 24 bold",
            bg='#080808', fg='#ff3b3b').pack(pady=30)
    
    # Registration fields
    fields = [
        ('name', "Full Name"),
        ('username', "Username"),
        ('password', "Password"),
        ('confirm_password', "Confirm Password"),
        ('phone', "Phone Number (10 digits)")
    ]
    
    for field_id, label in fields:
        tk.Label(register_frame, text=label, bg='#080808',
                fg='white', font="Helvetica 12").pack(pady=(10,5))
        entry = tk.Entry(register_frame, font="Helvetica 12", width=30,
                        show="*" if 'password' in field_id else "")
        entry.pack(pady=(0,10))
        entries['register'][field_id] = entry
    
    # Register button
    register_btn = tk.Button(register_frame, text="REGISTER",
                           font="Helvetica 12 bold",
                           bg='#ff3b3b', fg='white',
                           width=25, height=2,
                           command=handle_register)
    register_btn.pack(pady=20)
    
    # Login link
    login_link = tk.Label(register_frame, text="Already have an account? Login",
                        font="Helvetica 10", bg='#080808', fg='#ff3b3b',
                        cursor="hand2")
    login_link.pack(pady=20)
    login_link.bind("<Button-1>", lambda e: show_login_form())

    # Bind Enter key to submit
    login_window.bind('<Return>', lambda e: handle_login() if login_frame.winfo_viewable() else handle_register())
    
    # Show login form by default
    show_login_form()
    
    return login_window

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    create_login_window(root)
    root.mainloop()