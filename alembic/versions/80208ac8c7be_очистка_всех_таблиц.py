"""Очистка всех таблиц

Revision ID: 80208ac8c7be
Revises: 7c93aa07c473
Create Date: 2024-11-14 19:48:32.574736

"""
from typing import Sequence, Union

from alembic import op
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision: str = '80208ac8c7be'
down_revision: Union[str, None] = '7c93aa07c473'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Удаление данных из всех таблиц
    op.execute(text("DELETE FROM Points"))
    op.execute(text("DELETE FROM Links"))


def downgrade():
    # Здесь можно указать код отката, если требуется
    pass
