# VaxKavach - India Telemetry Arc

A secure, deterministic, and verifiable full-stack application for monitoring vaccine logistics.

## Tech Stack
* **Frontend:** React, Vite, TailwindCSS, Framer Motion, React-Simple-Maps
* **Backend:** FastAPI, PostgreSQL, PostGIS, SQLAlchemy, Alembic, WebSockets

## Running Locally

1. **Database:**
   Ensure you have Docker running and use:
   ```bash
   docker compose up -d db
   ```
   This spins up the PostGIS container on port 5432.

2. **Backend:**
   Create a virtual environment and install requirements:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r backend/requirements.txt
   ```
   
   Run migrations and seed the database:
   ```bash
   cd backend
   ./migrate.sh
   python seed.py
   ```
   
   Start the FastAPI server:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

3. **Frontend:**
   ```bash
   cd frontend
   npm install --legacy-peer-deps
   npm run dev
   ```

## Key Features
* **Deterministic Engine:** Analyzes Mean Kinetic Temperature (MKT) and temperature Rate of Change deterministically (no ML).
* **Live Telemetry:** Uses WebSockets to push live telemetry data and detection events to the frontend.
* **Geospatial Processing:** Converts `.shp` shapefiles into GeoJSON and utilizes PostGIS geometry types.
* **Audit Trail:** An append-only hashing system ensuring data integrity.
