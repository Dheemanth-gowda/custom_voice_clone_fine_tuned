from setuptools import setup, find_packages

setup(
    name="voice_clone",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi",
        "uvicorn",
        "sqlalchemy",
        "alembic",
        "pydantic",
        "pydantic-settings",
        "python-jose[cryptography]",
        "passlib[bcrypt]",
        "python-multipart",
        "redis",
        "psycopg2-binary",
        "python-dotenv",
        "librosa",
        "numpy",
        "torch",
        "soundfile",
    ],
) 