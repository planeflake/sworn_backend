"""Table names updated

Revision ID: b2c4a76f364b
Revises: e05363f36897
Create Date: 2024-10-12 14:30:05.232436

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b2c4a76f364b'
down_revision = 'e05363f36897'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('characters',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('player_id', sa.Integer(), nullable=False),
    sa.Column('level', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_table('character')
    with op.batch_alter_table('character_stats', schema=None) as batch_op:
        batch_op.create_foreign_key(None, 'characters', ['character_id'], ['id'])
        batch_op.create_foreign_key(None, 'stats', ['stat_id'], ['id'])

    with op.batch_alter_table('skills', schema=None) as batch_op:
        batch_op.add_column(sa.Column('category', sa.String(length=50), nullable=True))
        batch_op.add_column(sa.Column('parent_skill_id', sa.Integer(), nullable=True))
        batch_op.alter_column('name',
               existing_type=sa.VARCHAR(length=50),
               type_=sa.String(length=100),
               existing_nullable=False)
        batch_op.alter_column('description',
               existing_type=sa.VARCHAR(length=200),
               type_=sa.String(length=255),
               nullable=True)
        batch_op.create_foreign_key(None, 'skills', ['parent_skill_id'], ['id'])
        batch_op.drop_column('type')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('skills', schema=None) as batch_op:
        batch_op.add_column(sa.Column('type', sa.VARCHAR(length=50), autoincrement=False, nullable=False))
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.alter_column('description',
               existing_type=sa.String(length=255),
               type_=sa.VARCHAR(length=200),
               nullable=False)
        batch_op.alter_column('name',
               existing_type=sa.String(length=100),
               type_=sa.VARCHAR(length=50),
               existing_nullable=False)
        batch_op.drop_column('parent_skill_id')
        batch_op.drop_column('category')

    with op.batch_alter_table('character_stats', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_constraint(None, type_='foreignkey')

    op.create_table('character',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('player_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('level', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('id', name='character_pkey')
    )
    op.drop_table('characters')
    # ### end Alembic commands ###
