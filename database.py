"""
Database models for Appliance Service Tracker
Using Flask-SQLAlchemy ORM
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class Appliance(db.Model):
    """Represents an appliance in the inventory."""
    __tablename__ = 'appliances'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    model = db.Column(db.String(100), nullable=False)
    serial_number = db.Column(db.String(100), unique=True, nullable=True)
    location = db.Column(db.String(200))
    purchase_date = db.Column(db.String(20))
    status = db.Column(db.String(20), default='active')  # active | maintenance | retired

    service_requests = db.relationship('ServiceRequest', backref='appliance', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'model': self.model,
            'serial_number': self.serial_number,
            'location': self.location,
            'purchase_date': self.purchase_date,
            'status': self.status,
            'total_service_requests': len(self.service_requests)
        }

    def __repr__(self):
        return f'<Appliance {self.name} – {self.model}>'


class Technician(db.Model):
    """Represents a service technician."""
    __tablename__ = 'technicians'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    specialization = db.Column(db.String(200), nullable=False)
    contact = db.Column(db.String(20))
    available = db.Column(db.Boolean, default=True)

    assignments = db.relationship('ServiceRequest', backref='technician', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'specialization': self.specialization,
            'contact': self.contact,
            'available': self.available,
            'total_assigned': len(self.assignments)
        }

    def __repr__(self):
        return f'<Technician {self.name}>'


class ServiceRequest(db.Model):
    """Represents a maintenance/service request for an appliance."""
    __tablename__ = 'service_requests'

    id = db.Column(db.Integer, primary_key=True)
    appliance_id = db.Column(db.Integer, db.ForeignKey('appliances.id'), nullable=False)
    technician_id = db.Column(db.Integer, db.ForeignKey('technicians.id'), nullable=True)
    issue_description = db.Column(db.Text, nullable=False)
    priority = db.Column(db.String(10), default='medium')   # low | medium | high
    status = db.Column(db.String(20), default='open')        # open | in_progress | completed | cancelled
    notes = db.Column(db.Text, default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'appliance_id': self.appliance_id,
            'appliance_name': self.appliance.name if self.appliance else None,
            'appliance_model': self.appliance.model if self.appliance else None,
            'technician_id': self.technician_id,
            'technician_name': self.technician.name if self.technician else None,
            'issue_description': self.issue_description,
            'priority': self.priority,
            'status': self.status,
            'notes': self.notes,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M') if self.created_at else None,
            'completed_at': self.completed_at.strftime('%Y-%m-%d %H:%M') if self.completed_at else None,
        }

    def __repr__(self):
        return f'<ServiceRequest #{self.id} – {self.status}>'
