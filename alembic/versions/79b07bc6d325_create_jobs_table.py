"""create_jobs_table

Revision ID: 79b07bc6d325
Revises: 7a56dde5902f
Create Date: 2025-08-04 21:23:32.180549

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import enum


class JobStatus(str, enum.Enum):
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


# revision identifiers, used by Alembic.
revision: str = "79b07bc6d325"
down_revision: Union[str, None] = "7a56dde5902f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create table if it doesn't exist
    op.create_table(
        "jobs",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column("job_name", sa.String(), nullable=True),
        sa.Column("last_processed_id", sa.BigInteger(), nullable=True),
        sa.Column("status", sa.String(), nullable=True, server_default="processing"),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_jobs_id"), "jobs", ["id"], unique=False)
    op.create_index(op.f("ix_jobs_job_name"), "jobs", ["job_name"], unique=False)


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_jobs_job_name")
    op.execute("DROP INDEX IF EXISTS ix_jobs_id")
    op.execute("DROP TABLE IF EXISTS jobs")
    op.execute("DROP TYPE IF EXISTS jobstatus")
