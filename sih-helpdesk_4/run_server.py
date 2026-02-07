"""
Production Server Launcher for SIH Helpdesk
Uses Waitress WSGI server - no console encoding issues!
"""
import os
import sys

# Suppress all console output to avoid Unicode errors
os.environ['PYTHONIOENCODING'] = 'utf-8'

# Import the Flask app
from app import app, setup_database

if __name__ == "__main__":
    # Initialize database
    setup_database()
    
    print("=" * 50)
    print("SIH Helpdesk Server Starting...")
    print("=" * 50)
    print("Server: http://127.0.0.1:5000")
    print("Press CTRL+C to stop")
    print("=" * 50)
    
    # Use Waitress (production WSGI server)
    from waitress import serve
    serve(app, host='127.0.0.1', port=5000, threads=4)
