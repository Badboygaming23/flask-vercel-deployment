import jwt
import logging
from functools import wraps
from flask import request, jsonify
from config import Config
from supabase_client import supabase

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def authenticate_token(f):
    """
    Middleware to authenticate JWT tokens.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            auth_header = request.headers.get('Authorization')
            token = None
            
            if auth_header:
                parts = auth_header.split(' ')
                if len(parts) == 2 and parts[0] == 'Bearer':
                    token = parts[1]
            
            logger.info(f"authenticateToken: Incoming request to: {request.path}")
            logger.info(f"authenticateToken: Incoming token: {token[:10] + '...' if token else 'No token'}")
            
            if not token:
                logger.info(f"authenticateToken: No token provided for request to: {request.path}")
                return jsonify({'success': False, 'message': 'Access token required.'}), 401
            
            try:
                # Decode the JWT token
                user = jwt.decode(token, Config.JWT_SECRET, algorithms=['HS256'])
                logger.info(f"authenticateToken: JWT verified for user: {user.get('email')}, ID: {user.get('id')}")
                
                # Verify token exists in database
                response = supabase.table('users').select('id, email').eq('id', user['id']).eq('token', token).execute()
                
                if response.error:
                    logger.error(f"authenticateToken: DB Error during token validation for request to: {request.path}, Error: {response.error}")
                    return jsonify({'success': False, 'message': 'An error occurred during token validation.'}), 500
                
                users = response.data
                
                if not users or len(users) == 0:
                    logger.info(f"authenticateToken: Token not found in DB or revoked for user: {user.get('email')}, ID: {user.get('id')}, Request to: {request.path}")
                    return jsonify({'success': False, 'message': 'Invalid token. Please log in again.'}), 403
                
                stored_user = users[0]
                # Add user info to request context
                request.user = {'id': stored_user['id'], 'email': stored_user['email']}
                logger.info(f"authenticateToken: Token successfully validated in DB for user: {request.user['email']}, Request to: {request.path}")
                
                # Call the original function with user info
                return f(*args, **kwargs)
                
            except jwt.ExpiredSignatureError:
                logger.error(f"authenticateToken: JWT expired for request to: {request.path}")
                return jsonify({'success': False, 'message': 'Token has expired. Please log in again.'}), 403
            except jwt.InvalidTokenError:
                logger.error(f"authenticateToken: JWT invalid for request to: {request.path}")
                return jsonify({'success': False, 'message': 'Invalid token. Please log in again.'}), 403
                
        except Exception as err:
            logger.error(f"authenticateToken: Unexpected error for request to: {request.path}, Error: {str(err)}")
            return jsonify({'success': False, 'message': 'An unexpected error occurred during authentication.'}), 500
    
    return decorated_function