"""empty message

Revision ID: 0b4ee4b91350
Revises: 9c54afc39689
Create Date: 2019-04-12 18:17:06.886065

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0b4ee4b91350'
down_revision = '9c54afc39689'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('feature',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=128), nullable=True),
    sa.Column('desc', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('feature_importance',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('method', sa.String(length=128), nullable=True),
    sa.Column('heldout_chem', sa.Boolean(), nullable=True),
    sa.Column('crank', sa.String(length=64), nullable=True),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.Column('run_id', sa.String(length=128), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('feature_importance_value',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('feat_id', sa.Integer(), nullable=True),
    sa.Column('rank', sa.Integer(), nullable=True),
    sa.Column('weight', sa.Float(), nullable=True),
    sa.ForeignKeyConstraint(['feat_id'], ['feature.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('feature_importance_value')
    op.drop_table('feature_importance')
    op.drop_table('feature')
    # ### end Alembic commands ###