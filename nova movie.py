import tkinter as tk
from tkinter import ttk, messagebox, font as tkfont
from PIL import Image, ImageTk
import requests
from io import BytesIO
import urllib.parse
import qrcode
import datetime
import database
from PIL import Image, ImageDraw, ImageFont
import random
import os
from login import create_login_window
from admin_panel import create_admin_panel

from dotenv import load_dotenv
import os

load_dotenv()
MOVIE_API = os.getenv("MOVIE_API")




def initialize_globals():
    """
    Initialize all global variables needed for the application.
    
    Sets up:
    - TICKET_SAVE_PATH: Directory path for saving generated tickets
    - seat_buttons: List to store references to seat button widgets
    - selected_seats: List to track currently selected seats
    - selected_movie: Currently selected movie
    - movie_posters: Dictionary to cache movie poster images
    
    Also creates a 'tickets' subdirectory if it doesn't exist.
    """
    global TICKET_SAVE_PATH, seat_buttons, selected_seats, selected_movie, movie_posters
    
    TICKET_SAVE_PATH = "D:\\version 16-02-25\\tickets"
    # Create tickets directory if it doesn't exist
    tickets_dir = os.path.join(TICKET_SAVE_PATH, "tickets")
    if not os.path.exists(tickets_dir):
        os.makedirs(tickets_dir)
        
    seat_buttons = []
    selected_seats = []
    selected_movie = None
    movie_posters = {}

def fetch_movie_poster(movie_title):
    """
    Fetch and cache movie poster from OMDB API.
    
    Args:
        movie_title (str): Title of the movie to fetch poster for
        
    Returns:
        ImageTk.PhotoImage: Processed poster image ready for display
        None: If poster fetch fails
        
    Process:
    1. Checks if poster is already cached
    2. Makes API request to OMDB
    3. Downloads and processes poster image
    4. Resizes to 130x195 pixels
    5. Caches for future use
    """
    try:
        if (movie_title in movie_posters):
            return movie_posters[movie_title]

        
        url = f"http://www.omdbapi.com/?t={urllib.parse.quote(movie_title)}&apikey={MOVIE_API}"
        
        response = requests.get(url)
        movie_data = response.json()
        
        if movie_data.get('Poster') and movie_data['Poster'] != 'N/A':
            poster_response = requests.get(movie_data['Poster'])
            image = Image.open(BytesIO(poster_response.content))
            image = image.resize((130, 195), Image.Resampling.LANCZOS)
            movie_posters[movie_title] = ImageTk.PhotoImage(image)
            return movie_posters[movie_title]
        return None
    except Exception as e:
        print(f"Error fetching poster for {movie_title}: {e}")
        return None

def create_movie_card(parent, movie_data, idx):
    """
    Create a visual card display for a movie with hover effects.
    
    Args:
        parent: Parent widget to contain the card
        movie_data (dict): Movie information (title, genre, price, etc.)
        idx (int): Index for positioning the card
        
    Features:
    - Hover effects on entire card
    - Movie poster display
    - Title button with hover effect
    - Price display in red
    - Genre and show time information
    - Click handlers for selection
    """
    try:
        # Create main frame with hover effect
        movie_frame = tk.Frame(parent, bg='#151515', padx=20, pady=15)
        movie_frame.grid(row=0, column=idx, padx=15)
        
        def on_enter(e):
            movie_frame.config(bg='#202020')  # Slightly lighter on hover
            if title_btn:
                title_btn.config(bg='#ff3b3b')  # Highlight button on hover
        
        def on_leave(e):
            movie_frame.config(bg='#151515')  # Return to original color
            if title_btn and title_btn['text'] != selected_movie:
                title_btn.config(bg='#202020')  # Return button to original color
        
        movie_frame.bind('<Enter>', on_enter)
        movie_frame.bind('<Leave>', on_leave)
        
        def select_this_movie(event=None):
            select_movie(movie_data['title'])
        
        movie_frame.bind('<Button-1>', select_this_movie)
        
        poster = fetch_movie_poster(movie_data['title'])
        if poster:
            poster_label = tk.Label(movie_frame, image=poster, bg='#151515')
            poster_label.pack(pady=(0, 10))
            poster_label.bind('<Button-1>', select_this_movie)
            # Make poster label update its bg color with frame
            poster_label.bind('<Enter>', on_enter)
            poster_label.bind('<Leave>', on_leave)
        
        title_btn = tk.Button(movie_frame, 
                       text=movie_data['title'], 
                       width=25, height=2,
                       bg='#202020', 
                       fg='white', 
                       font="Helvetica 12 bold",
                       cursor="hand2",  # Add hand cursor
                       command=select_this_movie)
        title_btn.pack()
        
        for widget in movie_frame.winfo_children():
            if isinstance(widget, tk.Label):
                widget.bind('<Button-1>', select_this_movie)
                # Make labels update their bg color with frame
                widget.bind('<Enter>', on_enter)
                widget.bind('<Leave>', on_leave)
        
        price_label = tk.Label(movie_frame, 
                             text=f"₹{float(movie_data['price']):.2f}",
                             font="Helvetica 10 bold", 
                             bg='#151515', fg='#ff3b3b')
        price_label.pack(pady=(5, 0))
        
        genre_label = tk.Label(movie_frame, 
                             text=movie_data['genre'],
                             font="Helvetica 10", 
                             bg='#151515', fg='#888888')
        genre_label.pack(pady=(5, 0))
        
        time_str = movie_data['show_time']
        if isinstance(time_str, str) and len(time_str) > 8:
            time_str = time_str[:8]
        time_label = tk.Label(movie_frame, 
                            text=f"Show Time: {time_str}",
                            font="Helvetica 10", 
                            bg='#151515', fg='#888888')
        time_label.pack(pady=(5, 0))
            
    except Exception as e:
        print(f"Error creating movie card: {e}")

