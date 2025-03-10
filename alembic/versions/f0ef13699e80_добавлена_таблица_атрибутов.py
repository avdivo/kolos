"""Добавлена таблица атрибутов

Revision ID: f0ef13699e80
Revises: 27ec88ef844d
Create Date: 2025-01-22 18:21:58.850593

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f0ef13699e80'
down_revision: Union[str, None] = '27ec88ef844d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('attributes',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('key', sa.String(), nullable=False),
    sa.Column('value', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('key')
    )
    op.create_index(op.f('ix_attributes_id'), 'attributes', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_attributes_id'), table_name='attributes')
    op.drop_table('attributes')
    # ### end Alembic commands ###
