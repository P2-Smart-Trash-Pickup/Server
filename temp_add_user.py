import sqlite3
import hashlib
import getpass
import os

# Ensure the database directory exists
os.makedirs('./database', exist_ok=True)

# Database path
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
        userType TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    conn.commit()
    conn.close()

def hash_password(password):
    """Hash the password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def add_user():
    """Add a new user to the database"""
    username = input("Enter username: ")
    password = getpass.getpass("Enter password: ")
    confirm = getpass.getpass("Confirm password: ")
    
    if password != confirm:
        print("Passwords don't match!")
        return
    
    if input("Admin user? (y/n): ").lower() == 'y':
        user_type = "Admin"
    else:
        user_type = None
        
    password_hash = hash_password(password)
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO users (username, password_hash, userType)
        VALUES (?, ?, ?)
        ''', (username, password_hash, user_type))
        
        conn.commit()
        print(f"User '{username}' added successfully!")
    except sqlite3.IntegrityError:
        print(f"Username '{username}' already exists!")
    finally:
        conn.close()

if __name__ == "__main__":
    create_database()
    add_user()