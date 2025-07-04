import logging
import time
import os
from datetime import datetime
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from typing import Optional
import openai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# OpenAI configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
logger.info(f"OPENAI_API_KEY: {OPENAI_API_KEY}")
if not OPENAI_API_KEY:
    logger.warning("OPENAI_API_KEY not found in environment variables. OpenAI chat will be disabled.")
    openai_client = None
else:
    openai_client = openai.OpenAI(api_key=OPENAI_API_KEY)
    logger.info("OpenAI client initialized successfully")

# Create FastAPI instance
app = FastAPI(
    title="Simple Chat API",
    description="A simple API that responds to messages with both simple responses and OpenAI integration",
    version="1.0.0"
)

# Define the request models
class MessageRequest(BaseModel):
    message: str

class OpenAIChatRequest(BaseModel):
    message: str
    model: Optional[str] = "gpt-3.5-turbo"
    max_tokens: Optional[int] = 150
    temperature: Optional[float] = 0.7

# Define the response models
class MessageResponse(BaseModel):
    response: str
    original_message: str

class OpenAIChatResponse(BaseModel):
    response: str
    original_message: str
    model_used: str
    tokens_used: Optional[int] = None

# Middleware for request logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Middleware to log all incoming requests"""
    start_time = time.time()
    
    # Log request details
    logger.info(f"Request started: {request.method} {request.url}")
    logger.info(f"Client IP: {request.client.host if request.client else 'Unknown'}")
    logger.info(f"User Agent: {request.headers.get('user-agent', 'Unknown')}")
    
    # Process the request
    response = await call_next(request)
    
    # Calculate processing time
    process_time = time.time() - start_time
    
    # Log response details
    logger.info(f"Request completed: {request.method} {request.url} - Status: {response.status_code} - Duration: {process_time:.4f}s")
    
    return response