def create_premium_button(parent, text, command):
    """
    Create a styled button with hover effects.
    
    Args:
        parent: Parent widget
        text (str): Button text
        command: Function to execute on click
        
    Features:
    - Red background (#ff3b3b)
    - White text
    - Hover effect (darker red)
    - Bold font
    - Industrial-grade styling
    """
    btn = tk.Button(parent, text=text, bg="#ff3b3b", fg="white",
                   font="Helvetica 14 bold", command=command,
                   width=24, height=2, bd=0)
    
    def on_enter(e):
        btn['bg'] = '#ff1f1f'
    
    def on_leave(e):
        btn['bg'] = '#ff3b3b'
    
    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)
    return btn

def select_movie(movie):
    """
    Handle movie selection and update UI accordingly.
    
    Args:
        movie (str): Title of selected movie
        
    Process:
    1. Updates global selected_movie
    2. Finds movie container frame
    3. Resets all movie cards to default state
    4. Highlights selected movie card
    5. Updates button colors
    """
    global selected_movie
    selected_movie = movie
    print(f"Selected movie: {movie}")  # Debug print
    
    # Find the movies container frame
    movies_container = None
    for widget in movies_frame.winfo_children():
        if isinstance(widget, tk.Frame):
            movies_container = widget
            break
    
    if movies_container:
        # Reset all movie frames and buttons to default color
        for movie_frame in movies_container.winfo_children():
            if isinstance(movie_frame, tk.Frame):
                # Reset button color
                for child in movie_frame.winfo_children():
                    if isinstance(child, tk.Button):
                        child.config(bg='#202020')
                # Reset frame background
                movie_frame.config(bg='#151515')
        
        # Find and highlight the selected movie
        for movie_frame in movies_container.winfo_children():
            if isinstance(movie_frame, tk.Frame):
                for child in movie_frame.winfo_children():
                    if isinstance(child, tk.Button) and child['text'] == movie:
                        # Highlight button
                        child.config(bg='#ff3b3b')
                        # Highlight frame
                        movie_frame.config(bg='#202020')
                        break

