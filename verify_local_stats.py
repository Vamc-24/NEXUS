import requests
import time

BASE_URL = "http://127.0.0.1:5000"

def check():
    session = requests.Session()
    
    # 1. Get Initial Stats
    try:
        r = session.get(f"{BASE_URL}/api/stats?institute_id=Default")
        initial = r.json()
        print(f"Initial Stats: {initial}")
        count = initial.get("total", 0)
    except Exception as e:
        print(f"Failed to connect to {BASE_URL}. Is server running? {e}")
        return

    # 2. Submit Feedback
    print("Submitting feedback...")
    r = session.post(f"{BASE_URL}/api/feedback", json={
        "text": "The wifi in the hostel is terrible and water is cold.",
        "category": "Infrastructure",
        "role": "Student",
        "institute_id": "Default"
    })
    print(f"Submit Status: {r.status_code}")

    # 3. Check Stats again
    time.sleep(1)
    r = session.get(f"{BASE_URL}/api/stats?institute_id=Default")
    new_stats = r.json()
    print(f"New Stats: {new_stats}")
    
    new_count = new_stats.get("total", 0)
    
    if new_count > count:
        print("SUCCESS: Count incremented.")
    else:
        print("FAILURE: Count did not increment.")

if __name__ == "__main__":
    check()
