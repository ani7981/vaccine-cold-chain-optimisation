"""IoT diagnostics and Merkle compliance

Revision ID: d5a8120c9f11
Revises: c494607abb34
Create Date: 2026-09-08 23:45:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'd5a8120c9f11'
down_revision: Union[str, Sequence[str], None] = 'c494607abb34'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Add Dual-Probe IoT Diagnostics Columns to telemetry_readings
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    existing_cols = [c['name'] for c in inspector.get_columns('telemetry_readings')]

    if 'probe_1_temperature' not in existing_cols:
        op.add_column('telemetry_readings', sa.Column('probe_1_temperature', sa.Float(), nullable=True))
    if 'probe_2_temperature' not in existing_cols:
        op.add_column('telemetry_readings', sa.Column('probe_2_temperature', sa.Float(), nullable=True))
    if 'probe_discrepancy' not in existing_cols:
        op.add_column('telemetry_readings', sa.Column('probe_discrepancy', sa.Float(), nullable=True))
    if 'sequence_number' not in existing_cols:
        op.add_column('telemetry_readings', sa.Column('sequence_number', sa.Integer(), nullable=True))
    if 'battery_level' not in existing_cols:
        op.add_column('telemetry_readings', sa.Column('battery_level', sa.Float(), nullable=True))
    if 'signal_strength_dbm' not in existing_cols:
        op.add_column('telemetry_readings', sa.Column('signal_strength_dbm', sa.Integer(), nullable=True))
    if 'sensor_fault_flag' not in existing_cols:
        op.add_column('telemetry_readings', sa.Column('sensor_fault_flag', sa.String(), nullable=True))
    if 'sensor_fault_flags' not in existing_cols:
        op.add_column('telemetry_readings', sa.Column('sensor_fault_flags', sa.JSON(), nullable=True))
    if 'is_valid' not in existing_cols:
        op.add_column('telemetry_readings', sa.Column('is_valid', sa.Boolean(), server_default='true', nullable=True))

    # 2. Create audit_blocks Table for Merkle Tree Ledger
    tables = inspector.get_table_names()
    if 'audit_blocks' not in tables:
        op.create_table(
            'audit_blocks',
            sa.Column('id', sa.String(), nullable=False),
            sa.Column('block_index', sa.Integer(), nullable=False),
            sa.Column('merkle_root', sa.String(), nullable=False),
            sa.Column('event_count', sa.Integer(), nullable=False),
            sa.Column('start_time', sa.DateTime(timezone=True), nullable=False),
            sa.Column('end_time', sa.DateTime(timezone=True), nullable=False),
            sa.Column('previous_block_hash', sa.String(), nullable=False),
            sa.Column('block_hash', sa.String(), nullable=False),
            sa.Column('sealed_at', sa.DateTime(timezone=True), nullable=False),
            sa.Column('signer_identity', sa.String(), nullable=False),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('block_index')
        )
        op.create_index('ix_audit_blocks_id', 'audit_blocks', ['id'], unique=False)
        op.create_index('ix_audit_blocks_block_index', 'audit_blocks', ['block_index'], unique=True)
        op.create_index('ix_audit_blocks_merkle_root', 'audit_blocks', ['merkle_root'], unique=False)

    # 3. Create compliance_certificates Table for CDSCO / WHO-PQS Dossiers
    if 'compliance_certificates' not in tables:
        op.create_table(
            'compliance_certificates',
            sa.Column('id', sa.String(), nullable=False),
            sa.Column('certificate_id', sa.String(), nullable=False),
            sa.Column('shipment_id', sa.String(), nullable=False),
            sa.Column('batch_number', sa.String(), nullable=False),
            sa.Column('vaccine_name', sa.String(), nullable=False),
            sa.Column('manufacturer', sa.String(), nullable=False),
            sa.Column('doses_count', sa.Integer(), nullable=False),
            sa.Column('departure_depot', sa.String(), nullable=False),
            sa.Column('destination_depot', sa.String(), nullable=False),
            sa.Column('dispatched_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('arrived_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('total_transit_hours', sa.Float(), nullable=True),
            sa.Column('mean_kinetic_temperature_c', sa.Float(), nullable=False),
            sa.Column('mkt_allowable_limit_c', sa.Float(), nullable=False),
            sa.Column('thermal_compliance_status', sa.String(), nullable=False),
            sa.Column('excursion_duration_minutes', sa.Integer(), nullable=False),
            sa.Column('sensor_probe_fault_count', sa.Integer(), nullable=False),
            sa.Column('merkle_root_seal', sa.String(), nullable=False),
            sa.Column('verified_by_role', sa.String(), nullable=False),
            sa.Column('regulatory_standard', sa.String(), nullable=False),
            sa.Column('generated_at', sa.DateTime(timezone=True), nullable=False),
            sa.Column('dossier_json', sa.JSON(), nullable=True),
            sa.ForeignKeyConstraint(['shipment_id'], ['shipments.id']),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('certificate_id')
        )
        op.create_index('ix_compliance_certificates_id', 'compliance_certificates', ['id'], unique=False)
        op.create_index('ix_compliance_certificates_certificate_id', 'compliance_certificates', ['certificate_id'], unique=True)
        op.create_index('ix_compliance_certificates_shipment_id', 'compliance_certificates', ['shipment_id'], unique=False)


def downgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    tables = inspector.get_table_names()

    if 'compliance_certificates' in tables:
        op.drop_index('ix_compliance_certificates_shipment_id', table_name='compliance_certificates')
        op.drop_index('ix_compliance_certificates_certificate_id', table_name='compliance_certificates')
        op.drop_index('ix_compliance_certificates_id', table_name='compliance_certificates')
        op.drop_table('compliance_certificates')

    if 'audit_blocks' in tables:
        op.drop_index('ix_audit_blocks_merkle_root', table_name='audit_blocks')
        op.drop_index('ix_audit_blocks_block_index', table_name='audit_blocks')
        op.drop_index('ix_audit_blocks_id', table_name='audit_blocks')
        op.drop_table('audit_blocks')

    existing_cols = [c['name'] for c in inspector.get_columns('telemetry_readings')]
    if 'is_valid' in existing_cols:
        op.drop_column('telemetry_readings', 'is_valid')
    if 'sensor_fault_flags' in existing_cols:
        op.drop_column('telemetry_readings', 'sensor_fault_flags')
    if 'sensor_fault_flag' in existing_cols:
        op.drop_column('telemetry_readings', 'sensor_fault_flag')
    if 'signal_strength_dbm' in existing_cols:
        op.drop_column('telemetry_readings', 'signal_strength_dbm')
    if 'battery_level' in existing_cols:
        op.drop_column('telemetry_readings', 'battery_level')
    if 'sequence_number' in existing_cols:
        op.drop_column('telemetry_readings', 'sequence_number')
    if 'probe_discrepancy' in existing_cols:
        op.drop_column('telemetry_readings', 'probe_discrepancy')
    if 'probe_2_temperature' in existing_cols:
        op.drop_column('telemetry_readings', 'probe_2_temperature')
    if 'probe_1_temperature' in existing_cols:
        op.drop_column('telemetry_readings', 'probe_1_temperature')