def create_seat_layout(parent):
    """
    Create interactive seat selection interface.
    
    Args:
        parent: Parent widget
        
    Features:
    1. Left Panel:
        - Movie info
        - Price display
        - Total amount
        
    2. Right Panel:
        - Screen visualization
        - Interactive seat grid (A1-G7)
        - Color coding for seats
        - Aisle spacing
        
    3. Legend section for seat status
    4. Real-time total calculation
    """
    global selected_seats, seat_buttons
    selected_seats = []
    seat_buttons = []
    
    # Get movie data
    active_movies = database.get_active_movies_for_date(None)
    selected_movie_data = next((m for m in active_movies if m['title'] == selected_movie), None)
    
    if not selected_movie_data:
        messagebox.showerror("Error", "Movie data not found!")
        return
        
    occupied_seats = database.get_occupied_seats(selected_movie_data['movie_id'])
    
    # Create main container with gradient effect
    seat_frame = tk.Frame(parent, bg='#080808')
    seat_frame.pack(padx=30, pady=20, expand=True, fill='both')

    # Left panel for movie info and price
    left_panel = tk.Frame(seat_frame, bg='#101010', width=200)
    left_panel.pack(side='left', fill='y', padx=(0, 20))
    left_panel.pack_propagate(False)
    
    # Movie info section
    info_frame = tk.Frame(left_panel, bg='#101010')
    info_frame.pack(pady=20)
    
    # Movie title with shadow effect
    title_frame = tk.Frame(info_frame, bg='#101010')
    title_frame.pack(fill='x')
    
    tk.Label(title_frame, text=selected_movie,
            font=("Helvetica", 16, "bold"),
            bg='#101010', fg='#ff3b3b',
            wraplength=180).pack()
            
    # Show time with icon
    time_frame = tk.Frame(info_frame, bg='#101010')
    time_frame.pack(fill='x', pady=10)
    
    tk.Label(time_frame, text="🕒",
            font=("Helvetica", 12),
            bg='#101010', fg='#888888').pack(side='left', padx=5)
            
    tk.Label(time_frame, 
            text=f"{str(selected_movie_data['show_time'])[:5]}",
            font=("Helvetica", 12),
            bg='#101010', fg='white').pack(side='left')

    # Price section
    price_frame = tk.Frame(left_panel, bg='#101010')
    price_frame.pack(fill='x', pady=20)
    
    price = float(selected_movie_data['price'])
    
    tk.Label(price_frame, text="PRICE PER TICKET",
            font=("Helvetica", 10),
            bg='#101010', fg='#888888').pack()
            
    tk.Label(price_frame, text=f"₹{price:.2f}",
            font=("Helvetica", 18, "bold"),
            bg='#101010', fg='#ff3b3b').pack(pady=5)
    
    # Total amount display
    total_frame = tk.Frame(left_panel, bg='#101010')
    total_frame.pack(fill='x', pady=10)
    
    tk.Label(total_frame, text="TOTAL AMOUNT",
            font=("Helvetica", 10),
            bg='#101010', fg='#888888').pack()
            
    total_label = tk.Label(total_frame, text="₹0.00",
                          font=("Helvetica", 18, "bold"),
                          bg='#101010', fg='white')
    total_label.pack(pady=5)

    # Right panel for seat selection
    right_panel = tk.Frame(seat_frame, bg='#080808')
    right_panel.pack(side='left', expand=True, fill='both')

    # Screen section
    screen_frame = tk.Frame(right_panel, bg='#0a0a0a', height=30)
    screen_frame.pack(fill='x', pady=(0, 30))
    screen_frame.pack_propagate(False)
    
    tk.Label(screen_frame, text="SCREEN",
            font=("Helvetica", 8),
            bg='#0a0a0a', fg='#444444').pack(expand=True)

    # Seat grid with modern styling
    grid_frame = tk.Frame(right_panel, bg='#080808')
    grid_frame.pack()
    
    rows = "ABCDEFG"
    for row_idx, row in enumerate(rows):
        # Row label
        tk.Label(grid_frame, text=row,
                font=("Helvetica", 10, "bold"),
                bg='#080808', fg='#666666',
                width=2).grid(row=row_idx, column=0, padx=(0, 10))
        
        seat_row = []
        for col in range(7):
            seat_num = f"{row}{col+1}"
            
            # Create seat button with rounded corners effect
            seat_frame = tk.Frame(grid_frame, bg='#080808')
            seat_frame.grid(row=row_idx, column=col+1, padx=2, pady=2)
            
            btn = tk.Button(seat_frame, text=seat_num,
                          width=3, height=1,
                          font=("Helvetica", 8),
                          cursor="hand2",
                          relief="flat")
            btn.pack(padx=1, pady=1)
            
            if seat_num in occupied_seats:
                btn.config(bg='#333333', fg='#666666', state='disabled')
            else:
                btn.config(bg='#202020', fg='white')
                # Use lambda with default argument to capture correct seat_num
                btn.config(command=lambda s=seat_num: toggle_seat(s))
                
                def on_enter(e, button=btn):
                    if button['bg'] not in ['#ff3b3b', '#333333']:  # Don't highlight if selected or occupied
                        button.config(bg='#303030')
                        
                def on_leave(e, button=btn):
                    if button['bg'] not in ['#ff3b3b', '#333333']:  # Don't unhighlight if selected or occupied
                        button.config(bg='#202020')
                        
                btn.bind('<Enter>', on_enter)
                btn.bind('<Leave>', on_leave)
            
            seat_row.append(btn)
            
            # Add aisle
            if col == 3:
                spacer = tk.Frame(grid_frame, width=15, bg='#080808')
                spacer.grid(row=row_idx, column=col+2)
                
        seat_buttons.append(seat_row)

    # Legend section
    legend_frame = tk.Frame(right_panel, bg='#080808')
    legend_frame.pack(pady=20)
    
    legend_items = [
        ("Available", '#202020'),
        ("Selected", '#ff3b3b'),
        ("Booked", '#333333')
    ]
    
    for text, color in legend_items:
        item = tk.Frame(legend_frame, bg='#080808')
        item.pack(side='left', padx=10)
        
        # Seat indicator
        indicator = tk.Frame(item, bg=color, width=15, height=15)
        indicator.pack(side='left', padx=5)
        indicator.pack_propagate(False)
        
        # Legend text
        tk.Label(item, text=text,
                font=("Helvetica", 9),
                bg='#080808', fg='#888888').pack(side='left')

    def update_total():
        total = len(selected_seats) * price
        total_label.config(text=f"₹{total:.2f}")

    def toggle_seat(seat_num):
        """Handle seat selection/deselection."""
        row = ord(seat_num[0]) - ord('A')
        col = int(seat_num[1]) - 1
        button = seat_buttons[row][col]
        
        if seat_num in occupied_seats:
            return  # Don't allow toggling occupied seats
            
        if seat_num in selected_seats:  # If seat is already selected
            button.config(bg='#202020')  # Change back to available color
            selected_seats.remove(seat_num)
        else:  # If seat is available
            button.config(bg='#ff3b3b')  # Change to selected color
            selected_seats.append(seat_num)
            
        update_total()

    # Confirm booking button
    confirm_button = tk.Button(left_panel,
                             text="CONFIRM BOOKING",
                             font=("Helvetica", 12, "bold"),
                             bg='#ff3b3b',
                             fg='white',
                             relief='flat',
                             cursor='hand2',
                             command=confirm_booking)
    confirm_button.pack(side='bottom', pady=20, padx=20, fill='x')
    
    def on_confirm_enter(e):
        confirm_button.config(bg='#ff1f1f')
        
    def on_confirm_leave(e):
        confirm_button.config(bg='#ff3b3b')
        
    confirm_button.bind('<Enter>', on_confirm_enter)
    confirm_button.bind('<Leave>', on_confirm_leave)

