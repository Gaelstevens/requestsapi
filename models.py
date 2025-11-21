# models.py - NOUVEAU FICHIER PROPRE
from pydantic import BaseModel, validator
import re
from typing import Optional

class UserRegister(BaseModel):
    matricule: str
    name: str
    last_name: str
    email: str
    phone: str
    password: str

    @validator('matricule')
    def validate_matricule(cls, v):
        if len(v) > 15:
            raise ValueError('Le matricule ne peut pas dépasser 15 caractères')
        if not all(c.isalnum() or c in ['-', '_', '.'] for c in v):
            raise ValueError('Le matricule peut contenir lettres, chiffres, tirets, underscores et points')
        return v

    @validator('phone')
    def validate_phone(cls, v):
        if not v.isdigit() or len(v) != 9:
            raise ValueError('Le téléphone doit contenir 9 chiffres')
        return v

    @validator('name', 'last_name')
    def validate_name(cls, v):
        if len(v) > 255:
            raise ValueError('Le nom ne peut pas dépasser 100 caractères')
        if not re.match(r'^[a-zA-Z\s\-]+$', v):
            raise ValueError('Le nom ne peut contenir que des lettres, espaces et tirets')
        return v

class UserLogin(BaseModel):
    login: str
    password: str

class RequestSubmit(BaseModel):
    all_name: str
    matricule: str
    cycle: str
    level: int
    nom_code_ue: str
    note_exam: bool = False
    note_cc: bool = False
    note_tp: bool = False
    note_tpe: bool = False
    autre: bool = False
    comment: Optional[str] = None
    just_p: bool = False

    @validator('all_name')
    def validate_all_name(cls, v):
        if len(v) > 255:
            raise ValueError('Le nom complet ne peut pas dépasser 200 caractères')
        return v

    @validator('matricule')
    def validate_matricule(cls, v):
        if len(v) > 15:
            raise ValueError('Le matricule ne peut pas dépasser 15 caractères')
        return v

    @validator('cycle')
    def validate_cycle(cls, v):
        if len(v) > 50:
            raise ValueError('Le cycle ne peut pas dépasser 50 caractères')
        return v

    @validator('level')
    def validate_level(cls, v):
        if not 0 <= v <= 32767:
            raise ValueError('Le niveau doit être entre 0 et 32767')
        return v

    @validator('nom_code_ue')
    def validate_nom_code_ue(cls, v):
        if len(v) > 2048:
            raise ValueError('Le nom/code UE est trop long')
        return v

    @validator('comment')
    def validate_comment(cls, v):
        if v and len(v) > 5000:
            raise ValueError('Le commentaire ne peut pas dépasser 5000 caractères')
        return v