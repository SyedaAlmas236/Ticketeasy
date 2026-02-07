# TicketEasy 🎫⚡  
AI-Powered Smart Helpdesk & Ticket Management System (SIH)

TicketEasy is a smart IT helpdesk web application + REST API that helps employees raise support tickets, auto-classify them into the right category/team, and allows admins/agents to manage and resolve them faster.

It supports:
- Employee portal (raise ticket + track history)
- Agent/Admin dashboard (view, assign, update, resolve)
- AI ticket analysis (summary, sentiment, suggested steps)
- REST API (for chatbot / external integrations)
- SQLite database (easy local setup)

---

## ✨ Key Features

### 👩‍💻 Employee Side
- Login / Signup
- Raise a new ticket (subject, description, priority)
- Auto category detection
- View ticket history and status
- Basic chatbot support

### 🧑‍💼 Admin / Agent Side
- Agent login
- Dashboard to view all tickets
- Assign tickets to admins/agents
- Update ticket status (open → in-progress → resolved)
- Add remarks
- Manage categories

### 🤖 AI + Automation
- AI-powered ticket analysis using **Llama 3.1 (NVIDIA API)**
- Sentiment detection (Neutral / Positive / Negative)
- Suggested troubleshooting steps
- Redis caching for faster repeated queries (optional)

### 🔌 REST API
- Create tickets via API (auto-classification)
- Get ticket details
- List tickets (with pagination support)
- Update ticket status

---

## 🧰 Tech Stack

### Backend
- **Python**
- **Flask** (Web App + REST API)
- **Flask-SQLAlchemy** (ORM)
- **Flask-Login** (Authentication)
- **Flask-CORS** (Cross-origin support)

### Database
- **SQLite** (local DB stored in `/instance/`)

### AI / NLP
- **OpenAI Python SDK (AsyncOpenAI)**  
  (Used with NVIDIA Integrate API endpoint)
- **Llama 3.1 8B Instruct** (`meta/llama-3.1-8b-instruct`)
- **Redis** (optional caching)

### Frontend
- **HTML, CSS, JavaScript**
- Flask Templates (`/templates`)
- Static assets (`/static`)

### Email / Notifications
- **SendGrid API** (email support)

### Deployment / Server
- **Waitress** (production WSGI server)

---

## 📂 Project Structure

```bash
sih-helpdesk_4/
│
├── app.py                 # Main Flask web application
├── api_app.py             # Standalone REST API server
├── api_routes.py          # API endpoints
├── api_models.py          # API DB models
├── api_classifier.py      # Keyword-based ticket classifier
│
├── ai_engine.py           # LLM ticket analysis (summary/sentiment/steps)
├── chatbot.py             # AI chatbot logic (Llama 3.1)
│
├── models.py              # Web app DB models (User, Ticket, Category)
├── extensions.py          # db + login manager
│
├── templates/             # HTML templates
├── static/                # CSS + images
│
├── instance/
│   └── sih_helpdesk.db    # SQLite DB (local)
│
├── requirements_api.txt   # API dependencies
└── API_README.md          # Detailed REST API docs
```

---

## ⚙️ Setup & Installation (Local)

### 1) Extract project
```bash
unzip sih-helpdesk_4.zip
cd sih-helpdesk_4
```

### 2) Create virtual environment (recommended)
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

### 3) Install dependencies
> The repo contains `requirements_api.txt` for API mode.
```bash
pip install -r requirements_api.txt
```

> Note: The full web app (`app.py`) uses extra libraries like SendGrid, APScheduler, Redis, Pydantic, OpenAI SDK, etc.

---

## ▶️ Running the Project

## A) Run the REST API Server
```bash
python api_app.py
```

API runs at:
- `http://127.0.0.1:8000`

---

## B) Run the Full Web Application
```bash
python app.py
```

Web app runs at:
- `http://127.0.0.1:5000`

---

## 🔑 Environment Variables

Create a `.env` file (or set system env vars):

```env
# AI (NVIDIA Integrate API)
NVIDIA_API_KEY=your_key_here
REDIS_URL=redis://localhost:6379

# Optional: email
SENDGRID_API_KEY=your_sendgrid_key_here
```

> ⚠️ Security note: Do not commit API keys to GitHub.

---

## 🤖 AI Flow (How it Works)

### Ticket Analysis (LLM)
When a ticket is created, the system can call:
- `analyze_ticket_with_llm()` from `ai_engine.py`

It generates:
- **Summary**
- **Sentiment**
- **Suggested Steps**

Model used:
- **Llama 3.1 8B Instruct** via NVIDIA Integrate API.

### Ticket Classification (API)
The REST API uses a fast keyword-based classifier:
- `TicketClassifier` in `api_classifier.py`

Categories include:
- Network
- Application
- Hardware
- Access
- Software

---

## 📡 REST API Documentation

The API is documented in:  
📄 `API_README.md`

### Base URL
```
http://127.0.0.1:8000/api
```

### Endpoints

#### 1) Create Ticket
`POST /tickets`

Request:
```json
{
  "title": "VPN not connecting",
  "description": "Unable to connect to office VPN from home",
  "source": "chatbot",
  "urgency": "High"
}
```

Response:
```json
{
  "status": "success",
  "ticket": {
    "ticket_id": "IT-2026-001",
    "category": "Network",
    "assigned_team": "NetworkTeam",
    "status": "open"
  }
}
```

#### 2) Get Ticket by ID
`GET /tickets/<ticket_id>`

#### 3) List Tickets
`GET /tickets?page=1&limit=10`

#### 4) Update Ticket Status
`PATCH /tickets/<ticket_id>`

Example:
```json
{
  "status": "resolved"
}
```

#### 5) Health Check
`GET /health`

---

## 🗄️ Database

### Web App Tables
- `users`
- `tickets`
- `categories`
- `admin_categories`

### API Tables
- `api_tickets`

SQLite DB is stored in:
- `instance/sih_helpdesk.db`

---

## 🧪 Testing

### API Testing
- Open `test_api.html` in browser (mentioned in `API_README.md`)
- Or use Postman

---

## 🚀 Deployment Notes

- The API is production-ready with **Waitress**
- CORS enabled for frontend integrations
- Can be deployed on Render / Railway / VPS

---

## 👥 Team / SIH

This project was built for **Smart India Hackathon (SIH)** as a smart IT helpdesk automation solution.

---

## 📜 License
This project is for academic / hackathon use.
