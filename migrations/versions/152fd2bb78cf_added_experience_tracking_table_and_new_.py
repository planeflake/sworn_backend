"""Added experience tracking table and new fields to character table

Revision ID: 152fd2bb78cf
Revises: 5dfbf4e90acf
Create Date: 2024-10-17 21:35:44.044995

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '152fd2bb78cf'
down_revision = '5dfbf4e90acf'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('experience_for_level',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('level', sa.Integer(), nullable=False, default=1),
    sa.Column('experience', sa.Integer(), nullable=False, default=0),
    sa.PrimaryKeyConstraint('id')
    )
    
    with op.batch_alter_table('characters', schema=None) as batch_op:
        batch_op.add_column(sa.Column('max_health', sa.Integer(), nullable=False, server_default="10"))
        batch_op.add_column(sa.Column('health', sa.Integer(), nullable=False, server_default="10"))
        batch_op.add_column(sa.Column('max_energy', sa.Integer(), nullable=False, server_default="10"))
    
    # Remove the default once data is set
    batch_op.alter_column('max_health', server_default=None)
    batch_op.alter_column('health', server_default=None)
    batch_op.alter_column('max_energy', server_default=None)

    # ### end Alembic commands ###



def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('characters', schema=None) as batch_op:
        batch_op.drop_column('max_energy')
        batch_op.drop_column('health')
        batch_op.drop_column('max_health')

    op.drop_table('experience_for_level')
    # ### end Alembic commands ###
