"""Removing autoincreasment for Completed tasks

Revision ID: b7013d14fa25
Revises: ba19863aa2cb
Create Date: 2026-01-14 15:27:11.092965

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b7013d14fa25'
down_revision: Union[str, Sequence[str], None] = 'ba19863aa2cb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.execute("""
        ALTER TABLE completed_tasks
        ALTER COLUMN id DROP DEFAULT
    """)
    op.execute("""
        DROP SEQUENCE IF EXISTS completed_tasks_id_seq
    """)


def downgrade():
    op.execute("""
        CREATE SEQUENCE completed_tasks_id_seq OWNED BY completed_tasks.id
    """)
    op.execute("""
        ALTER TABLE completed_tasks
        ALTER COLUMN id SET DEFAULT nextval('completed_tasks_id_seq')
    """)
