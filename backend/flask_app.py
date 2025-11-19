import os
import sys
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import logging

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import our modules
from config import Config

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Enable CORS with specific configuration for our use case
CORS(app, 
     origins=[
         "http://127.0.0.1:5500",
         "http://localhost:5500",
         "https://flask-vercel-deployment-ten.vercel.app"
     ],
     supports_credentials=True,
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
     allow_headers=["Content-Type", "Authorization", "X-Requested-With"])

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import Supabase client after app initialization
try:
    from supabase_client import get_supabase_client
    supabase = get_supabase_client()
except Exception as e:
    logger.error(f"Failed to initialize Supabase client: {str(e)}")
    supabase = None

# Handle CORS preflight requests
@app.before_request
def handle_preflight():
    if request.method == "OPTIONS":
        response = jsonify()
        origin = request.headers.get('Origin', '')
        allowed_origins = [
            'http://127.0.0.1:5500',
            'http://localhost:5500',
            'https://flask-vercel-deployment-ten.vercel.app'
        ]
        
        if origin in allowed_origins:
            response.headers.add("Access-Control-Allow-Origin", origin)
        else:
            response.headers.add("Access-Control-Allow-Origin", "*")
            
        response.headers.add('Access-Control-Allow-Headers', "Content-Type,Authorization,X-Requested-With")
        response.headers.add('Access-Control-Allow-Methods', "GET, POST, PUT, DELETE, OPTIONS")
        response.headers.add('Access-Control-Allow-Credentials', "true")
        return response

# Add after_request handler to ensure CORS headers are added to all responses
@app.after_request
def after_request(response):
    origin = request.headers.get('Origin', '')
    allowed_origins = [
        'http://127.0.0.1:5500',
        'http://localhost:5500',
        'https://flask-vercel-deployment-ten.vercel.app'
    ]
    
    if origin in allowed_origins:
        response.headers.add("Access-Control-Allow-Origin", origin)
    # Don't add the header if it's already present to avoid duplicates
    elif "Access-Control-Allow-Origin" not in response.headers:
        response.headers.add("Access-Control-Allow-Origin", "*")
        
    response.headers.add('Access-Control-Allow-Credentials', "true")
    return response

# Serve static files from the frontend directory
@app.route('/')
def index():
    return send_from_directory('../frontend', 'index.html')

@app.route('/dashboard')
def dashboard():
    return send_from_directory('../frontend', 'dashboard.html')

# Serve all frontend static files
@app.route('/<path:filename>')
def frontend_files(filename):
    try:
        return send_from_directory('../frontend', filename)
    except FileNotFoundError:
        # If file not found, return 404
        return jsonify({'success': False, 'message': 'File not found'}), 404

# Serve images from the frontend/images directory
@app.route('/images/<path:filename>')
def images(filename):
    try:
        return send_from_directory('../frontend/images', filename)
    except FileNotFoundError:
        # If file not found, return 404
        return jsonify({'success': False, 'message': 'Image not found'}), 404

# Import and register blueprints after app initialization
try:
    from routes import auth_bp, user_bp, account_bp, item_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(account_bp)
    app.register_blueprint(item_bp)
except Exception as e:
    logger.error(f"Failed to import and register blueprints: {str(e)}")

# For Vercel serverless deployment
if __name__ != '__main__':
    app.logger.setLevel(logging.INFO)