#!/usr/bin/env python3
"""
Test script to verify the deployment is working correctly.
Run this after your deployment is live to check if the backend and database are functioning.
"""

import requests
import json
import sys

def test_backend_health(base_url):
    """Test the backend health endpoint."""
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Backend health check passed: {data}")
            return True
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend health check error: {e}")
        return False

def test_save_conversation(base_url):
    """Test saving a conversation to the database."""
    try:
        test_data = {
            "conversation_id": "test_conv_123",
            "messages": [
                {"role": "user", "content": "Hello, this is a test message"},
                {"role": "assistant", "content": "Hello! This is a test response"}
            ],
            "user_id": "test_user"
        }
        
        response = requests.post(f"{base_url}/save_conversation", 
                               json=test_data, 
                               timeout=10)
        
        if response.status_code == 201:
            print("✅ Conversation saved successfully")
            return True
        else:
            print(f"❌ Failed to save conversation: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error saving conversation: {e}")
        return False

def test_get_conversations(base_url):
    """Test retrieving conversations from the database."""
    try:
        response = requests.get(f"{base_url}/get_conversations?user_id=test_user", 
                              timeout=10)
        
        if response.status_code == 200:
            conversations = response.json()
            print(f"✅ Retrieved {len(conversations)} conversations")
            return True
        else:
            print(f"❌ Failed to get conversations: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error getting conversations: {e}")
        return False

def main():
    """Main test function."""
    # Replace with your actual deployment URL
    base_url = "http://localhost:5000"  # Change this to your deployment URL
    
    print("🧪 Testing CodeBuddy Backend Deployment")
    print("=" * 50)
    
    # Test backend health
    if not test_backend_health(base_url):
        print("\n❌ Backend is not responding. Please check your deployment.")
        sys.exit(1)
    
    # Test database operations
    if not test_save_conversation(base_url):
        print("\n❌ Database save operation failed.")
        sys.exit(1)
    
    if not test_get_conversations(base_url):
        print("\n❌ Database retrieval operation failed.")
        sys.exit(1)
    
    print("\n🎉 All tests passed! Your backend and database are working correctly.")
    print("\nTo test the full application:")
    print(f"1. Frontend should be available at: {base_url.replace('5000', '8501')}")
    print(f"2. Backend API is available at: {base_url}")
    print("3. Database is properly connected and functioning")

if __name__ == "__main__":
    main() 