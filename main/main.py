from fastapi import FastAPI, Request, Form, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from itsdangerous import URLSafeSerializer
from main.dbmodels import init_db, SessionLocal, User
from passlib.hash import sha256_crypt
from datetime import datetime, timedelta

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

SECRET_KEY = "your-secret-key"
serializer = URLSafeSerializer(SECRET_KEY)

init_db()

# Helper to get user from session cookie
def get_session_user(request: Request):
    token = request.cookies.get("session")
    if token:
        try:
            return serializer.loads(token)
        except:
            return None
    return None

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    user = get_session_user(request)
    if not user:
        return RedirectResponse("/login", status_code=302)
    return templates.TemplateResponse("index.html", {"request": request, "user": user})

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def login(response: Response, username: str = Form(...), password: str = Form(...)):
    db = SessionLocal()
    user = db.query(User).filter(User.email == username).first()
    db.close()

    if user and sha256_crypt.verify(password, user.password_hash):
        token = serializer.dumps({"email": user.email, "is_admin": user.is_admin})
        resp = RedirectResponse("/", status_code=302)
        resp.set_cookie(key="session", value=token, httponly=True)
        return resp

    return HTMLResponse("<h1>Invalid credentials</h1><p><a href='/login'>Try again</a></p>", status_code=401)

@app.get("/logout")
async def logout():
    resp = RedirectResponse("/login", status_code=302)
    resp.delete_cookie("session")
    return resp

@app.get("/api/latest-weight", response_class=HTMLResponse)
async def get_latest_weight():
    import random
    weight = round(random.uniform(2.0, 10.0), 2)
    return f"<p><strong>Latest Weight:</strong> {weight} kg</p>"

# ========== ADMIN: Add User Page ==========
@app.get("/add-user", response_class=HTMLResponse)
async def add_user_page(request: Request):
    user = get_session_user(request)
    if not user or not user.get("is_admin"):
        return RedirectResponse("/", status_code=302)
    return templates.TemplateResponse("CreateUser.html", {"request": request})

@app.post("/add-user")
async def add_user(
    request: Request,
    email: str = Form(...),
    temp_password: str = Form(...),
    is_admin: bool = Form(False),
):
    user = get_session_user(request)
    if not user or not user.get("is_admin"):
        return RedirectResponse("/", status_code=302)

    db = SessionLocal()
    existing = db.query(User).filter(User.email == email).first()
    if existing:
        db.close()
        return HTMLResponse("<h1>User already exists.</h1><a href='/add-user'>Go back</a>", status_code=409)

    new_user = User(
        email=email,
        password_hash=sha256_crypt.hash(temp_password),
        is_admin=is_admin,
        must_reset=True,
        temp_expiry=datetime.utcnow() + timedelta(hours=48)
    )
    db.add(new_user)
    db.commit()
    db.close()
    return RedirectResponse("/", status_code=302)
