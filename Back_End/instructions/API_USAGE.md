# Voice Cloning API Usage Guide

This guide provides step-by-step instructions for using the Voice Cloning API.

## Base URL
```
http://localhost:8000/api/v1
```

## Authentication
All API endpoints (except registration and login) require a JWT token in the Authorization header:
```
Authorization: Bearer <your_token>
```

## Step-by-Step Usage

### 1. User Registration
Register a new user to get started.

**Endpoint:** `POST /auth/register`

**Request Body:**
```json
{
    "email": "user@example.com",
    "username": "username",
    "full_name": "Full Name",
    "password": "your_password"
}
```

**Example using curl:**
```bash
curl -X POST 'http://localhost:8000/api/v1/auth/register' \
-H 'accept: application/json' \
-H 'Content-Type: application/json' \
-d '{
    "email": "user@example.com",
    "username": "username",
    "full_name": "Full Name",
    "password": "your_password"
}'
```

### 2. User Login
Login to get your access token.

**Endpoint:** `POST /auth/login`

**Request Body:**
```json
{
    "username": "user@example.com",
    "password": "your_password"
}
```

**Example using curl:**
```bash
curl -X POST 'http://localhost:8000/api/v1/auth/login' \
-H 'accept: application/json' \
-H 'Content-Type: application/json' \
-d '{
    "username": "user@example.com",
    "password": "your_password"
}'
```

**Response:**
```json
{
    "access_token": "your_jwt_token",
    "token_type": "bearer"
}
```

### 3. Update User Profile
Update your user profile information.

**Endpoint:** `PUT /users/me`

**Request Body:**
```json
{
    "full_name": "New Full Name",
    "email": "newemail@example.com"
}
```

**Example using curl:**
```bash
curl -X PUT 'http://localhost:8000/api/v1/users/me' \
-H 'accept: application/json' \
-H 'Content-Type: application/json' \
-H 'Authorization: Bearer your_jwt_token' \
-d '{
    "full_name": "New Full Name",
    "email": "newemail@example.com"
}'
```

### 4. Create Voice Model
Create a new voice model for cloning.

**Endpoint:** `POST /voice-clone/models`

**Request Body:**
```json
{
    "name": "My Voice Model",
    "description": "A voice model for my voice",
    "parameters": {
        "sample_rate": 22050,
        "hop_length": 256,
        "win_length": 1024
    }
}
```

**Example using curl:**
```bash
curl -X POST 'http://localhost:8000/api/v1/voice-clone/models' \
-H 'accept: application/json' \
-H 'Content-Type: application/json' \
-H 'Authorization: Bearer your_jwt_token' \
-d '{
    "name": "My Voice Model",
    "description": "A voice model for my voice",
    "parameters": {
        "sample_rate": 22050,
        "hop_length": 256,
        "win_length": 1024
    }
}'
```

### 5. List Voice Models
Get a list of all your voice models.

**Endpoint:** `GET /voice-clone/models`

**Example using curl:**
```bash
curl -X GET 'http://localhost:8000/api/v1/voice-clone/models' \
-H 'accept: application/json' \
-H 'Authorization: Bearer your_jwt_token'
```

### 6. Upload Voice Sample
Upload a voice sample for a specific model.

**Endpoint:** `POST /voice-clone/models/{model_id}/samples`

**Request Body (multipart/form-data):**
- `audio`: Audio file (WAV format)
- `emotion`: Emotion label (optional)
- `text`: Text content of the audio (optional)

**Example using curl:**
```bash
curl -X POST 'http://localhost:8000/api/v1/voice-clone/models/1/samples' \
-H 'accept: application/json' \
-H 'Authorization: Bearer your_jwt_token' \
-F 'audio=@/path/to/your/audio.wav' \
-F 'emotion=neutral' \
-F 'text=This is a test recording'
```

### 7. List Voice Samples
Get all voice samples for a specific model.

**Endpoint:** `GET /voice-clone/models/{model_id}/samples`

**Example using curl:**
```bash
curl -X GET 'http://localhost:8000/api/v1/voice-clone/models/1/samples' \
-H 'accept: application/json' \
-H 'Authorization: Bearer your_jwt_token'
```

### 8. Train Voice Model
Train a voice model using uploaded samples.

**Endpoint:** `POST /voice-clone/models/{model_id}/train`

**Example using curl:**
```bash
curl -X POST 'http://localhost:8000/api/v1/voice-clone/models/1/train' \
-H 'accept: application/json' \
-H 'Authorization: Bearer your_jwt_token'
```

**Response:**
```json
{
    "status": "training_started",
    "task_id": "task_id",
    "message": "Model training has been scheduled"
}
```

### 9. Generate Speech
Generate speech from text using a trained model.

**Endpoint:** `POST /voice-clone/models/{model_id}/generate`

**Request Body:**
```json
{
    "text": "Your text to convert to speech"
}
```

**Example using curl:**
```bash
curl -X POST 'http://localhost:8000/api/v1/voice-clone/models/1/generate' \
-H 'accept: application/json' \
-H 'Content-Type: application/json' \
-H 'Authorization: Bearer your_jwt_token' \
-d '{
    "text": "Your text to convert to speech"
}'
```

**Response (Immediate):**
```json
{
    "status": "success",
    "output_path": "/path/to/generated/audio.wav",
    "message": "Speech generated successfully"
}
```

