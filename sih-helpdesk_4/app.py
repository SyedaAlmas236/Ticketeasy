import os
import sys
import io

# CRITICAL: Force UTF-8 for Windows console to prevent UnicodeEncodeError
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

import secrets
import asyncio
from datetime import datetime
from pathlib import Path
from functools import wraps
from inspect import iscoroutinefunction

# --- IMPORT CHATBOT ---
from chatbot import get_chat_response

from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_cors import CORS
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content
from apscheduler.schedulers.background import BackgroundScheduler
import atexit

from extensions import db
from models import User, Ticket, Category, AdminCategories
from ai_engine import analyze_ticket_with_llm

# ------------------ APP INIT ------------------
app = Flask(__name__, static_folder="static")
CORS(app)
app.secret_key = secrets.token_hex(24)

BASE_DIR = Path(__file__).resolve().parent
instance_dir = BASE_DIR / "instance"
instance_dir.mkdir(exist_ok=True)
db_path = instance_dir / "sih_helpdesk.db"

app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path.as_posix()}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

AUTO_VERIFY_REGISTRATION = True
SUPER_ADMIN_EMAIL = "rajeevkulkarni1111@gmail.com"
SENDGRID_API_KEY = os.getenv(
    "SENDGRID_API_KEY",
    "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",
)
FROM_EMAIL = os.getenv("FROM_EMAIL", "rajeevsendgrid@gmail.com")


# ------------------ HELPER FUNCTIONS ------------------
def is_valid_email_domain(email):
    ALLOWED_DOMAINS = ["gmail.com", "hotmail.com", "zoho.com", "outlook.com", "yahoo.com", "live.com"]
    try:
        if "@" not in email:
            return False
        domain = email.split("@")[1].lower().strip()
        return domain in ALLOWED_DOMAINS
    except IndexError:
        return False


def send_raw_email(to_email, subject, body):
    api_key = SENDGRID_API_KEY.strip()
    from_addr = FROM_EMAIL.strip()
    to_addr = to_email.strip()
    if not api_key or "SG." not in api_key:
        return
    message = Mail(
        from_email=Email(from_addr),
        to_emails=To(to_addr),
        subject=subject,
        plain_text_content=Content("text/plain", body),
    )
    try:
        sg = SendGridAPIClient(api_key)
        sg.send(message)
    except Exception:
        pass


def notify_status_change(ticket, recipient_email, type="update"):
    user_name = ticket.creator.name if ticket.creator else "User"
    if type == "new_agent":
        subject = f"[Action Required] New Ticket #{ticket.id}: {ticket.subject}"
        body = f"New Ticket Assigned!\n\nID: #{ticket.id}\nPriority: {ticket.priority}\nDescription:\n{ticket.description}\n\nPlease review on dashboard."
    elif type == "new_user":
        subject = f"[Ticket #{ticket.id}] Received: {ticket.subject}"
        body = f"Hello {user_name},\n\nWe have received your ticket.\nID: #{ticket.id}\nStatus: {ticket.status}\n\nAn admin will review shortly."
    elif type == "update":
        subject = f"[Update] Ticket #{ticket.id} is now {ticket.status.upper()}"
        body = f"Hello {user_name},\n\nYour ticket status is now: {ticket.status.upper()}.\nSubject: {ticket.subject}"
    else:
        return
    send_raw_email(recipient_email, subject, body)


# ---------------------------------------------------------
#  ROUTING ALGORITHM: AGENT FOCUS + LEAST LOADED
# ---------------------------------------------------------
def get_best_agent_least_loaded(category_obj):
    admins = (
        db.session.query(User)
        .join(AdminCategories)
        .filter(
            User.role.in_(["agent", "admin"]),
            AdminCategories.category_id == category_obj.id,
        )
        .all()
    )

    if not admins:
        return None

    scored_admins = []

    for admin in admins:
        active_count = Ticket.query.filter(
            Ticket.assigned_admin_id == admin.id,
            Ticket.status.in_(["open", "in-progress"]),
        ).count()

        resolved_count = Ticket.query.filter(
            Ticket.assigned_admin_id == admin.id, Ticket.status == "resolved"
        ).count()

        scored_admins.append({"admin": admin, "open": active_count, "resolved": resolved_count})

    scored_admins.sort(key=lambda x: (x["open"], x["resolved"]))

    best_match = scored_admins[0]
    best_admin = best_match["admin"]

    return best_admin


