import os
import sys
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import logging

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import our modules
from config import Config
from supabase_client import get_supabase_client
from utils.mailer import send_otp_email, send_password_reset_email
from utils.supabase_storage import upload_file_to_supabase, delete_file_from_supabase
from middleware.auth import authenticate_token

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Enable CORS
CORS(app, supports_credentials=True)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Supabase client
supabase = get_supabase_client()

# Serve static files from the frontend directory
@app.route('/')
def index():
    return send_from_directory('../frontend', 'index.html')

@app.route('/dashboard')
def dashboard():
    return send_from_directory('../frontend', 'dashboard.html')

# Serve images from the frontend/images directory
@app.route('/images/<path:filename>')
def images(filename):
    return send_from_directory('../frontend/images', filename)

# Import and register blueprints
from routes import auth_bp, user_bp, account_bp, item_bp
app.register_blueprint(auth_bp)
app.register_blueprint(user_bp)
app.register_blueprint(account_bp)
app.register_blueprint(item_bp)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)