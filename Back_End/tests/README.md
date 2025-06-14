# Voice Cloning API Tests

This directory contains test scripts and data for testing the Voice Cloning API.

## Directory Structure

```
tests/
├── data/
│   ├── audio/
│   │   ├── raw/        # Raw audio samples
│   │   ├── processed/  # Processed audio files
│   │   └── generated/  # Generated voice samples
│   └── models/         # Voice model files
├── test_api_simulation.py
└── requirements-test.txt
```

## Setup

1. Install test dependencies:
```bash
pip install -r requirements-test.txt
```

2. Ensure the API server is running on `http://localhost:8000`

## Running Tests

To run the API simulation:

```bash
python test_api_simulation.py
```

The simulation will:
1. Register a new test user
2. Log in with the test user
3. Create a new voice model
4. List available voice models
5. Upload a test voice sample

## Test Data

The test script generates a simple sine wave audio file for testing voice sample uploads. The file is created in the `data/audio/raw` directory.

## Notes

- The test script uses a dummy audio file (sine wave) for testing voice sample uploads
- All API responses and status codes are printed to the console
- The script includes error handling and will stop if any step fails 