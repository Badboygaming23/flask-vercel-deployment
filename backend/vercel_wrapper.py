import os
import sys
import json
import io

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def handler(event, context):
    try:
        # Import the Flask app inside the handler to avoid initialization issues
        from flask_app import app
        
        # Convert Vercel event to WSGI environ
        environ = create_wsgi_environ(event, context)
        
        # Process the request through Flask using the WSGI interface
        from werkzeug.wrappers import Response
        response = Response.from_app(app, environ)
        
        # Ensure CORS headers are properly set
        headers = dict(response.headers)
        
        # Add CORS headers if they're not already present
        origin = environ.get('HTTP_ORIGIN', '')
        allowed_origins = [
            'http://127.0.0.1:5500',
            'http://localhost:5500',
            'https://flask-vercel-deployment-ten.vercel.app'
        ]
        
        if 'Access-Control-Allow-Origin' not in headers:
            if origin in allowed_origins:
                headers['Access-Control-Allow-Origin'] = origin
            else:
                headers['Access-Control-Allow-Origin'] = '*'
            
        # Add other necessary CORS headers
        if 'Access-Control-Allow-Methods' not in headers:
            headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
            
        if 'Access-Control-Allow-Headers' not in headers:
            headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With'
            
        if 'Access-Control-Allow-Credentials' not in headers:
            headers['Access-Control-Allow-Credentials'] = 'true'

        # Convert Flask response to Vercel format
        return {
            'statusCode': response.status_code,
            'headers': headers,
            'body': response.get_data(as_text=True)
        }
    except Exception as e:
        # Log the error for debugging
        print(f"Vercel handler error: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Return a simple error response with CORS headers
        try:
            origin = ''
            if isinstance(event, dict) and 'headers' in event and isinstance(event['headers'], dict):
                origin = event['headers'].get('origin', '')
            
            allowed_origins = [
                'http://127.0.0.1:5500',
                'http://localhost:5500',
                'https://flask-vercel-deployment-ten.vercel.app'
            ]
            
            cors_origin = '*'
            if origin in allowed_origins:
                cors_origin = origin
                
            return {
                'statusCode': 500,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': cors_origin,
                    'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
                    'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Requested-With',
                    'Access-Control-Allow-Credentials': 'true'
                },
                'body': json.dumps({
                    'error': 'Internal Server Error',
                    'message': 'An unexpected error occurred'
                })
            }
        except Exception as inner_e:
            # If we can't even create an error response, return a minimal one
            return {
                'statusCode': 500,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
                    'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Requested-With',
                    'Access-Control-Allow-Credentials': 'true'
                },
                'body': json.dumps({
                    'error': 'Internal Server Error',
                    'message': 'An unexpected error occurred'
                })
            }

def create_wsgi_environ(event, context):
    """Create a WSGI environ dict from Vercel event"""
    try:
        # Get request data
        method = event.get('method', 'GET') if isinstance(event, dict) else 'GET'
        path = event.get('path', '/') if isinstance(event, dict) else '/'
        query_string = event.get('queryString', '') if isinstance(event, dict) else ''
        headers = event.get('headers', {}) if isinstance(event, dict) else {}
        body = event.get('body', '') if isinstance(event, dict) else ''
        
        # Create environ dict
        environ = {
            'REQUEST_METHOD': method,
            'PATH_INFO': path,
            'QUERY_STRING': query_string,
            'CONTENT_TYPE': headers.get('content-type', ''),
            'CONTENT_LENGTH': str(len(body.encode()) if isinstance(body, str) else len(body)),
            'SERVER_NAME': 'localhost',
            'SERVER_PORT': '80',
            'SERVER_PROTOCOL': 'HTTP/1.1',
            'wsgi.version': (1, 0),
            'wsgi.url_scheme': 'http',
            'wsgi.input': io.BytesIO(body.encode() if isinstance(body, str) else body),
            'wsgi.errors': sys.stderr,
            'wsgi.multithread': False,
            'wsgi.multiprocess': False,
            'wsgi.run_once': True,
            'wsgi.async': False,
        }
        
        # Add HTTP headers
        for key, value in headers.items():
            environ[f'HTTP_{key.upper().replace("-", "_")}'] = value
        
        return environ
    except Exception as e:
        print(f"Error creating WSGI environ: {str(e)}")
        import traceback
        traceback.print_exc()
        # Return a minimal environ dict
        return {
            'REQUEST_METHOD': 'GET',
            'PATH_INFO': '/',
            'QUERY_STRING': '',
            'CONTENT_TYPE': '',
            'CONTENT_LENGTH': '0',
            'SERVER_NAME': 'localhost',
            'SERVER_PORT': '80',
            'SERVER_PROTOCOL': 'HTTP/1.1',
            'wsgi.version': (1, 0),
            'wsgi.url_scheme': 'http',
            'wsgi.input': io.BytesIO(b''),
            'wsgi.errors': sys.stderr,
            'wsgi.multithread': False,
            'wsgi.multiprocess': False,
            'wsgi.run_once': True,
            'wsgi.async': False,
        }