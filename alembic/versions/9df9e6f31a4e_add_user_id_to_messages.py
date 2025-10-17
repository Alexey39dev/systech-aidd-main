"""add_user_id_to_messages

Revision ID: 9df9e6f31a4e
Revises: 4b163d978e57
Create Date: 2025-10-16 17:09:12.031226

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9df9e6f31a4e'
down_revision: Union[str, Sequence[str], None] = '4b163d978e57'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema: добавление user_id в messages."""
    op.execute("""
        ALTER TABLE messages ADD COLUMN user_id INTEGER
    """)
    
    op.execute("""
        ALTER TABLE messages 
        ADD CONSTRAINT fk_messages_user_id 
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
    """)
    
    op.execute("""
        CREATE INDEX idx_messages_user_id ON messages(user_id)
    """)


def downgrade() -> None:
    """Downgrade schema: удаление user_id из messages."""
    op.execute("DROP INDEX IF EXISTS idx_messages_user_id")
    op.execute("ALTER TABLE messages DROP CONSTRAINT IF EXISTS fk_messages_user_id")
    op.execute("ALTER TABLE messages DROP COLUMN IF EXISTS user_id")
