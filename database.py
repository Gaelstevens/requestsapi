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
# database.py - Version SQLite corrigée
import sqlite3
import os
import asyncio
from threading import Lock

# Lock pour éviter les problèmes de concurrence
db_lock = Lock()
"""
def get_db_path():
    
    if 'VERCEL' in os.environ:
        # Sur Vercel, on utilise /tmp pour l'écriture
        return '/tmp/university_requests.db'
    else:
        return 'university_requests.db'
"""


def get_db_path():
    """"""Obtenir le chemin de la base de données""""""
    if 'VERCEL' in os.environ:
        # Sur Vercel, on utilise /tmp pour l'écriture
        return '/tmp/university_requests.db'
    else:
        return 'university_requests.db'






def init_db():
    """"""Initialiser la base de données avec les tables""""""
    db_path = get_db_path()
    print(f"Initialisation de la base de données à: {db_path}")
    
    with db_lock:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row  # Pour avoir des dictionnaires
        
        try:
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
            print("Base de données initialisée avec succès")
        except Exception as e:
            print(f"Erreur lors de l'initialisation: {e}")
        finally:
            conn.close()

# Initialiser la base au démarrage
init_db()

async def execute_query(query, params=()):
    """"""Exécuter une requête et retourner le dernier ID""""""
    def sync_execute():
        with db_lock:
            conn = sqlite3.connect(get_db_path())
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            try:
                cursor.execute(query, params)
                conn.commit()
                result = cursor.lastrowid
                return result
            except Exception as e:
                conn.rollback()
                raise e
            finally:
                conn.close()
    
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, sync_execute)

async def fetch_one(query, params=()):
    """"""Récupérer une seule ligne""""""
    def sync_fetch():
        with db_lock:
            conn = sqlite3.connect(get_db_path())
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            try:
                cursor.execute(query, params)
                result = cursor.fetchone()
                return dict(result) if result else None
            except Exception as e:
                raise e
            finally:
                conn.close()
    
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, sync_fetch)

async def fetch_all(query, params=()):
    """"""Récupérer toutes les lignes""""""
    def sync_fetch():
        with db_lock:
            conn = sqlite3.connect(get_db_path())
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            try:
                cursor.execute(query, params)
                results = cursor.fetchall()
                return [dict(row) for row in results]
            except Exception as e:
                raise e
            finally:
                conn.close()
    
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, sync_fetch)

async def test_connection():
    """"""Test simple de connexion""""""
    try:
        result = await fetch_one("SELECT sqlite_version() as version")
        return {"status": "success", "version": result['version']}
    except Exception as e:
        return {"status": "error", "message": str(e)}

"""





# database.py - Version SQLite corrigée
import sqlite3
import os
import asyncio
from threading import RLock

# Lock pour éviter les problèmes de concurrence
db_lock = RLock()


def get_db_path():
    """Obtenir le chemin de la base de données"""
    if 'VERCEL' in os.environ:
        # Sur Vercel, on utilise /tmp pour l'écriture (éphémère)
        return '/tmp/university_requests.db'
    else:
        return 'university_requests.db'


def init_db():
    """Initialiser la base de données avec les tables"""
    db_path = get_db_path()
    print(f"Initialisation de la base de données à: {db_path}")
    
    with db_lock:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        
        try:
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
        except Exception as e:
            print(f"Erreur lors de l'initialisation: {e}")
        finally:
            conn.close()


# On initialise la DB une seule fois
db_path = get_db_path()
if not os.path.exists(db_path):
    init_db()


async def execute_query(query, params=()):
    """Exécuter une requête SQL"""
    def sync_execute():
        with db_lock:
            conn = sqlite3.connect(get_db_path())
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            try:
                cursor.execute(query, params)
                conn.commit()
                return cursor.lastrowid
            finally:
                conn.close()
    
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
            return dict(result) if result else None
    
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
            rows = cursor.fetchall()
            conn.close()
            return [dict(r) for r in rows]
    
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, sync_fetch)


async def test_connection():
    try:
        result = await fetch_one("SELECT sqlite_version() as version")
        return {"status": "success", "version": result['version']}
    except Exception as e:
        return {"status": "error", "message": str(e)}