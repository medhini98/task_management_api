"""add attachments table

Revision ID: a1b2c3d4e5f6
Revises: d9ca6389d65c
Create Date: 2025-11-04

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "a1b2c3d4e5f6"
down_revision = "bd04f8602cc3"
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table(
        "attachments",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("task_id", sa.UUID(), nullable=False),
        sa.Column("uploader_id", sa.UUID(), nullable=True),
        sa.Column("filename", sa.String(length=512), nullable=False),
        sa.Column("content_type", sa.String(length=255), nullable=True),
        sa.Column("size_bytes", sa.BigInteger(), nullable=True),
        sa.Column("storage_key", sa.String(length=1024), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default="now()", nullable=False),
        sa.ForeignKeyConstraint(["task_id"], ["tasks.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["uploader_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_attachments_task_id", "attachments", ["task_id"])
    op.create_unique_constraint("uq_attachments_storage_key", "attachments", ["storage_key"])

def downgrade() -> None:
    op.drop_constraint("uq_attachments_storage_key", "attachments", type_="unique")
    op.drop_index("ix_attachments_task_id", table_name="attachments")
    op.drop_table("attachments")