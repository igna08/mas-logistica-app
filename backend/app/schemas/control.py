import uuid
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

# Schema for creating a control
class ControlCreate(BaseModel):
    recorrido_id: uuid.UUID
    tipo: str = Field(..., min_length=3) # e.g., 'fluidos', 'luces', 'neumaticos'
    detalle: Optional[Dict[str, Any]] = None
    foto: Optional[str] = None # URL

# Schema for representing a control from the DB
class Control(BaseModel):
    id: uuid.UUID
    recorrido_id: uuid.UUID
    tipo: str
    detalle: Optional[Dict[str, Any]] = None
    foto: Optional[str] = None
    creado_en: datetime

    class Config:
        from_attributes = True
