"""Create vehiculo_chofer_association table

Revision ID: bf4db2105673
Revises: b74ead67deda
Create Date: 2025-08-14 11:21:41.094862

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = 'bf4db2105673'
down_revision = 'b74ead67deda'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('vehiculo_chofer_association',
    sa.Column('usuario_id', sa.UUID(), nullable=False),
    sa.Column('vehiculo_id', sa.UUID(), nullable=False),
    sa.ForeignKeyConstraint(['usuario_id'], ['usuarios.id'], ),
    sa.ForeignKeyConstraint(['vehiculo_id'], ['vehiculos.id'], ),
    sa.PrimaryKeyConstraint('usuario_id', 'vehiculo_id')
    )


def downgrade():
    op.drop_table('vehiculo_chofer_association')
