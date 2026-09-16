"""Track observed usernames and sound media types without storing audio bytes."""
from alembic import op
import sqlalchemy as sa

revision = '32bc121e151d'
down_revision = '21ab121e151d'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('sounds', sa.Column('media_type', sa.String(), nullable=False, server_default='audio'))
    op.create_table('chat_members',
        sa.Column('chat_id', sa.BigInteger(), primary_key=True),
        sa.Column('user_id', sa.BigInteger(), primary_key=True),
        sa.Column('username', sa.String(), nullable=True))
    op.create_index('ix_chat_members_username', 'chat_members', ['username'])


def downgrade():
    op.drop_table('chat_members')
    op.drop_column('sounds', 'media_type')
