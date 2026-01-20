import sys
import os
import sqlite3
import uuid

# Setup path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.storage import SQLStorage

def verify_sql():
    print("\n--- VERIFYING SQL MIGRATION ---")
    
    # 1. Initialize
    try:
        storage = SQLStorage()
        print("[SUCCESS] SQLStorage initialized.")
        # print(f"         DB Path: {storage.db_path}")
    except Exception as e:
        print(f"[ERROR] Init failed: {e}")
        return

    # 2. Register Institute
    try:
        reg_data = {
            "name": "SQL verification Tech",
            "address": "123 Data Lane",
            "email": "sql@test.com",
            "admin_id": "admin",
            "password": "pass",
            "code": "SQL_TEST_01"
        }
        # Handle potential duplicate runs
        try:
             inst_id = storage.register_institute(reg_data)
             print(f"[SUCCESS] Registered Institute: {inst_id}")
        except ValueError:
             print("[INFO] Institute already exists (Expected on re-run).")
             inst_id = "SQL_TEST_01"

    except Exception as e:
        print(f"[ERROR] Registration failed: {e}")
        return

    # 3. Add Feedback
    try:
        fb_data = {
            "institute_id": inst_id,
            "text": "The migration to SQL is running smoothly.",
            "category": "Curriculum",
            "role": "Student"
        }
        record = storage.add_feedback(fb_data)
        print(f"[SUCCESS] Feedback Added. ID: {record['id']}")
    except Exception as e:
        print(f"[ERROR] Add Feedback failed: {e}")
        return

    # 4. Verify Stats (Read)
    try:
        stats = storage.get_feedback_stats(inst_id)
        print(f"[SUCCESS] Stats Retrieved: {stats['total']} total feedback.")
        if stats['total'] > 0:
            print(f"         Roles: {stats['roles']}")
    except Exception as e:
        print(f"[ERROR] Get Stats failed: {e}")
        return

    print("\n--- SQL VERIFICATION COMPLETE ---")

if __name__ == "__main__":
    verify_sql()