def generate_ticket_qr(booking_data):
    """Generate QR code with booking details."""
    qr_content = (
        f"NOVA MOVIES BOOKING\n"
        f"------------------\n"
        f"Booking ID: {booking_data['booking_id']}\n"
        f"Movie: {booking_data['movie_title']}\n"
        f"Show Time: {booking_data['show_time']}\n"
        f"Seats: {', '.join(booking_data['seat_numbers'])}\n"
        f"Customer: {booking_data['user_name']}\n"
        f"Phone: {booking_data['phone_number']}\n"
        f"Amount: ₹{booking_data['price']:.2f}\n"
        f"------------------\n"
        f"Scan to verify"
    )
    
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4
    )
    qr.add_data(qr_content)
    qr.make(fit=True)
    
    return qr.make_image(fill_color="black", back_color="white")

def create_ticket_image(booking_data, qr_image):
    """Create ticket image with movie poster and QR code."""
    # Create ticket background with fixed size
    width = 1000
    height = 500
    ticket = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(ticket)
    
    try:
        # Try to load Arial font
        try:
            title_font = ImageFont.truetype("arial.ttf", 48)
            heading_font = ImageFont.truetype("arial.ttf", 24)
            detail_font = ImageFont.truetype("arial.ttf", 20)
        except:
            title_font = ImageFont.load_default()
            heading_font = ImageFont.load_default()
            detail_font = ImageFont.load_default()
        
        # Add decorative elements
        draw.rectangle([0, 0, width, 80], fill='#ff3b3b')  # Header
        draw.rectangle([0, height-60, width, height], fill='#ff3b3b')  # Footer
        
        # Add title
        draw.text((40, 20), "NOVA MOVIES", font=title_font, fill='white')
        
        # Get movie poster
        poster = None
        if booking_data['movie_title'] in movie_posters:
            poster_photo = movie_posters[booking_data['movie_title']]
            poster = ImageTk.getimage(poster_photo)  # Convert PhotoImage back to PIL Image
            
        if poster:
            # Resize poster to fit ticket
            poster_height = 300
            poster_width = int((poster_height/poster.height) * poster.width)
            poster = poster.resize((poster_width, poster_height), Image.Resampling.LANCZOS)
            
            # Paste poster on left side
            poster_x = 40
            poster_y = 100
            ticket.paste(poster, (poster_x, poster_y))
            
            # Start details after poster
            details_x = poster_x + poster_width + 40
        else:
            details_x = 40
        
        # Add booking details
        y_pos = 120
        details = [
            ("Booking ID:", booking_data['booking_id']),
            ("Movie:", booking_data['movie_title']),
            ("Show Time:", booking_data['show_time']),
            ("Seats:", ', '.join(booking_data['seat_numbers'])),
            ("Customer:", booking_data['user_name']),
            ("Phone:", booking_data['phone_number']),
            ("Amount:", f"₹{booking_data['price']:.2f}")
        ]
        
        # Add details with proper spacing
        for label, value in details:
            draw.text((details_x, y_pos), label, font=heading_font, fill='#333333')
            draw.text((details_x + 160, y_pos), str(value), font=detail_font, fill='#000000')
            y_pos += 45
        
        # Resize QR code
        qr_size = 200
        qr_image = qr_image.resize((qr_size, qr_size))
        
        # Place QR code on right side
        qr_x = width - qr_size - 50
        qr_y = (height - qr_size) // 2
        ticket.paste(qr_image, (qr_x, qr_y))
        
        # Add verification text under QR
        verify_text = "Scan to verify"
        verify_width = draw.textlength(verify_text, font=detail_font)
        verify_x = qr_x + (qr_size - verify_width) // 2
        
        draw.text((verify_x, qr_y + qr_size + 10), verify_text, 
                 font=detail_font, fill='#666666')
        
        return ticket
        
    except Exception as e:
        print(f"Error creating ticket image: {e}")
        # Create simple fallback ticket
        draw.text((20, 20), "NOVA MOVIES TICKET", font=ImageFont.load_default(), fill='black')
        draw.text((20, 50), f"Booking ID: {booking_data['booking_id']}", 
                 font=ImageFont.load_default(), fill='black')
        ticket.paste(qr_image, (width-qr_image.size[0]-20, 20))
        return ticket

