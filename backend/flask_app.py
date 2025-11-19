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

# Enable CORS
CORS(app)

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
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add('Access-Control-Allow-Headers', "Content-Type,Authorization,X-Requested-With")
        response.headers.add('Access-Control-Allow-Methods', "GET, POST, PUT, DELETE, OPTIONS")
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

# Health check endpoint
@app.route('/health')
def health_check():
    return jsonify({'status': 'ok', 'message': 'Backend is running properly'})

# For Vercel serverless deployment
if __name__ != '__main__':
    app.logger.setLevel(logging.INFO)