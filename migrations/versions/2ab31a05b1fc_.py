"""empty message

Revision ID: 2ab31a05b1fc
Revises: d0c7b8e4b57c
Create Date: 2025-05-08 19:51:36.341521

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '2ab31a05b1fc'
down_revision = 'd0c7b8e4b57c'
branch_labels = None
depends_on = None


def upgrade():

    # Eliminar la restricción de clave foránea antes de eliminar la tabla 'review':
    op.drop_constraint('review_restaurant_fkey', 'review', type_='foreignkey')
    
    # Eliminar las tablas:
    op.drop_table('restaurant')
    op.drop_table('review')

    # Crear la nueva tabla 'image_view':
    op.create_table('image_view',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(length=100), nullable=False),
        sa.Column('filename', sa.String(length=255), nullable=False),
        sa.Column('processed_date', sa.DateTime(), nullable=True),
        sa.Column('red_pixels', sa.Integer(), nullable=True),
        sa.Column('green_pixels', sa.Integer(), nullable=True),
        sa.Column('blue_pixels', sa.Integer(), nullable=True),
        sa.Column('other_pixels', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    # Volver a crear la tabla 'review' con la clave foránea
    op.create_table('review',
        sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
        sa.Column('restaurant', sa.INTEGER(), autoincrement=False, nullable=True),
        sa.Column('user_name', sa.VARCHAR(length=30), autoincrement=False, nullable=True),
        sa.Column('rating', sa.INTEGER(), autoincrement=False, nullable=True),
        sa.Column('review_text', sa.VARCHAR(length=500), autoincrement=False, nullable=True),
        sa.Column('review_date', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
        sa.ForeignKeyConstraint(['restaurant'], ['restaurant.id'], name='review_restaurant_fkey', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name='review_pkey')
    )
    
    # Volver a crear la tabla 'restaurant'
    op.create_table('restaurant',
        sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
        sa.Column('name', sa.VARCHAR(length=50), autoincrement=False, nullable=True),
        sa.Column('street_address', sa.VARCHAR(length=50), autoincrement=False, nullable=True),
        sa.Column('description', sa.VARCHAR(length=250), autoincrement=False, nullable=True),
        sa.PrimaryKeyConstraint('id', name='restaurant_pkey')
    )

    # Eliminar la tabla 'image_view'
    op.drop_table('image_view')

