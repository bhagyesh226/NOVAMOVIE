import mysql.connector as mysql
from datetime import datetime
import hashlib

def create_database_connection():
    """Create a connection to MySQL server without selecting a database."""
    try:
        connection = mysql.connect(
            host="localhost",
            user="root",
            password="bhagyesh123",
            autocommit=True,
            connect_timeout=5,
            use_pure=True
        )
        return connection
    except mysql.Error as err:
        error_message = ""
        if err.errno == mysql.errorcode.CR_CONN_HOST_ERROR:
            error_message = (
                "\n[ERROR] Could not connect to MySQL server:"
                "\n1. Check if MySQL service is running"
                "\n2. Verify MySQL is installed correctly"
                "\n3. Check if port 3306 is not blocked"
                f"\nError details: {err}"
            )
        elif err.errno == mysql.errorcode.ER_ACCESS_DENIED_ERROR:
            error_message = (
                "\n[ERROR] Access denied:"
                "\n1. Username 'root' might be incorrect"
                "\n2. Password might be wrong"
                "\n3. User might not have required permissions"
                f"\nError details: {err}"
            )
        elif err.errno == 2003:
            error_message = (
                "\n[ERROR] MySQL server connection failed:"
                "\n1. MySQL service might not be running"
                "\n2. Server might be down"
                "\n3. Network issues might be present"
                f"\nError details: {err}"
            )
        else:
            error_message = f"\n[ERROR] Unexpected MySQL error: {err}"
        
        print(error_message)
        return None
    except Exception as e:
        print(f"\n[ERROR] Unexpected error while connecting to database: {e}")
        return None

def get_db_connection():
    """Create a connection to the nova_movie database."""
    try:
        connection = mysql.connect(
            host="localhost",
            user="root",
            password="bhagyesh123",
            database="nova_movie",
            autocommit=True,
            connect_timeout=5,
            use_pure=True
        )
        return connection
    except mysql.Error as err:
        error_message = ""
        if err.errno == mysql.errorcode.ER_BAD_DB_ERROR:
            print("\n[ERROR] Database 'nova_movie' not found. Attempting to create...")
            try:
                if create_database():
                    return get_db_connection()
                else:
                    error_message = "[ERROR] Failed to create database"
            except Exception as create_err:
                error_message = f"[ERROR] Database creation failed: {create_err}"
        elif err.errno == mysql.errorcode.CR_CONN_HOST_ERROR:
            error_message = (
                "\n[ERROR] Could not connect to MySQL server:"
                "\n1. Check if MySQL service is running"
                "\n2. Verify MySQL is installed correctly"
                "\n3. Check if port 3306 is not blocked"
            )
        elif err.errno == mysql.errorcode.ER_ACCESS_DENIED_ERROR:
            error_message = (
                "\n[ERROR] Access denied:"
                "\n1. Username 'root' might be incorrect"
                "\n2. Password might be wrong"
                "\n3. User might not have required permissions"
            )
        else:
            error_message = f"\n[ERROR] Unexpected MySQL error: {err}"
        
        print(error_message)
        return None
    except Exception as e:
        print(f"\n[ERROR] Unexpected error while connecting to database: {e}")
        return None

def check_login(username, password):
    """Check user login credentials."""
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        if not connection:
            raise Exception("Failed to establish database connection")
            
        cursor = connection.cursor(dictionary=True)
        
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
        cursor.execute("""
        SELECT user_id, name, role 
        FROM nm_users 
        WHERE username = %s AND password = %s
        """, (username, hashed_password))
        
        user = cursor.fetchone()
        if not user:
            print(f"[INFO] Login failed for username: {username}")
        return user
    
    except mysql.Error as err:
        error_message = f"[ERROR] MySQL error during login: {err}"
        if err.errno == mysql.errorcode.ER_NO_SUCH_TABLE:
            error_message = "[ERROR] Users table does not exist. Database might need initialization."
        print(error_message)
        return None
    except Exception as e:
        print(f"[ERROR] Unexpected error during login: {e}")
        return None
    finally:
        if cursor:
            try:
                cursor.close()
            except Exception as e:
                print(f"[ERROR] Failed to close cursor: {e}")
        if connection:
            try:
                connection.close()
            except Exception as e:
                print(f"[ERROR] Failed to close connection: {e}")

