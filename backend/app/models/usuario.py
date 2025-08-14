import uuid
from sqlalchemy import UUID
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db
from .associations import vehiculo_chofer_association
from sqlalchemy.orm import relationship

class Usuario(db.Model):
    __tablename__ = 'usuarios'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nombre = db.Column(db.Text, nullable=False)
    email = db.Column(db.Text, unique=True, nullable=False)
    password_hash = db.Column(db.Text, nullable=False)
    rol = db.Column(db.Text, nullable=False, default='chofer')
    profile_picture_url = db.Column(db.Text, nullable=True)
    activo = db.Column(db.Boolean, default=True)
    creado_en = db.Column(db.TIMESTAMP(timezone=True), server_default=db.func.now())

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    vehiculos_asignados = relationship(
        "Vehiculo",
        secondary=vehiculo_chofer_association,
        back_populates="choferes_asignados"
    )

    def __repr__(self):
        return f'<Usuario {self.nombre}>'

    def to_dict(self):
        return {
            "id": str(self.id),
            "nombre": self.nombre,
            "email": self.email,
            "rol": self.rol,
            "activo": self.activo,
            "profile_picture_url": self.profile_picture_url,
            "creado_en": self.creado_en.isoformat()
        }
