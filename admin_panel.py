import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import Calendar
import database
from datetime import datetime, timedelta

# Import refresh_movies_display from nova_movie module
try:
    from nova_movie import refresh_movies_display
except ImportError:
    def refresh_movies_display():
        """Fallback if import fails"""
        print("Warning: refresh_movies_display not imported")

def create_back_button(parent, command):
    """Create a styled back button."""
    back_btn = tk.Button(
        parent,
        text="← Back to Main",
        font=("Helvetica", 10, "bold"),
        bg="#202020",
        fg="white",
        bd=0,
        cursor="hand2",
        command=command
    )
    
    def on_enter(e):
        back_btn['bg'] = '#303030'
    
    def on_leave(e):
        back_btn['bg'] = '#202020'
    
    back_btn.bind("<Enter>", on_enter)
    back_btn.bind("<Leave>", on_leave)
    
    return back_btn

def create_admin_panel(root, user=None):
    """Create admin panel window with authentication check."""
    if user is None or user.get('role') != 'admin':
        messagebox.showerror("Access Denied", "You must be logged in as an admin to access this panel.")
        root.destroy()
        return False

    root.title("Nova Movies - Admin Dashboard")
    root.configure(bg='#080808')
    
    # Set window size and position
    window_width = 1280
    window_height = 720
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2
    root.geometry(f'{window_width}x{window_height}+{x}+{y}')
    
    def handle_back():
        if messagebox.askyesno("Confirm", "Return to main window? You will be logged out."):
            root.master.logged_in_user = None  # Clear login state
            root.destroy()
            root.master.deiconify()  # Show the main window
            # Update login button text in main window
            for widget in root.master.winfo_children():
                if isinstance(widget, tk.Button) and widget.cget('text') in ["Login", "Logout"]:
                    widget.config(text="Login")
            # Call refresh directly on the main window
            root.master.after(100, lambda: root.master.refresh_movies_display())
    
    # Add back button
    back_btn = create_back_button(root, handle_back)
    back_btn.place(x=20, y=20)
    
    # Create main container
    main_container = tk.Frame(root, bg='#080808')
    main_container.pack(expand=True, fill='both', padx=20, pady=20)

    # Welcome message for admin
    welcome_label = tk.Label(main_container, 
                           text=f"Welcome, {user.get('name', 'Admin')}!", 
                           font=("Helvetica", 16, "bold"),
                           bg='#080808', fg='#ff3b3b')
    welcome_label.pack(pady=(0, 20))

    # Create notebook for tabs
    style = ttk.Style()
    style.configure("Custom.TNotebook", background='#080808')
    style.configure("Custom.TNotebook.Tab", padding=[20, 10], font=('Helvetica', 10, 'bold'))
    
    notebook = ttk.Notebook(main_container, style="Custom.TNotebook")
    notebook.pack(expand=True, fill='both')

    # Create tabs
    users_frame = create_users_tab(notebook)
    movies_frame = create_movies_tab(notebook)
    seats_frame = create_seat_status_tab(notebook)

    notebook.add(users_frame, text='👥 User Management')
    notebook.add(movies_frame, text='🎬 Movie Management')
    notebook.add(seats_frame, text='💺 Seat Status')

    # Add logout button with hover effect
    logout_btn = tk.Button(root, text="Logout", bg='#ff3b3b', fg='white',
                          font=("Helvetica", 10, "bold"),
                          command=lambda: handle_logout(root))
    logout_btn.place(relx=0.95, rely=0.02, anchor='ne')

