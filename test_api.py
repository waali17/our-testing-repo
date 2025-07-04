import requests
import json

# API base URL
BASE_URL = "http://localhost:8000"

def test_chat_endpoint():
    """Test the chat endpoint with different messages"""
    
    # Test cases
    test_cases = [
        {"message": "How are you"},
        {"message": "Hello"},
        {"message": "Hi"},
        {"message": "Goodbye"},
        {"message": "What's the weather like?"}
    ]
    
    print("Testing Chat API Endpoint")
    print("=" * 40)
    
    for i, test_case in enumerate(test_cases, 1):
        try:
            print(f"\nTest {i}: Sending message: '{test_case['message']}'")
            
            # Make POST request to chat endpoint
            response = requests.post(
                f"{BASE_URL}/chat",
                json=test_case,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Success!")
                print(f"   Response: '{result['response']}'")
                print(f"   Original message: '{result['original_message']}'")
            else:
                print(f"❌ Error: {response.status_code}")
                print(f"   Response: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print("❌ Connection Error: Make sure the FastAPI server is running on localhost:8000")
            break
        except Exception as e:
            print(f"❌ Unexpected error: {str(e)}")

def test_health_endpoint():
    """Test the health check endpoint"""
    try:
        print("\nTesting Health Check Endpoint")
        print("=" * 40)
        
        response = requests.get(f"{BASE_URL}/health")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Health Check: {result}")
        else:
            print(f"❌ Health Check Failed: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Make sure the FastAPI server is running on localhost:8000")
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")

if __name__ == "__main__":
    print("FastAPI Chat Endpoint Test")
    print("Make sure the server is running with: python main.py")
    print("=" * 50)
    
    # Test health endpoint first
    test_health_endpoint()
    
    # Test chat endpoint
    test_chat_endpoint()
    
    print("\n" + "=" * 50)
    print("Test completed!") 