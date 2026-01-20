import sys
import os
import uuid

# Setup path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.storage import FirestoreStorage

def debug_path():
    print("\n--- DEBUGGING FIRESTORE PATHS ---")
    try:
        storage = FirestoreStorage(key_path='firebase_key.json')
    except Exception as e:
        print(f"Error init: {e}")
        return

    if not storage.db:
        print("DB Not Connected")
        return

    # 1. Test "Default" case (What user sees if ID is missing)
    default_ref = storage._get_data_collection('Default', 'feedback')
    print(f"1. Default/Missing ID Path -> {default_ref.path}")

    # 2. Test "Specific Institute" case (Goal)
    inst_id = "TEST_INST_001"
    target_ref = storage._get_data_collection(inst_id, 'feedback')
    print(f"2. Specific ID ({inst_id}) Path -> {target_ref.path}")

    print("\nCONCLUSION:")
    if "nexus_institutes" in target_ref.path and inst_id in target_ref.path:
        print("SUCCESS: Code is generating correct SUB-COLLECTION paths.")
    else:
        print("FAILURE: Code is generating incorrect paths.")

if __name__ == "__main__":
    debug_path()
