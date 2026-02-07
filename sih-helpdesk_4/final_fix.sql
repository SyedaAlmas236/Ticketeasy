BEGIN TRANSACTION;

---------------------------------------------------------
-- 1. Clean category_id values based on old text category
---------------------------------------------------------
UPDATE tickets
SET category_id = (
    SELECT id FROM categories WHERE LOWER(name) = LOWER(tickets.category)
)
WHERE category IS NOT NULL AND category_id IS NULL;

---------------------------------------------------------
-- 2. If category_id is still NULL, set default category (software)
---------------------------------------------------------
UPDATE tickets
SET category_id = (SELECT id FROM categories WHERE name = 'software')
WHERE category_id IS NULL;

---------------------------------------------------------
-- 3. Assign admins automatically based on admin_categories mapping
---------------------------------------------------------
UPDATE tickets
SET assigned_admin_id = (
    SELECT admin_id FROM admin_categories 
    WHERE category_id = tickets.category_id
    LIMIT 1
)
WHERE assigned_admin_id IS NULL;

---------------------------------------------------------
-- 4. Remove extra tables if needed (SAFE DROP)
---------------------------------------------------------
DROP TABLE IF EXISTS tickets_new;
DROP TABLE IF EXISTS tickets_old;

COMMIT;
