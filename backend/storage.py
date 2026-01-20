import json
import uuid
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import joinedload

db = SQLAlchemy()

# --- Models ---
class Institute(db.Model):
    __tablename__ = 'institutes'
    id = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.Text)
    email = db.Column(db.String(100))
    admin_id = db.Column(db.String(50))
    password = db.Column(db.String(200)) # Simple text for now, should be hash
    created_at = db.Column(db.String(50))

    # Relationships
    feedbacks = db.relationship('Feedback', backref='institute', lazy=True)
    results = db.relationship('Result', backref='institute', lazy=True)

class Feedback(db.Model):
    __tablename__ = 'feedback'
    id = db.Column(db.String(50), primary_key=True)
    institute_id = db.Column(db.String(50), db.ForeignKey('institutes.id'), nullable=False)
    text = db.Column(db.Text)
    category = db.Column(db.String(50))
    role = db.Column(db.String(50))
    user_id = db.Column(db.String(50))
    user_name = db.Column(db.String(100))
    is_verified = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.String(50))
    processed = db.Column(db.Boolean, default=False)
    status = db.Column(db.String(20))
    session = db.Column(db.String(50))

class Result(db.Model):
    __tablename__ = 'results'
    id = db.Column(db.String(50), primary_key=True)
    institute_id = db.Column(db.String(50), db.ForeignKey('institutes.id'), nullable=False)
    clusters = db.Column(db.Text) # JSON String
    timestamp = db.Column(db.String(50))

# --- Abstract Base ---
class StorageBase:
    def add_feedback(self, data): raise NotImplementedError
    def get_unprocessed_feedback(self, institute_id=None): raise NotImplementedError
    def mark_processed(self, feedback_ids): raise NotImplementedError
    def save_clusters(self, institute_id, clusters): raise NotImplementedError
    def get_latest_results(self, institute_id=None): raise NotImplementedError
    def register_institute(self, data): raise NotImplementedError
    def verify_institute(self, institute_id): raise NotImplementedError
    def register_admin(self, institute_id, admin_id, password): raise NotImplementedError
    def verify_admin(self, admin_id, password): raise NotImplementedError
    def get_feedback_stats(self, institute_id=None): raise NotImplementedError

# --- Implementation ---
class SQLAlchemyStorage(StorageBase):
    def __init__(self, db_instance):
        self.db = db_instance

    def register_institute(self, data):
        code = data.get('code')
        if not code:
            code = f"INST_{str(uuid.uuid4())[:6].upper()}"

        existing = Institute.query.filter_by(id=code).first()
        if existing:
            raise ValueError("Institute ID already exists")

        new_inst = Institute(
            id=code,
            name=data.get('name'),
            address=data.get('address'),
            email=data.get('email'),
            admin_id=data.get('admin_id'),
            password=data.get('password'),
            created_at=datetime.now().isoformat()
        )
        self.db.session.add(new_inst)
        self.db.session.commit()
        return code

    def verify_institute(self, institute_id):
        inst = Institute.query.get(institute_id)
        if inst:
            return {'valid': True, 'name': inst.name}
        return {'valid': False}

    def register_admin(self, institute_id, admin_id, password):
        inst = Institute.query.get(institute_id)
        if not inst: return False
        inst.admin_id = admin_id
        inst.password = password
        self.db.session.commit()
        return True

    def verify_admin(self, admin_id, password):
        inst = Institute.query.filter_by(admin_id=admin_id, password=password).first()
        if inst:
            return {'valid': True, 'institute_name': inst.name, 'institute_id': inst.id}
        return {'valid': False}

    def add_feedback(self, data):
        inst_id = data.get('institute_id', 'Default')
        # Ensure institute exists if strict, but let's be loose or ensure Default exists?
        # For SQL, foreign key fails if not exists.
        # We assume Institute is registered properly.
        
        new_id = str(uuid.uuid4())
        fb = Feedback(
            id=new_id,
            institute_id=inst_id,
            text=data.get('text'),
            category=data.get('category'),
            role=data.get('role', 'Anonymous'),
            user_id=data.get('user_id', 'N/A'),
            user_name=data.get('user_name', 'Anonymous'),
            is_verified=data.get('is_verified', False),
            timestamp=data.get('timestamp') or datetime.now().isoformat(),
            processed=False,
            status='pending',
            session=data.get('session', 'Default Session')
        )
        self.db.session.add(fb)
        self.db.session.commit()
        return {'id': new_id, 'institute_id': inst_id, 'status': 'pending'}

    def get_unprocessed_feedback(self, institute_id=None):
        query = Feedback.query.filter_by(processed=False)
        if institute_id:
            query = query.filter_by(institute_id=institute_id)
        results = query.all()
        
        # Convert to dicts
        return [{
            'id': r.id, 'text': r.text, 'category': r.category, 
            'role': r.role, 'timestamp': r.timestamp, 'institute_id': r.institute_id
        } for r in results]

    def get_all_feedback(self, institute_id=None):
        query = Feedback.query
        if institute_id:
            query = query.filter_by(institute_id=institute_id)
        
        # Sort by timestamp desc (if possible, but string timestamp needs care, assuming ISO format sorts okay or just reverse list)
        feedbacks = query.all()
        
        return [{
            'id': r.id, 'text': r.text, 'category': r.category, 
            'role': r.role, 'timestamp': r.timestamp, 'institute_id': r.institute_id
        } for r in feedbacks[::-1]] # Reverse to show newest first

    def mark_processed(self, feedback_ids):
        if not feedback_ids: return
        Feedback.query.filter(Feedback.id.in_(feedback_ids)).update(
            {Feedback.processed: True, Feedback.status: 'processed'},
            synchronize_session=False
        )
        self.db.session.commit()

    def get_feedback_stats(self, institute_id=None):
        query = Feedback.query
        if institute_id:
            query = query.filter_by(institute_id=institute_id)
        
        feedbacks = query.all()
        count = len(feedbacks)
        roles = {}
        categories = {}
        
        for f in feedbacks:
            r = f.role or 'Unknown'
            c = f.category or 'Other'
            roles[r] = roles.get(r, 0) + 1
            categories[c] = categories.get(c, 0) + 1
            
        # Get recent 5
        recent = [{
            'text': f.text[:50] + '...',
            'role': f.role,
            'category': f.category,
            'timestamp': f.timestamp
        } for f in feedbacks[-5:][::-1]]

        return {'total': count, 'roles': roles, 'categories': categories, 'recent': recent}

    def save_clusters(self, institute_id, clusters):
        new_id = str(uuid.uuid4())
        res = Result(
            id=new_id,
            institute_id=institute_id,
            clusters=json.dumps(clusters),
            timestamp=datetime.now().isoformat()
        )
        self.db.session.add(res)
        self.db.session.commit()

    def get_latest_results(self, institute_id=None):
        query = Result.query
        if institute_id:
            query = query.filter_by(institute_id=institute_id)
        
        res = query.order_by(Result.timestamp.desc()).first()
        if res:
            return {'clusters': json.loads(res.clusters)}
        return {'clusters': []}


    def get_global_stats(self):
        # Real-time counts
        data_points = Feedback.query.count()
        institutes_count = Institute.query.count()
        # Estimate students based on feedback or just return total feedback from students
        active_students = Feedback.query.filter_by(role='Student').count()

        return {
            'data_points': data_points, 
            'institutes': institutes_count, 
            'students': active_students
        }

# Factory removed - app.py should instantiate
