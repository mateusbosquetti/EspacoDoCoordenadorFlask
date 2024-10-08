"""empty message

Revision ID: e25839fa7c95
Revises: 3ec6ffd90804
Create Date: 2024-07-12 15:53:36.444049

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e25839fa7c95'
down_revision = '3ec6ffd90804'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('aula',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('materia', sa.String(), nullable=False),
    sa.Column('sala', sa.String(), nullable=False),
    sa.Column('dia', sa.String(), nullable=False),
    sa.Column('horario_inicio', sa.Time(), nullable=False),
    sa.Column('horario_fim', sa.Time(), nullable=False),
    sa.Column('professor_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['professor_id'], ['professor.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('aula')
    # ### end Alembic commands ###
