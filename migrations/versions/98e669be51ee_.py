"""empty message

Revision ID: 98e669be51ee
Revises: fd0df265a3dd
Create Date: 2024-08-01 19:09:50.619030

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '98e669be51ee'
down_revision = 'fd0df265a3dd'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('chat', schema=None) as batch_op:
        batch_op.add_column(sa.Column('is_group', sa.Boolean(), nullable=True))
        batch_op.add_column(sa.Column('name', sa.String(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('chat', schema=None) as batch_op:
        batch_op.drop_column('name')
        batch_op.drop_column('is_group')

    # ### end Alembic commands ###
