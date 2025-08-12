import uuid
from sqlalchemy import UUID, JSON
from app.extensions import db

class Control(db.Model):
    __tablename__ = 'controles'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    recorrido_id = db.Column(UUID(as_uuid=True), db.ForeignKey('recorridos.id'), nullable=False)

    tipo = db.Column(db.Text, nullable=False) # e.g., 'fluidos', 'luces', 'cubiertas', 'chapa'
    detalle = db.Column(JSON) # e.g., {"nivel_aceite": "ok", "liquido_frenos": "bajo"}
    foto = db.Column(db.Text) # URL to the photo in S3

    creado_en = db.Column(db.TIMESTAMP(timezone=True), server_default=db.func.now(), nullable=False)

    # Relationship
    recorrido = db.relationship('Recorrido', back_populates='controles')

    def __repr__(self):
        return f'<Control {self.id} - Tipo {self.tipo}>'
