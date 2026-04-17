"""
Unit Tests for Appliance Service Tracker
Run with: python -m pytest tests/ -v
"""

import pytest
import json
from app import app
from database import db, Appliance, ServiceRequest, Technician


@pytest.fixture
def client():
    """Set up a test client with an in-memory database."""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.drop_all()


def post_json(client, url, data):
    return client.post(url, data=json.dumps(data), content_type='application/json')

def put_json(client, url, data):
    return client.put(url, data=json.dumps(data), content_type='application/json')


# ── APPLIANCE TESTS ───────────────────────────────────────────────────────

class TestAppliances:

    def test_get_appliances_empty(self, client):
        """GET /api/appliances returns empty list initially."""
        res = client.get('/api/appliances')
        assert res.status_code == 200
        assert json.loads(res.data) == []

    def test_create_appliance_success(self, client):
        """POST /api/appliances creates a new appliance."""
        res = post_json(client, '/api/appliances', {
            'name': 'Refrigerator', 'model': 'GE Profile PFE28KYNFS',
            'serial_number': 'SN001', 'location': 'Kitchen A'
        })
        assert res.status_code == 201
        data = json.loads(res.data)
        assert data['name'] == 'Refrigerator'
        assert data['status'] == 'active'

    def test_create_appliance_missing_fields(self, client):
        """POST /api/appliances without required fields returns 400."""
        res = post_json(client, '/api/appliances', {'name': 'Refrigerator'})
        assert res.status_code == 400

    def test_get_appliance_by_id(self, client):
        """GET /api/appliances/<id> returns correct appliance."""
        post_json(client, '/api/appliances', {'name': 'Washer', 'model': 'GE GTW685'})
        res = client.get('/api/appliances/1')
        assert res.status_code == 200
        assert json.loads(res.data)['name'] == 'Washer'

    def test_get_appliance_not_found(self, client):
        """GET /api/appliances/999 returns 404."""
        res = client.get('/api/appliances/999')
        assert res.status_code == 404

    def test_update_appliance_status(self, client):
        """PUT /api/appliances/<id> updates status field."""
        post_json(client, '/api/appliances', {'name': 'Dryer', 'model': 'GE GTD42GASJWW'})
        res = put_json(client, '/api/appliances/1', {'status': 'maintenance'})
        assert res.status_code == 200
        assert json.loads(res.data)['status'] == 'maintenance'

    def test_delete_appliance(self, client):
        """DELETE /api/appliances/<id> removes the appliance."""
        post_json(client, '/api/appliances', {'name': 'AC', 'model': 'GE AHY08LZ'})
        res = client.delete('/api/appliances/1')
        assert res.status_code == 200
        assert client.get('/api/appliances/1').status_code == 404

    def test_appliance_count_in_list(self, client):
        """Multiple appliances are all returned in GET /api/appliances."""
        post_json(client, '/api/appliances', {'name': 'A1', 'model': 'M1'})
        post_json(client, '/api/appliances', {'name': 'A2', 'model': 'M2'})
        post_json(client, '/api/appliances', {'name': 'A3', 'model': 'M3'})
        res = client.get('/api/appliances')
        assert len(json.loads(res.data)) == 3


# ── SERVICE REQUEST TESTS ─────────────────────────────────────────────────

class TestServiceRequests:

    def setup_appliance(self, client):
        post_json(client, '/api/appliances', {'name': 'Refrigerator', 'model': 'GE PFE28'})

    def test_create_service_request_success(self, client):
        """POST /api/service-requests creates a new request."""
        self.setup_appliance(client)
        res = post_json(client, '/api/service-requests', {
            'appliance_id': 1, 'issue_description': 'Not cooling', 'priority': 'high'
        })
        assert res.status_code == 201
        data = json.loads(res.data)
        assert data['status'] == 'open'
        assert data['priority'] == 'high'

    def test_create_service_request_invalid_appliance(self, client):
        """POST /api/service-requests with non-existent appliance returns 404."""
        res = post_json(client, '/api/service-requests', {
            'appliance_id': 999, 'issue_description': 'Test'
        })
        assert res.status_code == 404

    def test_update_service_request_status(self, client):
        """PUT /api/service-requests/<id> updates status correctly."""
        self.setup_appliance(client)
        post_json(client, '/api/service-requests', {'appliance_id': 1, 'issue_description': 'Broken'})
        res = put_json(client, '/api/service-requests/1', {'status': 'in_progress'})
        assert json.loads(res.data)['status'] == 'in_progress'

    def test_filter_service_requests_by_status(self, client):
        """GET /api/service-requests?status=open returns only open requests."""
        self.setup_appliance(client)
        post_json(client, '/api/service-requests', {'appliance_id': 1, 'issue_description': 'Issue 1'})
        post_json(client, '/api/service-requests', {'appliance_id': 1, 'issue_description': 'Issue 2'})
        put_json(client, '/api/service-requests/2', {'status': 'completed'})
        res = client.get('/api/service-requests?status=open')
        data = json.loads(res.data)
        assert len(data) == 1
        assert data[0]['status'] == 'open'

    def test_delete_service_request(self, client):
        """DELETE /api/service-requests/<id> removes the request."""
        self.setup_appliance(client)
        post_json(client, '/api/service-requests', {'appliance_id': 1, 'issue_description': 'Broken'})
        res = client.delete('/api/service-requests/1')
        assert res.status_code == 200

    def test_missing_issue_description(self, client):
        """POST without issue_description returns 400."""
        self.setup_appliance(client)
        res = post_json(client, '/api/service-requests', {'appliance_id': 1})
        assert res.status_code == 400


# ── TECHNICIAN TESTS ──────────────────────────────────────────────────────

class TestTechnicians:

    def test_create_technician(self, client):
        """POST /api/technicians creates a technician."""
        res = post_json(client, '/api/technicians', {
            'name': 'Rajesh Kumar', 'specialization': 'HVAC', 'contact': '9876543210'
        })
        assert res.status_code == 201
        data = json.loads(res.data)
        assert data['name'] == 'Rajesh Kumar'
        assert data['available'] is True

    def test_create_technician_missing_fields(self, client):
        """POST /api/technicians without specialization returns 400."""
        res = post_json(client, '/api/technicians', {'name': 'Ravi'})
        assert res.status_code == 400

    def test_list_technicians(self, client):
        """GET /api/technicians returns all technicians."""
        post_json(client, '/api/technicians', {'name': 'T1', 'specialization': 'S1'})
        post_json(client, '/api/technicians', {'name': 'T2', 'specialization': 'S2'})
        res = client.get('/api/technicians')
        assert len(json.loads(res.data)) == 2


# ── STATS TESTS ───────────────────────────────────────────────────────────

class TestStats:

    def test_stats_endpoint(self, client):
        """GET /api/stats returns correct counts."""
        post_json(client, '/api/appliances', {'name': 'A1', 'model': 'M1'})
        post_json(client, '/api/appliances', {'name': 'A2', 'model': 'M2'})
        post_json(client, '/api/service-requests', {'appliance_id': 1, 'issue_description': 'Issue'})
        res = client.get('/api/stats')
        data = json.loads(res.data)
        assert data['total_appliances'] == 2
        assert data['open_requests'] == 1
        assert data['completed'] == 0
