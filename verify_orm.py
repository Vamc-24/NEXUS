import sys
import os
from flask import Flask

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from backend.storage import db, SQLAlchemyStorage

def verify_orm():
    print("\n--- VERIFYING SQLALCHEMY ORM ---")
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:' # Test in memory
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    
    with app.app_context():
        # 1. Create Tables
        db.create_all()
        print("[SUCCESS] Tables Created.")
        
        storage = SQLAlchemyStorage(db)
        
        # 2. Register
        try:
            inst_id = storage.register_institute({
                'name': 'ORM Tech',
                'code': 'ORM_001',
                'admin_id': 'admin',
                'password': 'pass'
            })
            print(f"[SUCCESS] Registered: {inst_id}")
        except Exception as e:
            print(f"[ERROR] Reg failed: {e}")
            return

        # 3. Add Feedback
        try:
            fb = storage.add_feedback({
                'institute_id': inst_id,
                'text': 'ORM works!',
                'role': 'Student',
                'category': 'Tech'
            })
            print(f"[SUCCESS] Feedback Added: {fb['id']}")
        except Exception as e:
            print(f"[ERROR] Feedback failed: {e}")
            return

        # 4. Stats
        stats = storage.get_feedback_stats(inst_id)
        print(f"[SUCCESS] Stats: {stats}")

    print("--- ORM VERIFIED ---")

if __name__ == '__main__':
    verify_orm()
