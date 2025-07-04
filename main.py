import logging
import time
from datetime import datetime
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from typing import Optional

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

# Create FastAPI instance
app = FastAPI(
    title="Simple Chat API",
    description="A simple API that responds to messages",
    version="1.0.0"
)

# Define the request model
class MessageRequest(BaseModel):
    message: str

# Define the response model
class MessageResponse(BaseModel):
    response: str
    original_message: str

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
    POST endpoint that takes a message and returns a response
    
    Args:
        request: MessageRequest object containing the input message
        
    Returns:
        MessageResponse object with the response and original message
    """
    # Log the incoming request
    logger.info(f"Chat endpoint called with message: '{request.message}'")
    
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
        logger.info(f"Successfully processed chat request. Original: '{input_message}' -> Response: '{response_text}'")
        
        return response_obj
        
    except Exception as e:
        # Log the error
        logger.error(f"Error processing chat request: {str(e)}", exc_info=True)
        logger.error(f"Failed message: '{request.message}'")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    logger.info("Health check endpoint accessed")
    return {"status": "healthy", "service": "Simple Chat API"}

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