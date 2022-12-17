"""Renamed field 'has_mailing' to 'addressee' in User model

Revision ID: c4a8c42af29c
Revises: 87c7d29e3ddb
Create Date: 2022-12-17 21:56:38.064310

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c4a8c42af29c'
down_revision = '87c7d29e3ddb'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('addressee', sa.Boolean(), nullable=True))
    op.drop_column('users', 'has_mailing')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('has_mailing', sa.BOOLEAN(), autoincrement=False, nullable=True))
    op.drop_column('users', 'addressee')
    # ### end Alembic commands ###
