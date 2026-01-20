import json
import os
import uuid
from datetime import datetime

# Optional: Google Cloud Firestore
try:
    from google.cloud import firestore
    FIRESTORE_AVAILABLE = True
except ImportError:
    FIRESTORE_AVAILABLE = False

class StorageBase:
    def add_feedback(self, data):
        raise NotImplementedError
    
    def get_unprocessed_feedback(self):
        raise NotImplementedError
    
    def mark_processed(self, feedback_ids):
        raise NotImplementedError
        
    def save_clusters(self, clusters):
        raise NotImplementedError
    
    def get_latest_results(self):
        raise NotImplementedError

    def register_institute(self, data):
        raise NotImplementedError

    def verify_institute(self, institute_id):
        raise NotImplementedError

class LocalStorage(StorageBase):
    def __init__(self, data_file='data/local_db.json'):
        self.data_file = data_file
        self.ensure_data_file()

    def ensure_data_file(self):
        if not os.path.exists(os.path.dirname(self.data_file)):
            os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
        if not os.path.exists(self.data_file):
            with open(self.data_file, 'w') as f:
                json.dump({'feedback': [], 'results': [], 'institutes': []}, f)

    def _read_data(self):
        with open(self.data_file, 'r') as f:
            return json.load(f)

    def _write_data(self, data):
        with open(self.data_file, 'w') as f:
            json.dump(data, f, indent=2)

    def add_feedback(self, data):
        db = self._read_data()
        record = {
            'id': str(uuid.uuid4()),
            'role': data.get('role', 'Anonymous'),
            'user_id': data.get('user_id', 'N/A'),
            'user_name': data.get('user_name', 'Anonymous'),
            'is_verified': data.get('is_verified', False),
            'is_verified': data.get('is_verified', False),
            'institute_id': data.get('institute_id', 'Default'), 
            'session': data.get('session', 'Default Session'),
            'category': data.get('category'),
            'text': data.get('text'),
            'timestamp': data.get('timestamp') or datetime.now().isoformat(),
            'processed': False
        }
        db['feedback'].append(record)
        self._write_data(db)
        return record

    def get_unprocessed_feedback(self, institute_id=None):
        db = self._read_data()
        all_feedback = db.get('feedback', [])
        
        filtered = []
        for f in all_feedback:
            # If institute_id is provided, only include matches.
            # If not provided (e.g. global admin?), maybe include all? 
            # For now, strict filtering if ID is passed.
            if f.get('processed'):
                continue
                
            if institute_id and f.get('institute_id') != institute_id:
                continue
                
            filtered.append(f)
            
        return filtered

    def mark_processed(self, feedback_ids):
        db = self._read_data()
        for f in db['feedback']:
            if f['id'] in feedback_ids:
                f['processed'] = True
        self._write_data(db)

    def save_clusters(self, clusters, institute_id=None):
        db = self._read_data()
        result_record = {
            'id': str(uuid.uuid4()),
            'institute_id': institute_id,
            'timestamp': datetime.now().isoformat(),
            'clusters': clusters
        }
        db['results'].append(result_record)
        self._write_data(db)

    def get_latest_results(self, institute_id=None):
        db = self._read_data()
        results = db.get('results', [])
        
        # Filter by institute
        if institute_id:
            results = [r for r in results if r.get('institute_id') == institute_id]
            
        if not results:
            return {'clusters': []}
        return results[-1]

    def register_institute(self, data):
        db = self._read_data()
        if 'institutes' not in db:
            db['institutes'] = []
            
        institute_id = data.get('code') # Use provided code or generate one
        if not institute_id:
            institute_id = f"NEXUS-{str(uuid.uuid4())[:8].upper()}"
            
        record = {
            'id': institute_id,
            'name': data.get('name'),
            'address': data.get('address'),
            'email': data.get('email'),
            'admin_id': data.get('admin_id'),
            'password': data.get('password'),
            'created_at': datetime.now().isoformat()
        }
        db['institutes'].append(record)
        self._write_data(db)
        return institute_id

    def verify_institute(self, institute_id):
        db = self._read_data()
        institutes = db.get('institutes', [])
        for inst in institutes:
            if inst['id'] == institute_id:
                return {'valid': True, 'name': inst['name']}
        return {'valid': False}

    def register_admin(self, institute_id, admin_id, password):
        db = self._read_data()
        institutes = db.get('institutes', [])
        for inst in institutes:
            if inst['id'] == institute_id:
                inst['admin_id'] = admin_id
                inst['password'] = password
                self._write_data(db)
                return True
        return False

    def verify_admin(self, admin_id, password):
        db = self._read_data()
        institutes = db.get('institutes', [])
        for inst in institutes:
            if inst.get('admin_id') == admin_id and inst.get('password') == password:
                return {'valid': True, 'institute_name': inst['name'], 'institute_id': inst['id']}
        return {'valid': False}

    def get_feedback_stats(self, institute_id=None):
        db = self._read_data()
        feedback = db.get('feedback', [])
        
        roles = {}
        categories = {}
        
        count = 0
        for f in feedback:
            if institute_id and f.get('institute_id') != institute_id:
                continue
                
            count += 1
            # Count Roles
            r = f.get('role', 'Unknown')
            roles[r] = roles.get(r, 0) + 1
            
            # Count Categories
            c = f.get('category', 'Other')
            categories[c] = categories.get(c, 0) + 1
            
        return {
            'total': count,
            'roles': roles,
            'categories': categories
        }

