"""empty message

Revision ID: b10bbb5e3412
Revises: 69fea846351b
Create Date: 2024-05-23 11:21:47.691893

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b10bbb5e3412'
down_revision = '69fea846351b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('contato', schema=None) as batch_op:
        batch_op.drop_column('email')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('contato', schema=None) as batch_op:
        batch_op.add_column(sa.Column('email', sa.VARCHAR(), nullable=True))

    # ### end Alembic commands ###