def generate_daily_report():
    with app.app_context():
        tickets = Ticket.query.all()
        categories = ["software", "hardware", "network", "database"]
        total = len(tickets)
        urgent = len([t for t in tickets if t.priority == "high"])
        lines = [
            f"DAILY REPORT - {datetime.now().strftime('%Y-%m-%d')}",
            "=" * 40,
            f"TOTAL: {total}",
            f"URGENT: {urgent}",
            "-" * 30,
        ]
        for cat in categories:
            ct = [t for t in tickets if (t.category or "").lower() == cat]
            lines.append(
                f"{cat.upper()}: Open {len([t for t in ct if t.status=='open'])} | Resolved {len([t for t in ct if t.status=='resolved'])}"
            )
        send_raw_email(SUPER_ADMIN_EMAIL, "Daily Helpdesk Summary", "\n".join(lines))


# ------------------ DECORATORS ------------------
def login_required(fn):
    if iscoroutinefunction(fn):
        @wraps(fn)
        async def async_wrapper(*args, **kwargs):
            if not session.get("user"):
                return redirect(url_for("auth", tab="login"))
            return await fn(*args, **kwargs)
        return async_wrapper
    else:
        @wraps(fn)
        def sync_wrapper(*args, **kwargs):
            if not session.get("user"):
                return redirect(url_for("auth", tab="login"))
            return fn(*args, **kwargs)
        return sync_wrapper


def agent_required(fn):
    if iscoroutinefunction(fn):
        @wraps(fn)
        async def async_wrapper(*args, **kwargs):
            u = session.get("user")
            if not u or u.get("role") not in ["agent", "manager", "admin", "super_admin"]:
                return redirect(url_for("agent_login"))
            return await fn(*args, **kwargs)
        return async_wrapper
    else:
        @wraps(fn)
        def sync_wrapper(*args, **kwargs):
            u = session.get("user")
            if not u or u.get("role") not in ["agent", "manager", "admin", "super_admin"]:
                return redirect(url_for("agent_login"))
            return fn(*args, **kwargs)
        return sync_wrapper


# ---------------- ROUTES -------------------
@app.route("/")
def landing():
    return render_template("landing.html")


@app.route("/auth")
def auth():
    tab = request.args.get("tab", "login")
    role = request.args.get("role")
    if tab == "register" and role:
        return redirect(url_for("register_agent" if role.lower() in ["agent", "admin"] else "register_employee"))
    return render_template("auth.html", tab=tab)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return redirect(url_for("auth", tab="login"))
    email = (request.form.get("email") or "").strip().lower()
    password = request.form.get("password") or ""
    if not is_valid_email_domain(email):
        flash("Restricted domain.", "error")
        return redirect(url_for("auth", tab="login"))
    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        flash("Invalid credentials.", "error")
        return redirect(url_for("auth", tab="login"))
    session["user"] = {
        "email": user.email,
        "name": user.name,
        "role": user.role,
        "employee_role": user.employee_role,
    }

    if user.email == SUPER_ADMIN_EMAIL or user.role == "super_admin":
        return redirect(url_for("super_admin_dashboard"))
    elif user.role in ["admin", "manager", "agent"]:
        return redirect(url_for("agent_dashboard"))
    else:
        return redirect(url_for("employee_home"))


@app.route("/agent/login", methods=["GET", "POST"])
def agent_login():
    if request.method == "GET":
        return render_template("agent_login.html")
    email = (request.form.get("email") or "").strip().lower()
    password = request.form.get("password") or ""

    user = User.query.filter(
        User.email == email,
        User.role.in_(["admin", "agent", "manager", "super_admin"]),
    ).first()

    if not user or not user.check_password(password):
        return redirect(url_for("agent_login"))
    session["user"] = {"email": user.email, "name": user.name, "role": user.role}

    if user.role == "super_admin" or user.email == SUPER_ADMIN_EMAIL:
        return redirect(url_for("super_admin_dashboard"))

    return redirect(url_for("agent_dashboard"))


@app.route("/register/employee", methods=["GET", "POST"])
def register_employee():
    if request.method == "GET":
        return render_template("register_employee.html")
    email = (request.form.get("email") or "").strip().lower()
    if User.query.filter_by(email=email).first():
        return redirect(url_for("auth", tab="login"))
    new_user = User(
        email=email,
        name=request.form.get("name"),
        role="employee",
        employee_role=request.form.get("employee_role"),
        verified=AUTO_VERIFY_REGISTRATION,
    )
    new_user.set_password(request.form.get("password"))
    db.session.add(new_user)
    db.session.commit()
    return redirect(url_for("auth", tab="login"))


