from backend.app import app, db
from backend.storage import Feedback, Result, Institute
import uuid
from datetime import datetime
import json

def seed_sql_data():
    with app.app_context():
        print("Creating tables if not exist...")
        db.create_all()
        
        # Ensure Default Institute Exists
        default_inst = Institute.query.get('Default')
        if not default_inst:
            print("Creating Default Institute...")
            default_inst = Institute(
                id='Default',
                name='Default Institute',
                address='123 Main St',
                email='admin@default.edu',
                admin_id='admin',
                password='admin', # Insecure, for dev only
                created_at=datetime.now().isoformat()
            )
            db.session.add(default_inst)
            db.session.commit()
        
        # Clear existing? Maybe not, or yes for clean state.
        # db.session.query(Feedback).delete()
        # db.session.query(AnalysisResult).delete()
        
        feedbacks_data = [
            {"role": "Student", "category": "course_content", "text": "The new AI curriculum is fantastic! Loving the hands-on labs.", "sentiment": "Positive"},
            {"role": "Student", "category": "course_content", "text": "Great explanation of Neural Networks in Prof. Smith's class.", "sentiment": "Positive"},
            {"role": "Student", "category": "facilities", "text": "The cafeteria food hygiene is really bad. I found an insect in my meal.", "sentiment": "Negative"},
            {"role": "Student", "category": "facilities", "text": "Food poisoning cases are rising. Please check the mess kitchen immediately.", "sentiment": "Negative"},
            {"role": "Student", "category": "facilities", "text": "Mess food quality has degraded significantly this week.", "sentiment": "Negative"},
            {"role": "Faculty", "category": "facilities", "text": "Projector in Lab 3 is flickering constantly. Hinders lectures.", "sentiment": "Negative"},
            {"role": "Faculty", "category": "facilities", "text": "We need more whiteboard markers in the staff room.", "sentiment": "Neutral"},
            {"role": "Staff", "category": "harassment", "text": "Corridor lights near the library are out. Safety concern at night.", "sentiment": "Negative"},
            {"role": "Student", "category": "exams", "text": "Exam schedule is too tight. Two major papers in one day.", "sentiment": "Negative"},
        ]

        print(f"Seeding {len(feedbacks_data)} feedbacks...")
        for f in feedbacks_data:
            fb = Feedback(
                id=str(uuid.uuid4()),
                role=f['role'],
                user_id='Anonymous',
                user_name='Anonymous',
                is_verified=False,
                institute_id='Default',
                category=f['category'],
                text=f['text'],
                timestamp=datetime.now(),
                processed=False # Crucial for analysis pick-up
            )
            db.session.add(fb)
        
        db.session.commit()
        print("Seeding Complete.")

if __name__ == "__main__":
    seed_sql_data()
