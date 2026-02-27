"""add_google_id_and_make_password_nullable

Revision ID: d0e38f0e1214
Revises: 55fe5eb4590c
Create Date: 2026-02-26 17:09:50.314507

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd0e38f0e1214'
down_revision: Union[str, Sequence[str], None] = '55fe5eb4590c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
