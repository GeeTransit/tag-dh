"""newsubmission

Revision ID: 7950a35f5dbd
Revises: 3077f28babcb
Create Date: 2020-05-03 07:13:47.252680

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7950a35f5dbd'
down_revision = '3077f28babcb'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("submission") as batch_op:
        batch_op.add_column(sa.Column('account_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('text', sa.Text(), nullable=False, server_default=""))
        batch_op.alter_column('text', server_default=None)
        batch_op.create_foreign_key('submission', 'account', ['account_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("submission") as batch_op:
        batch_op.drop_constraint('submission', type_='foreignkey')
        batch_op.drop_column('text')
        batch_op.drop_column('account_id')
    # ### end Alembic commands ###
