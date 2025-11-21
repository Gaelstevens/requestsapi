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

"""








# database.py - Version avec gestion d'erreurs robuste
import asyncpg
import os
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def get_db():
    """
    Établit une connexion à la base de données avec gestion d'erreurs complète
    """
    max_retries = 3
    retry_delay = 1  # seconde
    
    for attempt in range(max_retries):
        try:
            logger.info(f"Tentative de connexion {attempt + 1}/{max_retries}")
            
            conn = await asyncpg.connect(
                host=os.getenv('DB_HOST'),
                user=os.getenv('DB_USER'),
                password=os.getenv('DB_PASSWORD'),
                database=os.getenv('DB_NAME'),
                port=6543,
                timeout=30,
                command_timeout=60  # Timeout pour les commandes SQL
            )
            
            # Test de la connexion
            await conn.execute("SELECT 1")
            logger.info("✅ Connexion à la base de données réussie")
            
            return conn
            
        except asyncpg.InvalidPasswordError:
            logger.error("❌ Mot de passe de base de données incorrect")
            raise Exception("Erreur de configuration de la base de données")
            
        except asyncpg.ConnectionDoesNotExistError:
            logger.error("❌ La base de données n'existe pas")
            raise Exception("Base de données introuvable")
            
        except asyncpg.TooManyConnectionsError:
            logger.warning("⚠️ Trop de connexions, attente avant nouvelle tentative...")
            if attempt < max_retries - 1:
                import asyncio
                await asyncio.sleep(retry_delay * (attempt + 1))
                continue
            else:
                logger.error("❌ Nombre maximum de tentatives de connexion dépassé")
                raise Exception("Service temporairement indisponible - trop de connexions")
                
        except asyncpg.ConnectionFailureError as e:
            logger.warning(f"⚠️ Échec de connexion (tentative {attempt + 1}): {e}")
            if attempt < max_retries - 1:
                import asyncio
                await asyncio.sleep(retry_delay * (attempt + 1))
                continue
            else:
                logger.error("❌ Impossible de se connecter après plusieurs tentatives")
                raise Exception("Service de base de données temporairement indisponible")
                
        except Exception as e:
            logger.error(f"❌ Erreur inattendue lors de la connexion: {e}")
            raise Exception(f"Erreur de connexion: {str(e)}")
    
    raise Exception("Échec de toutes les tentatives de connexion")

async def test_connection():
    """
    Fonction de test de connexion pour le endpoint /test-db
    """
    try:
        conn = await get_db()
        
        # Test des tables
        users_exists = await conn.fetchval(
            "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'users')"
        )
        requests_exists = await conn.fetchval(
            "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'requests')"
        )
        
        # Test des données
        users_count = await conn.fetchval("SELECT COUNT(*) FROM users")
        requests_count = await conn.fetchval("SELECT COUNT(*) FROM requests")
        
        await conn.close()
        
        return {
            "status": "success",
            "database": "connectée",
            "tables": {
                "users": users_exists,
                "requests": requests_exists
            },
            "counts": {
                "users": users_count,
                "requests": requests_count
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Erreur lors du test de connexion: {e}")
        return {
            "status": "error",
            "message": str(e),
            "database": "non connectée"
        }