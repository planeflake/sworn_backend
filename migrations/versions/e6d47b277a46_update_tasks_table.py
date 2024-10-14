"""Update Tasks Table

Revision ID: e6d47b277a46
Revises: 0b632d4d92d0
Create Date: 2024-10-13 18:08:12.972576

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e6d47b277a46'
down_revision = '0b632d4d92d0'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('tasks', schema=None) as batch_op:
        batch_op.add_column(sa.Column('xp', sa.Integer(), nullable=False))
        batch_op.add_column(sa.Column('icon', sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column('resources', sa.JSON(), nullable=True))
        batch_op.add_column(sa.Column('starting_area_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('base_duration', sa.Integer(), nullable=False))
        batch_op.add_column(sa.Column('base_energy', sa.Integer(), nullable=False))
        batch_op.add_column(sa.Column('level_required', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('repeatable', sa.Boolean(), nullable=False))
        batch_op.add_column(sa.Column('unlocks_task_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('skill_id_level_required', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('skill_point_reward', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(None, 'tasks', ['unlocks_task_id'], ['id'])
        batch_op.create_foreign_key(None, 'starting_areas', ['starting_area_id'], ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('tasks', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('skill_point_reward')
        batch_op.drop_column('skill_id_level_required')
        batch_op.drop_column('unlocks_task_id')
        batch_op.drop_column('repeatable')
        batch_op.drop_column('level_required')
        batch_op.drop_column('base_energy')
        batch_op.drop_column('base_duration')
        batch_op.drop_column('starting_area_id')
        batch_op.drop_column('resources')
        batch_op.drop_column('icon')
        batch_op.drop_column('xp')

    # ### end Alembic commands ###
