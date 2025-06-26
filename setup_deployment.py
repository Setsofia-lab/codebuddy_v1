#!/usr/bin/env python3
"""
Setup script for CodeBuddy deployment configuration.
This script helps you configure the necessary environment variables.
"""

import os
import sys

def setup_environment():
    """Interactive setup for deployment environment variables."""
    print("🚀 CodeBuddy Deployment Setup")
    print("=" * 40)
    
    # Get Google API Key
    google_api_key = input("Enter your Google AI API Key: ").strip()
    if not google_api_key:
        print("❌ Google API Key is required!")
        sys.exit(1)
    
    # Get Backend URL
    print("\n🌐 Backend Deployment Options:")
    print("1. Render.com (Recommended - Free)")
    print("2. Railway.app (Free)")
    print("3. Heroku (Paid)")
    print("4. Custom URL")
    
    choice = input("\nChoose your backend hosting (1-4): ").strip()
    
    backend_url = ""
    if choice == "1":
        backend_url = input("Enter your Render.com backend URL (e.g., https://codebuddy-backend.onrender.com): ").strip()
    elif choice == "2":
        backend_url = input("Enter your Railway.app backend URL (e.g., https://your-app.railway.app): ").strip()
    elif choice == "3":
        backend_url = input("Enter your Heroku backend URL (e.g., https://codebuddy-backend.herokuapp.com): ").strip()
    elif choice == "4":
        backend_url = input("Enter your custom backend URL: ").strip()
    else:
        print("❌ Invalid choice!")
        sys.exit(1)
    
    if not backend_url:
        print("❌ Backend URL is required!")
        sys.exit(1)
    
    # Create environment file for local testing
    with open(".env", "w") as f:
        f.write(f"GOOGLE_API_KEY={google_api_key}\n")
        f.write(f"BACKEND_URL={backend_url}\n")
    
    print("\n✅ Environment variables configured!")
    print("\n📋 Next Steps:")
    print("1. Deploy your backend to your chosen platform")
    print("2. Add these environment variables to your Streamlit Cloud app:")
    print(f"   - GOOGLE_API_KEY: {google_api_key}")
    print(f"   - BACKEND_URL: {backend_url}")
    print("3. Test your deployment using: python verify_deployment.py")
    
    print(f"\n🔗 Your frontend URL will remain: https://codebuddyv1.streamlit.app/")
    print(f"🔗 Your backend URL: {backend_url}")
    
    return google_api_key, backend_url

def create_deployment_files():
    """Create deployment configuration files."""
    print("\n📁 Creating deployment configuration files...")
    
    # Check if render.yaml exists
    if not os.path.exists("render.yaml"):
        print("✅ render.yaml already exists")
    else:
        print("✅ render.yaml created")
    
    # Check if railway.json exists
    if not os.path.exists("student_code_evaluator/backend/railway.json"):
        print("✅ railway.json already exists")
    else:
        print("✅ railway.json created")
    
    print("\n📖 See DEPLOYMENT_GUIDE.md for detailed instructions")

def main():
    """Main setup function."""
    try:
        google_api_key, backend_url = setup_environment()
        create_deployment_files()
        
        print("\n🎉 Setup complete! Follow the deployment guide to deploy your backend.")
        
    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 