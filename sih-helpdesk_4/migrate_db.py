import sqlite3
from pathlib import Path

# Connect to the database
base_dir = Path(__file__).resolve().parent
db_path = base_dir / "instance" / "sih_helpdesk.db"
print(f"Connecting to database at: {db_path}")

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if column exists
    cursor.execute("PRAGMA table_info(tickets)")
    columns = [info[1] for info in cursor.fetchall()]
    
    if "remarks" not in columns:
        print("Adding 'remarks' column to 'tickets' table...")
        cursor.execute("ALTER TABLE tickets ADD COLUMN remarks TEXT")
        conn.commit()
        print("Column added successfully.")
    else:
        print("'remarks' column already exists.")
        
    conn.close()
except Exception as e:
    print(f"Error: {e}")
