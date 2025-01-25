"""fix refresh token length

Revision ID: 8c772b5d515c
Revises: 2b03cb411e65
Create Date: 2025-01-24 00:47:00.953177

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '8c772b5d515c'
down_revision: Union[str, None] = '2b03cb411e65'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###

    op.alter_column('choices', 'order_index',
               existing_type=sa.INTEGER(),
               server_default=None,
               nullable=True)
    op.alter_column('choices', 'created_at',
               existing_type=postgresql.TIMESTAMP(),
               server_default=None,
               existing_nullable=True)
    op.alter_column('notifications', 'is_read',
               existing_type=sa.BOOLEAN(),
               server_default=None,
               nullable=True)
    op.alter_column('notifications', 'created_at',
               existing_type=postgresql.TIMESTAMP(),
               server_default=None,
               existing_nullable=True)
    op.alter_column('questions', 'created_at',
               existing_type=postgresql.TIMESTAMP(),
               server_default=None,
               existing_nullable=True)
    op.alter_column('questions', 'updated_at',
               existing_type=postgresql.TIMESTAMP(),
               server_default=None,
               existing_nullable=True)
    op.alter_column('response_metadata', 'submitted_at',
               existing_type=postgresql.TIMESTAMP(),
               server_default=None,
               existing_nullable=True)
    op.drop_constraint('response_metadata_survey_response_id_fkey', 'response_metadata', type_='foreignkey')
    op.create_foreign_key(None, 'response_metadata', 'survey_responses', ['survey_response_id'], ['id'])
    op.alter_column('responses', 'created_at',
               existing_type=postgresql.TIMESTAMP(),
               server_default=None,
               existing_nullable=True)
    op.alter_column('roles', 'created_at',
               existing_type=postgresql.TIMESTAMP(),
               server_default=None,
               existing_nullable=True)
    op.alter_column('survey_responses', 'created_at',
               existing_type=postgresql.TIMESTAMP(),
               server_default=None,
               existing_nullable=True)
    op.alter_column('survey_settings', 'settings',
               existing_type=postgresql.JSONB(astext_type=sa.Text()),
               server_default=None,
               nullable=True)
    op.alter_column('survey_settings', 'created_at',
               existing_type=postgresql.TIMESTAMP(),
               server_default=None,
               existing_nullable=True)
    op.alter_column('survey_settings', 'updated_at',
               existing_type=postgresql.TIMESTAMP(),
               server_default=None,
               existing_nullable=True)
    op.alter_column('surveys', 'status',
               existing_type=sa.VARCHAR(length=20),
               server_default=None,
               nullable=True)
    op.alter_column('surveys', 'is_featured',
               existing_type=sa.BOOLEAN(),
               server_default=None,
               nullable=True)
    op.alter_column('surveys', 'is_verified',
               existing_type=sa.BOOLEAN(),
               server_default=None,
               nullable=True)
    op.alter_column('surveys', 'created_at',
               existing_type=postgresql.TIMESTAMP(),
               server_default=None,
               existing_nullable=True)
    op.alter_column('surveys', 'updated_at',
               existing_type=postgresql.TIMESTAMP(),
               server_default=None,
               existing_nullable=True)
    op.alter_column('user_tokens', 'refresh_token',
               existing_type=sa.VARCHAR(length=128),
               type_=sa.String(length=512),
               existing_nullable=False)
    op.alter_column('user_tokens', 'revoked',
               existing_type=sa.BOOLEAN(),
               server_default=None,
               nullable=True)
    op.alter_column('user_tokens', 'created_at',
               existing_type=postgresql.TIMESTAMP(),
               server_default=None,
               existing_nullable=True)
    op.alter_column('users', 'token_version',
               existing_type=sa.INTEGER(),
               server_default=None,
               existing_nullable=True)
    op.alter_column('users', 'is_active',
               existing_type=sa.BOOLEAN(),
               server_default=None,
               nullable=True)
    op.alter_column('users', 'created_at',
               existing_type=postgresql.TIMESTAMP(),
               server_default=None,
               existing_nullable=True)
    op.alter_column('users', 'updated_at',
               existing_type=postgresql.TIMESTAMP(),
               server_default=None,
               existing_nullable=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('users', 'updated_at',
               existing_type=postgresql.TIMESTAMP(),
               server_default=sa.text('now()'),
               existing_nullable=True)
    op.alter_column('users', 'created_at',
               existing_type=postgresql.TIMESTAMP(),
               server_default=sa.text('now()'),
               existing_nullable=True)
    op.alter_column('users', 'is_active',
               existing_type=sa.BOOLEAN(),
               server_default=sa.text('true'),
               nullable=False)
    op.alter_column('users', 'token_version',
               existing_type=sa.INTEGER(),
               server_default=sa.text('0'),
               existing_nullable=True)
    op.alter_column('user_tokens', 'created_at',
               existing_type=postgresql.TIMESTAMP(),
               server_default=sa.text('now()'),
               existing_nullable=True)
    op.alter_column('user_tokens', 'revoked',
               existing_type=sa.BOOLEAN(),
               server_default=sa.text('false'),
               nullable=False)
    op.alter_column('user_tokens', 'refresh_token',
               existing_type=sa.String(length=512),
               type_=sa.VARCHAR(length=128),
               existing_nullable=False)
    op.alter_column('surveys', 'updated_at',
               existing_type=postgresql.TIMESTAMP(),
               server_default=sa.text('now()'),
               existing_nullable=True)
    op.alter_column('surveys', 'created_at',
               existing_type=postgresql.TIMESTAMP(),
               server_default=sa.text('now()'),
               existing_nullable=True)
    op.alter_column('surveys', 'is_verified',
               existing_type=sa.BOOLEAN(),
               server_default=sa.text('false'),
               nullable=False)
    op.alter_column('surveys', 'is_featured',
               existing_type=sa.BOOLEAN(),
               server_default=sa.text('false'),
               nullable=False)
    op.alter_column('surveys', 'status',
               existing_type=sa.VARCHAR(length=20),
               server_default=sa.text("'draft'::character varying"),
               nullable=False)
    op.alter_column('survey_settings', 'updated_at',
               existing_type=postgresql.TIMESTAMP(),
               server_default=sa.text('now()'),
               existing_nullable=True)
    op.alter_column('survey_settings', 'created_at',
               existing_type=postgresql.TIMESTAMP(),
               server_default=sa.text('now()'),
               existing_nullable=True)
    op.alter_column('survey_settings', 'settings',
               existing_type=postgresql.JSONB(astext_type=sa.Text()),
               server_default=sa.text('\'{"require_login": false, "response_limit": null, "allow_anonymous": true}\'::jsonb'),
               nullable=False)
    op.alter_column('survey_responses', 'created_at',
               existing_type=postgresql.TIMESTAMP(),
               server_default=sa.text('now()'),
               existing_nullable=True)
    op.alter_column('roles', 'created_at',
               existing_type=postgresql.TIMESTAMP(),
               server_default=sa.text('now()'),
               existing_nullable=True)
    op.alter_column('responses', 'created_at',
               existing_type=postgresql.TIMESTAMP(),
               server_default=sa.text('now()'),
               existing_nullable=True)
    op.drop_constraint(None, 'response_metadata', type_='foreignkey')
    op.create_foreign_key('response_metadata_survey_response_id_fkey', 'response_metadata', 'survey_responses', ['survey_response_id'], ['id'], ondelete='CASCADE')
    op.alter_column('response_metadata', 'submitted_at',
               existing_type=postgresql.TIMESTAMP(),
               server_default=sa.text('now()'),
               existing_nullable=True)
    op.alter_column('questions', 'updated_at',
               existing_type=postgresql.TIMESTAMP(),
               server_default=sa.text('now()'),
               existing_nullable=True)
    op.alter_column('questions', 'created_at',
               existing_type=postgresql.TIMESTAMP(),
               server_default=sa.text('now()'),
               existing_nullable=True)
    op.alter_column('notifications', 'created_at',
               existing_type=postgresql.TIMESTAMP(),
               server_default=sa.text('now()'),
               existing_nullable=True)
    op.alter_column('notifications', 'is_read',
               existing_type=sa.BOOLEAN(),
               server_default=sa.text('false'),
               nullable=False)
    op.alter_column('choices', 'created_at',
               existing_type=postgresql.TIMESTAMP(),
               server_default=sa.text('now()'),
               existing_nullable=True)
    op.alter_column('choices', 'order_index',
               existing_type=sa.INTEGER(),
               server_default=sa.text('0'),
               nullable=False)
    op.drop_table('survey_analytics')
    # ### end Alembic commands ###
