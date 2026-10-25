"""create tasks table"""

import sqlalchemy as sa
from alembic import op

revision = "0001"
down_revision = None


def upgrade():
    op.create_table(
        "tasks",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("done", sa.Boolean, nullable=False, server_default=sa.false()),
    )


def downgrade():
    op.drop_table("tasks")
