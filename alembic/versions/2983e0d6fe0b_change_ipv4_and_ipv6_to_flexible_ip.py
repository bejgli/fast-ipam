"""Change ipv4 and ipv6 to flexible ip

Revision ID: 2983e0d6fe0b
Revises: a13a935e96d7
Create Date: 2023-05-19 22:11:00.037663

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2983e0d6fe0b'
down_revision = 'a13a935e96d7'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('subnet', sa.Column('ip', sa.String(), nullable=True))
    op.drop_index('ix_subnet_ip_v4', table_name='subnet')
    op.drop_index('ix_subnet_ip_v6', table_name='subnet')
    op.create_index(op.f('ix_subnet_ip'), 'subnet', ['ip'], unique=False)
    op.drop_column('subnet', 'ip_v4')
    op.drop_column('subnet', 'ip_v6')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('subnet', sa.Column('ip_v6', sa.VARCHAR(), nullable=True))
    op.add_column('subnet', sa.Column('ip_v4', sa.VARCHAR(), nullable=True))
    op.drop_index(op.f('ix_subnet_ip'), table_name='subnet')
    op.create_index('ix_subnet_ip_v6', 'subnet', ['ip_v6'], unique=False)
    op.create_index('ix_subnet_ip_v4', 'subnet', ['ip_v4'], unique=False)
    op.drop_column('subnet', 'ip')
    # ### end Alembic commands ###