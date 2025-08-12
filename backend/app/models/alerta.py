import uuid
from sqlalchemy import UUID
from app.extensions import db

class Alerta(db.Model):
    __tablename__ = 'alertas'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    recorrido_id = db.Column(UUID(as_uuid=True), db.ForeignKey('recorridos.id'), nullable=False)

    mensaje = db.Column(db.Text, nullable=False)
    leida = db.Column(db.Boolean, default=False, nullable=False)

    creado_en = db.Column(db.TIMESTAMP(timezone=True), server_default=db.func.now(), nullable=False)

    # Relationship
    recorrido = db.relationship('Recorrido', back_populates='alertas')

    def __repr__(self):
        return f'<Alerta {self.id}>'
