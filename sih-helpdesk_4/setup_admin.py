from app import app
from extensions import db
from models import User, Category, AdminCategories

def create_dept_manager(email, name, password, category_name):
    """
    Creates a user with role='manager' and links them to a category.
    This user will see ALL tickets in that category.
    """
    with app.app_context():
        # 1. Find or Create the User
        user = User.query.filter_by(email=email).first()
        
        if user:
            print(f"[WARN] User {email} already exists.")
            # Optional: Promote them if they are just an agent/admin
            if user.role != 'manager':
                user.role = 'manager'
                print(f"   -> PROMOTED {user.name} to MANAGER.")
        else:
            # Create new Manager
            user = User(email=email, name=name, role='manager', verified=True)
            user.set_password(password)
            db.session.add(user)
            print(f"[OK] Created New Manager: {name}")
        
        db.session.commit()

        # 2. Link to the Category (Critical for the Dashboard to work)
        category = Category.query.filter_by(name=category_name).first()
        if not category:
            print(f"[ERROR] Error: Category '{category_name}' does not exist! (Check spelling)")
            return

        # Check if link already exists
        link = AdminCategories.query.filter_by(admin_id=user.id, category_id=category.id).first()
        if not link:
            new_link = AdminCategories(admin_id=user.id, category_id=category.id)
            db.session.add(new_link)
            db.session.commit()
            print(f"[LINK] Linked {name} to {category_name} Department.")
        else:
            print(f"[INFO] {name} is already linked to {category_name}.")

        print("\nSUCCESS! Login credentials:")
        print(f"Email: {email}")
        print(f"Pass:  {password}")

if __name__ == "__main__":
    # --- EDIT THIS SECTION TO CREATE YOUR MANAGER ---
    create_dept_manager(
        email="techslayers4200@gmail.com", 
        name="Software_Dept_Head", 
        password="123", 
        category_name="software"  # Options: software, hardware, network, database
    )