# Voice Clone API Backend

This is the backend service for the Voice Clone application, built with FastAPI and SQLAlchemy.

## Setup

### Local Development

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up the database:
```bash
# Initialize Alembic
./run_alembic.sh init

# Create initial migration
./run_alembic.sh create "Initial migration"

# Apply migrations
./run_alembic.sh upgrade
```

4. Run the development server:
```bash
uvicorn app.main:app --reload
```

The API will be available at http://localhost:8000

### Using Docker/Podman

1. Build and run using Docker Compose:
```bash
docker-compose up --build
```

2. Or using Podman:
```bash
# Build the image
podman build -t voice-clone-api .

# Run the container
podman run -p 8000:8000 \
  -v ./storage:/app/storage \
  -v ./logs:/app/logs \
  voice-clone-api
```

## API Documentation

Once the server is running, you can access:
- Swagger UI documentation: http://localhost:8000/docs
- ReDoc documentation: http://localhost:8000/redoc

## Project Structure

```
Back_End/
├── alembic/              # Database migrations
├── app/
│   ├── api/             # API endpoints
│   ├── core/            # Core functionality
│   ├── db/              # Database models and session
│   ├── ml/              # Machine learning models
│   ├── schemas/         # Pydantic models
│   └── services/        # Business logic
├── storage/             # File storage
│   ├── audio/           # Audio files
│   └── models/          # ML models
├── tests/               # Test files
├── alembic.ini          # Alembic configuration
├── Dockerfile           # Container configuration
├── docker-compose.yml   # Docker Compose configuration
├── requirements.txt     # Python dependencies
└── run_alembic.sh       # Database migration script
```

## Development

1. Create a new migration:
```bash
./run_alembic.sh create "Description of changes"
```

2. Apply migrations:
```bash
./run_alembic.sh upgrade
```

3. Rollback migrations:
```bash
./run_alembic.sh downgrade
```

## Testing

Run tests with pytest:
```bash
pytest
```

## Container Management

### Using Docker Compose

- Start the application:
```bash
docker-compose up
```

- Start in detached mode:
```bash
docker-compose up -d
```

- Stop the application:
```bash
docker-compose down
```

### Using Podman

- Build the image:
```bash
podman build -t voice-clone-api .
```

- Run the container:
```bash
podman run -p 8000:8000 voice-clone-api
```

- Run with volume mounts:
```bash
podman run -p 8000:8000 \
  -v ./storage:/app/storage \
  -v ./logs:/app/logs \
  voice-clone-api
```

## Environment Variables

The following environment variables can be configured:

- `PYTHONPATH`: Set to `/app` in container
- `PYTHONUNBUFFERED`: Set to `1` for better logging
- `SQLALCHEMY_DATABASE_URL`: Database connection URL (default: SQLite)
- `SECRET_KEY`: Secret key for JWT tokens
- `ACCESS_TOKEN_EXPIRE_MINUTES`: JWT token expiration time

## Storage Structure

### Audio Storage
- `storage/audio/raw/`: Original voice recordings
- `storage/audio/processed/`: Cleaned and processed audio files
- `storage/audio/generated/`: Generated voice samples

### Model Storage
- `storage/models/`: Saved model weights and checkpoints

## Authentication

The system uses JWT-based authentication with the following features:
- User registration and login
- Password hashing
- Token-based session management
- Role-based access control

## Logging

Logs are stored in the `logs/` directory with the following structure:
- `app.log`: Application logs
- `error.log`: Error logs
- `access.log`: API access logs

## API Documentation

Once the server is running, access the API documentation at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc 