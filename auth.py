# auth.py (reste identique)
"""from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)"""

#ff





"""
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """"""Hasher un mot de passe en le tronquant à 72 caractères si nécessaire""""""
    # Double sécurité : troncature + hachage
    truncated_password = password[:72] if len(password) > 72 else password
    return pwd_context.hash(truncated_password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """"""Vérifier un mot de passe""""""
    truncated_password = plain_password[:72] if len(plain_password) > 72 else plain_password
    return pwd_context.verify(truncated_password, hashed_password)



"""


"""

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def _truncate_to_72_bytes(s: str) -> str:
    """"""Tronque silencieusement une string à 72 bytes (UTF-8) pour bcrypt.""""""
    b = s.encode("utf-8")
    if len(b) > 72:
        b = b[:72]
    return b.decode("utf-8", errors="ignore")

def hash_password(password: str) -> str:
    password = _truncate_to_72_bytes(password)  # coupe silencieusement
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    plain_password = _truncate_to_72_bytes(plain_password)
    return pwd_context.verify(plain_password, hashed_password)"""

from passlib.context import CryptContext

# Utilise argon2 au lieu de bcrypt (stable sur Vercel)
pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto"
)

def hash_password(password: str) -> str:
    """Hash sécurisé avec Argon2 (pas de limite 72 bytes, compatible Vercel)."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Vérifie un mot de passe via Argon2."""
    return pwd_context.verify(plain_password, hashed_password)