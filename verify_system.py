import requests
import time
import sys

BASE_URL = 'http://localhost:5000/api'

def test_workflow():
    print("Testing Student Feedback Analysis System...")
    
    # 1. Submit Feedback
    feedbacks = [
        {"category": "course_content", "text": "The lectures are too fast and I can't keep up with the slides."},
        {"category": "course_content", "text": "Please slow down during the math sections. It's confusing."},
        {"category": "facilities", "text": "The air conditioning in room 302 is broken. It's too hot."},
        {"category": "facilities", "text": "It is very hot in the classroom, hard to concentrate."},
        {"category": "exams", "text": "The midterm was very difficult and didn't cover what was in the homework."}
    ]
    
    print(f"\nSubmitting {len(feedbacks)} feedback items...")
    for fb in feedbacks:
        try:
            res = requests.post(f"{BASE_URL}/feedback", json=fb)
            if res.status_code == 201:
                print(f"  - Submitted: {fb['text'][:30]}...")
            else:
                print(f"  - Failed: {res.text}")
        except requests.exceptions.ConnectionError:
            print("  - Connection Error: Is the server running?")
            sys.exit(1)

    # 2. Trigger Processing
    print("\nTriggering AI Processing...")
    res = requests.post(f"{BASE_URL}/process")
    if res.status_code == 200:
        print("  - Processing started/completed.")
        print(f"  - Response: {res.json()}")
    else:
        print(f"  - Failed to trigger processing: {res.text}")

    # 3. Get Results
    print("\nFetching Results...")
    res = requests.get(f"{BASE_URL}/results")
    if res.status_code == 200:
        data = res.json()
        print("\nAnalysis Results:")
        clusters = data.get('clusters', [])
        print(f"  - Found {len(clusters)} clusters.")
        for i, cluster in enumerate(clusters):
            print(f"\n  Cluster {i+1} ({cluster.get('theme')}) - {cluster['count']} items:")
            print(f"    Problem: {cluster['problem_statement']}")
            print(f"    Solutions: {cluster['solutions']}")
    else:
        print(f"  - Failed to get results: {res.text}")

if __name__ == "__main__":
    # Wait a bit for server to handle if just started
    time.sleep(1)
    test_workflow()
