"""create invoices"""
import sqlalchemy as sa
from alembic import op

revision = "0001"
down_revision = None


def upgrade() -> None:
    op.create_table(
        "invoices",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("stripe_id", sa.String(64), nullable=False),
        sa.Column("amount_cents", sa.Integer, nullable=False),
    )


def downgrade() -> None:
    op.drop_table("invoices")
