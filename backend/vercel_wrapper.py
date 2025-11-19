"""
Vercel wrapper for Flask application.
This file allows the Flask app to run on Vercel serverless functions.
"""

import os
import sys
from flask_app import app

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the Flask app
from flask_app import app

# Vercel requires a 'handler' function
def handler(request, context):
    # Import Vercel's WSGI adapter
    from werkzeug.wrappers import Response
    from werkzeug.urls import url_parse
    
    # Create a WSGI environment from the request
    environ = {
        'REQUEST_METHOD': request.method,
        'PATH_INFO': request.path,
        'QUERY_STRING': request.query_string.decode('utf-8') if request.query_string else '',
        'CONTENT_TYPE': request.headers.get('Content-Type', ''),
        'CONTENT_LENGTH': str(len(request.body)) if request.body else '0',
        'SERVER_NAME': 'localhost',
        'SERVER_PORT': '80',
        'SERVER_PROTOCOL': 'HTTP/1.1',
        'wsgi.version': (1, 0),
        'wsgi.url_scheme': 'http',
        'wsgi.input': request.body if request.body else b'',
        'wsgi.errors': sys.stderr,
        'wsgi.multithread': False,
        'wsgi.multiprocess': False,
        'wsgi.run_once': False,
        'wsgi.async': False,
    }
    
    # Add headers
    for header_name, header_value in request.headers.items():
        environ[f'HTTP_{header_name.upper().replace("-", "_")}'] = header_value
    
    # Create a response
    response = Response.from_app(app, environ)
    
    # Return the response in Vercel format
    return {
        'statusCode': response.status_code,
        'headers': dict(response.headers),
        'body': response.get_data(as_text=True)
    }