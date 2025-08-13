"""create_topics_table

Revision ID: 7a56dde5902f
Revises: 841457b3948c
Create Date: 2025-08-04 21:22:19.834474

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "7a56dde5902f"
down_revision: Union[str, None] = "841457b3948c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create table if it doesn't exist
    op.create_table(
        "topics",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column("label", sa.String(500), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_topics_id"), "topics", ["id"], unique=False)
    op.create_index(op.f("ix_topics_label"), "topics", ["label"], unique=True)


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_topics_label")
    op.execute("DROP INDEX IF EXISTS ix_topics_id")
    op.execute("DROP TABLE IF EXISTS topics")
