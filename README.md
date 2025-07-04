# Simple Chat API

A FastAPI application that provides a simple chat endpoint where you can send messages and receive responses.

## Features

- POST endpoint for chat interactions
- Automatic API documentation with Swagger UI
- Health check endpoint
- Input validation using Pydantic models

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

### Method 1: Using Python directly
```bash
python main.py
```

### Method 2: Using uvicorn
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

The server will start on `http://localhost:8000`

## API Endpoints

### 1. Root Endpoint
- **URL**: `GET /`
- **Description**: Welcome message
- **Response**: `{"message": "Welcome to Simple Chat API"}`

### 2. Chat Endpoint
- **URL**: `POST /chat`
- **Description**: Send a message and get a response
- **Request Body**:
```json
{
    "message": "How are you"
}
```
- **Response**:
```json
{
    "response": "I am fine",
    "original_message": "How are you"
}
```

### 3. Health Check
- **URL**: `GET /health`
- **Description**: Check if the service is running
- **Response**: `{"status": "healthy", "service": "Simple Chat API"}`

## API Documentation

Once the server is running, you can access:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## Example Usage

### Using curl
```bash
curl -X POST "http://localhost:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{"message": "How are you"}'
```

### Using Python requests
```python
import requests

url = "http://localhost:8000/chat"
data = {"message": "How are you"}
response = requests.post(url, json=data)
print(response.json())
```

## Response Logic

The API has simple response logic:
- "How are you" → "I am fine"
- "Hello" or "Hi" → "Hello! How can I help you?"
- "Bye" or "Goodbye" → "Goodbye! Have a great day!"
- Any other message → Echo response with assistance offer

## Error Handling

The API includes proper error handling for:
- Invalid JSON requests
- Missing required fields
- Internal server errors 