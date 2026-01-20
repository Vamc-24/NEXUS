import requests
import json
import time

BASE_URL = "http://127.0.0.1:5000"

def verify_analyze():
    print("\n--- VERIFYING ANALYZE API ---")
    
    # 1. Register
    code = f"API_TEST_{int(time.time())}"
    reg_data = {
        "name": "API Test Inst",
        "code": code,
        "admin_id": "admin",
        "password": "pass"
    }
    
    try:
        r = requests.post(f"{BASE_URL}/api/institute/register", json=reg_data)
        if r.status_code != 201:
            print(f"[ERROR] Register failed: {r.text}")
            return
        print(f"[SUCCESS] Registered: {code}")
        
        # 2. Add Dummy Feedback
        fb_data = {
            "institute_id": code,
            "text": "The lab equipment is outdated and computers are slow.",
            "category": "Inferstructure",
            "role": "Student"
        }
        r = requests.post(f"{BASE_URL}/api/feedback", json=fb_data)
        print(f"[SUCCESS] Feedback Added: {r.status_code}")
        
        # 3. Trigger Analysis (The Button Click)
        print("[INFO] Triggering Analysis (Clicking 'Analyze')...")
        r = requests.post(f"{BASE_URL}/api/process", json={"institute_id": code})
        
        if r.status_code == 200:
            print("[SUCCESS] Analysis Complete!")
            print(f"Response: {r.json()}")
        else:
             print(f"[ERROR] Analysis Failed: {r.text}")

    except Exception as e:
        print(f"[ERROR] Connection failed: {e}")

if __name__ == "__main__":
    verify_analyze()
