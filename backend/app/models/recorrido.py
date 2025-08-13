import uuid
from sqlalchemy import UUID
from app.extensions import db

class Recorrido(db.Model):
    __tablename__ = 'recorridos'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    chofer_id = db.Column(UUID(as_uuid=True), db.ForeignKey('usuarios.id'), nullable=False)
    vehiculo_id = db.Column(UUID(as_uuid=True), db.ForeignKey('vehiculos.id'), nullable=False)

    fecha_inicio = db.Column(db.TIMESTAMP(timezone=True), server_default=db.func.now(), nullable=False)
    fecha_fin = db.Column(db.TIMESTAMP(timezone=True))

    km_inicial = db.Column(db.Numeric)
    km_final = db.Column(db.Numeric)

    estado_inicial = db.Column(db.Text)
    estado_final = db.Column(db.Text)

    combustible_litros = db.Column(db.Numeric)
    combustible_costo = db.Column(db.Numeric)
    combustible_foto = db.Column(db.Text) # URL to the photo in S3

    observaciones_inicio = db.Column(db.Text)
    observaciones_fin = db.Column(db.Text)

    # Status values: abierto, cerrado, en_revision, aprobado
    status = db.Column(db.Text, nullable=False, default='abierto')

    # Relationships
    chofer = db.relationship('Usuario', backref=db.backref('recorridos', lazy=True))
    vehiculo = db.relationship('Vehiculo', back_populates='recorridos')

    controles = db.relationship('Control', back_populates='recorrido', lazy='dynamic', cascade="all, delete-orphan")
    alertas = db.relationship('Alerta', back_populates='recorrido', lazy='dynamic', cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Recorrido {self.id} - Vehiculo {self.vehiculo_id}>'
