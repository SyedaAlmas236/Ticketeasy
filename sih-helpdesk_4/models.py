from datetime import datetime
from extensions import db, hash_password, verify_password
from flask_login import UserMixin
import json

class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(180), unique=True, nullable=False)
    name = db.Column(db.String(180))
    password_hash = db.Column(db.String(256), nullable=False)
    # Roles: 'super_admin', 'manager' (Dept Head), 'agent' (Worker), 'employee' (User)
    role = db.Column(db.String(30))           
    employee_role = db.Column(db.String(120))
    verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    assigned_tickets = db.relationship('Ticket', back_populates='assigned_admin', foreign_keys='Ticket.assigned_admin_id')
    created_tickets = db.relationship('Ticket', back_populates='creator', foreign_keys='Ticket.created_by_id')

    def set_password(self, password: str):
        self.password_hash = hash_password(password)

    def check_password(self, password: str) -> bool:
        return verify_password(self.password_hash, password)

class Category(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)

    tickets = db.relationship('Ticket', back_populates='category_obj')
    admins = db.relationship('User', secondary='admin_categories', backref='categories_handled')

class AdminCategories(db.Model):
    __tablename__ = 'admin_categories'
    admin_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), primary_key=True)

class Ticket(db.Model):
    __tablename__ = 'tickets'

    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(255))
    description = db.Column(db.Text)
    priority = db.Column(db.String(20))
    status = db.Column(db.String(30))
    category = db.Column(db.String(80))
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    assigned_admin_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    sentiment = db.Column(db.String(50), default="Neutral")
    remarks = db.Column(db.Text)
    _suggested_steps = db.Column("suggested_steps", db.Text, default="[]") 

    category_obj = db.relationship('Category', back_populates='tickets', foreign_keys=[category_id])
    assigned_admin = db.relationship('User', back_populates='assigned_tickets', foreign_keys=[assigned_admin_id])
    creator = db.relationship('User', back_populates='created_tickets', foreign_keys=[created_by_id])

    @property
    def suggested_steps(self):
        try: return json.loads(self._suggested_steps)
        except: return []

    @suggested_steps.setter
    def suggested_steps(self, value):
        self._suggested_steps = json.dumps(value)