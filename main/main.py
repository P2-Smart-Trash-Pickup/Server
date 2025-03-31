from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import random

app = FastAPI()

# Mount /static folder for CSS
app.mount("/static", StaticFiles(directory="static"), name="static")

# Setup templates
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/latest", response_class=HTMLResponse)
async def latest_data(request: Request):
    distance = random.randint(10, 200)
    weight = round(random.uniform(0.5, 10.0), 2)
    return templates.TemplateResponse("_latest_data.html", {
        "request": request,
        "distance": distance,
        "weight": weight
    })