@app.on_event("startup")
async def startup_event():
    """Log when the application starts"""
    logger.info("=" * 50)
    logger.info("Simple Chat API is starting up...")
    logger.info(f"Startup time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    if openai_client:
        logger.info("OpenAI integration: ENABLED")
    else:
        logger.warning("OpenAI integration: DISABLED (no API key)")
    logger.info("=" * 50)

@app.on_event("shutdown")
async def shutdown_event():
    """Log when the application shuts down"""
    logger.info("=" * 50)
    logger.info("Simple Chat API is shutting down...")
    logger.info(f"Shutdown time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 50)

@app.get("/")
async def root():
    """Root endpoint"""
    logger.info("Root endpoint accessed")
    return {"message": "Welcome to Simple Chat API"}

@app.post("/chat", response_model=MessageResponse)
async def chat_endpoint(request: MessageRequest):
    """
    POST endpoint that takes a message and returns a simple response
    
    Args:
        request: MessageRequest object containing the input message
        
    Returns:
        MessageResponse object with the response and original message
    """
    # Log the incoming request
    logger.info(f"Simple chat endpoint called with message: '{request.message}'")
    
    try:
        # Get the input message
        input_message = request.message.strip()
        logger.info(f"Processing message: '{input_message}'")
        
        # Simple response logic
        if input_message.lower() == "how are you":
            response_text = "I am fine"
            logger.info("Response: 'I am fine' (matched: 'how are you')")
        elif input_message.lower() == "hello" or input_message.lower() == "hi":
            response_text = "Hello! How can I help you?"
            logger.info("Response: 'Hello! How can I help you?' (matched: 'hello/hi')")
        elif input_message.lower() == "bye" or input_message.lower() == "goodbye":
            response_text = "Goodbye! Have a great day!"
            logger.info("Response: 'Goodbye! Have a great day!' (matched: 'bye/goodbye')")
        else:
            response_text = f"I received your message: '{input_message}'. How can I assist you?"
            logger.info(f"Response: Echo response for unmatched message: '{input_message}'")
        
        # Create response object
        response_obj = MessageResponse(
            response=response_text,
            original_message=input_message
        )
        
        # Log successful response
        logger.info(f"Successfully processed simple chat request. Original: '{input_message}' -> Response: '{response_text}'")
        
        return response_obj
        
    except Exception as e:
        # Log the error
        logger.error(f"Error processing simple chat request: {str(e)}", exc_info=True)
        logger.error(f"Failed message: '{request.message}'")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/chat/openai", response_model=OpenAIChatResponse)
async def openai_chat_endpoint(request: OpenAIChatRequest):
    """
    POST endpoint that uses OpenAI to generate responses
    
    Args:
        request: OpenAIChatRequest object containing the input message and OpenAI parameters
        
    Returns:
        OpenAIChatResponse object with the AI response and metadata
    """
    # Check if OpenAI is available
    if not openai_client:
        logger.error("OpenAI chat endpoint called but OpenAI is not configured")
        raise HTTPException(
            status_code=503, 
            detail="OpenAI service is not available. Please set OPENAI_API_KEY environment variable."
        )
    
    # Log the incoming request
    logger.info(f"OpenAI chat endpoint called with message: '{request.message}'")
    logger.info(f"Model: {request.model}, Max tokens: {request.max_tokens}, Temperature: {request.temperature}")
    
    try:
        # Get the input message
        input_message = request.message.strip()
        logger.info(f"Processing OpenAI message: '{input_message}'")
        
        # Call OpenAI API
        logger.info(f"Calling OpenAI API with model: {request.model}")
        
        response = openai_client.chat.completions.create(
            model=request.model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant. Provide concise and friendly responses."},
                {"role": "user", "content": input_message}
            ],
            max_tokens=request.max_tokens,
            temperature=request.temperature
        )
        
        # Extract the response
        ai_response = response.choices[0].message.content
        tokens_used = response.usage.total_tokens if response.usage else None
        
        logger.info(f"OpenAI response received: '{ai_response}'")
        logger.info(f"Tokens used: {tokens_used}")
        
        # Create response object
        response_obj = OpenAIChatResponse(
            response=ai_response,
            original_message=input_message,
            model_used=request.model,
            tokens_used=tokens_used
        )
        
        # Log successful response
        logger.info(f"Successfully processed OpenAI chat request. Original: '{input_message}' -> Response: '{ai_response}'")
        
        return response_obj
        
    except openai.AuthenticationError as e:
        logger.error(f"OpenAI authentication error: {str(e)}")
        raise HTTPException(status_code=401, detail="OpenAI authentication failed. Please check your API key.")
    
    except openai.RateLimitError as e:
        logger.error(f"OpenAI rate limit error: {str(e)}")
        raise HTTPException(status_code=429, detail="OpenAI rate limit exceeded. Please try again later.")
    
    except openai.APIError as e:
        logger.error(f"OpenAI API error: {str(e)}")
        raise HTTPException(status_code=502, detail=f"OpenAI API error: {str(e)}")
    
    except Exception as e:
        # Log the error
        logger.error(f"Error processing OpenAI chat request: {str(e)}", exc_info=True)
        logger.error(f"Failed message: '{request.message}'")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    logger.info("Health check endpoint accessed")
    
    health_status = {
        "status": "healthy", 
        "service": "Simple Chat API",
        "openai_status": "enabled" if openai_client else "disabled"
    }
    
    return health_status

# Exception handler for unhandled exceptions
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler to log all unhandled exceptions"""
    logger.error(f"Unhandled exception occurred: {str(exc)}", exc_info=True)
    logger.error(f"Request URL: {request.url}")
    logger.error(f"Request method: {request.method}")
    return {"error": "Internal server error", "detail": str(exc)}

if __name__ == "__main__":
    import uvicorn
    
    logger.info("Starting FastAPI server with uvicorn...")
    logger.info("Server will be available at: http://localhost:8000")
    logger.info("API documentation will be available at: http://localhost:8000/docs")
    
    uvicorn.run(app, host="0.0.0.0", port=8000) 