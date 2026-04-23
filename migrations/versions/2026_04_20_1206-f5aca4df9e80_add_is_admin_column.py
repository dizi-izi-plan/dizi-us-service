"""add_is_admin_column

Revision ID: f5aca4df9e80
Revises: 809d684bfa5a
Create Date: 2026-04-20 12:06:48.504565

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f5aca4df9e80'
down_revision: Union[str, Sequence[str], None] = '809d684bfa5a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        'users',
        sa.Column('is_admin', sa.Boolean(), nullable=False, server_default=sa.text('false'))
    )
    op.alter_column('users', 'is_admin', server_default=None)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('users', 'is_admin')
