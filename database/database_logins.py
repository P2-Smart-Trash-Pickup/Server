import sqlite3
from getpass import getpass
import hashlib

db_path = './database/user_auth.db'

def create_database():
    """Create the database and users table if they don't exist"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        email TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    conn.commit()
    conn.close()

def hash_password(password):
    """Hash the password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def register_user():
    """Register a new user"""
    username = input("Enter username: ")
    password = getpass("Enter password: ")
    email = input("Enter email (optional): ") or None
    
    password_hash = hash_password(password)
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO users (username, password_hash, email)
        VALUES (?, ?, ?)
        ''', (username, password_hash, email))
        
        conn.commit()
        print("User registered successfully!")
    except sqlite3.IntegrityError:
        print("Username already exists. Please choose another.")
    finally:
        conn.close()

def login_user():
    """Authenticate a user"""
    username = input("Username: ")
    password = getpass("Password: ")
    
    password_hash = hash_password(password)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
    SELECT username FROM users 
    WHERE username = ? AND password_hash = ?
    ''', (username, password_hash))
    
    user = cursor.fetchone()
    conn.close()
    
    if user:
        print(f"Login successful! Welcome, {user[0]}.")
        return True
    else:
        print("Invalid username or password.")
        return False

def main():
    create_database()
    
    while True:
        print("\nUser Authentication System")
        print("1. Register")
        print("2. Login")
        print("3. Exit")
        
        choice = input("Select an option: ")
        
        if choice == '1':
            register_user()
        elif choice == '2':
            login_user()
        elif choice == '3':
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()