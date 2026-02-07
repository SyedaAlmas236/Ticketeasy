BEGIN TRANSACTION;

-- 1. Create categories table
CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(80) UNIQUE
);

-- Insert default categories
INSERT OR IGNORE INTO categories (name) VALUES
('software'),
('hardware'),
('network'),
('knowledge');

---------------------------------------------------------

-- 2. Create admin_categories mapping table
CREATE TABLE IF NOT EXISTS admin_categories (
    admin_id INTEGER NOT NULL,
    category_id INTEGER NOT NULL,
    PRIMARY KEY (admin_id, category_id),
    FOREIGN KEY (admin_id) REFERENCES users(id),
    FOREIGN KEY (category_id) REFERENCES categories(id)
);

---------------------------------------------------------

-- 3. Add assigned_admin_id to tickets table
ALTER TABLE tickets ADD COLUMN assigned_admin_id INTEGER REFERENCES users(id);

---------------------------------------------------------

-- 4. Convert old TEXT category → category_id
-- Create new table with correct schema
CREATE TABLE tickets_new (
    id INTEGER PRIMARY KEY,
    subject VARCHAR(255),
    description TEXT,
    priority VARCHAR(20),
    status VARCHAR(30),
    category VARCHAR(80),
    category_id INTEGER,
    created_by_id INTEGER,
    created_at DATETIME,
    assigned_admin_id INTEGER,
    FOREIGN KEY (category_id) REFERENCES categories(id),
    FOREIGN KEY (assigned_admin_id) REFERENCES users(id)
);

-- Copy old data
INSERT INTO tickets_new (id, subject, description, priority, status, category, created_by_id, created_at)
SELECT id, subject, description, priority, status, category, created_by_id, created_at FROM tickets;

---------------------------------------------------------

-- 5. Fill category_id using old text category
UPDATE tickets_new
SET category_id = (SELECT id FROM categories WHERE LOWER(name) = LOWER(category))
WHERE category IS NOT NULL;

---------------------------------------------------------

-- 6. Replace old table
ALTER TABLE tickets RENAME TO tickets_old;
ALTER TABLE tickets_new RENAME TO tickets;

-- Keep old table as backup (developer can delete later)

COMMIT;