def show_ticket_popup(ticket_path, booking_data):
    """Show ticket in a popup window after booking."""
    popup = tk.Toplevel()
    popup.title("Your Ticket")
    popup.configure(bg='#080808')
    
    # Calculate window size based on ticket image size
    ticket_image = Image.open(ticket_path)
    width, height = ticket_image.size
    
    # Add some padding
    window_width = width + 40
    window_height = height + 100
    
    # Center the window
    center_window(popup, window_width, window_height)
    
    # Convert ticket image for tkinter
    ticket_photo = ImageTk.PhotoImage(ticket_image)
    
    # Create main container
    container = tk.Frame(popup, bg='#080808', padx=20, pady=20)
    container.pack(expand=True, fill='both')
    
    # Show success message
    tk.Label(
        container,
        text="Booking Confirmed!",
        font=("Helvetica", 16, "bold"),
        fg='#ff3b3b',
        bg='#080808'
    ).pack(pady=(0, 10))
    
    # Show booking ID
    tk.Label(
        container,
        text=f"Booking ID: {booking_data['booking_id']}",
        font=("Helvetica", 12),
        fg='white',
        bg='#080808'
    ).pack(pady=(0, 20))
    
    # Show ticket image
    ticket_label = tk.Label(
        container,
        image=ticket_photo,
        bg='#080808'
    )
    ticket_label.image = ticket_photo  # Keep reference
    ticket_label.pack()
    
    # Add close button
    close_btn = tk.Button(
        container,
        text="Close",
        font=("Helvetica", 12, "bold"),
        bg='#ff3b3b',
        fg='white',
        command=popup.destroy,
        relief='flat',
        cursor='hand2',
        padx=20,
        pady=5
    )
    close_btn.pack(pady=20)
    
    # Add hover effect
    def on_enter(e):
        close_btn.config(bg='#ff1f1f')
    def on_leave(e):
        close_btn.config(bg='#ff3b3b')
    
    close_btn.bind('<Enter>', on_enter)
    close_btn.bind('<Leave>', on_leave)

