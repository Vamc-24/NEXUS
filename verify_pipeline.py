import requests
import json
import time

BASE_URL = 'http://localhost:5000/api'

def add_feedback():
    feedback_samples = [
        {"category": "teaching_style", "text": "The lectures are too fast and hard to follow."},
        {"category": "teaching_style", "text": "I can't keep up with the professor's pace."},
        {"category": "facilities", "text": "The air conditioning in the lab is broken."},
        {"category": "facilities", "text": "It's too hot in the computer lab to concentrate."}
    ]
    
    print("Adding sample feedback...")
    for item in feedback_samples:
        try:
            requests.post(f"{BASE_URL}/feedback", json=item)
            print(f"Added: {item['text'][:20]}...")
        except Exception as e:
            print(f"Failed to add feedback: {e}")

def trigger_pipeline():
    print("\nTriggering AI Pipeline...")
    try:
        response = requests.post(f"{BASE_URL}/process")
        print(f"Status: {response.status_code}")
        print("Response:", json.dumps(response.json(), indent=2))
    except Exception as e:
        print(f"Failed to trigger pipeline: {e}")

if __name__ == "__main__":
    add_feedback()
    time.sleep(1)
    trigger_pipeline()
