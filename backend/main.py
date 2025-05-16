"""
FastAPI application for user authentication and page management.

This module handles:
- User session management
- Page routing with authentication
- Login/logout functionality
- Serving static files and templates
"""

from fastapi import FastAPI, Request, Response, Form, Depends, HTTPException, status 
from fastapi.responses import HTMLResponse, RedirectResponse  # For returning HTML content
from fastapi.staticfiles import StaticFiles  # For serving static files (CSS, images)
from fastapi.templating import Jinja2Templates  # Template engine for HTML
import os
import sqlite3
import sys
from typing import Optional
from itsdangerous import URLSafeTimedSerializer, BadSignature

# Add parent directory to path to allow database module import
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.database_logins import hash_password

# Create FastAPI application instance
app = FastAPI()

# Set up file paths for the application
frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend")
static_path = os.path.join(frontend_path, "static")
templates_path = os.path.join(frontend_path, "templates")

# Make static files accessible at /static URL
app.mount("/static", StaticFiles(directory=static_path), name="static")
# Configure template engine with correct directory
templates = Jinja2Templates(directory=templates_path)

# Session Management Configuration
SECRET_KEY = "your_secret_key"  # Replace with your actual secret key
serializer = URLSafeTimedSerializer(SECRET_KEY)

def get_username_from_session(request: Request) -> Optional[str]:
    """
    Retrieve username from session cookie.
    
    Args:
        request: FastAPI Request object containing cookies
        
    Returns:
        str: Username if session is valid
        None: If no session or invalid session
    """
    session_cookie = request.cookies.get("session")
    if not session_cookie:
        return None
    
    try:
        username = serializer.loads(session_cookie)
        return username
    except BadSignature:
        return None

@app.get("/", response_class=HTMLResponse)
async def read_index(request: Request):
    """
    Serve the homepage.
    
    Redirects to login page if user is not authenticated.
    
    Args:
        request: FastAPI Request object
        
    Returns:
        TemplateResponse: Rendered index.html template
        RedirectResponse: To login page if not authenticated
    """
    username = get_username_from_session(request)
    if not username:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    return templates.TemplateResponse("index.html", {"request": request, "username": username})

@app.get("/MartinPics", response_class=HTMLResponse)
async def read_martinpics(request: Request):
    """
    Serve the MartinPics page.
    
    Redirects to login page if user is not authenticated, with return URL.
    
    Args:
        request: FastAPI Request object
        
    Returns:
        TemplateResponse: Rendered MartinPics.html template
        RedirectResponse: To login page if not authenticated
    """
    username = get_username_from_session(request)
    if not username:
        return RedirectResponse(url="/login?next=MartinPics", status_code=status.HTTP_303_SEE_OTHER)
    return templates.TemplateResponse("MartinPics.html", {"request": request, "username": username})

@app.get("/Notifications", response_class=HTMLResponse)
async def read_notifications(request: Request):
    """
    Serve the Notifications page.
    
    Redirects to login page if user is not authenticated, with return URL.
    
    Args:
        request: FastAPI Request object
        
    Returns:
        TemplateResponse: Rendered Notifications.html template
        RedirectResponse: To login page if not authenticated
    """
    username = get_username_from_session(request)
    if not username:
        return RedirectResponse(url="/login?next=Notifications", status_code=status.HTTP_303_SEE_OTHER)
    return templates.TemplateResponse("Notifications.html", {"request": request, "username": username})

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, next: str = ""):
    """
    Serve the login page.
    
    Args:
        request: FastAPI Request object
        next: Optional URL to redirect to after successful login
        
    Returns:
        TemplateResponse: Rendered login.html template
    """
    return templates.TemplateResponse("login.html", {"request": request, "next": next, "error": None})

@app.post("/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...), next: str = Form("")):
    """
    Handle login form submission.
    
    Args:
        request: FastAPI Request object
        username: Submitted username from form
        password: Submitted password from form
        next: URL to redirect to after successful login
        
    Returns:
        RedirectResponse: To target page after successful login
        TemplateResponse: Login page with error message if authentication fails
    """
    try:
        # Use correct path relative to the project root, not the backend dir
        db_path = os.path.join("..", "database", "user_auth.db")
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        password_hash = hash_password(password)
        
        cursor.execute('''
        SELECT username, userType FROM users 
        WHERE username = ? AND password_hash = ?
        ''', (username, password_hash))
        
        user = cursor.fetchone()
        conn.close()
        
        if user:
            # Create session cookie
            session = serializer.dumps(username)
            response = RedirectResponse(url=f"/{next}" if next else "/", status_code=status.HTTP_303_SEE_OTHER)
            response.set_cookie(key="session", value=session, httponly=True)
            return response
        else:
            return templates.TemplateResponse("login.html", {"request": request, "next": next, "error": "Invalid username or password"})
    except Exception as e:
        import traceback
        print(f"Login error: {str(e)}")
        print(traceback.format_exc())
        return templates.TemplateResponse("login.html", {"request": request, "next": next, "error": f"System error: {str(e)}"})

@app.get("/logout")
async def logout():
    """
    Handle user logout.
    
    Clears the session cookie and redirects to homepage.
    
    Returns:
        RedirectResponse: To homepage after clearing session
    """
    response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie(key="session")
    return response