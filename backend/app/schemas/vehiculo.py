import uuid
from pydantic import BaseModel, constr, Field
from typing import Optional
from datetime import datetime

# Pydantic schema for creating a vehiculo
class VehiculoCreate(BaseModel):
    patente: constr(strip_whitespace=True, to_upper=True, min_length=6, max_length=10)
    modelo: Optional[str] = None
    zona: Optional[str] = None
    activo: bool = True

# Pydantic schema for updating a vehiculo
class VehiculoUpdate(BaseModel):
    patente: Optional[constr(strip_whitespace=True, to_upper=True, min_length=6, max_length=10)] = None
    modelo: Optional[str] = None
    zona: Optional[str] = None
    activo: Optional[bool] = None

# Pydantic schema for representing a vehiculo from the DB
class Vehiculo(BaseModel):
    id: uuid.UUID
    patente: str
    modelo: Optional[str] = None
    zona: Optional[str] = None
    activo: bool
    creado_en: datetime

    class Config:
        from_attributes = True # Replaces orm_mode in Pydantic v2