def confirm_booking():
    """Handle booking confirmation and ticket generation."""
    if not selected_seats:
        messagebox.showwarning("No Seats", "Please select seats first!")
        return
        
    if not hasattr(root, 'logged_in_user') or not root.logged_in_user:
        messagebox.showinfo("Login Required", "Please login to book tickets")
        return
        
    try:
        # Get movie data
        active_movies = database.get_active_movies_for_date(None)
        selected_movie_data = next((m for m in active_movies if m['title'] == selected_movie), None)
        
        # Get user details from database
        connection = database.get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT name, phone_number 
            FROM nm_users 
            WHERE user_id = %s
        """, (root.logged_in_user['user_id'],))
        user_data = cursor.fetchone()
        
        # Generate unique booking ID
        booking_id = f"NM{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Prepare booking data for QR
        booking_data = {
            'booking_id': booking_id,
            'movie_title': selected_movie,
            'show_time': str(selected_movie_data['show_time']),
            'seat_numbers': selected_seats,
            'user_name': user_data['name'],
            'phone_number': user_data['phone_number'],
            'price': float(selected_movie_data['price']) * len(selected_seats)
        }
        
        # Save seats to database
        for seat in selected_seats:
            cursor.execute("""
                INSERT INTO nm_seats (movie_id, user_id, seat_number, booking_date)
                VALUES (%s, %s, %s, CURDATE())
            """, (selected_movie_data['movie_id'], root.logged_in_user['user_id'], seat))
            
        connection.commit()
        
        # Generate QR code
        qr_image = generate_ticket_qr(booking_data)
        
        # Create ticket image
        ticket_image = create_ticket_image(booking_data, qr_image)
        
        # Generate and save ticket
        ticket_filename = f"ticket_{booking_id}.png"
        ticket_path = os.path.join(TICKET_SAVE_PATH, "tickets", ticket_filename)
        ticket_image.save(ticket_path)
        
        # Show ticket popup instead of message box
        show_ticket_popup(ticket_path, booking_data)
        
        # Close seat selection window
        parent = seat_buttons[0][0].master.master.master.master
        if isinstance(parent, tk.Toplevel):
            parent.destroy()
            
    except Exception as e:
        messagebox.showerror("Error", f"Failed to complete booking: {str(e)}")
        if 'connection' in locals():
            connection.rollback()
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()

def check_login_status():
    """
    Verify user login status and handle login process.
    
    Returns:
        bool: True if user is logged in, False otherwise
        
    Process:
    1. Checks if user is already logged in
    2. Shows login window if not logged in
    3. Waits for login completion
    4. Updates login state
    """
    if not hasattr(root, 'logged_in_user') or root.logged_in_user is None:
        login_window = create_login_window(root)
        root.wait_window(login_window)  # Wait for login window to close
        if hasattr(login_window, 'logged_in_user'):
            root.logged_in_user = login_window.logged_in_user
        return root.logged_in_user is not None
    return True

def create_back_button(parent, command):
    """
    Create styled back button with hover effect.
    
    Args:
        parent: Parent widget
        command: Function to execute on click
    """
    # Create container frame for button with background
    container = tk.Frame(parent, bg='#080808')
    
    # Create the back button with enhanced styling
    back_btn = tk.Button(
        container,
        text="← Back to Home Page",  # Changed text
        font=("Helvetica", 13, "bold"),
        bg="#ff3b3b",
        fg="white",
        bd=0,
        cursor="hand2",
        padx=25,
        pady=10,
        command=command,
        relief='flat'
    )
    back_btn.pack(pady=5)
    
    def on_enter(e):
        back_btn['bg'] = '#ff1f1f'
        back_btn['text'] = "← Return to Home Page"  # Changed hover text
    
    def on_leave(e):
        back_btn['bg'] = '#ff3b3b'
        back_btn['text'] = "← Back to Home Page"  # Changed original text
    
    back_btn.bind("<Enter>", on_enter)
    back_btn.bind("<Leave>", on_leave)
    
    return container

def show_seat_selection_window():
    """
    Display seat selection interface with validation.
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
    center_window(seat_window, 1200, 720)  # Made larger for better visibility
    seat_window.configure(bg='#080808')
    
    # Create a header frame for the back button
    header_frame = tk.Frame(seat_window, bg='#080808')
    header_frame.pack(fill='x', padx=20, pady=(15, 0))
    
    # Add back button with enhanced visibility
    back_container = create_back_button(header_frame, seat_window.destroy)
    back_container.pack(side='left', anchor='nw')
    
    # Add a separator line below the header
    separator = tk.Frame(seat_window, height=2, bg='#202020')
    separator.pack(fill='x', padx=20, pady=(15, 0))
    
    # Main container with proper padding - adjusted to account for header
    main_container = tk.Frame(seat_window, bg='#080808')
    main_container.pack(expand=True, fill='both', padx=50, pady=20)
    
    # Left section for poster and movie info
    left_frame = tk.Frame(main_container, bg='#080808', width=250)  # Wider for poster
    left_frame.pack(side='left', padx=(0, 50), fill='y')
    left_frame.pack_propagate(False)
    
    poster_container = tk.Frame(left_frame, bg='#080808')
    poster_container.pack(pady=(40, 0))
    
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
                         font="Helvetica 16 bold",
                         bg="#080808", 
                         fg="#ff3b3b",
                         justify='center',
                         wraplength=220)
    movie_info.pack(pady=15)

    # Right section for seats with proper spacing
    right_frame = tk.Frame(main_container, bg='#080808')
    right_frame.pack(side='left', expand=True, fill='both', padx=(0, 30))
    
    create_seat_layout(right_frame)

def login_function():
    """
    Create and handle login window.
    
    Features:
    - Username/password fields
    - Login button
    - Error handling
    - Styled interface
    """
    login_window = tk.Toplevel()
    login_window.title("Login")
    center_window(login_window, 400, 300)
    login_window.configure(bg='#080808')
    
    # Add your login form widgets here
    tk.Label(login_window, text="Login", font="Helvetica 20 bold", 
            bg='#080808', fg='#ff3b3b').pack(pady=20)
    
    # Username
    tk.Label(login_window, text="Username:", bg='#080808', 
            fg='white', font="Helvetica 12").pack(pady=(0,5))
    username_entry = tk.Entry(login_window, font="Helvetica 12")
    username_entry.pack(pady=(0,15))
    
    # Password
    tk.Label(login_window, text="Password:", bg='#080808', 
            fg='white', font="Helvetica 12").pack(pady=(0,5))
    password_entry = tk.Entry(login_window, show="*", font="Helvetica 12")
    password_entry.pack(pady=(0,20))
    
    # Login button
    login_btn = create_premium_button(login_window, "LOGIN", login_window.destroy)
    login_btn.pack()

