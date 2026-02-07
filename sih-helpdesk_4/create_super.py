from app import app
from extensions import db
from models import User

def create_super_admin():
    with app.app_context():
        email = "rajeevkulkarni1111@gmail.com"
        user = User.query.filter_by(email=email).first()
        if user:
            print("Super Admin exists. Updating password...")
            user.set_password("123")
            user.role = "super_admin" # Ensure role is correct
            db.session.commit()
            print(f"SUCCESS: Super Admin password reset to '123' for: {email}")
            return

        super_admin = User(email=email, name="CEO Super Admin", role="super_admin", verified=True)
        super_admin.set_password("123")
        
        db.session.add(super_admin)
        db.session.commit()
        print(f"SUCCESS: Super Admin created: {email}")

if __name__ == "__main__":
    create_super_admin()