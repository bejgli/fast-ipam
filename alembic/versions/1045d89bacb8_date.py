"""date

Revision ID: 1045d89bacb8
Revises: dca44e5cfe40
Create Date: 2023-06-09 20:56:37.929035

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1045d89bacb8'
down_revision = 'dca44e5cfe40'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('host', sa.Column('date_created', sa.DateTime(), nullable=False))
    op.add_column('host', sa.Column('date_updated', sa.DateTime(), nullable=False))
    op.add_column('subnet', sa.Column('date_created', sa.DateTime(), nullable=False))
    op.add_column('subnet', sa.Column('date_updated', sa.DateTime(), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('subnet', 'date_updated')
    op.drop_column('subnet', 'date_created')
    op.drop_column('host', 'date_updated')
    op.drop_column('host', 'date_created')
    # ### end Alembic commands ###
