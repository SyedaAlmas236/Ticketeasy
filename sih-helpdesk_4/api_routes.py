"""
REST API Routes for Smart Helpdesk
Production-ready endpoints with proper error handling
"""
from flask import Blueprint, request, jsonify
from api_models import db, APITicket
from api_classifier import TicketClassifier
from datetime import datetime
from sqlalchemy import desc

api_bp = Blueprint('api', __name__, url_prefix='/api')

def generate_ticket_id():
    """Generate unique ticket ID: IT-2025-001"""
    year = datetime.now().year
    
    # Get last ticket ID for this year
    last_ticket = APITicket.query.filter(
        APITicket.ticket_id.like(f'IT-{year}-%')
    ).order_by(desc(APITicket.id)).first()
    
    if last_ticket:
        # Extract number and increment
        last_num = int(last_ticket.ticket_id.split('-')[-1])
        new_num = last_num + 1
    else:
        new_num = 1
    
    return f"IT-{year}-{new_num:03d}"


@api_bp.route('/tickets', methods=['POST'])
def create_ticket():
    """
    POST /api/tickets
    Create new ticket with auto-classification
    
    Required fields: title, description, source, urgency
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['title', 'description', 'source', 'urgency']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({
                    'error': f'Missing required field: {field}',
                    'status': 'error'
                }), 400
        
        # Validate source
        valid_sources = ['chatbot', 'email', 'glpi', 'solman', 'web']
        if data['source'] not in valid_sources:
            return jsonify({
                'error': f'Invalid source. Must be one of: {", ".join(valid_sources)}',
                'status': 'error'
            }), 400
        
        # Validate urgency
        valid_urgencies = ['Low', 'Medium', 'High', 'Critical']
        if data['urgency'] not in valid_urgencies:
            return jsonify({
                'error': f'Invalid urgency. Must be one of: {", ".join(valid_urgencies)}',
                'status': 'error'
            }), 400
        
        # Auto-classify using NLP
        category, assigned_team = TicketClassifier.classify(
            data['title'],
            data['description']
        )
        
        # Generate ticket ID
        ticket_id = generate_ticket_id()
        
        # Create ticket
        ticket = APITicket(
            ticket_id=ticket_id,
            title=data['title'],
            description=data['description'],
            source=data['source'],
            urgency=data['urgency'],
            category=category,
            assigned_team=assigned_team,
            status='open'
        )
        
        db.session.add(ticket)
        db.session.commit()
        
        # Return success response
        return jsonify({
            'message': 'Ticket created successfully',
            'status': 'success',
            'ticket': ticket.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500


@api_bp.route('/tickets/<ticket_id>', methods=['GET'])
def get_ticket(ticket_id):
    """
    GET /api/tickets/{ticket_id}
    Fetch single ticket by ID
    """
    ticket = APITicket.query.filter_by(ticket_id=ticket_id).first()
    
    if not ticket:
        return jsonify({
            'error': 'Ticket not found',
            'status': 'error'
        }), 404
    
    return jsonify({
        'status': 'success',
        'ticket': ticket.to_dict()
    }), 200


@api_bp.route('/tickets', methods=['GET'])
def list_tickets():
    """
    GET /api/tickets
    List all tickets with optional filters
    
    Query params:
    - status: filter by status (open|in-progress|resolved)
    - team: filter by assigned team
    - source: filter by source
    - urgency: filter by urgency level
    """
    query = APITicket.query
    
    # Apply filters
    if 'status' in request.args:
        query = query.filter_by(status=request.args['status'])
    
    if 'team' in request.args:
        query = query.filter_by(assigned_team=request.args['team'])
    
    if 'source' in request.args:
        query = query.filter_by(source=request.args['source'])
    
    if 'urgency' in request.args:
        query = query.filter_by(urgency=request.args['urgency'])
    
    # Order by created_at descending (newest first)
    tickets = query.order_by(desc(APITicket.created_at)).all()
    
    return jsonify({
        'status': 'success',
        'count': len(tickets),
        'tickets': [ticket.to_dict() for ticket in tickets]
    }), 200


@api_bp.route('/tickets/<ticket_id>', methods=['PATCH'])
def update_ticket(ticket_id):
    """
    PATCH /api/tickets/{ticket_id}
    Update ticket status or other fields
    """
    ticket = APITicket.query.filter_by(ticket_id=ticket_id).first()
    
    if not ticket:
        return jsonify({
            'error': 'Ticket not found',
            'status': 'error'
        }), 404
    
    try:
        data = request.get_json()
        
        # Update allowed fields
        if 'status' in data:
            valid_statuses = ['open', 'in-progress', 'resolved']
            if data['status'] in valid_statuses:
                ticket.status = data['status']
        
        if 'urgency' in data:
            valid_urgencies = ['Low', 'Medium', 'High', 'Critical']
            if data['urgency'] in valid_urgencies:
                ticket.urgency = data['urgency']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Ticket updated successfully',
            'status': 'success',
            'ticket': ticket.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500


@api_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Smart Helpdesk API',
        'timestamp': datetime.utcnow().isoformat()
    }), 200
