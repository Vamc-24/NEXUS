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

class LocalStorage(StorageBase):
    def __init__(self, data_file='data/local_db.json'):
        self.data_file = data_file
        self.ensure_data_file()

    def ensure_data_file(self):
        if not os.path.exists(os.path.dirname(self.data_file)):
            os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
        if not os.path.exists(self.data_file):
            with open(self.data_file, 'w') as f:
                json.dump({'feedback': [], 'results': []}, f)

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
            'category': data.get('category'),
            'text': data.get('text'),
            'timestamp': data.get('timestamp') or datetime.now().isoformat(),
            'processed': False
        }
        db['feedback'].append(record)
        self._write_data(db)
        return record

    def get_unprocessed_feedback(self):
        db = self._read_data()
        return [f for f in db['feedback'] if not f.get('processed')]

    def mark_processed(self, feedback_ids):
        db = self._read_data()
        for f in db['feedback']:
            if f['id'] in feedback_ids:
                f['processed'] = True
        self._write_data(db)

    def save_clusters(self, clusters):
        db = self._read_data()
        result_record = {
            'id': str(uuid.uuid4()),
            'timestamp': datetime.now().isoformat(),
            'clusters': clusters
        }
        db['results'].append(result_record)
        self._write_data(db)

    def get_latest_results(self):
        db = self._read_data()
        if not db['results']:
            return {'clusters': []}
        return db['results'][-1]

class FirestoreStorage(StorageBase):
    def __init__(self, collection='student_feedback'):
        if not FIRESTORE_AVAILABLE:
            raise ImportError("Firestore libraries not installed.")
        self.db = firestore.Client()
        self.collection = self.db.collection(collection)
        self.results_collection = self.db.collection('analysis_results')

    def add_feedback(self, data):
        record = {
            'category': data.get('category'),
            'text': data.get('text'),
            'timestamp': data.get('timestamp') or datetime.utcnow().isoformat(),
            'processed': False
        }
        update_time, ref = self.collection.add(record)
        return {**record, 'id': ref.id}

    def get_unprocessed_feedback(self):
        docs = self.collection.where('processed', '==', False).stream()
        feedback = []
        for doc in docs:
            d = doc.to_dict()
            d['id'] = doc.id
            feedback.append(d)
        return feedback

    def mark_processed(self, feedback_ids):
        # Batch write would be better, but doing simple updates for now
        for fid in feedback_ids:
            self.collection.document(fid).update({'processed': True})

    def save_clusters(self, clusters):
        record = {
            'timestamp': datetime.utcnow().isoformat(),
            'clusters': clusters
        }
        self.results_collection.add(record)

    def get_latest_results(self):
        query = self.results_collection.order_by('timestamp', direction=firestore.Query.DESCENDING).limit(1)
        docs = list(query.stream())
        if not docs:
            return {'clusters': []}
        return docs[0].to_dict()

# Factory
def get_storage():
    # In a real deployed env, checking for GOOGLE_CLOUD_PROJECT or similar env var
    # to switch to Firestore would be ideal.
    # For this prototype task, defaulting to LocalStorage unless configured otherwise.
    if os.environ.get('USE_FIRESTORE') == 'true':
        print("Using Firestore Storage")
        return FirestoreStorage()
    print("Using Local Storage")
    return LocalStorage()
