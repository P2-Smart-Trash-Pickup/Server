from fastapi import FastAPI, Request, Response, Form, Depends, HTTPException, status 
from fastapi.responses import HTMLResponse, RedirectResponse  # For returning HTML content
from fastapi.staticfiles import StaticFiles  # For serving static files (CSS, images)
from fastapi.templating import Jinja2Templates  # Template engine for HTML
import os
import sqlite3
import sys
from typing import Optional
from itsdangerous import URLSafeTimedSerializer, BadSignature

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

# Session Management
SECRET_KEY = "your_secret_key"  # Replace with your actual secret key
serializer = URLSafeTimedSerializer(SECRET_KEY)

def get_username_from_session(request: Request) -> Optional[str]:
    session_cookie = request.cookies.get("session")
    if not session_cookie:
        return None
    
    try:
        username = serializer.loads(session_cookie)
        return username
    except BadSignature:
        return None

# Route for homepage
@app.get("/", response_class=HTMLResponse)
async def read_index(request: Request):
    username = get_username_from_session(request)
    if not username:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    return templates.TemplateResponse("index.html", {"request": request, "username": username})

# Route for Martin Pictures page
@app.get("/MartinPics", response_class=HTMLResponse)
async def read_martinpics(request: Request):
    username = get_username_from_session(request)
    if not username:
        return RedirectResponse(url="/login?next=MartinPics", status_code=status.HTTP_303_SEE_OTHER)
    return templates.TemplateResponse("MartinPics.html", {"request": request, "username": username})

# Route for Notifications page - fix the function name to avoid duplicate names
@app.get("/Notifications", response_class=HTMLResponse)
async def read_notifications(request: Request):
    username = get_username_from_session(request)
    if not username:
        return RedirectResponse(url="/login?next=Notifications", status_code=status.HTTP_303_SEE_OTHER)
    return templates.TemplateResponse("Notifications.html", {"request": request, "username": username})

# Login page route
@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, next: str = ""):
    return templates.TemplateResponse("login.html", {"request": request, "next": next, "error": None})

# Login form handler
@app.post("/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...), next: str = Form("")):
    try:
        # Use correct path relative to the project root, not the backend dir
        # Assuming you run uvicorn from the backend directory
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

# Logout route
@app.get("/logout")
async def logout():
    response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie(key="session")
    return response