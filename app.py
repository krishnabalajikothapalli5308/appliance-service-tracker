"""
Appliance Service Tracker
A full-stack web application for managing appliance maintenance records
and service requests.

Author: Kothapalli Krishna Balaji
GitHub: github.com/krishnabalajikothapalli5308
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for
from database import db, Appliance, ServiceRequest, Technician
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///appliance_tracker.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'gea-tracker-secret-2025'

db.init_app(app)


# ──────────────────────────────────────────────
# PAGE ROUTES
# ──────────────────────────────────────────────

@app.route('/')
def index():
    """Home / Admin Dashboard"""
    return render_template('index.html')


@app.route('/technician')
def technician_view():
    """Technician Dashboard"""
    return render_template('technician.html')


# ──────────────────────────────────────────────
# API – APPLIANCES
# ──────────────────────────────────────────────

@app.route('/api/appliances', methods=['GET'])
def get_appliances():
    appliances = Appliance.query.all()
    return jsonify([a.to_dict() for a in appliances])


@app.route('/api/appliances/<int:appliance_id>', methods=['GET'])
def get_appliance(appliance_id):
    appliance = Appliance.query.get_or_404(appliance_id)
    return jsonify(appliance.to_dict())


@app.route('/api/appliances', methods=['POST'])
def create_appliance():
    data = request.get_json()
    if not data or not data.get('name') or not data.get('model'):
        return jsonify({'error': 'name and model are required'}), 400

    appliance = Appliance(
        name=data['name'],
        model=data['model'],
        serial_number=data.get('serial_number') or None,
        location=data.get('location', ''),
        purchase_date=data.get('purchase_date', ''),
        status='active'
    )
    db.session.add(appliance)
    db.session.commit()
    return jsonify(appliance.to_dict()), 201


@app.route('/api/appliances/<int:appliance_id>', methods=['PUT'])
def update_appliance(appliance_id):
    appliance = Appliance.query.get_or_404(appliance_id)
    data = request.get_json()
    if 'name' in data:
        appliance.name = data['name']
    if 'model' in data:
        appliance.model = data['model']
    if 'serial_number' in data:
        appliance.serial_number = data['serial_number']
    if 'location' in data:
        appliance.location = data['location']
    if 'status' in data:
        appliance.status = data['status']
    db.session.commit()
    return jsonify(appliance.to_dict())


@app.route('/api/appliances/<int:appliance_id>', methods=['DELETE'])
def delete_appliance(appliance_id):
    appliance = Appliance.query.get_or_404(appliance_id)
    db.session.delete(appliance)
    db.session.commit()
    return jsonify({'message': f'Appliance {appliance_id} deleted'})


# ──────────────────────────────────────────────
# API – SERVICE REQUESTS
# ──────────────────────────────────────────────

@app.route('/api/service-requests', methods=['GET'])
def get_service_requests():
    status_filter = request.args.get('status')
    if status_filter:
        requests_list = ServiceRequest.query.filter_by(status=status_filter).all()
    else:
        requests_list = ServiceRequest.query.order_by(ServiceRequest.created_at.desc()).all()
    return jsonify([r.to_dict() for r in requests_list])


@app.route('/api/service-requests/<int:req_id>', methods=['GET'])
def get_service_request(req_id):
    sr = ServiceRequest.query.get_or_404(req_id)
    return jsonify(sr.to_dict())


@app.route('/api/service-requests', methods=['POST'])
def create_service_request():
    data = request.get_json()
    if not data or not data.get('appliance_id') or not data.get('issue_description'):
        return jsonify({'error': 'appliance_id and issue_description are required'}), 400

    # Verify appliance exists
    appliance = Appliance.query.get(data['appliance_id'])
    if not appliance:
        return jsonify({'error': 'Appliance not found'}), 404

    sr = ServiceRequest(
        appliance_id=data['appliance_id'],
        issue_description=data['issue_description'],
        priority=data.get('priority', 'medium'),
        status='open',
        created_at=datetime.utcnow()
    )
    db.session.add(sr)
    db.session.commit()
    return jsonify(sr.to_dict()), 201


@app.route('/api/service-requests/<int:req_id>', methods=['PUT'])
def update_service_request(req_id):
    sr = ServiceRequest.query.get_or_404(req_id)
    data = request.get_json()
    if 'status' in data:
        sr.status = data['status']
        if data['status'] == 'completed':
            sr.completed_at = datetime.utcnow()
    if 'technician_id' in data:
        sr.technician_id = data['technician_id']
    if 'notes' in data:
        sr.notes = data['notes']
    db.session.commit()
    return jsonify(sr.to_dict())


@app.route('/api/service-requests/<int:req_id>', methods=['DELETE'])
def delete_service_request(req_id):
    sr = ServiceRequest.query.get_or_404(req_id)
    db.session.delete(sr)
    db.session.commit()
    return jsonify({'message': f'Service request {req_id} deleted'})


# ──────────────────────────────────────────────
# API – TECHNICIANS
# ──────────────────────────────────────────────

@app.route('/api/technicians', methods=['GET'])
def get_technicians():
    technicians = Technician.query.all()
    return jsonify([t.to_dict() for t in technicians])


@app.route('/api/technicians', methods=['POST'])
def create_technician():
    data = request.get_json()
    if not data or not data.get('name') or not data.get('specialization'):
        return jsonify({'error': 'name and specialization are required'}), 400
    tech = Technician(
        name=data['name'],
        specialization=data['specialization'],
        contact=data.get('contact', ''),
        available=True
    )
    db.session.add(tech)
    db.session.commit()
    return jsonify(tech.to_dict()), 201


# ──────────────────────────────────────────────
# API – DASHBOARD STATS
# ──────────────────────────────────────────────

@app.route('/api/stats', methods=['GET'])
def get_stats():
    total_appliances = Appliance.query.count()
    open_requests = ServiceRequest.query.filter_by(status='open').count()
    in_progress = ServiceRequest.query.filter_by(status='in_progress').count()
    completed = ServiceRequest.query.filter_by(status='completed').count()
    total_technicians = Technician.query.count()

    return jsonify({
        'total_appliances': total_appliances,
        'open_requests': open_requests,
        'in_progress': in_progress,
        'completed': completed,
        'total_technicians': total_technicians
    })


# ──────────────────────────────────────────────
# INIT DB WITH SEED DATA
# ──────────────────────────────────────────────

def seed_data():
    """Seed the database with sample data if empty."""
    if Appliance.query.count() == 0:
        appliances = [
            Appliance(name='Refrigerator', model='GE Profile PFE28KYNFS', serial_number='SN10023', location='Kitchen Block A', purchase_date='2022-01-15', status='active'),
            Appliance(name='Washing Machine', model='GE GTW685BSLWS', serial_number='SN10024', location='Laundry Room B', purchase_date='2021-06-10', status='active'),
            Appliance(name='Dishwasher', model='GE GDT630PYMFS', serial_number='SN10025', location='Kitchen Block B', purchase_date='2023-03-20', status='maintenance'),
            Appliance(name='Air Conditioner', model='GE AHY08LZ', serial_number='SN10026', location='Office Block C', purchase_date='2020-09-05', status='active'),
            Appliance(name='Microwave Oven', model='GE JES1072SHSS', serial_number='SN10027', location='Break Room', purchase_date='2022-11-30', status='active'),
        ]
        db.session.add_all(appliances)

    if Technician.query.count() == 0:
        technicians = [
            Technician(name='Rajesh Kumar', specialization='Refrigeration & HVAC', contact='9876543210', available=True),
            Technician(name='Sunita Sharma', specialization='Washing Machines & Dryers', contact='9876543211', available=True),
            Technician(name='Anil Verma', specialization='Kitchen Appliances', contact='9876543212', available=False),
        ]
        db.session.add_all(technicians)

    if ServiceRequest.query.count() == 0:
        service_requests = [
            ServiceRequest(appliance_id=1, issue_description='Refrigerator not cooling properly, compressor making noise', priority='high', status='open', created_at=datetime.utcnow()),
            ServiceRequest(appliance_id=3, issue_description='Dishwasher door latch broken, water leaking', priority='high', status='in_progress', technician_id=3, created_at=datetime.utcnow()),
            ServiceRequest(appliance_id=2, issue_description='Routine annual maintenance check', priority='low', status='completed', technician_id=2, notes='All components checked and cleaned', created_at=datetime.utcnow(), completed_at=datetime.utcnow()),
        ]
        db.session.add_all(service_requests)

    db.session.commit()


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        seed_data()
    app.run(debug=True, port=5000)
