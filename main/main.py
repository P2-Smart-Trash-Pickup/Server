import os
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

SECRET_KEY = os.getenv("SECRET_KEY", "fallback-secret-key")  # Loads a secret key from environment variable or uses a fallback
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

    if user and sha256_crypt.verify(password, user.password_hash):
        if user.must_reset:
            # Store only email in session for password reset
            token = serializer.dumps({"email": user.email, "force_reset": True})
            resp = RedirectResponse("/change-password", status_code=302)
        else:
            token = serializer.dumps({"email": user.email, "is_admin": user.is_admin})
            resp = RedirectResponse("/", status_code=302)

        resp.set_cookie(key="session", value=token, httponly=True)
        db.close()
        return resp

    db.close()
    return HTMLResponse("<h1>Invalid credentials</h1><p><a href='/login'>Try again</a></p>", status_code=401)

@app.get("/change-password", response_class=HTMLResponse)
async def change_password_page(request: Request):
    user = get_session_user(request)
    if not user or not user.get("force_reset"):
        return RedirectResponse("/", status_code=302)
    return templates.TemplateResponse("ChangePassword.html", {"request": request})

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

@app.post("/change-password")
async def change_password(
    request: Request,
    new_password: str = Form(...),
    confirm_password: str = Form(...),
):
    user = get_session_user(request)
    if not user or not user.get("force_reset"):
        return RedirectResponse("/", status_code=302)

    if new_password != confirm_password:
        return HTMLResponse("<h1>Passwords do not match.</h1><a href='/change-password'>Try again</a>", status_code=400)

    db = SessionLocal()
    user_obj = db.query(User).filter(User.email == user["email"]).first()
    user_obj.password_hash = sha256_crypt.hash(new_password)
    user_obj.must_reset = False
    db.commit()

    # Get values before session closes
    email = user_obj.email
    is_admin = user_obj.is_admin
    db.close()

    token = serializer.dumps({"email": email, "is_admin": is_admin})
    resp = RedirectResponse("/", status_code=302)
    resp.set_cookie(key="session", value=token, httponly=True)
    return resp

