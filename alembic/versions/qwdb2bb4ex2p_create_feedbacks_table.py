"""create feedbacks table

Revision ID: qwdb2bb4ex2p
Revises:
Create Date: 2024-03-19 10:00:00.000000

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "qwdb2bb4ex2p"
down_revision = "f3db2bb4e6d7"  # This makes it depend on the users table migration
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "feedbacks",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column("sender_id", sa.String(), nullable=True),
        sa.Column("product_name", sa.String(), nullable=True),
        sa.Column("feedback_text", sa.String(), nullable=True),
        sa.Column("media_urls", sa.JSON(), nullable=True, server_default="[]"),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), onupdate=sa.text("now()")),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_feedbacks_id"), "feedbacks", ["id"], unique=False)
    op.create_index(
        op.f("ix_feedbacks_sender_id"), "feedbacks", ["sender_id"], unique=False
    )


def downgrade():
    op.drop_index(op.f("ix_feedbacks_sender_id"), table_name="feedbacks")
    op.drop_index(op.f("ix_feedbacks_id"), table_name="feedbacks")
    op.drop_table("feedbacks")
