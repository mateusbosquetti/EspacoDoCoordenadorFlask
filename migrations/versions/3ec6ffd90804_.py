"""empty message

Revision ID: 3ec6ffd90804
Revises: d15bdefb6944
Create Date: 2024-07-12 15:37:16.336223

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3ec6ffd90804'
down_revision = 'd15bdefb6944'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('professor',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('nome', sa.String(), nullable=False),
    sa.Column('setor_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['setor_id'], ['setor.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('professor')
    # ### end Alembic commands ###