**Response (Background Processing):**
```json
{
    "status": "generation_started",
    "task_id": "task_id",
    "message": "Speech generation has been scheduled",
    "estimated_time": "2-3 minutes per minute of audio"
}
```

### 10. Get Model Status
Get the status of a voice model.

**Endpoint:** `GET /voice-clone/models/{model_id}/status`

**Example using curl:**
```bash
curl -X GET 'http://localhost:8000/api/v1/voice-clone/models/1/status' \
-H 'accept: application/json' \
-H 'Authorization: Bearer your_jwt_token'
```

**Response:**
```json
{
    "id": 1,
    "name": "My Voice Model",
    "status": "ready",
    "created_at": "2025-06-14T15:19:44",
    "updated_at": "2025-06-14T15:20:00",
    "samples_count": 10
}
```

### 11. Get Storage Quota
Get storage usage and quota information.

**Endpoint:** `GET /voice-clone/storage/quota`

**Example using curl:**
```bash
curl -X GET 'http://localhost:8000/api/v1/voice-clone/storage/quota' \
-H 'accept: application/json' \
-H 'Authorization: Bearer your_jwt_token'
```

**Response:**
```json
{
    "user_id": 1,
    "model_usage_mb": 100,
    "model_quota_mb": 1024,
    "sample_usage_mb": 50,
    "sample_quota_mb": 512,
    "model_quota_percent": 9.77,
    "sample_quota_percent": 9.77
}
```

### 12. Cleanup Storage
Manually trigger storage cleanup.

**Endpoint:** `POST /voice-clone/cleanup`

**Example using curl:**
```bash
curl -X POST 'http://localhost:8000/api/v1/voice-clone/cleanup' \
-H 'accept: application/json' \
-H 'Authorization: Bearer your_jwt_token'
```

**Response:**
```json
{
    "status": "cleanup_started",
    "task_id": "task_id",
    "message": "Storage cleanup has been scheduled"
}
```

## Complete Workflow Example

Here's a complete example of using the API to create and use a voice model:

1. **Register and Login:**
```bash
# Register
curl -X POST 'http://localhost:8000/api/v1/auth/register' \
-H 'Content-Type: application/json' \
-d '{
    "email": "user@example.com",
    "username": "username",
    "full_name": "Full Name",
    "password": "your_password"
}'

# Login
curl -X POST 'http://localhost:8000/api/v1/auth/login' \
-H 'Content-Type: application/json' \
-d '{
    "username": "user@example.com",
    "password": "your_password"
}'
```

2. **Create Voice Model:**
```bash
curl -X POST 'http://localhost:8000/api/v1/voice-clone/models' \
-H 'Authorization: Bearer your_jwt_token' \
-H 'Content-Type: application/json' \
-d '{
    "name": "My Voice Model",
    "description": "A voice model for my voice",
    "parameters": {
        "sample_rate": 22050,
        "hop_length": 256,
        "win_length": 1024
    }
}'
```

3. **Upload Voice Samples:**
```bash
# Upload multiple samples
for file in samples/*.wav; do
    curl -X POST 'http://localhost:8000/api/v1/voice-clone/models/1/samples' \
    -H 'Authorization: Bearer your_jwt_token' \
    -F "audio=@$file" \
    -F "emotion=neutral" \
    -F "text=$(basename $file .wav)"
done
```

4. **Train Model:**
```bash
curl -X POST 'http://localhost:8000/api/v1/voice-clone/models/1/train' \
-H 'Authorization: Bearer your_jwt_token'
```

5. **Check Model Status:**
```bash
curl -X GET 'http://localhost:8000/api/v1/voice-clone/models/1/status' \
-H 'Authorization: Bearer your_jwt_token'
```

6. **Generate Speech:**
```bash
curl -X POST 'http://localhost:8000/api/v1/voice-clone/models/1/generate' \
-H 'Authorization: Bearer your_jwt_token' \
-H 'Content-Type: application/json' \
-d '{
    "text": "Hello, this is a test of the voice cloning system."
}'
```

7. **Monitor Storage Usage:**
```bash
curl -X GET 'http://localhost:8000/api/v1/voice-clone/storage/quota' \
-H 'Authorization: Bearer your_jwt_token'
```

8. **Cleanup Storage (if needed):**
```bash
curl -X POST 'http://localhost:8000/api/v1/voice-clone/cleanup' \
-H 'Authorization: Bearer your_jwt_token'
```

## Best Practices

1. **Voice Samples:**
   - Use clear, high-quality recordings
   - Record in a quiet environment
   - Speak naturally and consistently
   - Use 30-second samples for best results
   - Include a variety of speech patterns

2. **Model Training:**
   - Wait for all samples to upload before training
   - Monitor training progress
   - Keep track of model versions
   - Clean up old models regularly

3. **Text Generation:**
   - Break long texts into manageable chunks
   - Use proper punctuation
   - Avoid special characters
   - Consider emotion and tone

4. **Storage Management:**
   - Monitor storage usage regularly
   - Clean up unused models and samples
   - Keep track of quotas
   - Use background processing for long tasks

## Error Handling

The API uses standard HTTP status codes:

- 200: Success
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 500: Internal Server Error

Error responses include a detail message:
```json
{
    "detail": "Error message here"
}
```

## Rate Limiting

The API implements rate limiting to prevent abuse:
- 100 requests per minute per user
- 1000 requests per hour per user
- 10000 requests per day per user

Rate limit headers are included in responses:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 99
X-RateLimit-Reset: 1623600000
```

## Support

For additional support or questions, please contact the API administrator. 