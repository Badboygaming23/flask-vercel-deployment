"""
Script to run the Flask application.
"""

if __name__ == "__main__":
    try:
        from flask_app import app
        print("Starting Flask application...")
        print("Access the application at: http://localhost:5000")
        app.run(host='0.0.0.0', port=5000, debug=True)
    except Exception as e:
        print(f"Error starting Flask application: {e}")