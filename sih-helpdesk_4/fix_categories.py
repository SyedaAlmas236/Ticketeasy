from app import app
from extensions import db
from models import Category

def remove_unwanted_category():
    with app.app_context():
        # 1. Find the extra category (usually 'knowledge')
        # If you have a different one you want to delete, change the name below.
        cat_to_remove = Category.query.filter_by(name='knowledge').first()
        
        if cat_to_remove:
            print(f"Found unwanted category: {cat_to_remove.name}")
            db.session.delete(cat_to_remove)
            db.session.commit()
            print("[OK] Successfully deleted! You should now have 4.")
        else:
            print("[WARN] Could not find 'knowledge'. Checking what you actually have...")
            
        # 2. Print current categories to verify
        current_cats = Category.query.all()
        print("\n--- Current Categories in DB ---")
        for c in current_cats:
            print(f"- {c.name}")

if __name__ == "__main__":
    remove_unwanted_category()