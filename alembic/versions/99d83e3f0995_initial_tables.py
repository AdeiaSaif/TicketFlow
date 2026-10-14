"""initial tables

Revision ID: 99d83e3f0995
Revises: 
Create Date: 2026-10-14 19:07:59.592710

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = '99d83e3f0995'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    # 1. Users Table
    op.create_table(
        'Users',
        sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('password', sa.String(), nullable=False),
        sa.Column('role', sa.String(), nullable=False),
        sa.Column('create_date', sa.DateTime(), nullable=False),
    )

    # 2. Events Table
    op.create_table(
        'Events',
        sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
        sa.Column('org_id', sa.Integer(), sa.ForeignKey('Users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('venue', sa.String(), nullable=False),
        sa.Column('city', sa.String(), nullable=False),
        sa.Column('category', sa.String(), nullable=False),
        sa.Column('event_status', sa.String(), nullable=False),
        sa.Column('start_at_datetime', sa.DateTime(), nullable=False),
    )

    # 3. TicketType Table
    op.create_table(
        'TicketType',
        sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
        sa.Column('event_id', sa.Integer(), sa.ForeignKey('Events.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('price', sa.Integer(), nullable=False),
        sa.Column('total_seats', sa.Integer(), nullable=False),
        sa.Column('available_seats', sa.Integer(), nullable=False),
    )

    # 4. Booking Table
    op.create_table(
        'Booking',
        sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
        sa.Column('customer_id', sa.Integer(), sa.ForeignKey('Users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('event_id', sa.Integer(), sa.ForeignKey('Events.id', ondelete='CASCADE'), nullable=False),
        sa.Column('booking_status', sa.String(), nullable=False),
        sa.Column('total_amount', sa.Integer(), nullable=False),
        sa.Column('expire_at', sa.DateTime(), nullable=False),
        sa.Column('create_date', sa.DateTime(), nullable=False),
    )

    # 5. Payment Table
    op.create_table(
        'Payment',
        sa.Column('id', sa.Integer(), primary_key=True, index=True, nullable=False),
        sa.Column('booking_id', sa.Integer(), sa.ForeignKey('Booking.id'), nullable=True),
        sa.Column('amount', sa.Integer(), nullable=False),
        sa.Column('status', sa.Enum('pending', 'success', 'failed', name='paymentstatus'), nullable=True),
        sa.Column('paid_at', sa.DateTime(), nullable=False),
    )

    # 6. BookingItem Table
    op.create_table(
        'BookingItem',
        sa.Column('id', sa.Integer(), primary_key=True, index=True, nullable=False),
        sa.Column('booking_id', sa.Integer(), sa.ForeignKey('Booking.id'), nullable=True),
        sa.Column('ticket_type_id', sa.Integer(), sa.ForeignKey('TicketType.id'), nullable=True),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('unit_price', sa.Integer(), nullable=False),
    )

def downgrade() -> None:
    op.drop_table('BookingItem')
    op.drop_table('Payment')
    op.drop_table('Booking')
    op.drop_table('TicketType')
    op.drop_table('Events')
    op.drop_table('Users')
    op.execute("DROP TYPE IF EXISTS paymentstatus;")