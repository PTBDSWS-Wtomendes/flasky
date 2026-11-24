"""cria tabela disciplinas

Revision ID: c8f1a3b2d4e5
Revises: b7c2d4e9f106
Create Date: 2026-11-24 19:45:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = 'c8f1a3b2d4e5'
down_revision = 'b7c2d4e9f106'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'disciplinas',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('nome', sa.String(length=64), nullable=False),
        sa.Column('semestre', sa.String(length=32), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('nome'),
    )


def downgrade():
    op.drop_table('disciplinas')
