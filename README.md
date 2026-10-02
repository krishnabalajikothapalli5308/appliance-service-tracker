# 🔧 Appliance Service Tracker

A full-stack web application for managing appliance maintenance records and service requests — built as part of a campus internship application for **GE Appliances (a Haier Company)**.

> **Author:** Kothapalli Krishna Balaji | B.Tech CSE, 3rd Year
> **GitHub:** [github.com/krishnabalajikothapalli5308](https://github.com/krishnabalajikothapalli5308)
> **LinkedIn:** [linkedin.com/in/krishna-balaji-259a1631b](https://linkedin.com/in/krishna-balaji-259a1631b)

---

## 🌐 Live Demo

| Portal | Link |
|---|---|
| 🖥 Admin Dashboard | [appliance-service-tracker.vercel.app](https://appliance-service-tracker.vercel.app) |
| 🔧 Technician Portal | [appliance-service-tracker.vercel.app/technician](https://appliance-service-tracker.vercel.app/technician) |

> **No setup needed — click and explore the live app directly.**

---

## 📋 Project Overview

ServiceTrack simulates a real-world appliance management system with two role-based portals:

- **Admin Dashboard** — manage appliances, create/assign service requests, track technician workloads
- **Technician Portal** — view assigned jobs and update job status and notes

Built using **Agile methodology** with clearly defined sprints, RESTful API design, and systematic software documentation.

---

## 🛠 Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3, Flask, Flask-SQLAlchemy |
| Database | SQLite (dev) / MySQL (prod-ready) |
| Frontend | HTML5, CSS3, Vanilla JavaScript |
| Testing | pytest |
| Deployment | Vercel |
| Version Control | Git / GitHub |

---

## 🖥 Screenshots

### Admin Dashboard
> Stat cards, appliance table, service request management — all in one view.

### Technician Portal
> Filter by technician, update job status and notes in real time.

---

## 🗂 Project Structure

```
appliance-service-tracker/
│
├── app.py               # Flask application + REST API routes
├── database.py          # SQLAlchemy ORM models
├── vercel.json          # Vercel deployment config
├── requirements.txt     # Python dependencies
│
├── templates/
│   ├── index.html       # Admin dashboard
│   └── technician.html  # Technician portal
│
├── static/
│   ├── css/style.css    # Stylesheet
│   └── js/
│       ├── main.js      # Admin dashboard JS
│       └── technician.js# Technician portal JS
│
└── tests/
    └── test_api.py      # Unit tests (pytest) — 18 tests
```

---

## ⚙️ System Design

### Data Models

```
Appliance
  ├── id, name, model, serial_number
  ├── location, purchase_date, status
  └── → ServiceRequests (one-to-many)

Technician
  ├── id, name, specialization
  ├── contact, available
  └── → ServiceRequests (one-to-many)

ServiceRequest
  ├── id, issue_description, priority, status
  ├── notes, created_at, completed_at
  ├── → Appliance (FK)
  └── → Technician (FK, nullable)
```

### Application Flowchart

```
[Admin opens app]
       │
       ▼
[Dashboard loads stats via GET /api/stats]
       │
       ├──► [View Appliances]
       │         │
       │    [Add Appliance] ──► POST /api/appliances ──► [DB Insert] ──► [Reload table]
       │    [Delete]        ──► DELETE /api/appliances/<id>
       │
       ├──► [View Service Requests]
       │         │
       │    [New Request] ──► POST /api/service-requests ──► [Validate appliance] ──► [DB Insert]
       │    [Edit/Assign] ──► PUT /api/service-requests/<id> ──► [Update status + technician]
       │    [Delete]      ──► DELETE /api/service-requests/<id>
       │
       └──► [View Technicians]
                 │
            [Add Technician] ──► POST /api/technicians ──► [DB Insert]

[Technician opens /technician]
       │
       ▼
[Select name from dropdown]
       │
       ▼
[GET /api/service-requests → filter by technician_id]
       │
       ▼
[Update job] ──► PUT /api/service-requests/<id> ──► [Status + notes saved]
```

---

## 🚀 REST API Reference

### Appliances

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/appliances` | List all appliances |
| GET | `/api/appliances/<id>` | Get single appliance |
| POST | `/api/appliances` | Create new appliance |
| PUT | `/api/appliances/<id>` | Update appliance |
| DELETE | `/api/appliances/<id>` | Delete appliance |

### Service Requests

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/service-requests` | List all (supports `?status=open`) |
| GET | `/api/service-requests/<id>` | Get single request |
| POST | `/api/service-requests` | Create new request |
| PUT | `/api/service-requests/<id>` | Update status / assign technician |
| DELETE | `/api/service-requests/<id>` | Delete request |

### Technicians

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/technicians` | List all technicians |
| POST | `/api/technicians` | Add new technician |

### Dashboard

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/stats` | Aggregate counts for dashboard |

---

## 🏃 How to Run Locally

```bash
# 1. Clone the repo
git clone https://github.com/krishnabalajikothapalli5308/appliance-service-tracker.git
cd appliance-service-tracker

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the app
python app.py

# 5. Open in browser
# Admin view:      http://localhost:5000
# Technician view: http://localhost:5000/technician
```

---

## 🧪 Running Tests

```bash
python -m pytest tests/ -v
```

**18 tests covering:**
- CRUD operations for all three models
- Input validation — missing fields return 400
- Foreign key validation — invalid appliance ID returns 404
- Status filtering for service requests
- Stats endpoint accuracy
- Cascade delete behaviour

---

## 🔄 Agile Development Approach

| Sprint | Focus | Deliverables |
|--------|-------|--------------|
| Sprint 1 | Backend foundation | Flask app, DB models, all REST API endpoints |
| Sprint 2 | Frontend + role-based views | Admin dashboard, Technician portal, dynamic JS |
| Sprint 3 | Testing + documentation | pytest unit tests, README, API reference |

---

## 🌱 Future Improvements

- [ ] MySQL integration for production deployment
- [ ] JWT-based authentication for Admin/Technician roles
- [ ] Email notifications when service requests are assigned
- [ ] Export service history reports to PDF/Excel
- [ ] Mobile-responsive PWA version

---

## 📄 License

MIT License — free to use and modify.
