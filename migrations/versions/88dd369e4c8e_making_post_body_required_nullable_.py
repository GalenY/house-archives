"""making Post.body required(nullable=False), to see if Alembic is able to modify constraints now that I have setup a naming convention for db contrains

Revision ID: 88dd369e4c8e
Revises: 65ca08e9a257
Create Date: 2019-01-13 00:19:22.068015

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '88dd369e4c8e'
down_revision = '65ca08e9a257'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('post', schema=None) as batch_op:
        batch_op.alter_column('body',
               existing_type=sa.VARCHAR(length=140),
               nullable=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('post', schema=None) as batch_op:
        batch_op.alter_column('body',
               existing_type=sa.VARCHAR(length=140),
               nullable=True)

    # ### end Alembic commands ###