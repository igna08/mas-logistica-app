from app.extensions import db
from sqlalchemy import Table, Column, ForeignKey

vehiculo_chofer_association = Table(
    'vehiculo_chofer_association',
    db.metadata,
    Column('usuario_id', ForeignKey('usuarios.id'), primary_key=True),
    Column('vehiculo_id', ForeignKey('vehiculos.id'), primary_key=True)
)
