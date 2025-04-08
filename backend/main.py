from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse  # For returning HTML content
from fastapi.staticfiles import StaticFiles  # For serving static files (CSS, images)
from fastapi.templating import Jinja2Templates  # Template engine for HTML
import os

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


# Route for homepage
@app.get("/", response_class=HTMLResponse)
async def read_index(request: Request):
    # Render index.html with username
    return templates.TemplateResponse("index.html", {"request": request, "username": "User"})

# Route for Martin Pictures page
@app.get("/MartinPics", response_class=HTMLResponse)
async def read_martinpics(request: Request):
    # Render MartinPics.html with username
    return templates.TemplateResponse("MartinPics.html", {"request": request, "username": "User"})

# Route for Notifications page
@app.get("/Notifications", response_class=HTMLResponse)
async def read_martinpics(request: Request):
    # Render Notifications.html with username
    return templates.TemplateResponse("Notifications.html", {"request": request, "username": "User"})