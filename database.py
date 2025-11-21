import asyncpg
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