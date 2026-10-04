"""registra emails enviados

Revision ID: b7c2d4e9f106
Revises: 66a8c581e07d
Create Date: 2026-10-04 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = 'b7c2d4e9f106'
down_revision = '66a8c581e07d'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'sent_emails',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('sender', sa.String(length=255), nullable=False),
        sa.Column('recipients', sa.Text(), nullable=False),
        sa.Column('subject', sa.String(length=255), nullable=False),
        sa.Column('body', sa.Text(), nullable=False),
        sa.Column('sent_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )


def downgrade():
    op.drop_table('sent_emails')