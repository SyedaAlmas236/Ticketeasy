"""
Smart Helpdesk REST API - Main Application
Production-ready Flask API with CORS and error handling
"""
import os
import sys
import io

# Force UTF-8 for Windows console
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

from flask import Flask, jsonify
from flask_cors import CORS
from api_models import db
from api_routes import api_bp

# Create Flask app
app = Flask(__name__)

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///api_helpdesk.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JSON_SORT_KEYS'] = False

# Initialize extensions
db.init_app(app)
CORS(app)  # Enable CORS for all routes

# Register blueprints
app.register_blueprint(api_bp)

# Root endpoint
@app.route('/')
def index():
    return jsonify({
        'service': 'Smart Helpdesk REST API',
        'version': '1.0.0',
        'status': 'running',
        'endpoints': {
            'create_ticket': 'POST /api/tickets',
            'get_ticket': 'GET /api/tickets/{ticket_id}',
            'list_tickets': 'GET /api/tickets',
            'update_ticket': 'PATCH /api/tickets/{ticket_id}',
            'health': 'GET /api/health'
        },
        'documentation': 'See API_README.md for Postman examples'
    }), 200

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'error': 'Resource not found',
        'status': 'error'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'error': 'Internal server error',
        'status': 'error'
    }), 500

# Initialize database
def init_db():
    with app.app_context():
        db.create_all()
        print("✓ Database initialized successfully")

if __name__ == '__main__':
    # Create database tables
    init_db()
    
    print("=" * 60)
    print("Smart Helpdesk REST API Server")
    print("=" * 60)
    print("Server: http://127.0.0.1:8000")
    print("API Docs: http://127.0.0.1:8000/")
    print("Test in Postman: POST http://127.0.0.1:8000/api/tickets")
    print("=" * 60)
    
    # Use Waitress for production
    try:
        from waitress import serve
        serve(app, host='0.0.0.0', port=8000, threads=4)
    except ImportError:
        print("Install waitress: pip install waitress")
        app.run(host='0.0.0.0', port=8000, debug=False)