@app.route("/register/agent", methods=["GET", "POST"])
def register_agent():
    if request.method == "GET":
        return render_template("register_agent.html", categories=Category.query.all())
    email = (request.form.get("email") or "").strip().lower()
    if User.query.filter_by(email=email).first():
        return redirect(url_for("auth", tab="login"))

    new_agent = User(
        email=email,
        name=request.form.get("name"),
        role="agent",
        verified=True,
    )
    new_agent.set_password(request.form.get("password"))
    db.session.add(new_agent)
    db.session.commit()
    db.session.add(
        AdminCategories(admin_id=new_agent.id, category_id=int(request.form.get("category_id")))
    )
    db.session.commit()
    return redirect(url_for("agent_login"))


@app.route("/employee/home")
@login_required
def employee_home():
    user = session.get("user")
    if user.get("role") in ["admin", "manager", "agent"]:
        return redirect(url_for("agent_dashboard"))

    db_user = User.query.filter_by(email=user["email"]).first()
    if not db_user:
        flash("DB user missing.", "error")
        return redirect(url_for("logout"))

    total_tickets = Ticket.query.filter_by(created_by_id=db_user.id).count()
    open_count = Ticket.query.filter_by(created_by_id=db_user.id, status="open").count()
    inprog_count = Ticket.query.filter_by(created_by_id=db_user.id, status="in-progress").count()
    resolved_count = Ticket.query.filter_by(created_by_id=db_user.id, status="resolved").count()

    stats = {
        "total": total_tickets,
        "open": open_count,
        "in_progress": inprog_count,
        "resolved": resolved_count,
    }

    recent = db_user.created_tickets
    recent.sort(key=lambda x: x.created_at, reverse=True)
    recent = recent[:10]

    return render_template("employee_home.html", user=user, stats=stats, recent=recent)


@app.route("/employee/history")
@login_required
def emp_history():
    user = session.get("user")
    db_user = User.query.filter_by(email=user["email"]).first()
    tickets = Ticket.query.filter_by(created_by_id=db_user.id).order_by(Ticket.created_at.desc()).all()
    return render_template("emp_history.html", tickets=tickets, user=user)


@app.route("/tickets/new", methods=["GET", "POST"])
@login_required
async def raise_ticket():
    user_session = session.get("user")
    db_user = User.query.filter_by(email=user_session["email"]).first()
    if request.method == "GET":
        return render_template("raise_ticket.html", user=user_session)

    subject = request.form.get("subject")
    description = request.form.get("description")

    try:
        analysis = await analyze_ticket_with_llm(subject, description)
    except Exception:
        class Fallback:
            category = "software"
            priority = "medium"
            sentiment = "Neutral"
            suggested_steps = ""
        analysis = Fallback()

    category_obj = Category.query.filter_by(name=getattr(analysis, "category", None)).first() or Category.query.first()

    assigned_agent = get_best_agent_least_loaded(category_obj)

    if not assigned_agent:
        assigned_agent = User.query.filter(User.role.in_(["admin", "manager"])).first()

    ticket = Ticket(
        subject=subject,
        description=description,
        priority=getattr(analysis, "priority", "medium"),
        status="open",
        category=category_obj.name if category_obj else "software",
        category_id=category_obj.id if category_obj else None,
        creator=db_user,
        assigned_admin_id=assigned_agent.id if assigned_agent else None,
        sentiment=getattr(analysis, "sentiment", ""),
        suggested_steps=getattr(analysis, "suggested_steps", ""),
    )
    db.session.add(ticket)
    db.session.commit()

    try:
        if assigned_agent and assigned_agent.email:
            notify_status_change(ticket, assigned_agent.email, type="new_agent")
    except Exception:
        pass

    try:
        if db_user.email:
            notify_status_change(ticket, db_user.email, type="new_user")
    except Exception:
        pass

    admin_name = assigned_agent.name if assigned_agent else "IT Support"
    if getattr(analysis, "sentiment", "") == "Furious":
        flash(f"Critical Priority! Assigned to {admin_name} for immediate review.", "error")
    else:
        flash(f"Ticket Created! Successfully assigned to {admin_name}.", "success")

    return redirect(url_for("employee_home"))


