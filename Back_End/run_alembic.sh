#!/bin/bash

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run Alembic commands
case "$1" in
    "init")
        alembic init alembic
        ;;
    "create")
        alembic revision --autogenerate -m "$2"
        ;;
    "upgrade")
        alembic upgrade head
        ;;
    "downgrade")
        alembic downgrade -1
        ;;
    "history")
        alembic history
        ;;
    *)
        echo "Usage: $0 {init|create|upgrade|downgrade|history}"
        echo "  init: Initialize alembic"
        echo "  create <message>: Create a new migration"
        echo "  upgrade: Upgrade to latest version"
        echo "  downgrade: Downgrade one version"
        echo "  history: Show migration history"
        exit 1
        ;;
esac 