#!/bin/bash
cd $(dirname $0)
source ../.venv/bin/activate
alembic revision --autogenerate -m "Initial models"
alembic upgrade head
