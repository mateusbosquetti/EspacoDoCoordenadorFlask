"""empty message

Revision ID: 6b5aad684c3e
Revises: 6f6fe8220b3f
Create Date: 2024-07-12 14:39:40.255755

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6b5aad684c3e'
down_revision = '6f6fe8220b3f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('teste',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('teste')
    # ### end Alembic commands ###
