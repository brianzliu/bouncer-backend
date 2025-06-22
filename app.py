import os
import logging
from flask import Flask, jsonify, request, Response, stream_with_context
from flask_cors import CORS
from dotenv import load_dotenv

from utils.background_check import rs, face_search_formatted, deep_search, analyze_with_claude

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Production configuration
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file upload

def check_environment():
    """Check that required environment variables are set"""
    required_vars = [
        'CUSTOM-SEARCH-API',
        'SEARCH-ENGINE-ID', 
        'GEMINI-API',
        'CLAUDE-API-KEY',
        'FACECHECK-API-TOKEN'
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        logger.error(f"Missing environment variables: {', '.join(missing_vars)}")
        # Don't crash in production, just log the error
    else:
        logger.info("All required environment variables are set")

# Check environment on startup
check_environment()

@app.route('/')
def home():
    """Health check endpoint"""
    return jsonify({
        "message": "Bouncer API - Person Intelligence Service",
        "status": "healthy",
        "version": "1.0.0"
    })

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for load balancers"""
    return jsonify({"status": "healthy"}), 200

@app.route('/rs', methods=['POST'])
def rs_query():
    """Text-based reverse search endpoint"""
    try:
        # Parse & validate JSON body
        payload = request.get_json(silent=True)
        if not payload or "text" not in payload:
            return jsonify({"error": "Request JSON must include 'text'"}), 400

        text = payload["text"]
        num_results = payload.get("num_results", 10)
        
        # Validate input
        if not text.strip():
            return jsonify({"error": "Text query cannot be empty"}), 400
        
        if num_results > 20:  # Rate limiting
            num_results = 20

        logger.info(f"Text search request: '{text[:50]}...' ({num_results} results)")
        
        # Call search function
        results = rs(text, num_results=num_results)
        
        logger.info(f"Text search completed: {len(results)} results found")
        return jsonify({"results": results}), 200

    except Exception as e:
        logger.error(f"Text search error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/face-search', methods=['POST'])
def face_search_query():
    """Face-based reverse search endpoint"""
    try:
        # Check if an image file was uploaded
        if 'image' not in request.files:
            return jsonify({"error": "Request must include an image file with key 'image'"}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({"error": "No image file selected"}), 400
        
        # Check file type
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}
        if not ('.' in file.filename and file.filename.rsplit('.', 1)[1].lower() in allowed_extensions):
            return jsonify({"error": "Invalid file type. Supported formats: png, jpg, jpeg, gif, bmp, webp"}), 400
        
        logger.info(f"Face search request: {file.filename}")
        
        # Read the image data
        image_data = file.read()
        
        # Validate file size (already handled by MAX_CONTENT_LENGTH, but good to check)
        if len(image_data) == 0:
            return jsonify({"error": "Empty image file"}), 400
        
        # Perform face search
        results = face_search_formatted(image_data)
        
        logger.info(f"Face search completed: {len(results)} results found")
        return jsonify({"results": results}), 200
        
    except Exception as e:
        logger.error(f"Face search error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/deep-search', methods=['POST'])
def deep_search_endpoint():
    """
    Comprehensive search endpoint that combines face search and text search,
    then provides detailed summaries of all found pages.
    """
    try:
        # Get text query if provided
        text_query = request.form.get('text', '').strip()
        
        # Get image data if provided
        image_data = None
        if 'image' in request.files:
            file = request.files['image']
            if file.filename != '':
                # Check file type
                allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}
                if '.' in file.filename and file.filename.rsplit('.', 1)[1].lower() in allowed_extensions:
                    image_data = file.read()
                    if len(image_data) == 0:
                        return jsonify({"error": "Empty image file"}), 400
                else:
                    return jsonify({"error": "Invalid image file type. Supported formats: png, jpg, jpeg, gif, bmp, webp"}), 400
        
        # Validate that at least one search method is provided
        if not text_query and not image_data:
            return jsonify({"error": "Must provide either 'text' query or 'image' file (or both)"}), 400
        
        # Get optional parameters
        num_text_results = request.form.get('num_text_results', 10, type=int)
        if num_text_results > 20:  # Rate limiting
            num_text_results = 20
        
        logger.info(f"Deep search request: text='{text_query[:50] if text_query else 'None'}...', image={'Yes' if image_data else 'No'}")
        
        # Perform comprehensive deep search
        results = deep_search(
            image_data=image_data,
            text_query=text_query if text_query else None,
            num_text_results=num_text_results
        )
        
        logger.info(f"Deep search completed: {results.get('total_results', 0)} results processed")
        return jsonify(results), 200
        
    except Exception as e:
        logger.error(f"Deep search error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/analyze-summaries', methods=['POST'])
def analyze_summaries_endpoint():
    """
    Comprehensive analysis endpoint that performs deep search and Claude analysis in one call.
    """
    try:
        # Get prompt from form data
        prompt = request.form.get('prompt', '').strip()
        if not prompt:
            return jsonify({"error": "Request must include 'prompt' field"}), 400
        
        # Get text query if provided
        text_query = request.form.get('text', '').strip()
        
        # Get image data if provided
        image_data = None
        if 'image' in request.files:
            file = request.files['image']
            if file.filename != '':
                # Check file type
                allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}
                if '.' in file.filename and file.filename.rsplit('.', 1)[1].lower() in allowed_extensions:
                    image_data = file.read()
                    if len(image_data) == 0:
                        return jsonify({"error": "Empty image file"}), 400
                else:
                    return jsonify({"error": "Invalid image file type. Supported formats: png, jpg, jpeg, gif, bmp, webp"}), 400
        
        # Validate that at least one search method is provided
        if not text_query and not image_data:
            return jsonify({"error": "Must provide either 'text' query or 'image' file (or both)"}), 400
        
        # Get optional parameters
        num_text_results = request.form.get('num_text_results', 10, type=int)
        if num_text_results > 20:  # Rate limiting
            num_text_results = 20
        
        logger.info(f"Analysis request: prompt='{prompt[:50]}...', text='{text_query[:50] if text_query else 'None'}...', image={'Yes' if image_data else 'No'}")
        
        # Step 1: Perform deep search
        summaries_data = deep_search(
            image_data=image_data,
            text_query=text_query if text_query else None,
            num_text_results=num_text_results
        )
        
        # Check if deep search found results
        if "error" in summaries_data:
            return jsonify(summaries_data), 404
        
        # Step 2: Analyze with Claude
        analysis = analyze_with_claude(prompt, summaries_data)
        
        logger.info("Analysis completed successfully")
        
        # Format response as: score:explanation:raw_json_summaries
        import json
        raw_summaries_json = json.dumps(summaries_data, separators=(',', ':'))
        formatted_response = f"{analysis}:{raw_summaries_json}"
        
        # Return the formatted response with score, explanation, and raw JSON
        return formatted_response, 200, {'Content-Type': 'text/plain'}
        
    except Exception as e:
        logger.error(f"Analysis error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.errorhandler(413)
def too_large(e):
    """Handle file too large error"""
    return jsonify({"error": "File too large. Maximum size is 16MB"}), 413

@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors"""
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(e):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {str(e)}")
    return jsonify({"error": "Internal server error"}), 500

# Only run with debug in development
if __name__ == '__main__':
    # This will only run in development
    port = int(os.environ.get('PORT', 5001))
    debug = os.environ.get('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)