import requests
import argparse
import os
import google.generativeai as genai
import time
import urllib.request
import base64
import tempfile
import anthropic
import logging
from dotenv import load_dotenv

# Configure logging
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# Clean up any proxy-related environment variables that might interfere
for proxy_var in ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy']:
    if proxy_var in os.environ:
        logger.warning(f"Removing proxy environment variable: {proxy_var}")
        del os.environ[proxy_var]

CUSTOM_SEARCH_API = os.getenv("CUSTOM-SEARCH-API")
SEARCH_ENGINE_ID = os.getenv("SEARCH-ENGINE-ID")
GEMINI_API = os.getenv("GEMINI-API")
CLAUDE_API_KEY = os.getenv("CLAUDE-API-KEY")  # Add your Claude API key to .env file

# Facecheck.id configuration
FACECHECK_TESTING_MODE = False
FACECHECK_APITOKEN = os.getenv("FACECHECK-API-TOKEN")

genai.configure(api_key=GEMINI_API)

def rs(text, num_results=10):
    """
    Perform a Google Custom Search for pages containing the given text.
    """
    if not CUSTOM_SEARCH_API or not SEARCH_ENGINE_ID:
        raise Exception("Google Custom Search API credentials not configured")
    
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": CUSTOM_SEARCH_API,
        "cx": SEARCH_ENGINE_ID,
        "q": f"intext:{text}",
        "num": min(num_results, 10)  # Google API limit
    }
    
    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        if 'error' in data:
            raise Exception(f"Google API Error: {data['error'].get('message', 'Unknown error')}")
        
        results = []
        for item in data.get("items", []):
            results.append({
                "title": item.get("title"),
                "link": item.get("link"),
                "snippet": item.get("snippet")
            })
        
        logger.info(f"Text search completed: {len(results)} results for query '{text[:50]}...'")
        return results
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Google Search API request failed: {str(e)}")
        raise Exception(f"Search request failed: {str(e)}")

import requests
from bs4 import BeautifulSoup

def deep_search(image_data=None, text_query=None, num_text_results=10):
    """
    Perform comprehensive search using both face search and text search,
    then fetch and summarize all resulting pages.
    
    Args:
        image_data: Image data for face search (optional)
        text_query: Text query for regular search (optional)
        num_text_results: Number of text search results to retrieve
    
    Returns:
        Combined summaries from both face search and text search results
    """
    model = genai.GenerativeModel('models/gemini-2.0-flash')
    all_results = []
    
    # 1. Perform face search if image provided
    if image_data:
        try:
            face_results = face_search_formatted(image_data)
            # Add source type to distinguish results
            for result in face_results:
                result['source'] = 'face_search'
                all_results.append(result)
            logger.info(f"Face search found {len(face_results)} results")
        except Exception as e:
            logger.error(f"Face search failed: {e}")
    
    # 2. Perform text search if query provided
    if text_query:
        try:
            text_results = rs(text_query, num_results=num_text_results)
            # Add source type to distinguish results
            for result in text_results:
                result['source'] = 'text_search'
                all_results.append(result)
            logger.info(f"Text search found {len(text_results)} results")
        except Exception as e:
            logger.error(f"Text search failed: {e}")
    
    if not all_results:
        logger.warning("No results found from either search method")
        return {"error": "No results found from either search method"}
    
    # 3. Remove duplicate links
    seen_links = set()
    unique_results = []
    for item in all_results:
        if item['link'] not in seen_links:
            seen_links.add(item['link'])
            unique_results.append(item)
    
    logger.info(f"Processing {len(unique_results)} unique links for deep search...")
    
    # 4. Perform deep search on all unique results
    summaries = []
    for i, item in enumerate(unique_results, 1):
        try:
            logger.info(f"Processing link {i}/{len(unique_results)}: {item['link']}")
            
            # Download the page with better error handling
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            resp = requests.get(item['link'], timeout=15, headers=headers, allow_redirects=True)
            resp.raise_for_status()

            # Extract visible text
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.extract()
            
            text = soup.get_text(separator='\n', strip=True)
            excerpt = '\n'.join(text.splitlines()[:500])  # first ~500 lines to stay under context limit

            if not excerpt.strip():
                raise Exception("No readable content found")

            # Build a targeted prompt
            prompt = (
                "Here is some page content:\n\n"
                f"{excerpt}\n\n"
                "Please write a concise, one-paragraph summary of the above."
            )

            # Generate the summary with error handling
            try:
                response = model.generate_content(prompt)
                summary = response.text.strip() if response.text else "No summary generated"
            except Exception as gemini_error:
                logger.warning(f"Gemini API error for {item['link']}: {gemini_error}")
                summary = "Summary generation failed"

            summaries.append({
                "title": item['title'],
                "link": item['link'],
                "snippet": item.get('snippet', ''),
                "source": item['source'],
                "summary": summary
            })
            
        except Exception as e:
            logger.warning(f"Failed to process {item['link']}: {e}")
            summaries.append({
                "title": item['title'],
                "link": item['link'],
                "snippet": item.get('snippet', ''),
                "source": item['source'],
                "summary": f"Failed to retrieve summary: {str(e)}"
            })

    return {
        "total_results": len(summaries),
        "face_search_count": len([s for s in summaries if s['source'] == 'face_search']),
        "text_search_count": len([s for s in summaries if s['source'] == 'text_search']),
        "summaries": summaries
    }

