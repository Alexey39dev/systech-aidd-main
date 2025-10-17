"""create_messages_table

Revision ID: 8c240cbf9c6f
Revises: 
Create Date: 2025-10-16 14:55:40.176737

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8c240cbf9c6f'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema: создание таблицы messages."""
    op.execute("""
        CREATE TABLE messages (
            id SERIAL PRIMARY KEY,
            role VARCHAR(20) NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP NOT NULL DEFAULT NOW(),
            length INTEGER NOT NULL,
            deleted_at TIMESTAMP NULL
        )
    """)
    
    op.execute("""
        CREATE INDEX idx_messages_deleted_at ON messages(deleted_at)
    """)


def downgrade() -> None:
    """Downgrade schema: удаление таблицы messages."""
    op.execute("DROP TABLE IF EXISTS messages CASCADE")
