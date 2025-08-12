import uuid
from sqlalchemy import UUID
from app.extensions import db

class Vehiculo(db.Model):
    __tablename__ = 'vehiculos'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patente = db.Column(db.Text, unique=True, nullable=False)
    modelo = db.Column(db.Text)
    zona = db.Column(db.Text)
    activo = db.Column(db.Boolean, default=True, nullable=False)
    creado_en = db.Column(db.TIMESTAMP(timezone=True), server_default=db.func.now(), nullable=False)

    # Relationship to Recorrido model
    recorridos = db.relationship('Recorrido', back_populates='vehiculo', lazy='dynamic')

    def __repr__(self):
        return f'<Vehiculo {self.patente}>'