def refresh_movies_display():
    """
    Update movie display to show current active movies.
    
    Process:
    1. Clears existing display
    2. Updates movie dates
    3. Fetches active movies
    4. Creates movie cards
    5. Adds booking button
    6. Shows message if no movies
    """
    global movies_frame
    
    # Clear existing movies
    for widget in movies_frame.winfo_children():
        widget.destroy()
    
    try:
        # Update dates for active movies
        database.update_movie_dates()
        
        # Get active movies
        active_movies = database.get_active_movies_for_date(None)
        
        if active_movies:
            # Create a container for movie cards
            movies_container = tk.Frame(movies_frame, bg='#101010')
            movies_container.pack(expand=True, fill='both')
            
            # Display movies
            for idx, movie in enumerate(active_movies):
                movie_data = {
                    'title': movie['title'],
                    'genre': movie['genre'],
                    'price': movie['price'],
                    'show_time': str(movie['show_time']),
                    'show_date': movie['show_date']
                }
                create_movie_card(movies_container, movie_data, idx)

            # Add booking button
            book_button = create_premium_button(movies_frame, "BOOK NOW", show_seat_selection_window)
            book_button.pack(pady=20)
            
        else:
            # Show message if no movies are available
            no_movies_label = tk.Label(
                movies_frame,
                text="No shows scheduled for today",
                font=("Helvetica", 14),
                bg='#101010',
                fg='#888888'
            )
            no_movies_label.pack(pady=50)
            
    except Exception as e:
        print(f"Error refreshing movies: {e}")
        messagebox.showerror("Error", f"Failed to refresh movies: {str(e)}")

def find_login_button(root_window):
    """
    Locate login button in widget hierarchy.
    
    Args:
        root_window: Main window widget
        
    Returns:
        Button widget or None
    
    Process:
    Searches through frames and widgets to find login/logout button
    """
    for widget in root_window.winfo_children():
        if isinstance(widget, tk.Frame):  # Check frames
            for child in widget.winfo_children():
                if isinstance(child, tk.Frame):  # Check nested frames
                    for button in child.winfo_children():
                        if isinstance(button, tk.Button) and button.cget('text') in ["Login", "Logout"]:
                            return button
        elif isinstance(widget, tk.Button) and widget.cget('text') in ["Login", "Logout"]:
            return widget
    return None

def handle_login_click():
    """
    Process login button clicks.
    
    Features:
    1. Shows login window if not logged in
    2. Handles admin panel access
    3. Updates button text
    4. Manages window visibility
    """
    global login_button
    
    if not hasattr(root, 'logged_in_user') or root.logged_in_user is None:
        login_window = create_login_window(root)
        root.wait_window(login_window)
        if hasattr(login_window, 'logged_in_user') and login_window.logged_in_user:
            root.logged_in_user = login_window.logged_in_user
            # Update login button text
            login_button.config(text="Logout")
            
            # If admin, show admin panel and hide main window
            if root.logged_in_user['role'] == 'admin':
                root.withdraw()  # Hide main window
                admin_window = tk.Toplevel(root)
                admin_window.protocol("WM_DELETE_WINDOW", 
                                   lambda: handle_admin_logout(admin_window))
                create_admin_panel(admin_window, root.logged_in_user)
    else:
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            root.logged_in_user = None
            login_button.config(text="Login")  # Directly update the global login_button
            root.deiconify()  # Show main window if it was hidden
            refresh_movies_display()

def handle_admin_logout(admin_window):
    """
    Process admin logout.
    
    Args:
        admin_window: Admin panel window
        
    Process:
    1. Confirms logout
    2. Clears login state
    3. Updates button text
    4. Shows main window
    5. Refreshes display
    """
    global login_button
    
    if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
        root.logged_in_user = None
        login_button.config(text="Login")  # Directly update the global login_button
        admin_window.destroy()
        root.deiconify()  # Show main window
        refresh_movies_display()

