""" import asyncpg
import os
import ssl

async def get_db():
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE  # nécessaire pour Supabase sur Vercel

    return await asyncpg.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        port=6543,
        ssl=ssl_context
    )

"""


# database.py - Version SQLite
import sqlite3
import os
from contextlib import asynccontextmanager
import asyncio
from threading import Lock

# Lock pour éviter les problèmes de concurrence
db_lock = Lock()

def get_db_path():
    """Obtenir le chemin de la base de données"""
    if os.getenv('VERCEL'):
        # Sur Vercel, on utilise /tmp pour l'écriture
        return '/tmp/university_requests.db'
    else:
        return 'university_requests.db'

def init_db():
    """Initialiser la base de données avec les tables"""
    db_path = get_db_path()
    
    with db_lock:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row  # Pour avoir des dictionnaires
        
        # Créer la table users
        conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                matricule TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                phone TEXT NOT NULL,
                password TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Créer la table requests
        conn.execute('''
            CREATE TABLE IF NOT EXISTS requests (
                request_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                all_name TEXT NOT NULL,
                matricule TEXT NOT NULL,
                cycle TEXT NOT NULL,
                level INTEGER NOT NULL,
                nom_code_ue TEXT NOT NULL,
                note_exam BOOLEAN DEFAULT FALSE,
                note_cc BOOLEAN DEFAULT FALSE,
                note_tp BOOLEAN DEFAULT FALSE,
                note_tpe BOOLEAN DEFAULT FALSE,
                autre BOOLEAN DEFAULT FALSE,
                comment TEXT,
                just_p BOOLEAN DEFAULT FALSE,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        conn.commit()
        conn.close()

# Initialiser la base au démarrage
init_db()

async def get_db():
    """Obtenir une connexion à la base de données"""
    # Pour SQLite, on utilise une approche synchrone dans un thread
    def sync_get_conn():
        db_path = get_db_path()
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    # Exécuter dans un thread pour éviter de bloquer l'event loop
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, sync_get_conn)

async def execute_query(query, params=()):
    """Exécuter une requête et retourner le résultat"""
    def sync_execute():
        with db_lock:
            conn = sqlite3.connect(get_db_path())
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            result = cursor.lastrowid
            conn.close()
            return result
    
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, sync_execute)

async def fetch_one(query, params=()):
    """Récupérer une seule ligne"""
    def sync_fetch():
        with db_lock:
            conn = sqlite3.connect(get_db_path())
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query, params)
            result = cursor.fetchone()
            conn.close()
            return result
    
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, sync_fetch)

async def fetch_all(query, params=()):
    """Récupérer toutes les lignes"""
    def sync_fetch():
        with db_lock:
            conn = sqlite3.connect(get_db_path())
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query, params)
            result = cursor.fetchall()
            conn.close()
            return result
    
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, sync_fetch)

async def test_connection():
    """Test simple de connexion"""
    try:
        result = await fetch_one("SELECT sqlite_version() as version")
        return {"status": "success", "version": result['version']}
    except Exception as e:
        return {"status": "error", "message": str(e)}