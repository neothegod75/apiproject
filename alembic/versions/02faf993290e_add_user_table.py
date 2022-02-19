"""add user table

Revision ID: 02faf993290e
Revises: e9f83b2578c3
Create Date: 2022-02-17 22:11:53.895906

"""
from alembic import op
import sqlalchemy as sa

# class User(Base):
#     __tablename__ ="users"
#     id = Column(Integer, primary_key=True, nullable=False)
#     email = Column(String, nullable=False, unique=True)
#     password = Column(String, nullable=False)
#     created_at = Column(TIMESTAMP(timezone=True), nullable = False, server_default=text('now()'))

# revision identifiers, used by Alembic.
revision = '02faf993290e'
down_revision = 'e9f83b2578c3'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('users', sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(), nullable=False),
    sa.Column('password', sa.String(), nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )  
    pass


def downgrade():
    op.drop_table('users')
    pass
