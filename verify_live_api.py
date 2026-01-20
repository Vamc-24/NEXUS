import requests
import time

BASE_URL = "https://nexus-tbc3.onrender.com"

def verify_live():
    print(f"\n--- VERIFYING LIVE SITE: {BASE_URL} ---")
    
    # 1. Register a FRESH Institute (Crucial for fresh DB)
    code = f"LIVE_TEST_{int(time.time())}"
    print(f"[INFO] Attempting to Register Institute: {code}")
    
    reg_data = {
        "name": "Live Cloud Test",
        "code": code,
        "admin_id": "admin",
        "password": "pass"
    }
    
    try:
        r = requests.post(f"{BASE_URL}/api/institute/register", json=reg_data)
        print(f"[REGISTER] Status: {r.status_code}")
        print(f"[REGISTER] Response: {r.text}")
        
        if r.status_code != 201:
            print("[CRITICAL] Registration Failed. Database might be read-only or not connected.")
            return

        # 2. Add Feedback to this NEW Institute
        print(f"[INFO] Submitting Feedback to {code}...")
        fb_data = {
            "institute_id": code,
            "text": "Live verified feedback.",
            "category": "Cloud",
            "role": "Tester"
        }
        r = requests.post(f"{BASE_URL}/api/feedback", json=fb_data)
        print(f"[FEEDBACK] Status: {r.status_code}")
        print(f"[FEEDBACK] Response: {r.text}")
        
        if r.status_code == 201:
             print("[SUCCESS] Live Database is Writable!")
        else:
             print("[ERROR] Feedback Submission Failed.")

    except Exception as e:
        print(f"[EXCEPTION] Connection failed: {e}")

if __name__ == "__main__":
    verify_live()
