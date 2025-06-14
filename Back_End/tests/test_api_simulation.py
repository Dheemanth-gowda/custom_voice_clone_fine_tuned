import requests
import json
import os
from pathlib import Path
import time

BASE_URL = "http://localhost:8000/api/v1"
TEST_DATA_DIR = Path(__file__).parent / "data"

def test_registration():
    """Test user registration"""
    print("\n=== Testing User Registration ===")
    response = requests.post(
        f"{BASE_URL}/auth/register",
        json={
            "email": "test4@example.com",
            "username": "testuser4",
            "full_name": "Test User 4",
            "password": "testpassword123"
        }
    )
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.json()

def test_login(email: str, password: str):
    """Test user login"""
    print("\n=== Testing User Login ===")
    response = requests.post(
        f"{BASE_URL}/auth/login",
        data={
            "username": email,
            "password": password
        }
    )
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.json()

def test_create_voice_model(token: str):
    """Test voice model creation"""
    print("\n=== Testing Voice Model Creation ===")
    response = requests.post(
        f"{BASE_URL}/voice-clone/models",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "Test Voice Model",
            "description": "A test voice model for simulation",
            "parameters": {
                "sample_rate": 22050,
                "hop_length": 256,
                "win_length": 1024
            }
        }
    )
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.json()

def test_list_voice_models(token: str):
    """Test listing voice models"""
    print("\n=== Testing Voice Model Listing ===")
    response = requests.get(
        f"{BASE_URL}/voice-clone/models",
        headers={"Authorization": f"Bearer {token}"}
    )
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.json()

def test_upload_voice_sample(token: str, model_id: int):
    """Test voice sample upload"""
    print("\n=== Testing Voice Sample Upload ===")
    # Create a dummy audio file for testing
    audio_path = TEST_DATA_DIR / "audio" / "raw" / "test_sample.wav"
    audio_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Create a simple sine wave audio file using librosa
    import librosa
    import numpy as np
    import soundfile as sf
    
    # Generate a 1-second sine wave at 440 Hz
    sr = 22050
    t = np.linspace(0, 1, sr)
    audio = np.sin(2 * np.pi * 440 * t)
    sf.write(str(audio_path), audio, sr)
    
    # Upload the sample
    with open(audio_path, "rb") as f:
        response = requests.post(
            f"{BASE_URL}/voice-clone/models/{model_id}/samples",
            headers={"Authorization": f"Bearer {token}"},
            files={"audio_file": ("test_sample.wav", f, "audio/wav")},
            data={
                "emotion": "neutral",
                "text": "This is a test sample."
            }
        )
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.json()

def run_simulation():
    """Run the complete API simulation"""
    print("Starting API Simulation...")
    
    # Test registration
    user_data = test_registration()
    if user_data.get("id"):
        print("Registration successful!")
    else:
        print("Registration failed!")
        return
    
    # Test login
    token_data = test_login("test4@example.com", "testpassword123")
    if token_data.get("access_token"):
        print("Login successful!")
        token = token_data["access_token"]
    else:
        print("Login failed!")
        return
    
    # Test voice model creation
    model_data = test_create_voice_model(token)
    if model_data.get("id"):
        print("Voice model creation successful!")
        model_id = model_data["id"]
    else:
        print("Voice model creation failed!")
        return
    
    # Test listing voice models
    models = test_list_voice_models(token)
    if isinstance(models, list):
        print("Voice model listing successful!")
    else:
        print("Voice model listing failed!")
        return
    
    # Test voice sample upload
    sample_data = test_upload_voice_sample(token, model_id)
    if sample_data.get("id"):
        print("Voice sample upload successful!")
    else:
        print("Voice sample upload failed!")
        return
    
    print("\nSimulation completed successfully!")

if __name__ == "__main__":
    run_simulation() 