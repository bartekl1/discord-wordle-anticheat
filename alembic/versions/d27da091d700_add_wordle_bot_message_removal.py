"""add wordle bot message removal

Revision ID: d27da091d700
Revises: c8c690d41941
Create Date: 2025-11-30 14:38:43.669498

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd27da091d700'
down_revision: Union[str, Sequence[str], None] = 'c8c690d41941'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('guilds', sa.Column('delete_wordle_messages', sa.Boolean(), server_default='0', nullable=False))
    pass


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('guilds', 'delete_wordle_messages')
    pass
