# 🚀 Quick Start Guide

Get the Bouncer Backend up and running in 5 minutes!

## ⚡ Super Quick Setup

### 1. Install Python Dependencies
```bash
pip install flask flask-cors requests python-dotenv google-generativeai beautifulsoup4 anthropic
```

### 2. Start the Server
```bash
python start_server.py
```

The script will:
- ✅ Check and install missing dependencies
- 📝 Create a sample `.env` file if needed
- 🚀 Start the server on `http://localhost:5001`

### 3. Test the Server
Open your browser and go to: `http://localhost:5001`

You should see: `{"message": "Welcome to the Bouncer API"}`

## 🔑 API Keys Setup

Edit the `.env` file that was created with your actual API keys:

```bash
# Required for basic functionality
CUSTOM-SEARCH-API=your_google_api_key
SEARCH-ENGINE-ID=your_search_engine_id
GEMINI-API=your_gemini_key

# Optional for advanced features
CLAUDE-API-KEY=your_claude_key
FACECHECK-API-TOKEN=your_facecheck_token
```

### Quick API Key Links:
- **Google Search**: [console.cloud.google.com](https://console.cloud.google.com/)
- **Gemini**: [aistudio.google.com](https://aistudio.google.com/)
- **Claude**: [console.anthropic.com](https://console.anthropic.com/)
- **Facecheck**: [facecheck.id](https://facecheck.id/)

## 🧪 Quick Test

### Test Text Search:
```bash
curl -X POST http://localhost:5001/rs \
  -H "Content-Type: application/json" \
  -d '{"text": "test search"}'
```

### Test with Image:
```bash
python test_face_search.py your_image.jpg
```

## 📚 Full Documentation

See `README.md` for complete documentation and advanced usage.

## 🆘 Quick Troubleshooting

**Server won't start?**
- Check Python version (3.7+)
- Run: `pip install --upgrade pip`

**API errors?**
- Verify API keys in `.env` file
- Check API quotas and billing

**Port conflicts?**
- Server uses port 5001 (not 5000) to avoid macOS conflicts

## 🎯 What's Next?

1. Set up your API keys in `.env`
2. Test the endpoints with the test scripts
3. Build your application using the API
4. Check `README.md` for detailed documentation 