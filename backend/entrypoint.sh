#!/bin/sh
set -e

echo "=== VaxKavach Production Backend Boot ==="

# Wait for database readiness
echo "Waiting for PostGIS database to accept connections..."
python -c "
import time
import os
import psycopg2

db_url = os.getenv('DATABASE_URL', 'postgresql://vaxkavach:vaxpassword@db:5432/vaxkavach_db')
for attempt in range(30):
    try:
        conn = psycopg2.connect(db_url)
        conn.close()
        print('PostGIS database is ready and accepting connections!')
        break
    except Exception as e:
        print(f'Attempt {attempt + 1}/30: Waiting 2s...')
        time.sleep(2)
else:
    print('ERROR: Database connection timed out after 60 seconds.')
    exit(1)
"

# Run Alembic migrations
echo "Executing database migrations (alembic upgrade head)..."
alembic upgrade head

# Seed database if unseeded
echo "Verifying operational seeds..."
python -c "
from app.core.database import SessionLocal
from app.models.all import Depot
db = SessionLocal()
try:
    if db.query(Depot).count() == 0:
        print('Depot registry is empty. Executing seed_db()...')
        from seed import seed_db
        seed_db()
        print('Seed complete.')
    else:
        print('Depot registry verified (already seeded).')
finally:
    db.close()
"

echo "Launching VaxKavach application..."
exec "$@"