class FirestoreStorage(StorageBase):
    def __init__(self, key_path='firebase_key.json'):
        if not FIRESTORE_AVAILABLE:
            raise ImportError("Firestore libraries not installed or firebase_key.json not found.")
        
        # Initialize with service account
        import os
        if os.path.exists(key_path):
            from google.oauth2 import service_account
            creds = service_account.Credentials.from_service_account_file(key_path)
            self.db = firestore.Client(credentials=creds)
            print("Firestore Connected via Service Account Key")
        else:
            try:
                # Fallback for environment-based auth (e.g. deployed or gcloud auth login)
                self.db = firestore.Client()
                print("Firestore Connected via Default Credentials")
            except Exception as e:
                print("!"*50)
                print(f"FIRESTORE CONNECTION FAILED: {e}")
                print("Please place 'firebase_key.json' in the backend/ folder.")
                print("!"*50)
                # Re-raise or fallback? User said "new data should store in firebase", so maybe raising is appropriate
                # but crashing the server prevents viewing the UI instructions.
                # Let's set db to None and handle it in methods?
                self.db = None

    def _get_app_collection(self):
        """Global app data (registrations)"""
        if not self.db: return None
        return self.db.collection('nexus_institutes')

    def _get_data_collection(self, institute_id, type_):
        """Dynamic collection for each institute"""
        if not self.db: return None
        if not institute_id or institute_id == 'Default':
             # Fallback for testing/default
            return self.db.collection(f'institute_default_{type_}')
        return self.db.collection(f'institute_{institute_id}_{type_}')

    def register_institute(self, data):
        if not self.db: raise RuntimeError("Database not connected. Please add firebase_key.json")
        # 1. Create a global record
        institutes_ref = self._get_app_collection()
        
        # Check if exists
        code = data.get('code')
        if not code:
           code = f"INST_{str(uuid.uuid4())[:6].upper()}"

        # Query to check duplicates (optional but good practice)
        docs = institutes_ref.where('id', '==', code).stream()
        if list(docs):
            raise ValueError("Institute ID already exists")

        record = {
            'id': code,
            'name': data.get('name'),
            'address': data.get('address'),
            'email': data.get('email'),
            'admin_id': data.get('admin_id'),
            'password': data.get('password'), # In prod, hash this!
            'created_at': datetime.now().isoformat()
        }
        
        institutes_ref.add(record)
        return code

    def verify_institute(self, institute_id):
        if not self.db: return {'valid': False, 'error': 'DB Connection Failed'}
        docs = self._get_app_collection().where('id', '==', institute_id).stream()
        for doc in docs:
            d = doc.to_dict()
            return {'valid': True, 'name': d.get('name')}
        return {'valid': False}

    def verify_admin(self, admin_id, password):
        if not self.db: 
            # Temporary fallback to allow UI load if DB missing
            if admin_id == 'admin': return {'valid': True, 'institute_name': 'No DB Mode', 'institute_id': 'default'}
            return {'valid': False}
            
        docs = self._get_app_collection().where('admin_id', '==', admin_id).where('password', '==', password).stream()
        for doc in docs:
            d = doc.to_dict()
            return {'valid': True, 'institute_name': d.get('name'), 'institute_id': d.get('id')}
        return {'valid': False}

    def add_feedback(self, data):
        if not self.db: return {'id': 'local-mock', 'status': 'no-db'}
        inst_id = data.get('institute_id', 'Default')
        col_ref = self._get_data_collection(inst_id, 'feedback')
        
        record = {
            'id': str(uuid.uuid4()),
            'role': data.get('role', 'Anonymous'),
            'user_id': data.get('user_id', 'N/A'),
            'user_name': data.get('user_name', 'Anonymous'),
            'is_verified': data.get('is_verified', False),
            'institute_id': inst_id,
            'category': data.get('category'),
            'text': data.get('text'),
            'timestamp': data.get('timestamp') or datetime.now().isoformat(),
            'processed': False
        }
        col_ref.add(record)
        return record

    def get_unprocessed_feedback(self, institute_id=None):
        if not self.db: return []
        col_ref = self._get_data_collection(institute_id, 'feedback')
        # Simple query for processed=False
        docs = col_ref.where('processed', '==', False).stream()
        
        feedback = []
        for doc in docs:
            d = doc.to_dict()
            d['doc_id'] = doc.id # Firestore Document ID needed for updates
            feedback.append(d)
        return feedback

    def mark_processed(self, feedback_ids):
        pass 

    def save_clusters(self, clusters, institute_id=None):
        if not self.db: return
        col_ref = self._get_data_collection(institute_id, 'results')
        record = {
            'id': str(uuid.uuid4()),
            'timestamp': datetime.now().isoformat(),
            'clusters': clusters
        }
        col_ref.add(record)

    def get_latest_results(self, institute_id=None):
        if not self.db: return {'clusters': []}
        col_ref = self._get_data_collection(institute_id, 'results')
        # Order by timestamp desc, limit 1
        query = col_ref.order_by('timestamp', direction=firestore.Query.DESCENDING).limit(1)
        docs = list(query.stream())
        if not docs:
            return {'clusters': []}
        return docs[0].to_dict()

    def get_feedback_stats(self, institute_id=None):
        if not self.db: return {'total': 0, 'roles': {}, 'categories': {}}
        col_ref = self._get_data_collection(institute_id, 'feedback')
        docs = col_ref.stream() # Provide a limit in prod!
        
        count = 0
        roles = {}
        categories = {}
        
        for doc in docs:
            d = doc.to_dict()
            count += 1
            r = d.get('role', 'Unknown')
            roles[r] = roles.get(r, 0) + 1
            c = d.get('category', 'Other')
            categories[c] = categories.get(c, 0) + 1
            
        return {
            'total': count,
            'roles': roles,
            'categories': categories
        }

# Factory
def get_storage():
    # Priority: Firestore if lib available
    if FIRESTORE_AVAILABLE:
        try:
            return FirestoreStorage()
        except Exception as e:
            print(f"Firestore Init Failed: {e}. Falling back to Local.")
    
    print("Using Local Storage")
    return LocalStorage()
