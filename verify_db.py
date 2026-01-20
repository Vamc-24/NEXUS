import sys
import os
import uuid
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.storage import FirestoreStorage

def verify_structure():
    print("Initializing Storage...")
    try:
        storage = FirestoreStorage(key_path='backend/firebase_key.json')
    except Exception as e:
        print(f"Failed to init storage: {e}")
        return

    if not storage.db:
        print("Firestore not connected (No Key Found). Cannot verify.")
        return

    print("Storage initialized.")
    
    # Test Data
    inst_id = "VERIFY_TEST_INST_" + str(uuid.uuid4())[:8]
    print(f"Test Institute ID: {inst_id}")
    
    # 1. Register Institute (Parent Document)
    print("Registering Institute...")
    inst_data = {
        'code': inst_id,
        'name': 'Verification Test Institute',
        'address': '123 Test Lane',
        'email': 'test@verify.com',
        'admin_id': 'admin_test',
        'password': 'pass'
    }
    
    try:
        storage.register_institute(inst_data)
        print(f"[SUCCESS] Institute document created at: nexus_institutes/{inst_id}")
    except Exception as e:
        print(f"[ERROR] Failed to register institute: {e}")

    # 2. Add Feedback (Subcollection)
    print("Adding Feedback...")
    fb_data = {
        'institute_id': inst_id,
        'role': 'Student',
        'category': 'Academics',
        'text': 'This is a test feedback to verify subcollection structure.'
    }
    
    try:
        record = storage.add_feedback(fb_data)
        print(f"[SUCCESS] Feedback added.")
        print(f"Check Firestore Console for path: nexus_institutes/{inst_id}/feedback/{record['id']}")
    except Exception as e:
        print(f"[ERROR] Failed to add feedback: {e}")

if __name__ == "__main__":
    verify_structure()