def search_by_face(image_file_path):
    """
    Perform reverse image search using facecheck.id
    """
    if not FACECHECK_APITOKEN:
        raise Exception("Facecheck API token not configured")
    
    if FACECHECK_TESTING_MODE:
        logger.info('Running in TESTING MODE - results are inaccurate, but credits are NOT deducted')

    site = 'https://facecheck.id'
    headers = {'accept': 'application/json', 'Authorization': FACECHECK_APITOKEN}
    
    try:
        with open(image_file_path, 'rb') as f:
            files = {'images': f, 'id_search': None}
            response = requests.post(site + '/api/upload_pic', headers=headers, files=files, timeout=30).json()

        if response['error']:
            raise Exception(f"{response['error']} ({response['code']})")

        id_search = response['id_search']
        logger.info(f"Face search initiated: {response['message']} id_search={id_search}")
        json_data = {'id_search': id_search, 'with_progress': True, 'status_only': False, 'demo': FACECHECK_TESTING_MODE}

        # Add timeout to prevent infinite loops
        max_attempts = 60  # 60 seconds max
        attempts = 0
        
        while attempts < max_attempts:
            response = requests.post(site + '/api/search', headers=headers, json=json_data, timeout=30).json()
            if response['error']:
                raise Exception(f"{response['error']} ({response['code']})")
            if response['output']:
                logger.info(f"Face search completed: {len(response['output']['items'])} results found")
                return response['output']['items']
            
            logger.info(f"Face search progress: {response['progress']}%")
            time.sleep(1)
            attempts += 1
        
        raise Exception("Face search timed out after 60 seconds")
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Facecheck API request failed: {str(e)}")
        raise Exception(f"Face search request failed: {str(e)}")

def face_search_formatted(image_data, num_results=3):
    """
    Wrapper function for face search that handles image data and formats results
    consistently with the existing API format.
    Returns the top 3 most similar faces sorted by similarity score.
    """
    # Create a temporary file to store the uploaded image
    with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_file:
        temp_file.write(image_data)
        temp_file_path = temp_file.name

    try:
        # Perform the face search
        raw_results = search_by_face(temp_file_path)
        
        # Sort results by similarity score in descending order (highest scores first)
        sorted_results = sorted(raw_results, key=lambda x: x['score'], reverse=True)
        
        # Format results to match existing API structure, taking top 3 most similar
        results = []
        for i, item in enumerate(sorted_results[:3]):  # Always take top 3 most similar
            results.append({
                "title": f"Face Match (Score: {item['score']}%)",
                "link": item['url'],
                "snippet": f"Face similarity score: {item['score']}% - Found on webpage"
            })
        
        return results
        
    finally:
        # Clean up temporary file
        import os
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)

def analyze_with_claude(prompt, summaries_data):
    """
    Analyze the deep search summaries using Claude Sonnet 4 based on user prompt.
    
    Args:
        prompt (str): User's analysis prompt/question
        summaries_data (dict): JSON output from deep_search function
    
    Returns:
        str: Claude's analysis text response
    """
    if not CLAUDE_API_KEY:
        raise Exception("Claude API key not found. Please set CLAUDE-API-KEY in your .env file")
    
    try:
        # Initialize Claude client with explicit parameters only
        client = anthropic.Anthropic(
            api_key=CLAUDE_API_KEY,
            # Don't pass any proxy or other parameters that might cause issues
        )
    except Exception as init_error:
        logger.error(f"Failed to initialize Claude client: {init_error}")
        raise Exception(f"Claude client initialization failed: {str(init_error)}")
    
    # Prepare the context from summaries
    context = ""
    
    for i, result in enumerate(summaries_data.get('summaries', []), 1):
        context += f"""
Result {i} (Source: {result.get('source', 'unknown')}):
- Title: {result.get('title', 'N/A')}
- Link: {result.get('link', 'N/A')}
- Original Snippet: {result.get('snippet', 'N/A')}
- AI Summary: {result.get('summary', 'N/A')}
---
"""
    
    # Create the full prompt for Claude
    full_prompt = f"""
You are an expert analyst reviewing the trustworthiness of a person based on the search results where 0 is most trustworthy and 100 is least trustworthy, rounded to the ones digit. Do not output any other text/letters besides a number.
As for strict guidelines, you must base your output number on the User's Analysis Request based on what the user deems more risky and less risky pieces of information. 

After providing the numerical score, add a colon (:) and then provide a brief explanation (2-3 sentences) of why you assigned this specific risk score based on the evidence found in the search results.

Format your response exactly as: <number>:<explanation>

{context}

User's Analysis Request:
{prompt}
"""
    
    try:
        # Call Claude Sonnet (use Claude 3.5 Sonnet which is more stable)
        response = client.messages.create(
            model="claude-sonnet-4-20250514",  # Claude 3.5 Sonnet (more stable)
            max_tokens=1000,  # Reduced for simple numeric response
            temperature=0.1,  # Low temperature for more focused analysis
            messages=[
                {
                    "role": "user",
                    "content": full_prompt
                }
            ]
        )
        
        # Extract text from response content
        if response.content and len(response.content) > 0:
            result_text = response.content[0].text.strip()
            logger.info(f"Claude analysis completed: {result_text}")
            return result_text
        else:
            raise Exception("Empty response from Claude API")
        
    except Exception as e:
        logger.error(f"Claude API call failed: {str(e)}")
        raise Exception(f"Claude API error: {str(e)}")

def main():
    # testing
    parser = argparse.ArgumentParser(description="Search Google Custom Search for any text.")
    parser.add_argument("text", help="Text to search for.")
    parser.add_argument("--results", type=int, default=10, help="Number of search results to retrieve.")
    args = parser.parse_args()

    rs_json = rs(args.text, num_results=args.results)
    # Uncomment to perform deep search
    summaries = deep_search(rs_json)
    for item in summaries:
        print(f"Title: {item['title']}\nLink: {item['link']}\nSummary: {item['summary']}\n")
    
if __name__ == "__main__":
    main()


