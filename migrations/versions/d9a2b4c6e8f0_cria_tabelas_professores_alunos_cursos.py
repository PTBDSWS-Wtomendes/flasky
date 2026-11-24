"""cria tabelas professores, alunos e cursos

Revision ID: d9a2b4c6e8f0
Revises: c8f1a3b2d4e5
Create Date: 2026-11-24 19:50:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = 'd9a2b4c6e8f0'
down_revision = 'c8f1a3b2d4e5'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'cursos',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('nome', sa.String(length=120), nullable=False),
        sa.Column('descricao', sa.String(length=250), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('nome'),
    )
    op.create_table(
        'professores',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('nome', sa.String(length=120), nullable=False),
        sa.Column('disciplina_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['disciplina_id'], ['disciplinas.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_table(
        'alunos',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('nome', sa.String(length=120), nullable=False),
        sa.Column('disciplina_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['disciplina_id'], ['disciplinas.id']),
        sa.PrimaryKeyConstraint('id'),
    )


def downgrade():
    op.drop_table('alunos')
    op.drop_table('professores')
    op.drop_table('cursos')
