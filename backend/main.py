from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os

app = FastAPI()


frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend")
static_path = os.path.join(frontend_path, "static")
templates_path = os.path.join(frontend_path, "templates")

app.mount("/static", StaticFiles(directory=static_path), name="static")
templates = Jinja2Templates(directory=templates_path)


@app.get("/", response_class=HTMLResponse)
async def read_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "username": "User"})
