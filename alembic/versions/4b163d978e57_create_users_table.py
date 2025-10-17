"""create_users_table

Revision ID: 4b163d978e57
Revises: 8c240cbf9c6f
Create Date: 2025-10-16 17:08:50.216248

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4b163d978e57'
down_revision: Union[str, Sequence[str], None] = '8c240cbf9c6f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema: создание таблицы users."""
    op.execute("""
        CREATE TABLE users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(100) NOT NULL,
            created_at TIMESTAMP NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
            deleted_at TIMESTAMP NULL
        )
    """)
    
    op.execute("""
        CREATE INDEX idx_users_username ON users(username) WHERE deleted_at IS NULL
    """)
    
    op.execute("""
        CREATE INDEX idx_users_deleted_at ON users(deleted_at)
    """)


def downgrade() -> None:
    """Downgrade schema: удаление таблицы users."""
    op.execute("DROP TABLE IF EXISTS users CASCADE")
