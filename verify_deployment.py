#!/usr/bin/env python3
"""
Deployment verification script for CodeBuddy.
This script tests both the backend and frontend to ensure they're working correctly.
"""

import requests
import time
import sys

def test_backend(base_url):
    """Test the backend API."""
    print("🔍 Testing Backend API...")
    
    # Test root endpoint
    try:
        response = requests.get(f"{base_url}/", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Backend root endpoint: {data['message']}")
        else:
            print(f"❌ Backend root endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend root endpoint error: {e}")
        return False
    
    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Backend health check: {data['status']}")
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend health check error: {e}")
        return False
    
    return True

def test_database(base_url):
    """Test database operations."""
    print("\n🗄️ Testing Database Operations...")
    
    # Test saving a conversation
    test_data = {
        "conversation_id": "test_deployment_123",
        "messages": [
            {"role": "user", "content": "Test message from deployment verification"},
            {"role": "assistant", "content": "Test response from deployment verification"}
        ],
        "user_id": "deployment_test_user"
    }
    
    try:
        response = requests.post(f"{base_url}/save_conversation", 
                               json=test_data, 
                               timeout=10)
        if response.status_code == 201:
            print("✅ Conversation saved successfully")
        else:
            print(f"❌ Failed to save conversation: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error saving conversation: {e}")
        return False
    
    # Test retrieving conversations
    try:
        response = requests.get(f"{base_url}/get_conversations?user_id=deployment_test_user", 
                              timeout=10)
        if response.status_code == 200:
            conversations = response.json()
            print(f"✅ Retrieved {len(conversations)} conversations")
        else:
            print(f"❌ Failed to get conversations: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error getting conversations: {e}")
        return False
    
    return True

def test_frontend(frontend_url):
    """Test the frontend."""
    print(f"\n🌐 Testing Frontend...")
    
    try:
        response = requests.get(frontend_url, timeout=10)
        if response.status_code == 200:
            print("✅ Frontend is accessible")
            return True
        else:
            print(f"❌ Frontend returned status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Frontend error: {e}")
        return False

def main():
    """Main verification function."""
    print("🚀 CodeBuddy Deployment Verification")
    print("=" * 50)
    
    # Get deployment URL from command line or use default
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    else:
        base_url = "http://localhost:5000"  # Change this to your deployment URL
    
    frontend_url = base_url.replace(":5000", ":8501")
    
    print(f"Backend URL: {base_url}")
    print(f"Frontend URL: {frontend_url}")
    print()
    
    # Test backend
    if not test_backend(base_url):
        print("\n❌ Backend tests failed!")
        sys.exit(1)
    
    # Test database
    if not test_database(base_url):
        print("\n❌ Database tests failed!")
        sys.exit(1)
    
    # Test frontend
    if not test_frontend(frontend_url):
        print("\n❌ Frontend tests failed!")
        sys.exit(1)
    
    print("\n🎉 All tests passed! Your CodeBuddy deployment is working correctly!")
    print("\n📋 Summary:")
    print(f"   • Backend API: {base_url}")
    print(f"   • Frontend: {frontend_url}")
    print(f"   • Database: Connected and functional")
    print("\n🔗 You can now access your application at the frontend URL above.")

if __name__ == "__main__":
    main() 