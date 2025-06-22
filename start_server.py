#!/usr/bin/env python3
"""
Bouncer Backend Startup Script
Checks dependencies and starts the Flask server
"""

import os
import sys
import subprocess

def check_dependencies():
    """Check if all required packages are installed"""
    print("🔍 Checking dependencies...")
    
    required_packages = [
        'flask', 'flask_cors', 'requests', 'python-dotenv', 
        'google-generativeai', 'beautifulsoup4', 'anthropic'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing packages: {', '.join(missing_packages)}")
        print("📦 Installing missing packages...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + missing_packages)
        print("✅ Dependencies installed!")
    else:
        print("✅ All dependencies are installed!")

def check_env_file():
    """Check if .env file exists and has required keys"""
    print("\n🔑 Checking environment configuration...")
    
    env_path = '.env'
    if not os.path.exists(env_path):
        print("⚠️  .env file not found!")
        print("📝 Creating sample .env file...")
        
        sample_env = """# Google Custom Search API
CUSTOM-SEARCH-API=your_google_custom_search_api_key
SEARCH-ENGINE-ID=your_google_search_engine_id

# Google Gemini API (for page summaries)
GEMINI-API=your_gemini_api_key

# Claude API (for trustworthiness analysis)
CLAUDE-API-KEY=your_claude_api_key

# Facecheck.id API
FACECHECK-API-TOKEN=your_facecheck_api_token
"""
        
        with open(env_path, 'w') as f:
            f.write(sample_env)
        
        print("✅ Sample .env file created!")
        print("🔧 Please edit .env file with your actual API keys before using the server.")
        return False
    else:
        print("✅ .env file found!")
        return True

def start_server():
    """Start the Flask server"""
    print("\n🚀 Starting Bouncer Backend Server...")
    print("📍 Server will be available at: http://localhost:5001")
    print("🛑 Press Ctrl+C to stop the server")
    print("-" * 50)
    
    try:
        from app import app
        app.run(host='0.0.0.0', port=5001, debug=True)
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Server error: {e}")
        print("💡 Check your .env file and API keys")

def main():
    print("=" * 60)
    print("🎯 BOUNCER BACKEND - PERSON INTELLIGENCE API")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not os.path.exists('app.py'):
        print("❌ app.py not found! Please run this script from the backend directory.")
        sys.exit(1)
    
    # Check dependencies
    check_dependencies()
    
    # Check environment file
    env_ready = check_env_file()
    
    if not env_ready:
        print("\n⚠️  Please configure your API keys in .env file before starting the server.")
        print("📖 See README.md for detailed setup instructions.")
        return
    
    # Start server
    start_server()

if __name__ == "__main__":
    main() 