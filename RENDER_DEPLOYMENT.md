# Deploy Bouncer Backend on Render

## Quick Setup

1. **Fork/Clone this repository**

2. **Create a new Web Service on Render:**
   - Go to [Render Dashboard](https://dashboard.render.com)
   - Click "New" → "Web Service"
   - Connect your GitHub repository

3. **Configure the deployment:**
   - **Language:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
   - **Environment:** Production

## Environment Variables

Set these environment variables in your Render service settings:

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

# Flask Environment
FLASK_ENV=production
```

## Getting API Keys

### Google Custom Search API
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Enable the Custom Search API
3. Create credentials (API Key)
4. Create a Custom Search Engine at [cse.google.com](https://cse.google.com)

### Google Gemini API
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create an API key

### Claude API
1. Go to [Anthropic Console](https://console.anthropic.com/)
2. Create an API key

### Facecheck.id API
1. Sign up at [facecheck.id](https://facecheck.id)
2. Get your API token from the dashboard

## API Endpoints

- `GET /` - Health check
- `GET /health` - Health check for load balancers
- `POST /rs` - Text-based reverse search
- `POST /face-search` - Face-based reverse search
- `POST /deep-search` - Comprehensive search (text + face)
- `POST /analyze-summaries` - AI analysis of search results

## Production Features

✅ **Gunicorn WSGI server** for production performance  
✅ **Structured logging** for debugging  
✅ **Environment variable validation**  
✅ **Rate limiting** (20 results max per request)  
✅ **File upload limits** (16MB max)  
✅ **Comprehensive error handling**  
✅ **Request timeouts** and retry logic  
✅ **Security headers** and CORS configuration  

## Deployment Commands

These are handled automatically by Render:

```bash
# Build
pip install -r requirements.txt

# Start
gunicorn app:app
```

## Health Checks

The service includes health check endpoints that Render can use:
- `GET /health` returns `{"status": "healthy"}`

## Troubleshooting

1. **Check environment variables** are set correctly
2. **Monitor logs** in Render dashboard for errors
3. **Verify API keys** are valid and have proper permissions
4. **Check rate limits** on external APIs

## Scaling

Render will automatically scale your service based on traffic. The app is optimized for:
- Multiple concurrent requests
- Efficient memory usage
- Fast response times
- Graceful error handling

Your service will be available at: `https://your-service-name.onrender.com` 