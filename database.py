""" # database.py
import psycopg2
from contextlib import contextmanager
import os

def get_db_connection():
    return psycopg2.connect(
        host=os.getenv('DB_HOST'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME'),
        port=os.getenv('DB_PORT', 5432)
    )

@contextmanager
def get_db():
    conn = get_db_connection()
    try:
        yield conn
    finally:
        conn.close() 


# database.py - Version asyncpg
import asyncpg
import os
from contextlib import asynccontextmanager

async def get_db_connection():
    return await asyncpg.connect(
        host=os.getenv('DB_HOST'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME'),
        port=os.getenv('DB_PORT', 5432)
    )

@asynccontextmanager
async def get_db():
    conn = await get_db_connection()
    try:
        yield conn
    finally:
        await conn.close()

"""



# database.py - Version robuste
import asyncpg
import os

async def get_db_connection():
    """Établit une connexion à la base de données"""
    try:
        conn = await asyncpg.connect(
            host=os.getenv('DB_HOST'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            database=os.getenv('DB_NAME'),
            port=5432,
            timeout=30
        )
        return conn
    except Exception as e:
        print(f"Erreur de connexion à la base: {e}")
        raise

# Alias pour compatibilité
get_db = get_db_connection