def create_main_widgets(root):
    """
    Set up main application interface.
    
    Args:
        root: Main window widget
        
    Features:
    1. Pattern background
    2. Animated logo
    3. Movie display area
    4. Login button
    5. Modern styling
    """
    global movies_frame, main_frame, login_button
    
    # Add refresh_movies_display as a method of root window
    root.refresh_movies_display = refresh_movies_display
    
    # Create outer frame
    outer_frame = tk.Frame(root, bg='#080808')
    outer_frame.place(relwidth=1, relheight=1)
    
    # Create pattern canvas
    pattern_canvas = tk.Canvas(outer_frame, bg='#080808', highlightthickness=0)
    pattern_canvas.place(relwidth=1, relheight=1)
    for i in range(0, 1440, 20):
        pattern_canvas.create_line(i, 0, i, 900, fill='#0a0a0a', width=1)
    for i in range(0, 900, 20):
        pattern_canvas.create_line(0, i, 1440, i, fill='#0a0a0a', width=1)

    # Create main frame
    main_frame = tk.Frame(outer_frame, bg='#101010', padx=50, pady=40)
    main_frame.place(relx=0.5, rely=0.5, anchor="center")

    # Create modern header with animation
    header_frame = tk.Frame(main_frame, bg='#101010')
    header_frame.grid(row=0, column=0, columnspan=7, pady=(0, 35))
    
    # Create logo container
    logo_container = tk.Frame(header_frame, bg='#101010')
    logo_container.pack()
    
    # Main logo text
    logo_text = tk.Label(
        logo_container, 
        text="NOVA", 
        font=("Helvetica", 45, "bold"),
        bg='#101010', 
        fg='#ff3b3b'
    )
    logo_text.pack(side='left', padx=(0,10))
    
    # Movies text with different color
    movies_text = tk.Label(
        logo_container, 
        text="MOVIES", 
        font=("Helvetica", 45, "bold"),
        bg='#101010', 
        fg='#ffffff'
    )
    movies_text.pack(side='left')
    
    # Add tagline
    tagline = tk.Label(
        header_frame,
        text="Experience Cinema Like Never Before",
        font=("Helvetica", 12),
        bg='#101010',
        fg='#666666'
    )
    tagline.pack(pady=(5,0))
    
    def animate_logo(widget, original_color, highlight_color='#ff5555'):
        """Create subtle pulsing animation for logo."""
        current_color = widget.cget('fg')
        new_color = highlight_color if current_color == original_color else original_color
        widget.config(fg=new_color)
        # Repeat animation every 2 seconds
        widget.after(2000, lambda: animate_logo(widget, original_color, highlight_color))
    
    # Start logo animation
    animate_logo(logo_text, '#ff3b3b')
    
    def on_header_enter(e):
        tagline.config(fg='#888888')  # Brighten tagline on hover
        
    def on_header_leave(e):
        tagline.config(fg='#666666')  # Return to original color
    
    # Add hover effect to entire header
    header_frame.bind('<Enter>', on_header_enter)
    header_frame.bind('<Leave>', on_header_leave)

    # Create movies frame
    movies_frame = tk.Frame(main_frame, bg='#101010')
    movies_frame.grid(row=2, column=0, columnspan=7, pady=(0, 30))

    # Add modern login button with hover effect
    login_button = tk.Button(
        outer_frame, 
        text="Login", 
        bg="#ff3b3b", 
        fg="white",
        font=("Helvetica", 11, "bold"),
        command=handle_login_click,
        relief="flat",  # Remove button border
        padx=20,  # Add horizontal padding
        pady=8,   # Add vertical padding
        cursor="hand2"  # Show hand cursor on hover
    )
    login_button.place(relx=0.95, rely=0.05, anchor='ne')
    
    def on_login_enter(e):
        if e.widget.winfo_exists():  # Use event widget instead of global
            e.widget.config(bg='#ff1f1f')  # Darker red on hover
        
    def on_login_leave(e):
        if e.widget.winfo_exists():  # Use event widget instead of global
            e.widget.config(bg='#ff3b3b')  # Original red
        
    login_button.bind("<Enter>", on_login_enter)
    login_button.bind("<Leave>", on_login_leave)

    # Initial refresh of movies display
    refresh_movies_display()

def center_window(window, width, height):
    """
    Center a window on screen.
    
    Args:
        window: Window to center
        width (int): Window width
        height (int): Window height
        
    Process:
    Calculates position for center of screen
    """
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    window.geometry(f'{width}x{height}+{x}+{y}')

def main():
    """
    Main application entry point.
    
    Process:
    1. Checks database connection
    2. Initializes globals
    3. Creates main window
    4. Sets up UI
    5. Starts event loop
    
    Error handling:
    - Database connection issues
    - Initialization failures
    """
    global root, movies_frame
    
    try:
        # Check database connection first
        try:
            conn = database.get_db_connection()
            if conn:
                conn.close()
        except Exception as e:
            messagebox.showerror(
                "Database Error",
                f"Failed to connect to database. Please check if MySQL is running and credentials are correct.\n\nError: {str(e)}"
            )
            return
            
        # Ensure seats table exists
        database.ensure_seats_table_exists()
        
        # Clear only old seat data (from previous days)
        database.clear_old_seat_data()
        
        # Initialize global variables
        initialize_globals()
        
        # Create main window
        root = tk.Tk()
        root.title("Nova Movies Booking")
        root.logged_in_user = None
        
        # Configure root window
        root.configure(bg='#080808')
        center_window(root, 960, 540)  # 16:9 aspect ratio (540p)
        
        # Create main widgets
        create_main_widgets(root)
        
        # Start the main event loop
        root.mainloop()
        
    except Exception as e:
        print(f"Error starting application: {e}")
        messagebox.showerror("Error", f"Failed to start application: {str(e)}")

# Make sure to call main() when the script is run directly
if __name__ == "__main__":
    main()

