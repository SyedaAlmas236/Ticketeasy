import sqlite3
from pathlib import Path

base_dir = Path(__file__).resolve().parent
db_path = base_dir / "instance" / "sih_helpdesk.db"

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("--- LATEST USER ---")
cursor.execute("SELECT id, email, role, name FROM users ORDER BY id DESC LIMIT 1")
user = cursor.fetchone()
if user:
    print(f"User: {user}")
    uid = user[0]
    
    print("\n--- ASSIGNED CATEGORY ---")
    cursor.execute(f"SELECT ac.category_id, c.name FROM admin_categories ac JOIN categories c ON ac.category_id = c.id WHERE ac.admin_id = {uid}")
    cat = cursor.fetchone()
    if cat:
        print(f"Category: {cat[1]} (ID: {cat[0]})")
    else:
        print("No category assigned.")
        
    print("\n--- ASSIGNED TICKETS ---")
    cursor.execute(f"SELECT id, subject, status FROM tickets WHERE assigned_admin_id = {uid}")
    tickets = cursor.fetchall()
    if tickets:
        for t in tickets: print(f"Ticket #{t[0]}: {t[1]} [{t[2]}]")
    else:
        print("No tickets assigned.")
else:
    print("No users found.")

conn.close()
