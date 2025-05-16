"""
User authentication database operations.

This module provides functions for:
- Creating the authentication database
- Hashing passwords
- Registering new users
- Authenticating users
"""

import sqlite3
from getpass import getpass
import hashlib

# Database file path
db_path = './database/user_auth.db'

def create_database():
    """
    Initialize the database and create users table if it doesn't exist.
    
    The users table contains:
    - id: Primary key
    - username: Unique identifier
    - password_hash: Hashed password
    - userType: Optional user type (e.g., 'Admin')
    - created_at: Timestamp of account creation
    """
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

def hash_password(password: str) -> str:
    """
    Hash a password using SHA-256 algorithm.
    
    Args:
        password: Plain text password to hash
        
    Returns:
        str: Hexadecimal string representation of the hash
    """
    return hashlib.sha256(password.encode()).hexdigest()

def register_user():
    """
    Register a new user through interactive prompt.
    
    Collects:
    - Username
    - Password (hidden input)
    - User type (admin or regular user)
    
    Handles duplicate username errors.
    """
    username = input("Enter username: ")
    password = getpass("Enter password: ")
    if(input("Admin (y/n): ") == "y"):
        userType = "Admin"
        print(f"User type {userType}")
    else:
        userType = None
        print(f"User type {userType}")

    password_hash = hash_password(password)
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO users (username, password_hash, userType)
        VALUES (?, ?, ?)
        ''', (username, password_hash, userType))
        
        conn.commit()
        print("User registered successfully!")
    except sqlite3.IntegrityError:
        print("Username already exists. Please choose another.")
    finally:
        conn.close()

def login_user() -> bool:
    """
    Authenticate a user through interactive prompt.
    
    Returns:
        bool: True if authentication succeeded, False otherwise
    """
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
    """
    Main entry point for command-line user authentication system.
    
    Provides menu for:
    1. User registration
    2. User login
    3. Exit
    """
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