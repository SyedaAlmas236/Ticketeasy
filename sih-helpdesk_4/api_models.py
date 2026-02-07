"""
API Database Models for Smart Helpdesk REST API
SQLite with SQLAlchemy ORM
"""
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class APITicket(db.Model):
    """REST API Ticket Model"""
    __tablename__ = 'api_tickets'
    
    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(db.String(50), unique=True, nullable=False)  # IT-2025-001
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    source = db.Column(db.String(20), nullable=False)  # chatbot|email|glpi|solman|web
    urgency = db.Column(db.String(20), nullable=False)  # Low|Medium|High|Critical
    category = db.Column(db.String(50), nullable=False)  # Network|Application|Hardware|Access|Software
    assigned_team = db.Column(db.String(50), nullable=False)  # NetworkTeam|AppTeam|HardwareTeam|AccessTeam
    status = db.Column(db.String(20), default='open')  # open|in-progress|resolved
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Convert to JSON-serializable dictionary"""
        return {
            'id': self.id,
            'ticket_id': self.ticket_id,
            'title': self.title,
            'description': self.description,
            'source': self.source,
            'urgency': self.urgency,
            'category': self.category,
            'assigned_team': self.assigned_team,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<APITicket {self.ticket_id}: {self.title}>'