def register_user(name, username, password, phone_number):
    """Register a new user."""
    connection = get_db_connection()
    cursor = connection.cursor()
    
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    
    try:
        cursor.execute("""
        INSERT INTO nm_users (name, username, password, phone_number)
        VALUES (%s, %s, %s, %s)
        """, (name, username, hashed_password, phone_number))
        
        connection.commit()
        return True
    
    except mysql.Error as err:
        print(f"Error: {err}")
        connection.rollback()
        return False
    
    finally:
        cursor.close()
        connection.close()

def create_database():
    """Create the database and required tables."""
    connection = None
    cursor = None
    try:
        print("\n=== Database Setup Starting ===")
        
        connection = create_database_connection()
        if not connection:
            print("Failed to connect to MySQL server")
            return False
            
        cursor = connection.cursor()
        
        cursor.execute("SHOW DATABASES LIKE 'nova_movie'")
        exists = cursor.fetchone()
        
        if not exists:
            cursor.execute("CREATE DATABASE nova_movie")
            print("[+] Database 'nova_movie' created successfully!")
        else:
            print("[+] Database 'nova_movie' already exists")

        cursor.execute("USE nova_movie")
        
        cursor.execute("SHOW TABLES LIKE 'nm_users'")
        if not cursor.fetchone():
            cursor.execute("""
            CREATE TABLE nm_users (
                user_id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                username VARCHAR(50) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                phone_number VARCHAR(15),
                role ENUM('admin', 'customer') DEFAULT 'customer',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            print("[+] Table 'nm_users' created successfully!")
        else:
            print("[+] Table 'nm_users' already exists")

        cursor.execute("SHOW TABLES LIKE 'nm_movies'")
        if not cursor.fetchone():
            cursor.execute("""
            CREATE TABLE nm_movies (
                movie_id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(100) NOT NULL,
                genre VARCHAR(50),
                price DECIMAL(10,2) NOT NULL,
                show_date DATE,
                show_time TIME,
                status ENUM('active', 'inactive') DEFAULT 'inactive',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            print("[+] Table 'nm_movies' created successfully!")
        else:
            print("[+] Table 'nm_movies' already exists")

        cursor.execute("SHOW TABLES LIKE 'nm_seats'")
        if not cursor.fetchone():
            cursor.execute("""
            CREATE TABLE nm_seats (
                seat_id INT AUTO_INCREMENT PRIMARY KEY,
                movie_id INT,
                user_id INT,
                seat_number VARCHAR(3) NOT NULL,
                booking_date DATE NOT NULL,
                CONSTRAINT fk_movie 
                    FOREIGN KEY (movie_id) 
                    REFERENCES nm_movies(movie_id)
                    ON DELETE CASCADE,
                CONSTRAINT fk_user
                    FOREIGN KEY (user_id) 
                    REFERENCES nm_users(user_id)
                    ON DELETE CASCADE,
                UNIQUE KEY unique_seat (movie_id, seat_number, booking_date)
            ) ENGINE=InnoDB
            """)
            print("[+] Table 'nm_seats' created successfully!")
        else:
            print("[+] Table 'nm_seats' already exists")

        cursor.execute("SELECT * FROM nm_users WHERE username = 'kingsman' AND role = 'admin'")
        if not cursor.fetchone():
            admin_password = hashlib.sha256("iamyash".encode()).hexdigest()
            cursor.execute("""
            INSERT INTO nm_users (name, username, password, phone_number, role)
            VALUES ('Admin', 'kingsman', %s, '1234567890', 'admin')
            """, (admin_password,))
            print("[+] Admin user created successfully!")
            print("    Username: kingsman")
            print("    Password: iamyash")
        else:
            print("[+] Admin user already exists")
            print("    Username: kingsman")
            print("    Password: iamyash")

        connection.commit()
        print("\n=== Database Setup Complete ===")
        print("[+] All tables verified")
        print("[+] System ready to use")
        return True
        
    except mysql.Error as err:
        print(f"\n❌ MySQL Error: {err}")
        if err.errno == mysql.errorcode.CR_CONN_HOST_ERROR:
            print("Could not connect to MySQL server. Please check if MySQL is running.")
        elif err.errno == mysql.errorcode.ER_ACCESS_DENIED_ERROR:
            print("Access denied. Please check your username and password.")
        if connection:
            connection.rollback()
        return False
    except Exception as e:
        print(f"\n❌ Error creating database: {e}")
        if connection:
            connection.rollback()
        return False
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def get_active_movies_for_date(show_date):
    """Get active movies for a specific date."""
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    try:
        query = """
            SELECT * FROM nm_movies 
            WHERE status = 'active' 
            AND show_date = CURDATE()
            ORDER BY show_time
        """
        cursor.execute(query)
        return cursor.fetchall()
        
    except Exception as e:
        print(f"Database error in get_active_movies_for_date: {e}")
        return []
        
    finally:
        cursor.close()
        connection.close()

def check_time_slot_available(show_time, movie_id=None):
    """Check if a time slot is available."""
    connection = get_db_connection()
    cursor = connection.cursor()
    
    try:
        if movie_id:
            cursor.execute("""
                SELECT COUNT(*) FROM nm_movies 
                WHERE show_time = %s 
                AND status = 'active'
                AND movie_id != %s
                AND show_date = CURDATE()
            """, (show_time, movie_id))
        else:
            cursor.execute("""
                SELECT COUNT(*) FROM nm_movies 
                WHERE show_time = %s 
                AND status = 'active'
                AND show_date = CURDATE()
            """, (show_time,))
            
        count = cursor.fetchone()[0]
        return count == 0
        
    finally:
        cursor.close()
        connection.close()

def set_movie_active_status(movie_id, status, show_time=None):
    """Set a movie's active status and optionally update its show time."""
    connection = get_db_connection()
    cursor = connection.cursor()
    
    try:
        if status == 'active':
            active_count = get_active_movie_count()
            
            cursor.execute("SELECT status FROM nm_movies WHERE movie_id = %s", (movie_id,))
            current_status = cursor.fetchone()[0]
            
            if current_status != 'active' and active_count >= 3:
                raise Exception("Maximum limit of 3 active movies reached. Please deactivate another movie first.")
            
            if show_time:
                if not check_time_slot_available(show_time, movie_id):
                    raise Exception(f"Time slot {show_time[:5]} is already taken by another movie")
                
                # Clear any existing seats for this movie when activating
                cursor.execute("""
                    DELETE FROM nm_seats 
                    WHERE movie_id = %s 
                    AND booking_date = CURDATE()
                """, (movie_id,))
                
                cursor.execute("""
                    UPDATE nm_movies 
                    SET status = %s,
                        show_time = %s,
                        show_date = CURDATE()
                    WHERE movie_id = %s
                """, (status, show_time, movie_id))
                
        else:  # When deactivating
            # Clear all seats for this movie
            cursor.execute("""
                DELETE FROM nm_seats 
                WHERE movie_id = %s 
                AND booking_date = CURDATE()
            """, (movie_id,))
            
            cursor.execute("""
                UPDATE nm_movies 
                SET status = %s,
                    show_date = CURDATE()
                WHERE movie_id = %s
            """, (status, movie_id))
            
        connection.commit()
        return True
        
    except Exception as e:
        print(f"Error setting movie status: {e}")
        connection.rollback()
        raise
        
    finally:
        cursor.close()
        connection.close()

def update_movie_dates():
    """Update active movies to current date."""
    connection = get_db_connection()
    cursor = connection.cursor()
    
    try:
        cursor.execute("""
            UPDATE nm_movies 
            SET show_date = CURDATE()
            WHERE status = 'active'
        """)
        
        connection.commit()
        return True
        
    except Exception as e:
        print(f"Error updating movie dates: {e}")
        connection.rollback()
        return False
        
    finally:
        cursor.close()
        connection.close()

def get_occupied_seats(movie_id):
    """Get occupied seats for a movie on current date."""
    connection = get_db_connection()
    cursor = connection.cursor()
    
    try:
        cursor.execute("""
            SELECT seat_number 
            FROM nm_seats 
            WHERE movie_id = %s 
            AND booking_date = CURDATE()
        """, (movie_id,))
        
        return [row[0] for row in cursor.fetchall()]
        
    finally:
        cursor.close()
        connection.close()

def mark_seats_as_occupied(movie_id, seat_numbers, user_id):
    """Mark seats as occupied for a movie."""
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        if not connection:
            raise Exception("Failed to establish database connection")
            
        cursor = connection.cursor()
        
        # First check if seats are still available
        occupied_seats = []
        for seat in seat_numbers:
            cursor.execute("""
                SELECT seat_number 
                FROM nm_seats 
                WHERE movie_id = %s 
                AND seat_number = %s 
                AND booking_date = CURDATE()
            """, (movie_id, seat))
            if cursor.fetchone():
                occupied_seats.append(seat)
        
        if occupied_seats:
            raise Exception(
                f"Seats {', '.join(occupied_seats)} are already booked. "
                "Please refresh and try again."
            )
        
        # If all seats are available, proceed with booking
        for seat in seat_numbers:
            cursor.execute("""
                INSERT INTO nm_seats (movie_id, user_id, seat_number, booking_date)
                VALUES (%s, %s, %s, CURDATE())
            """, (movie_id, user_id, seat))
            
        connection.commit()
        print(f"[SUCCESS] Successfully booked seats: {', '.join(seat_numbers)}")
        return True
        
    except mysql.Error as err:
        error_message = f"[ERROR] MySQL error while booking seats: {err}"
        if err.errno == mysql.errorcode.ER_DUP_ENTRY:
            error_message = "[ERROR] Seat(s) already booked. Please refresh and try again."
        elif err.errno == mysql.errorcode.ER_NO_REFERENCED_ROW_2:
            error_message = "[ERROR] Invalid movie_id or user_id provided."
        print(error_message)
        if connection:
            connection.rollback()
        return False
    except Exception as e:
        print(f"[ERROR] Unexpected error while booking seats: {e}")
        if connection:
            connection.rollback()
        return False
    finally:
        if cursor:
            try:
                cursor.close()
            except Exception as e:
                print(f"[ERROR] Failed to close cursor: {e}")
        if connection:
            try:
                connection.close()
            except Exception as e:
                print(f"[ERROR] Failed to close connection: {e}")

def clear_old_seat_data():
    """Clear seat data only from previous days, not current day."""
    connection = get_db_connection()
    cursor = connection.cursor()
    
    try:
        cursor.execute("""
            SELECT COUNT(*) 
            FROM nm_seats 
            WHERE booking_date < CURDATE()
        """)
        old_records = cursor.fetchone()[0]
        
        if old_records > 0:
            cursor.execute("""
                DELETE FROM nm_seats 
                WHERE booking_date < CURDATE()
            """)
            connection.commit()
            print("[+] Old seat data cleared successfully")
        else:
            print("[+] No old seat data to clear")
            
        return True
        
    except Exception as e:
        print(f"Error clearing old seats: {e}")
        connection.rollback()
        return False
        
    finally:
        cursor.close()
        connection.close()

def get_movie_seat_status(movie_id=None):
    """Get seat status for all active movies or a specific movie."""
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    try:
        if movie_id:
            cursor.execute("""
                SELECT m.movie_id, m.title, m.show_time, 
                       GROUP_CONCAT(s.seat_number) as booked_seats
                FROM nm_movies m
                LEFT JOIN nm_seats s ON m.movie_id = s.movie_id 
                    AND s.booking_date = CURDATE()
                WHERE m.movie_id = %s
                AND m.status = 'active'
                GROUP BY m.movie_id
            """, (movie_id,))
        else:
            cursor.execute("""
                SELECT m.movie_id, m.title, m.show_time, 
                       GROUP_CONCAT(s.seat_number) as booked_seats
                FROM nm_movies m
                LEFT JOIN nm_seats s ON m.movie_id = s.movie_id 
                    AND s.booking_date = CURDATE()
                WHERE m.status = 'active'
                GROUP BY m.movie_id
            """)
        
        return cursor.fetchall()
        
    finally:
        cursor.close()
        connection.close()

def ensure_seats_table_exists():
    """Ensure seats table exists without clearing data."""
    connection = get_db_connection()
    cursor = connection.cursor()
    
    try:
        cursor.execute("SHOW TABLES LIKE 'nm_seats'")
        if not cursor.fetchone():
            cursor.execute("""
            CREATE TABLE nm_seats (
                seat_id INT AUTO_INCREMENT PRIMARY KEY,
                movie_id INT,
                user_id INT,
                seat_number VARCHAR(3) NOT NULL,
                booking_date DATE NOT NULL,
                CONSTRAINT fk_movie 
                    FOREIGN KEY (movie_id) 
                    REFERENCES nm_movies(movie_id)
                    ON DELETE CASCADE,
                CONSTRAINT fk_user
                    FOREIGN KEY (user_id) 
                    REFERENCES nm_users(user_id)
                    ON DELETE CASCADE,
                UNIQUE KEY unique_seat (movie_id, seat_number, booking_date)
            ) ENGINE=InnoDB
            """)
            print("✓ Seats table created successfully")
            connection.commit()
        return True
        
    except Exception as e:
        print(f"Error ensuring seats table: {e}")
        connection.rollback()
        return False
        
    finally:
        cursor.close()
        connection.close()

def get_active_movie_count():
    """Get count of currently active movies."""
    connection = get_db_connection()
    cursor = connection.cursor()
    
    try:
        cursor.execute("""
            SELECT COUNT(*) 
            FROM nm_movies 
            WHERE status = 'active' 
            AND show_date = CURDATE()
        """)
        return cursor.fetchone()[0]
        
    finally:
        cursor.close()
        connection.close()

def clear_seats_for_movie(movie_id=None):
    """Clear seat bookings for a specific movie or all movies."""
    connection = get_db_connection()
    cursor = connection.cursor()
    
    try:
        if movie_id:
            cursor.execute("""
                DELETE FROM nm_seats 
                WHERE movie_id = %s 
                AND booking_date = CURDATE()
            """, (movie_id,))
            message = "Seats cleared for selected movie"
        else:
            cursor.execute("""
                DELETE FROM nm_seats 
                WHERE booking_date = CURDATE()
            """)
            message = "Seats cleared for all movies"
            
        connection.commit()
        return True, message
        
    except Exception as e:
        print(f"Error clearing seats: {e}")
        connection.rollback()
        return False, str(e)
        
    finally:
        cursor.close()
        connection.close()

def clear_single_seat(movie_id, seat_number):
    """Clear booking for a single seat."""
    connection = get_db_connection()
    cursor = connection.cursor()
    
    try:
        cursor.execute("""
            DELETE FROM nm_seats 
            WHERE movie_id = %s 
            AND seat_number = %s 
            AND booking_date = CURDATE()
        """, (movie_id, seat_number))
            
        connection.commit()
        return True, "Seat booking cleared successfully"
        
    except Exception as e:
        print(f"Error clearing seat: {e}")
        connection.rollback()
        return False, str(e)
        
    finally:
        cursor.close()
        connection.close()

def check_active_movies_for_date(show_date, exclude_movie_id=None):
    """Check number of active movies for a specific date."""
    connection = get_db_connection()
    cursor = connection.cursor()
    
    try:
        if exclude_movie_id:
            cursor.execute("""
                SELECT COUNT(*) 
                FROM nm_movies 
                WHERE status = 'active' 
                AND show_date = %s
                AND movie_id != %s
            """, (show_date, exclude_movie_id))
        else:
            cursor.execute("""
                SELECT COUNT(*) 
                FROM nm_movies 
                WHERE status = 'active' 
                AND show_date = %s
            """, (show_date,))
            
        count = cursor.fetchone()[0]
        return count
        
    except Exception as e:
        print(f"Error checking active movies: {e}")
        return 0
        
    finally:
        cursor.close()
        connection.close()

if __name__ == "__main__":
    create_database()
