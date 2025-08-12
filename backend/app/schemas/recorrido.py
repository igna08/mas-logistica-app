import uuid
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal

# First, define schemas for nested objects if they are to be included
class Control(BaseModel):
    id: uuid.UUID
    tipo: str
    detalle: Optional[dict] = None
    foto: Optional[str] = None
    creado_en: datetime

    class Config:
        from_attributes = True

class Alerta(BaseModel):
    id: uuid.UUID
    mensaje: str
    leida: bool
    creado_en: datetime

    class Config:
        from_attributes = True


# Schema for starting a recorrido
class RecorridoCreate(BaseModel):
    vehiculo_id: uuid.UUID
    km_inicial: Decimal = Field(..., gt=0)
    estado_inicial: Optional[str] = None
    observaciones_inicio: Optional[str] = None
    # chofer_id will be taken from the JWT token


# Schema for ending a recorrido
class RecorridoEnd(BaseModel):
    km_final: Decimal = Field(..., gt=0)
    estado_final: Optional[str] = None
    combustible_litros: Optional[Decimal] = Field(None, gt=0)
    combustible_costo: Optional[Decimal] = Field(None, gt=0)
    combustible_foto: Optional[str] = None # URL
    observaciones_fin: Optional[str] = None


# Full schema for representing a recorrido from the DB
class Recorrido(BaseModel):
    id: uuid.UUID
    chofer_id: uuid.UUID
    vehiculo_id: uuid.UUID
    fecha_inicio: datetime
    fecha_fin: Optional[datetime] = None
    km_inicial: Optional[Decimal] = None
    km_final: Optional[Decimal] = None
    estado_inicial: Optional[str] = None
    estado_final: Optional[str] = None
    combustible_litros: Optional[Decimal] = None
    combustible_costo: Optional[Decimal] = None
    combustible_foto: Optional[str] = None
    observaciones_inicio: Optional[str] = None
    observaciones_fin: Optional[str] = None
    estado: str

    # Nested data for detail view
    controles: List[Control] = []
    alertas: List[Alerta] = []

    class Config:
        from_attributes = True
        # Pydantic v2 needs this to handle Decimal type
        json_encoders = {
            Decimal: lambda v: float(v)
        }
