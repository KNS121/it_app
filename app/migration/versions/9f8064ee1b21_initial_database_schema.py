"""Initial database schema

Revision ID: 9f8064ee1b21
Revises:
Create Date: 2025-02-04 15:26:15.071477

"""
from typing import Sequence, Union

import geoalchemy2
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '9f8064ee1b21'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Создаем таблицы
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis")
    op.create_table('farmers',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('phone_number', sa.String(), nullable=False),
    sa.Column('first_name', sa.String(), nullable=False),
    sa.Column('last_name', sa.String(), nullable=False),
    sa.Column('farm_name', sa.String(), nullable=False),
    sa.Column('date_of_birth', sa.Date(), nullable=False),
    sa.Column('email', sa.String(), nullable=False),
    sa.Column('address', sa.Text(), nullable=False),
    sa.Column('photo', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('phone_number')
    )
    op.create_table('roles',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('phone_number', sa.String(), nullable=False),
    sa.Column('first_name', sa.String(), nullable=False),
    sa.Column('last_name', sa.String(), nullable=False),
    sa.Column('email', sa.String(), nullable=False),
    sa.Column('password', sa.String(), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('phone_number')
    )
    op.create_table('fields',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('geometry', geoalchemy2.types.Geometry(geometry_type='POLYGON', srid=4326, from_text='ST_GeomFromEWKT', name='geometry', nullable=False), nullable=False, comment='Polygon geometry in WKT format'),
    sa.Column('area_hectares', sa.Float(), sa.Computed('ST_Area(geometry::geography) / 10000', ), nullable=False, comment='Automatically calculated area in hectares'),
    sa.Column('crop_rotation', sa.String(), nullable=True),
    sa.Column('cultivation_technology', sa.String(), nullable=True),
    sa.Column('farmer_id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['farmer_id'], ['farmers.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )

    # Проверяем существование индекса перед его созданием
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    indexes = inspector.get_indexes('fields')
    index_names = [index['name'] for index in indexes]

    if 'idx_fields_geometry' not in index_names:
        op.create_index('idx_fields_geometry', 'fields', ['geometry'], unique=False, postgresql_using='gist')

    op.create_table('user_roles',
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('role_id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('user_id', 'role_id')
    )
    # Удаление этой строки
    # op.drop_table('spatial_ref_sys')

def downgrade() -> None:
    # Удаление этой строки
    # op.create_table('spatial_ref_sys',
    # sa.Column('srid', sa.INTEGER(), autoincrement=False, nullable=False),
    # sa.Column('auth_name', sa.VARCHAR(length=256), autoincrement=False, nullable=True),
    # sa.Column('auth_srid', sa.INTEGER(), autoincrement=False, nullable=True),
    # sa.Column('srtext', sa.VARCHAR(length=2048), autoincrement=False, nullable=True),
    # sa.Column('proj4text', sa.VARCHAR(length=2048), autoincrement=False, nullable=True),
    # sa.CheckConstraint('srid > 0 AND srid <= 998999', name='spatial_ref_sys_srid_check'),
    # sa.PrimaryKeyConstraint('srid', name='spatial_ref_sys_pkey')
    # )
    op.drop_table('user_roles')
    op.drop_index('idx_fields_geometry', table_name='fields', postgresql_using='gist')
    op.drop_table('fields')
    op.drop_table('users')
    op.drop_table('roles')
    op.drop_table('farmers')
