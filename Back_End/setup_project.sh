#!/bin/bash

# Create necessary directories
mkdir -p app/api/v1/endpoints
mkdir -p app/core
mkdir -p app/db/models
mkdir -p app/schemas
mkdir -p app/services
mkdir -p app/ml/models
mkdir -p app/ml/preprocessing
mkdir -p app/ml/training
mkdir -p storage/audio/{raw,processed,generated}
mkdir -p storage/models
mkdir -p logs
mkdir -p alembic/versions
mkdir -p tests/{api,services,ml}

# Create __init__.py files
touch app/__init__.py
touch app/api/__init__.py
touch app/api/v1/__init__.py
touch app/api/v1/endpoints/__init__.py
touch app/core/__init__.py
touch app/db/__init__.py
touch app/db/models/__init__.py
touch app/schemas/__init__.py
touch app/services/__init__.py
touch app/ml/__init__.py
touch app/ml/models/__init__.py
touch app/ml/preprocessing/__init__.py
touch app/ml/training/__init__.py
touch tests/__init__.py
touch tests/api/__init__.py
touch tests/services/__init__.py
touch tests/ml/__init__.py

# Create .gitkeep files to preserve empty directories
touch storage/audio/raw/.gitkeep
touch storage/audio/processed/.gitkeep
touch storage/audio/generated/.gitkeep
touch storage/models/.gitkeep
touch logs/.gitkeep

# Set permissions
chmod +x run_alembic.sh
chmod +x setup_project.sh

echo "Project structure setup complete!" 