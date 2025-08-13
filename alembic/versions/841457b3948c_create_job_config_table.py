"""create_job_config_table

Revision ID: 841457b3948c
Revises: qwdb2bb4ex2p
Create Date: 2025-08-04 21:21:46.861436

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "841457b3948c"
down_revision: Union[str, None] = "qwdb2bb4ex2p"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create table if it doesn't exist
    op.create_table(
        "job_configs",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column("config", sa.JSON(), nullable=True, server_default="{}"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_job_configs_id"), "job_configs", ["id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_job_configs_id"), table_name="job_configs")
    op.drop_table("job_configs")
