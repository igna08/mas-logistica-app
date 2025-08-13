"""Rename estado to status in recorridos

Revision ID: b74ead67deda
Revises: 1ffcab570e4a
Create Date: 2025-08-13 10:17:47.487079

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b74ead67deda'
down_revision = '1ffcab570e4a'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('recorridos', schema=None) as batch_op:
        batch_op.alter_column('estado', new_column_name='status')


def downgrade():
    with op.batch_alter_table('recorridos', schema=None) as batch_op:
        batch_op.alter_column('status', new_column_name='estado')