def create_users_tab(parent):
    frame = tk.Frame(parent, bg='#151515')
    frame.pack(expand=True, fill='both', padx=10, pady=10)

    # Title
    title_label = tk.Label(frame, text="User Management", 
                          font=("Helvetica", 16, "bold"),
                          bg='#151515', fg='white')
    title_label.pack(pady=(0, 20))

    # Create treeview
    columns = ('ID', 'Name', 'Username', 'Phone', 'Role', 'Created At')
    tree = ttk.Treeview(frame, columns=columns, show='headings', height=20)
    
    # Configure columns
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=100)

    # Add scrollbar
    scrollbar = ttk.Scrollbar(frame, orient='vertical', command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    
    tree.pack(side='left', expand=True, fill='both')
    scrollbar.pack(side='right', fill='y')

    def load_users():
        for item in tree.get_children():
            tree.delete(item)
            
        conn = database.get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM nm_users")
        
        for user in cursor.fetchall():
            tree.insert('', 'end', values=(
                user['user_id'],
                user['name'],
                user['username'],
                user['phone_number'],
                user['role'],
                user['created_at']
            ))
            
        cursor.close()
        conn.close()

    # Add refresh button
    tk.Button(frame, text="Refresh", command=load_users,
             bg='#ff3b3b', fg='white').pack(pady=10)

    # Add delete button
    tk.Button(frame, text="Delete User", 
             command=lambda: delete_user(tree) and load_users(),
             bg='#ff3b3b', fg='white').pack(side='left', padx=5)

    # Load initial data
    load_users()
    return frame

def create_movies_tab(parent):
    frame = tk.Frame(parent, bg='#151515')
    frame.pack(expand=True, fill='both', padx=10, pady=10)

    # Title
    title_label = tk.Label(frame, text="Movie Management", 
                          font=("Helvetica", 16, "bold"),
                          bg='#151515', fg='white')
    title_label.pack(pady=(0, 20))

    # Create treeview
    columns = ('ID', 'Title', 'Genre', 'Price', 'Show Date', 'Show Time', 'Status')
    tree = ttk.Treeview(frame, columns=columns, show='headings', height=20)
    
    # Configure columns
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=100)

    # Add scrollbar
    scrollbar = ttk.Scrollbar(frame, orient='vertical', command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    
    tree.pack(side='left', expand=True, fill='both')
    scrollbar.pack(side='right', fill='y')

    def load_movies():
        for item in tree.get_children():
            tree.delete(item)
            
        conn = database.get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM nm_movies ORDER BY show_date, show_time")
        
        for movie in cursor.fetchall():
            tree.insert('', 'end', values=(
                movie['movie_id'],
                movie['title'],
                movie['genre'],
                f"₹{movie['price']}",
                movie['show_date'],
                movie['show_time'],
                movie['status']
            ))
            
        cursor.close()
        conn.close()

    def add_edit_movie(movie_id=None):
        """Create window for adding/editing movies."""
        window = tk.Toplevel()
        window.title("Edit Movie" if movie_id else "Add Movie")
        window.configure(bg='#151515')
        window.geometry("500x600")

        # Get existing data if editing
        movie_data = {}
        if movie_id:
            conn = database.get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM nm_movies WHERE movie_id = %s", (movie_id,))
            movie_data = cursor.fetchone() or {}
            cursor.close()
            conn.close()

        # Create form fields
        tk.Label(window, text="Movie Title:", bg='#151515', fg='white').pack(pady=5)
        title_entry = tk.Entry(window, width=40)
        title_entry.insert(0, movie_data.get('title', ''))
        title_entry.pack(pady=5)

        tk.Label(window, text="Genre:", bg='#151515', fg='white').pack(pady=5)
        genres = [
            'Action',
            'Adventure', 
            'Animation',
            'Comedy',
            'Crime',
            'Drama',
            'Fantasy',
            'Horror',
            'Mystery',
            'Romance',
            'Sci-Fi',
            'Thriller',
            'Documentary',
            'Family',
            'Musical',
            'War',
            'Western',
            'Superhero'
        ]
        genre_var = tk.StringVar(value=movie_data.get('genre', genres[0]))
        genre_combo = ttk.Combobox(window, textvariable=genre_var, values=genres)
        genre_combo.pack(pady=5)

        tk.Label(window, text="Price (₹):", bg='#151515', fg='white').pack(pady=5)
        price_entry = tk.Entry(window, width=40)
        price_entry.insert(0, movie_data.get('price', '200.00'))
        price_entry.pack(pady=5)

        # Date picker
        tk.Label(window, text="Show Date:", bg='#151515', fg='white').pack(pady=5)
        date_frame = tk.Frame(window, bg='#151515')
        date_frame.pack(pady=5)
        
        # Create calendar widget
        current_date = datetime.now()
        cal = Calendar(date_frame, 
                      selectmode='day',
                      year=current_date.year,
                      month=current_date.month,
                      day=current_date.day,
                      date_pattern='yyyy-mm-dd')
        cal.pack(pady=5)
        
        # Set date if editing and date exists
        if movie_data and movie_data.get('show_date'):
            try:
                # Convert date to string format if it's a datetime object
                if isinstance(movie_data['show_date'], datetime):
                    date_str = movie_data['show_date'].strftime('%Y-%m-%d')
                else:
                    date_str = str(movie_data['show_date'])
                cal.selection_set(date_str)
            except Exception as e:
                print(f"Error setting date: {e}")
                # If there's an error, keep the current date

        # Status (default to inactive for new movies)
        tk.Label(window, text="Status:", bg='#151515', fg='white').pack(pady=5)
        status_var = tk.StringVar(value=movie_data.get('status', 'inactive'))
        status_frame = tk.Frame(window, bg='#151515')
        status_frame.pack(pady=5)
        
        tk.Radiobutton(status_frame, text="Active", variable=status_var, 
                      value="active", bg='#151515', fg='white').pack(side='left')
        tk.Radiobutton(status_frame, text="Inactive", variable=status_var, 
                      value="inactive", bg='#151515', fg='white').pack(side='left')

        def save_movie():
            # Validate fields
            if not all([title_entry.get(), genre_var.get(), price_entry.get()]):
                messagebox.showerror("Error", "Please fill all fields!")
                return

            try:
                price = float(price_entry.get())
            except ValueError:
                messagebox.showerror("Error", "Invalid price!")
                return

            # Check active movie limit for the selected date
            if status_var.get() == 'active':
                active_count = database.check_active_movies_for_date(
                    cal.get_date(), 
                    movie_id
                )
                
                if active_count >= 3:
                    messagebox.showerror(
                        "Error", 
                        "Maximum limit of 3 active movies reached for this date! "
                        "Please deactivate another movie first or choose a different date."
                    )
                    return

            # Save to database
            conn = database.get_db_connection()
            cursor = conn.cursor()
            
            try:
                if movie_id:
                    cursor.execute("""
                        UPDATE nm_movies 
                        SET title = %s, genre = %s, price = %s,
                            show_date = %s, status = %s
                        WHERE movie_id = %s
                    """, (
                        title_entry.get(),
                        genre_var.get(),
                        price,
                        cal.get_date(),
                        status_var.get(),
                        movie_id
                    ))
                else:
                    cursor.execute("""
                        INSERT INTO nm_movies 
                        (title, genre, price, show_date, status)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (
                        title_entry.get(),
                        genre_var.get(),
                        price,
                        cal.get_date(),
                        status_var.get()
                    ))
                
                conn.commit()
                messagebox.showinfo("Success", 
                    "Movie updated successfully!" if movie_id else "Movie added successfully!")
                window.destroy()
                load_movies()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save movie: {str(e)}")
                conn.rollback()
            
            finally:
                cursor.close()
                conn.close()

        # Save button
        tk.Button(window, text="Save Changes", command=save_movie,
                 bg='#ff3b3b', fg='white', font=("Helvetica", 12, "bold")).pack(pady=20)

    def toggle_movie_status():
        """Handle movie status toggle with improved UI."""
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a movie")
            return
        
        movie_id = tree.item(selected[0])['values'][0]
        movie_title = tree.item(selected[0])['values'][1]
        current_status = tree.item(selected[0])['values'][6]
        new_status = 'inactive' if current_status == 'active' else 'active'
        
        if new_status == 'active':
            # Check active movie limit
            active_count = database.get_active_movie_count()
            if active_count >= 3:
                messagebox.showerror(
                    "Error", 
                    "Maximum limit of 3 active movies reached!\nPlease deactivate another movie first."
                )
                return
            
            # Create and configure time selection dialog
            time_dialog = tk.Toplevel()
            time_dialog.title(f"Set Show Time - {movie_title}")
            time_dialog.geometry("400x500")
            time_dialog.configure(bg='#151515')
            
            # Center the dialog
            screen_width = time_dialog.winfo_screenwidth()
            screen_height = time_dialog.winfo_screenheight()
            x = (screen_width - 400) // 2
            y = (screen_height - 500) // 2
            time_dialog.geometry(f"400x500+{x}+{y}")
            
            # Create main container
            main_frame = tk.Frame(time_dialog, bg='#151515', padx=30, pady=20)
            main_frame.pack(expand=True, fill='both')
            
            # Header
            header_frame = tk.Frame(main_frame, bg='#151515')
            header_frame.pack(fill='x', pady=(0, 20))
            
            tk.Label(header_frame, 
                    text="Activate Movie", 
                    font=("Helvetica", 16, "bold"),
                    bg='#151515', fg='#ff3b3b').pack()
                    
            tk.Label(header_frame, 
                    text=movie_title,
                    font=("Helvetica", 12),
                    bg='#151515', fg='white').pack(pady=5)
            
            # Time slots section
            tk.Label(main_frame, 
                    text="Select Available Time Slot", 
                    font=("Helvetica", 12, "bold"),
                    bg='#151515', fg='white').pack(pady=(0, 10))
            
            # Create time slots container
            time_frame = tk.Frame(main_frame, bg='#151515')
            time_frame.pack(pady=10)
            
            # Fixed show times
            times = ["10:00:00", "13:00:00", "16:00:00", "19:00:00"]
            selected_time = tk.StringVar()
            time_buttons = []
            
            def select_time(time):
                selected_time.set(time)
                for btn in time_buttons:
                    if btn['text'] == time[:5]:
                        btn.configure(bg='#ff3b3b', fg='white')
                    else:
                        btn.configure(bg='#202020', fg='white')
            
            # Create time slot buttons
            for time in times:
                try:
                    if database.check_time_slot_available(time, movie_id):
                        btn = tk.Button(time_frame, 
                                      text=time[:5],
                                      width=10, height=2,
                                      font=("Helvetica", 11),
                                      bg='#202020', fg='white',
                                      command=lambda t=time: select_time(t))
                        btn.pack(pady=5)
                        time_buttons.append(btn)
                    else:
                        # Show unavailable time slots as disabled
                        tk.Button(time_frame,
                                 text=f"{time[:5]} (Taken)",
                                 width=15, height=2,
                                 font=("Helvetica", 11),
                                 bg='#333333', fg='#666666',
                                 state='disabled').pack(pady=5)
                except Exception as e:
                    print(f"Error checking time slot {time}: {e}")
            
            def confirm_time():
                if not selected_time.get():
                    messagebox.showwarning("Warning", "Please select a time slot")
                    return
                    
                try:
                    database.set_movie_active_status(movie_id, new_status, selected_time.get())
                    messagebox.showinfo("Success", 
                                      f"Movie '{movie_title}' activated\nShow time set to {selected_time.get()[:5]}")
                    load_movies()
                    time_dialog.destroy()
                except Exception as e:
                    messagebox.showerror("Error", str(e))
            
            # Buttons frame
            button_frame = tk.Frame(main_frame, bg='#151515')
            button_frame.pack(pady=20)
            
            # Cancel button
            tk.Button(button_frame,
                     text="Cancel",
                     width=12,
                     font=("Helvetica", 11),
                     bg='#333333', fg='white',
                     command=time_dialog.destroy).pack(side='left', padx=5)
            
            # Confirm button
            tk.Button(button_frame,
                     text="Activate",
                     width=12,
                     font=("Helvetica", 11, "bold"),
                     bg='#ff3b3b', fg='white',
                     command=confirm_time).pack(side='left', padx=5)
            
        else:
            # Deactivating movie
            if messagebox.askyesno("Confirm Deactivate", 
                                 f"Are you sure you want to deactivate '{movie_title}'?"):
                try:
                    database.set_movie_active_status(movie_id, new_status)
                    messagebox.showinfo("Success", f"Movie '{movie_title}' deactivated")
                    load_movies()
                except Exception as e:
                    messagebox.showerror("Error", str(e))

    # Add buttons frame
    button_frame = tk.Frame(frame, bg='#151515')
    button_frame.pack(pady=10)
    
    tk.Button(button_frame, text="Add Movie", command=lambda: add_edit_movie(),
             bg='#ff3b3b', fg='white').pack(side='left', padx=5)
    edit_btn = tk.Button(
        button_frame, 
        text="Edit Movie",
        bg='#ff3b3b', 
        fg='white',
        command=lambda: add_edit_movie(
            int(tree.item(tree.selection()[0])['values'][0]) if tree.selection() else None
        )
    )
    edit_btn.pack(side='left', padx=5)
    tk.Button(button_frame, text="Refresh", command=load_movies,
             bg='#ff3b3b', fg='white').pack(side='left', padx=5)

    # Add delete button
    tk.Button(button_frame, text="Delete Movie", 
             command=lambda: delete_movie(tree) and load_movies(),
             bg='#ff3b3b', fg='white').pack(side='left', padx=5)

    # Add status toggle button
    tk.Button(button_frame, text="Toggle Active Status", 
             command=toggle_movie_status,
             bg='#ff3b3b', fg='white').pack(side='left', padx=5)

    # Load initial data
    load_movies()
    return frame

def create_seat_status_tab(parent):
    """Create tab for viewing seat status."""
    frame = tk.Frame(parent, bg='#080808')
    frame.pack(expand=True, fill='both', padx=20, pady=20)

    # Top section with controls
    top_frame = tk.Frame(frame, bg='#080808')
    top_frame.pack(fill='x', pady=(0, 20))
    
    # Left side - Title
    tk.Label(top_frame, 
            text="Seat Management", 
            font=("Helvetica", 24, "bold"),
            bg='#080808', fg='#ff3b3b').pack(side='left')

    # Right side - Controls
    controls_frame = tk.Frame(top_frame, bg='#080808')
    controls_frame.pack(side='right')

    # Auto refresh switch with modern design
    auto_refresh_var = tk.BooleanVar(value=False)
    switch_frame = tk.Frame(controls_frame, bg='#080808')
    switch_frame.pack(side='left', padx=15)
    
    tk.Label(switch_frame, text="Auto Refresh", 
            font=("Helvetica", 10),
            bg='#080808', fg='#666666').pack(side='left', padx=(0,10))
            
    tk.Checkbutton(switch_frame, 
                   variable=auto_refresh_var,
                   bg='#080808', fg='white',
                   selectcolor='#ff3b3b',
                   activebackground='#080808').pack(side='left')

    # Refresh and Clear All buttons
    buttons_frame = tk.Frame(controls_frame, bg='#080808')
    buttons_frame.pack(side='left')
    
    def clear_all_seats():
        if messagebox.askyesno("Confirm Clear All", 
                             "⚠️ Warning: This will clear ALL seat bookings for today.\n\n"
                             "This action cannot be undone!", 
                             icon='warning'):
            success, message = database.clear_seats_for_movie()
            if success:
                messagebox.showinfo("Success", "✓ " + message)
                refresh_seat_status()
            else:
                messagebox.showerror("Error", f"Failed to clear seats: {message}")

    tk.Button(buttons_frame,
              text="⟳ Refresh",
              command=lambda: refresh_seat_status(),
              bg='#202020', fg='white',
              font=("Helvetica", 10),
              width=12,
              relief='flat').pack(side='left', padx=5)
              
    tk.Button(buttons_frame,
              text="🗑️ Clear All",
              command=clear_all_seats,
              bg='#ff3b3b', fg='white',
              font=("Helvetica", 10, "bold"),
              width=12,
              relief='flat').pack(side='left', padx=5)

    # Main content area
    content_frame = tk.Frame(frame, bg='#101010')
    content_frame.pack(expand=True, fill='both')

    def create_movie_card(movie_data, parent):
        """Create modern card for each movie."""
        card = tk.Frame(parent, bg='#151515', padx=20, pady=15)
        card.pack(fill='x', padx=15, pady=8)
        
        # Header with movie info and controls
        header = tk.Frame(card, bg='#151515')
        header.pack(fill='x', pady=(0,15))
        
        # Left side - Movie info
        info = tk.Frame(header, bg='#151515')
        info.pack(side='left')
        
        tk.Label(info, 
                text=movie_data['title'],
                font=("Helvetica", 16, "bold"),
                bg='#151515', fg='white').pack(anchor='w')
                
        tk.Label(info,
                text=f"🕒 {str(movie_data['show_time'])[:5]}",
                font=("Helvetica", 12),
                bg='#151515', fg='#888888').pack(anchor='w')

        # Right side - Stats and controls
        controls = tk.Frame(header, bg='#151515')
        controls.pack(side='right')
        
        booked_seats = movie_data['booked_seats'].split(',') if movie_data['booked_seats'] else []
        total_seats = 49
        booked_count = len(booked_seats)
        available = total_seats - booked_count
        
        # Stats with icons
        stats = tk.Frame(controls, bg='#151515')
        stats.pack(side='left', padx=15)
        
        tk.Label(stats,
                text=f"🔴 {booked_count} Booked",
                font=("Helvetica", 12),
                bg='#151515', fg='#ff3b3b').pack(side='left', padx=10)
                
        tk.Label(stats,
                text=f"🟢 {available} Available",
                font=("Helvetica", 12),
                bg='#151515', fg='#4CAF50').pack(side='left', padx=10)

        # Clear button
        def clear_movie_seats():
            if messagebox.askyesno("Confirm Clear",
                                 f"Clear all bookings for '{movie_data['title']}'?",
                                 icon='warning'):
                success, message = database.clear_seats_for_movie(movie_data['movie_id'])
                if success:
                    messagebox.showinfo("Success", "✓ " + message)
                    refresh_seat_status()
                else:
                    messagebox.showerror("Error", f"Failed to clear seats: {message}")

        tk.Button(controls,
                 text="Clear Seats",
                 command=clear_movie_seats,
                 bg='#ff3b3b', fg='white',
                 font=("Helvetica", 10),
                 relief='flat').pack(side='right')

        # Seat grid
        seats_frame = tk.Frame(card, bg='#151515')
        seats_frame.pack(fill='x')
        
        def show_booking_details(seat_num):
            """Show booking details for a seat."""
            try:
                connection = database.get_db_connection()
                cursor = connection.cursor(dictionary=True)
                
                # Get booking details including user info
                cursor.execute("""
                    SELECT s.*, u.name, u.phone_number 
                    FROM nm_seats s
                    JOIN nm_users u ON s.user_id = u.user_id
                    WHERE s.movie_id = %s 
                    AND s.seat_number = %s 
                    AND s.booking_date = CURDATE()
                """, (movie_data['movie_id'], seat_num))
                
                booking = cursor.fetchone()
                cursor.close()
                connection.close()
                
                if booking:
                    # Create details window
                    details_window = tk.Toplevel()
                    details_window.title(f"Booking Details - Seat {seat_num}")
                    details_window.configure(bg='#151515')
                    
                    # Center the window
                    window_width = 400
                    window_height = 350  # Increased height for new button
                    screen_width = details_window.winfo_screenwidth()
                    screen_height = details_window.winfo_screenheight()
                    x = (screen_width - window_width) // 2
                    y = (screen_height - window_height) // 2
                    details_window.geometry(f"{window_width}x{window_height}+{x}+{y}")
                    
                    # Add details
                    tk.Label(details_window, 
                            text="Booking Details",
                            font=("Helvetica", 16, "bold"),
                            bg='#151515', fg='#ff3b3b').pack(pady=20)
                    
                    details_frame = tk.Frame(details_window, bg='#151515')
                    details_frame.pack(pady=10)
                    
                    details = [
                        ("Movie", movie_data['title']),
                        ("Seat", seat_num),
                        ("Customer Name", booking['name']),
                        ("Phone Number", booking['phone_number']),
                        ("Booking Date", booking['booking_date'].strftime("%Y-%m-%d")),
                    ]
                    
                    for label, value in details:
                        row = tk.Frame(details_frame, bg='#151515')
                        row.pack(pady=5, fill='x')
                        
                        tk.Label(row, text=f"{label}:", 
                                font=("Helvetica", 11),
                                width=15, anchor='e',
                                bg='#151515', fg='#888888').pack(side='left', padx=5)
                                
                        tk.Label(row, text=value,
                                font=("Helvetica", 11, "bold"),
                                bg='#151515', fg='white').pack(side='left', padx=5)
                    
                    # Add buttons frame
                    buttons_frame = tk.Frame(details_window, bg='#151515')
                    buttons_frame.pack(pady=20)
                    
                    def clear_single_booking():
                        if messagebox.askyesno("Confirm Clear",
                                             f"Are you sure you want to clear the booking for seat {seat_num}?",
                                             icon='warning'):
                            success, message = database.clear_single_seat(movie_data['movie_id'], seat_num)
                            if success:
                                messagebox.showinfo("Success", f"Booking for seat {seat_num} has been cleared")
                                details_window.destroy()
                                refresh_seat_status()  # Refresh the seat display
                            else:
                                messagebox.showerror("Error", f"Failed to clear booking: {message}")
                    
                    # Clear booking button
                    tk.Button(buttons_frame,
                             text="Clear Booking",
                             command=clear_single_booking,
                             bg='#ff3b3b', fg='white',
                             font=("Helvetica", 11),
                             width=15).pack(side='left', padx=5)
                    
                    # Close button
                    tk.Button(buttons_frame,
                             text="Close",
                             command=details_window.destroy,
                             bg='#333333', fg='white',
                             font=("Helvetica", 11),
                             width=15).pack(side='left', padx=5)
                    
            except Exception as e:
                messagebox.showerror("Error", f"Failed to fetch booking details: {str(e)}")
            finally:
                if 'cursor' in locals():
                    cursor.close()
                if 'connection' in locals():
                    connection.close()
        
        rows = "ABCDEFG"
        for row_idx, row in enumerate(rows):
            tk.Label(seats_frame,
                    text=row,
                    font=("Helvetica", 10),
                    bg='#151515', fg='#666666').grid(row=row_idx, column=0, padx=10)
            
            for col in range(7):
                seat_num = f"{row}{col+1}"
                is_booked = seat_num in booked_seats
                
                seat = tk.Frame(seats_frame,
                              bg='#ff3b3b' if is_booked else '#202020',
                              width=35, height=35)
                seat.grid(row=row_idx, column=col+1, padx=2, pady=2)
                seat.pack_propagate(False)
                
                seat_label = tk.Label(seat,
                        text=seat_num,
                        font=("Helvetica", 8),
                        bg='#151515' if is_booked else '#101010',
                        fg='white')
                seat_label.pack(expand=True)
                
                if is_booked:
                    # Make booked seats clickable
                    seat_label.bind('<Button-1>', lambda e, s=seat_num: show_booking_details(s))
                    seat_label.configure(cursor='hand2')  # Change cursor to hand on hover
                    
                    # Add tooltip
                    create_tooltip(seat_label, "Click to view booking details")
                
                if col == 3:  # Add aisle
                    tk.Frame(seats_frame, width=20, bg='#151515').grid(
                        row=row_idx, column=col+2)

    def refresh_seat_status():
        # Clear existing content
        for widget in content_frame.winfo_children():
            widget.destroy()

        movies = database.get_movie_seat_status()
        
        if not movies:
            empty = tk.Frame(content_frame, bg='#101010')
            empty.pack(expand=True)
            
            tk.Label(empty,
                    text="No Active Movies",
                    font=("Helvetica", 18, "bold"),
                    bg='#101010', fg='#666666').pack(pady=(100,10))
            tk.Label(empty,
                    text="Activate movies to view seat status",
                    font=("Helvetica", 12),
                    bg='#101010', fg='#444444').pack()
            return

        # Create scrollable container
        canvas = tk.Canvas(content_frame, bg='#101010', highlightthickness=0)
        scrollbar = ttk.Scrollbar(content_frame, orient="vertical", command=canvas.yview)
        scrollable = tk.Frame(canvas, bg='#101010')
        
        scrollable.bind("<Configure>",
                       lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        canvas.create_window((0, 0), window=scrollable, anchor="nw", width=canvas.winfo_reqwidth())
        canvas.configure(yscrollcommand=scrollbar.set)

        # Create movie cards
        for movie in movies:
            create_movie_card(movie, scrollable)

        canvas.pack(side="left", fill="both", expand=True, pady=10)
        scrollbar.pack(side="right", fill="y")

    def auto_refresh():
        if auto_refresh_var.get():
            refresh_seat_status()
            frame.after(30000, auto_refresh)  # Refresh every 30 seconds

    # Start auto-refresh if enabled
    auto_refresh()
    
    # Initial load
    refresh_seat_status()
    return frame

def create_tooltip(widget, text):
    """Create tooltip for widgets."""
    def show_tooltip(event):
        tooltip = tk.Toplevel()
        tooltip.wm_overrideredirect(True)
        tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
        
        label = tk.Label(tooltip, text=text, bg='#333333', fg='white',
                        relief='solid', borderwidth=1)
        label.pack()
        
        def hide_tooltip():
            tooltip.destroy()
            
        widget.tooltip = tooltip
        widget.bind('<Leave>', lambda e: hide_tooltip())
        
    widget.bind('<Enter>', show_tooltip)

def handle_logout(root):
    """Handle admin logout."""
    if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
        # Get reference to main window
        main_window = root.master
        
        # Clear login state
        main_window.logged_in_user = None
        
        # Destroy admin window
        root.destroy()
        
        # Show and update main window
        main_window.deiconify()
        
        # Update login button text
        for widget in main_window.winfo_children():
            if isinstance(widget, tk.Button) and widget.cget('text') in ["Login", "Logout"]:
                widget.config(text="Login")
        
        # Call refresh directly on the main window
        main_window.after(100, lambda: main_window.refresh_movies_display())

def delete_user(tree):
    """Delete selected user."""
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Warning", "Please select a user to delete")
        return
        
    if not messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this user?"):
        return
        
    try:
        connection = database.get_db_connection()
        cursor = connection.cursor()
        
        for item in selected:
            user_id = tree.item(item)['values'][0]
            cursor.execute("DELETE FROM nm_users WHERE user_id = %s", (user_id,))
            
        connection.commit()
        messagebox.showinfo("Success", "User(s) deleted successfully")
        return True
        
    except Exception as e:
        print(f"Error deleting user: {e}")
        messagebox.showerror("Error", f"Failed to delete user: {str(e)}")
        return False
        
    finally:
        cursor.close()
        connection.close()

def delete_movie(tree):
    """Delete selected movie."""
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Warning", "Please select a movie to delete")
        return
        
    if not messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this movie?"):
        return
        
    try:
        connection = database.get_db_connection()
        cursor = connection.cursor()
        
        for item in selected:
            movie_id = tree.item(item)['values'][0]
            cursor.execute("DELETE FROM nm_movies WHERE movie_id = %s", (movie_id,))
            
        connection.commit()
        messagebox.showinfo("Success", "Movie(s) deleted successfully")
        return True
        
    except Exception as e:
        print(f"Error deleting movie: {e}")
        messagebox.showerror("Error", f"Failed to delete movie: {str(e)}")
        return False
        
    finally:
        cursor.close()
        connection.close()

def show_seat_selection_window():
    """
    Display seat selection interface with validation.
    
    Process:
    1. Validates movie selection
    2. Checks login status
    3. Retrieves movie data
    4. Creates seat selection window
    5. Shows movie info and seat grid
    """
    if not selected_movie:
        messagebox.showerror("Error", "Please select a movie first!")
        return
        
    # Check login status before proceeding
    if not check_login_status():
        messagebox.showinfo("Login Required", "Please login to book tickets")
        return

    # Get the selected movie's data
    active_movies = database.get_active_movies_for_date(None)
    selected_movie_data = next((m for m in active_movies if m['title'] == selected_movie), None)
    
    if not selected_movie_data:
        messagebox.showerror("Error", "Movie data not found!")
        return

    seat_window = tk.Toplevel()
    seat_window.title(f"Seat Selection - {selected_movie}")
    # Set window size slightly larger than main window (960x540)
    center_window(seat_window, 1080, 640)  # Proportionally larger than main window
    seat_window.configure(bg='#080808')
    
    # Add back button
    back_btn = create_back_button(seat_window, seat_window.destroy)
    back_btn.place(x=20, y=20)
    
    # Main container with proper padding
    main_container = tk.Frame(seat_window, bg='#080808')
    main_container.pack(expand=True, fill='both', padx=40, pady=20)
    
    # Left section for poster and movie info
    left_frame = tk.Frame(main_container, bg='#080808', width=220)  # Slightly wider for poster
    left_frame.pack(side='left', padx=(0, 40), fill='y')
    left_frame.pack_propagate(False)
    
    poster_container = tk.Frame(left_frame, bg='#080808')
    poster_container.pack(pady=(40, 0))  # Good top padding
    
    # Fetch poster if not already in cache
    if selected_movie not in movie_posters:
        fetch_movie_poster(selected_movie)
    
    if selected_movie in movie_posters:
        poster_label = tk.Label(poster_container, 
                              image=movie_posters[selected_movie],
                              bg='#080808')
        poster_label.pack()
    
    # Show movie info with show time
    movie_info = tk.Label(poster_container, 
                         text=f"{selected_movie}\nShow Time: {str(selected_movie_data['show_time'])[:5]}", 
                         font="Helvetica 15 bold",  # Good readable size
                         bg="#080808", 
                         fg="#ff3b3b",
                         justify='center',
                         wraplength=200)  # Ensure long titles wrap properly
    movie_info.pack(pady=10)

    # Right section for seats with proper spacing
    right_frame = tk.Frame(main_container, bg='#080808')
    right_frame.pack(side='left', expand=True, fill='both', padx=(0, 20))
    
    create_seat_layout(right_frame)

if __name__ == "__main__":
    messagebox.showerror("Access Denied", "Please login through the main application.")