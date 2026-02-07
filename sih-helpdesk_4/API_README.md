# Smart Helpdesk REST API Documentation

## 🚀 Quick Start

### Installation
```bash
cd c:\sih-helpdesk_4
pip install -r requirements_api.txt
python api_app.py
```

Server starts at: **http://127.0.0.1:8000**

### Test in Browser
Open: `test_api.html` in your browser

---

## 📡 API Endpoints

### Base URL
```
Local: http://127.0.0.1:8000
Production: https://your-app.onrender.com
```

---

## 1. Create Ticket (POST)

**Endpoint**: `POST /api/tickets`

**Description**: Create new ticket with auto-classification

**Headers**:
```
Content-Type: application/json
```

**Request Body**:
```json
{
  "title": "VPN not connecting",
  "description": "Unable to connect to office VPN from home",
  "source": "chatbot",
  "urgency": "High"
}
```

**Response** (201 Created):
```json
{
  "message": "Ticket created successfully",
  "status": "success",
  "ticket": {
    "id": 1,
    "ticket_id": "IT-2025-001",
    "title": "VPN not connecting",
    "description": "Unable to connect to office VPN from home",
    "source": "chatbot",
    "urgency": "High",
    "category": "Network",
    "assigned_team": "NetworkTeam",
    "status": "open",
    "created_at": "2025-12-09T15:30:00",
    "updated_at": "2025-12-09T15:30:00"
  }
}
```

### Postman Test:
```bash
curl -X POST http://127.0.0.1:8000/api/tickets \
  -H "Content-Type: application/json" \
  -d '{
    "title": "VPN not connecting",
    "description": "Cannot connect to office network",
    "source": "chatbot",
    "urgency": "High"
  }'
```

---

## 2. Get Single Ticket (GET)

**Endpoint**: `GET /api/tickets/{ticket_id}`

**Example**: `GET /api/tickets/IT-2025-001`

**Response** (200 OK):
```json
{
  "status": "success",
  "ticket": {
    "id": 1,
    "ticket_id": "IT-2025-001",
    "title": "VPN not connecting",
    ...
  }
}
```

**Response** (404 Not Found):
```json
{
  "error": "Ticket not found",
  "status": "error"
}
```

### Postman Test:
```bash
curl http://127.0.0.1:8000/api/tickets/IT-2025-001
```

---

## 3. List All Tickets (GET)

**Endpoint**: `GET /api/tickets`

**Query Parameters (all optional)**:
- `status` - Filter by status (open|in-progress|resolved)
- `team` - Filter by team (NetworkTeam|AppTeam|HardwareTeam|AccessTeam)
- `source` - Filter by source (chatbot|email|glpi|solman|web)
- `urgency` - Filter by urgency (Low|Medium|High|Critical)

**Examples**:
```
GET /api/tickets
GET /api/tickets?status=open
GET /api/tickets?team=NetworkTeam&urgency=Critical
GET /api/tickets?source=chatbot
```

**Response** (200 OK):
```json
{
  "status": "success",
  "count": 5,
  "tickets": [
    {
      "id": 1,
      "ticket_id": "IT-2025-001",
      ...
    },
    ...
  ]
}
```

### Postman Test:
```bash
# List all tickets
curl http://127.0.0.1:8000/api/tickets

# Filter by status
curl "http://127.0.0.1:8000/api/tickets?status=open"

# Filter by team
curl "http://127.0.0.1:8000/api/tickets?team=NetworkTeam"
```

---

## 4. Update Ticket (PATCH)

**Endpoint**: `PATCH /api/tickets/{ticket_id}`

**Request Body**:
```json
{
  "status": "in-progress"
}
```

**Response** (200 OK):
```json
{
  "message": "Ticket updated successfully",
  "status": "success",
  "ticket": { ... }
}
```

### Postman Test:
```bash
curl -X PATCH http://127.0.0.1:8000/api/tickets/IT-2025-001 \
  -H "Content-Type: application/json" \
  -d '{"status": "in-progress"}'
```

---

## 5. Health Check

**Endpoint**: `GET /api/health`

**Response**:
```json
{
  "status": "healthy",
  "service": "Smart Helpdesk API",
  "timestamp": "2025-12-09T15:30:00"
}
```

---

## 🧠 Auto-Classification

The API automatically classifies tickets based on keywords:

| Category | Keywords | Team |
|----------|----------|------|
| **Network** | VPN, router, connectivity, IP, network | NetworkTeam |
| **Application** | Outlook, SAP, Teams, GLPI, application | AppTeam |
| **Hardware** | laptop, printer, mouse, keyboard, screen | HardwareTeam |
| **Access** | password, login, account, permission | AccessTeam |
| **Software** | Windows, Office, installation, patch | SoftwareTeam |

**Example**:
```json
{
  "title": "Cannot access VPN",
  "description": "Getting connection timeout"
}
```
→ Auto-classified as **Network** → Assigned to **NetworkTeam**

---

## 🌐 Deploy to Render/Railway

### Render.com
1. Push code to GitHub
2. Go to [Render.com](https://render.com) → New Web Service
3. Connect GitHub repo
4. Render auto-detects `Procfile`
5. Click "Create Web Service"
6. Your API is live at: `https://your-app.onrender.com`

### Railway.app
1. Push code to GitHub
2. Go to [Railway.app](https://railway.app) → New Project
3. Deploy from GitHub
4. Railway auto-detects Python
5. Your API is live!

---

## ✅ Postman Collection

### Create Ticket
```
Method: POST
URL: http://127.0.0.1:8000/api/tickets
Headers: Content-Type: application/json
Body (raw JSON):
{
  "title": "Outlook not opening",
  "description": "Application crashes on startup",
  "source": "email",
  "urgency": "Medium"
}
```

### Get Ticket
```
Method: GET
URL: http://127.0.0.1:8000/api/tickets/IT-2025-001
```

### List Tickets (Filtered)
```
Method: GET
URL: http://127.0.0.1:8000/api/tickets?status=open&team=NetworkTeam
```

### Update Ticket Status
```
Method: PATCH
URL: http://127.0.0.1:8000/api/tickets/IT-2025-001
Headers: Content-Type: application/json
Body (raw JSON):
{
  "status": "resolved"
}
```

---

## 📁 Project Structure

```
c:\sih-helpdesk_4\
├── api_app.py             # Main Flask application
├── api_models.py          # SQLAlchemy database models
├── api_routes.py          # REST API endpoints
├── api_classifier.py      # Auto-classification logic
├── api_helpdesk.db        # SQLite database (auto-created)
├── requirements_api.txt   # Python dependencies
├── Procfile               # Deployment config
├── runtime.txt            # Python version
├── test_api.html          # Browser test page
└── API_README.md          # This file
```

---

## 🎯 SIH Demo Tips

1. **Show Auto-Classification**: Create tickets with different keywords
2. **Demo Multi-Source**: Use different `source` values (chatbot, email, glpi)
3. **Filter Demo**: Show filtering by team, status, urgency
4. **Production Ready**: API uses Waitress (production WSGI server)
5. **CORS Enabled**: Works with any frontend (React, Angular, chatbot)

---

## 🔧 Troubleshooting

**Port already in use**:
```python
# In api_app.py, change port:
serve(app, host='0.0.0.0', port=9000, threads=4)
```

**Database reset**:
```bash
# Delete database and restart:
del api_helpdesk.db
python api_app.py
```

**CORS errors**:
The API enables CORS for all origins. If issues persist, check browser console.

---

## 📞 Support

For issues or questions, refer to the main application documentation or contact the development team.

**API Version**: 1.0.0  
**Last Updated**: December 2025
