import uuid
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UsuarioBase(BaseModel):
    email: EmailStr
    nombre: str
    rol: str
    profile_picture_url: Optional[str] = None

class UsuarioCreate(UsuarioBase):
    password: str

class UsuarioUpdate(BaseModel):
    nombre: Optional[str] = None
    profile_picture_url: Optional[str] = None

class Usuario(UsuarioBase):
    id: uuid.UUID
    activo: bool
    creado_en: datetime

    class Config:
        from_attributes = True
