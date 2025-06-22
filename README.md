# Bouncer Backend - Person Intelligence API

A comprehensive Flask API for person intelligence gathering using facial recognition, text search, and AI analysis.

## 🚀 Features

- **Facial Recognition Search**: Uses facecheck.id to find similar faces across the web
- **Text-based Search**: Google Custom Search integration for email/text queries  
- **Deep Search**: Combines both search methods and summarizes all found pages
- **AI Analysis**: Claude Sonnet 4 trustworthiness scoring based on search results
- **Multiple Endpoints**: Individual APIs for each function plus comprehensive analysis

## 📋 API Endpoints

| Endpoint | Method | Description |
|----------|---------|-------------|
| `/` | GET | Health check - Welcome message |
| `/health` | GET | Server health status |
| `/rs` | POST | Text-based search (JSON body: `{"text": "query"}`) |
| `/face-search` | POST | Face search (form-data: `image` file) |
| `/deep-search` | POST | Combined search (form-data: `text`, `image`) |
| `/analyze-summaries` | POST | Claude AI analysis (JSON body: `{"prompt": "...", "summaries_data": {...}}`) |

## 🛠️ Setup Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Environment Configuration
Create a `.env` file in the backend directory:

```bash
# Google Custom Search API
CUSTOM-SEARCH-API=your_google_custom_search_api_key
SEARCH-ENGINE-ID=your_google_search_engine_id

# Google Gemini API (for page summaries)
GEMINI-API=your_gemini_api_key

# Claude API (for trustworthiness analysis)
CLAUDE-API-KEY=your_claude_api_key

# Facecheck.id API
FACECHECK-API-TOKEN=your_facecheck_api_token
```

### 3. Get API Keys

#### Google Custom Search:
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Enable Custom Search API
3. Create credentials and get API key
4. Set up a Custom Search Engine at [cse.google.com](https://cse.google.com/)

#### Google Gemini:
1. Visit [Google AI Studio](https://aistudio.google.com/)
2. Get your API key

#### Claude (Anthropic):
1. Sign up at [Anthropic Console](https://console.anthropic.com/)
2. Create an API key

#### Facecheck.id:
1. Register at [facecheck.id](https://facecheck.id/)
2. Get your API token

### 4. Run the Server
```bash
python app.py
```

Server will start on `http://localhost:5001`

## 🧪 Testing

### Test Individual Endpoints:

**Face Search:**
```bash
python test_face_search.py image.jpg
```

**Deep Search:**
```bash
python test_deep_search.py --text "john.doe@email.com"
python test_deep_search.py --image person.jpg
python test_deep_search.py --text "john.doe@email.com" --image person.jpg
```

**Claude Analysis:**
```bash
python test_claude_analysis.py --text "john.doe@email.com"
```

### Example API Usage:

**Text Search:**
```bash
curl -X POST http://localhost:5001/rs \
  -H "Content-Type: application/json" \
  -d '{"text": "john.doe@email.com"}'
```

**Face Search:**
```bash
curl -X POST http://localhost:5001/face-search \
  -F "image=@person.jpg"
```

**Deep Search:**
```bash
curl -X POST http://localhost:5001/deep-search \
  -F "text=john.doe@email.com" \
  -F "image=@person.jpg"
```

## 📊 Response Formats

### Text Search (`/rs`):
```json
{
  "results": [
    {
      "title": "Page Title",
      "link": "https://example.com",
      "snippet": "Page excerpt..."
    }
  ]
}
```

### Face Search (`/face-search`):
```json
{
  "results": [
    {
      "title": "Face Match (Score: 95%)",
      "link": "https://example.com",
      "snippet": "Face similarity score: 95% - Found on webpage"
    }
  ]
}
```

### Deep Search (`/deep-search`):
```json
{
  "total_results": 8,
  "face_search_count": 3,
  "text_search_count": 5,
  "summaries": [
    {
      "title": "Page Title",
      "link": "https://example.com",
      "snippet": "Original snippet",
      "source": "face_search|text_search",
      "summary": "AI-generated summary of page content"
    }
  ]
}
```

### Claude Analysis (`/analyze-summaries`):
Returns plain text with a floating point number (0.00-1.00) representing trustworthiness score.

## 🔒 Security Notes

- Keep all API keys in `.env` file (never commit to version control)
- Facecheck.id is currently in testing mode (no credits deducted, but less accurate)
- Set `FACECHECK_TESTING_MODE = False` in `utils/background_check.py` for production

## 🐛 Troubleshooting

**Port 5000 conflicts (macOS):**
- App runs on port 5001 to avoid Apple AirPlay conflicts

**API Key errors:**
- Verify all keys are correctly set in `.env`
- Check API quotas and billing

**Face search issues:**
- Ensure image formats are supported (jpg, png, gif, etc.)
- Check facecheck.id API status

**Deep search timeouts:**
- Some pages may fail to load (handled gracefully)
- Large result sets may take several minutes

## 📁 File Structure

```
backend/
├── app.py                    # Main Flask application
├── utils/
│   └── background_check.py   # Core search functions
├── requirements.txt          # Python dependencies
├── .env                      # Environment variables (create this)
├── test_face_search.py       # Face search testing
├── test_deep_search.py       # Deep search testing
├── test_claude_analysis.py   # Claude analysis testing
└── README.md                 # This file
```

## 💡 Usage Tips

1. **Start with face search** to test facecheck.id integration
2. **Use deep search** for comprehensive intelligence gathering  
3. **Apply Claude analysis** with specific risk assessment prompts
4. **Combine all methods** for complete person profiling

## 🤝 Support

For issues or questions, check the test scripts for examples and verify your API keys are configured correctly.