@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_message = (data.get("message") or "").strip()
    history = data.get("history", [])
    if not user_message:
        return jsonify({"response": "Say something!"})

    try:
        bot_reply = asyncio.run(get_chat_response(user_message, history))
        return jsonify({"response": bot_reply["text"], "redirect": bot_reply.get("redirect")})
    except Exception:
        return jsonify({"response": "System Error.", "redirect": None})


@app.route("/dashboard")
@login_required
def dashboard():
    return redirect(url_for("employee_home"))


@app.route("/agent/dashboard")
@agent_required
def agent_dashboard():
    agent_session = session.get("user")
    db_agent = User.query.filter_by(email=agent_session["email"]).first()

    if db_agent.role == "manager":
        cat_link = AdminCategories.query.filter_by(admin_id=db_agent.id).first()
        if cat_link:
            tickets = Ticket.query.filter_by(category_id=cat_link.category_id).order_by(Ticket.created_at.desc()).all()
        else:
            tickets = []
    else:
        tickets = Ticket.query.filter_by(assigned_admin_id=db_agent.id).order_by(Ticket.created_at.desc()).all()

    stats = {
        "total": len(tickets),
        "open": len([t for t in tickets if t.status == "open"]),
        "in_progress": len([t for t in tickets if t.status == "in-progress"]),
        "resolved": len([t for t in tickets if t.status == "resolved"]),
        "high": len([t for t in tickets if t.priority == "high"]),
        "medium": len([t for t in tickets if t.priority == "medium"]),
        "low": len([t for t in tickets if t.priority == "low"]),
    }

    return render_template("agent_dashboard.html", admin=db_agent, tickets=tickets, stats=stats)


@app.route("/super-admin")
@login_required
def super_admin_dashboard():
    tickets = Ticket.query.order_by(Ticket.created_at.desc()).all()

    stats = {
        "total": len(tickets),
        "open": len([t for t in tickets if t.status == "open"]),
        "in_progress": len([t for t in tickets if t.status == "in-progress"]),
        "resolved": len([t for t in tickets if t.status == "resolved"]),
        "software": len([t for t in tickets if (t.category or "").lower() == "software"]),
        "hardware": len([t for t in tickets if (t.category or "").lower() == "hardware"]),
        "network": len([t for t in tickets if (t.category or "").lower() == "network"]),
        "database": len([t for t in tickets if (t.category or "").lower() == "database"]),
    }

    return render_template("super_dashboard.html", admin=session["user"], tickets=tickets, stats=stats)


@app.route("/ticket/<int:ticket_id>")
@login_required
def ticket_detail(ticket_id):
    t = Ticket.query.get_or_404(ticket_id)
    return render_template("ticket_detail.html", ticket=t, user=session["user"])


@app.route("/ticket/<int:ticket_id>/update", methods=["POST"])
@agent_required
def ticket_update(ticket_id):
    t = Ticket.query.get_or_404(ticket_id)
    old_status = t.status
    new_status = request.form.get("status") or t.status
    remarks = (request.form.get("remarks") or "").strip()

    if new_status in ["in-progress", "resolved"] and not remarks:
        flash("Remarks are required to update status to In Progress or Resolved.", "error")
        return redirect(url_for("ticket_detail", ticket_id=ticket_id))

    t.status = new_status
    t.priority = request.form.get("priority") or t.priority
    if remarks:
        t.remarks = remarks

    db.session.commit()
    if old_status != t.status:
        try:
            notify_status_change(t, t.creator.email, type="update")
        except Exception:
            pass
    return redirect(url_for("ticket_detail", ticket_id=ticket_id))


@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("landing"))


def setup_database():
    with app.app_context():
        db.create_all()
        for c in ["software", "hardware", "network", "database"]:
            if not Category.query.filter_by(name=c).first():
                db.session.add(Category(name=c))
        db.session.commit()


if __name__ == "__main__":
    setup_database()
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=generate_daily_report, trigger="cron", hour=18, minute=0)
    scheduler.start()
    atexit.register(lambda: scheduler.shutdown())
    
    # START WITH WAITRESS (production server) to avoid console encoding issues
    print("=" * 50)
    print("SIH Helpdesk Server Starting...")
    print("Server: http://127.0.0.1:5000")
    print("Press CTRL+C to stop")
    print("=" * 50)
    
    try:
        from waitress import serve
        serve(app, host='127.0.0.1', port=5000, threads=4)
    except ImportError:
        print("WARNING: Install waitress for better performance: pip install waitress")
        print("Falling back to Flask dev server (may have console issues)")
        app.run(debug=False, port=5000, use_reloader=False)
