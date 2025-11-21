# main.py pour Supabase
from fastapi import FastAPI, Request, Form, Depends, HTTPException, status, Cookie
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import psycopg2
import json
import base64
import hmac
import hashlib

from database import get_db
from models import UserRegister, UserLogin, RequestSubmit
from auth import hash_password, verify_password

app = FastAPI(title="Gestion des Requêtes Universitaires")

# Configuration des templates
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Clé secrète pour signer les cookies
SECRET_KEY = "ma-cle-secrete-pour-les-cookies-2024"

def sign_data(data: str) -> str:
    """Signer les données du cookie"""
    return hmac.new(SECRET_KEY.encode(), data.encode(), hashlib.sha256).hexdigest()

def create_user_cookie(user_data: dict) -> str:
    """Créer un cookie utilisateur signé"""
    data_json = json.dumps(user_data)
    data_b64 = base64.b64encode(data_json.encode()).decode()
    signature = sign_data(data_b64)
    return f"{data_b64}.{signature}"

def verify_user_cookie(cookie_data: str) -> dict:
    """Vérifier et décoder le cookie utilisateur"""
    try:
        if not cookie_data:
            return None
        data_b64, signature = cookie_data.split(".")
        if sign_data(data_b64) != signature:
            return None
        data_json = base64.b64decode(data_b64).decode()
        return json.loads(data_json)
    except:
        return None

# Dépendance pour vérifier l'utilisateur connecté
def get_current_user(user_data: str = Cookie(None)):
    if not user_data:
        raise HTTPException(status_code=303, headers={"Location": "/login"})
    
    user = verify_user_cookie(user_data)
    if not user:
        raise HTTPException(status_code=303, headers={"Location": "/login"})
    
    return user

# Routes
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("base.html", {"request": request})

@app.get("/register", response_class=HTMLResponse)
async def register_form(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/register")
async def register_user(request: Request):
    form_data = await request.form()
    
    try:
        user_data = UserRegister(
            matricule=form_data.get("matricule"),
            name=form_data.get("name"),
            last_name=form_data.get("last_name"),
            email=form_data.get("email"),
            phone=form_data.get("phone"),
            password=form_data.get("password")
        )
        
        with get_db() as conn:
            with conn.cursor() as cursor:
                # Vérifier si l'email ou matricule existe déjà
                cursor.execute(
                    "SELECT user_id FROM users WHERE email = %s OR matricule = %s",
                    (user_data.email, user_data.matricule)
                )
                if cursor.fetchone():
                    raise HTTPException(status_code=400, detail="Email ou matricule déjà utilisé")
                
                # Créer l'utilisateur
                cursor.execute(
                    """INSERT INTO users (matricule, name, last_name, email, phone, password) 
                    VALUES (%s, %s, %s, %s, %s, %s)""",
                    (user_data.matricule, user_data.name, user_data.last_name, 
                     user_data.email, user_data.phone, hash_password(user_data.password))
                )
                conn.commit()
                
        return RedirectResponse(url="/login", status_code=303)
        
    except Exception as e:
        return templates.TemplateResponse("register.html", {
            "request": request, 
            "error": str(e)
        })

@app.get("/login", response_class=HTMLResponse)
async def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def login_user(request: Request):
    form_data = await request.form()
    
    try:
        login_data = UserLogin(
            login=form_data.get("login"),
            password=form_data.get("password")
        )
        
        with get_db() as conn:
            with conn.cursor() as cursor:
                # Chercher l'utilisateur par email ou matricule
                cursor.execute(
                    """SELECT user_id, matricule, name, last_name, email, password 
                    FROM users WHERE email = %s OR matricule = %s""",
                    (login_data.login, login_data.login)
                )
                user = cursor.fetchone()
                
                if not user or not verify_password(login_data.password, user['password']):
                    raise HTTPException(status_code=400, detail="Identifiants incorrects")
                
                # Créer les données utilisateur pour le cookie
                user_session = {
                    'user_id': user['user_id'],
                    'matricule': user['matricule'],
                    'name': user['name'],
                    'last_name': user['last_name'],
                    'email': user['email']
                }
                
                # Créer le cookie signé
                user_cookie = create_user_cookie(user_session)
                
                response = RedirectResponse(url="/dashboard", status_code=303)
                response.set_cookie(
                    key="user_data", 
                    value=user_cookie,
                    httponly=True,
                    max_age=24*60*60
                )
                return response
                
    except Exception as e:
        return templates.TemplateResponse("login.html", {
            "request": request, 
            "error": str(e)
        })

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, current_user: dict = Depends(get_current_user)):
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "user": current_user
    })

@app.get("/submit-request", response_class=HTMLResponse)
async def submit_request_form(request: Request, current_user: dict = Depends(get_current_user)):
    return templates.TemplateResponse("submit_request.html", {
        "request": request,
        "user": current_user
    })

@app.post("/submit-request")
async def submit_request(request: Request, current_user: dict = Depends(get_current_user)):
    form_data = await request.form()
    
    try:
        request_data = RequestSubmit(
            all_name=f"{current_user['name']} {current_user['last_name']}",
            matricule=current_user['matricule'],
            cycle=form_data.get("cycle"),
            level=int(form_data.get("level")),
            nom_code_ue=form_data.get("nom_code_ue"),
            note_exam=bool(form_data.get("note_exam")),
            note_cc=bool(form_data.get("note_cc")),
            note_tp=bool(form_data.get("note_tp")),
            note_tpe=bool(form_data.get("note_tpe")),
            autre=bool(form_data.get("autre")),
            comment=form_data.get("comment"),
            just_p=bool(form_data.get("just_p"))
        )
        
        with get_db() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """INSERT INTO requests 
                    (user_id, all_name, matricule, cycle, level, nom_code_ue, 
                     note_exam, note_cc, note_tp, note_tpe, autre, comment, just_p) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                    (current_user['user_id'], request_data.all_name, request_data.matricule,
                     request_data.cycle, request_data.level, request_data.nom_code_ue,
                     request_data.note_exam, request_data.note_cc, request_data.note_tp,
                     request_data.note_tpe, request_data.autre, request_data.comment,
                     request_data.just_p)
                )
                conn.commit()
                
        return RedirectResponse(url="/my-requests", status_code=303)
        
    except Exception as e:
        return templates.TemplateResponse("submit_request.html", {
            "request": request,
            "user": current_user,
            "error": str(e)
        })

@app.get("/my-requests", response_class=HTMLResponse)
async def my_requests(request: Request, current_user: dict = Depends(get_current_user)):
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM requests WHERE user_id = %s ORDER BY created_at DESC",
                (current_user['user_id'],)
            )
            requests = cursor.fetchall()
    
    return templates.TemplateResponse("my_requests.html", {
        "request": request,
        "user": current_user,
        "requests": requests
    })

@app.get("/logout")
async def logout():
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie("user_data")
    return response