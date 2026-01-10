import requests
import time
import json

BASE_URL = "http://localhost:5000"

def verify():
    print("Verifying Feedback Analysis System...")
    
    # 1. Submit Feedback
    print("1. Submitting feedback...")
    payload = {
        "text": "The curriculum is outdated and we need more practical python projects.",
        "category": "curriculum"
    }
    try:
        res = requests.post(f"{BASE_URL}/api/feedback", json=payload)
        res.raise_for_status()
        print("   Feedback submitted successfully.")
    except Exception as e:
        print(f"   Failed to submit feedback: {e}")
        return False

    # 2. Trigger Processing
    print("2. Triggering processing...")
    try:
        res = requests.post(f"{BASE_URL}/api/process")
        res.raise_for_status()
        print("   Processing triggered successfully.")
    except Exception as e:
        print(f"   Failed to trigger processing: {e}")
        return False

    # 3. Check Results
    print("3. Checking results...")
    try:
        res = requests.get(f"{BASE_URL}/api/results")
        res.raise_for_status()
        data = res.json()
        
        clusters = data.get('clusters', [])
        if not clusters:
            print("   No clusters found. Processing might have failed or no data.")
            return False
            
        first_cluster = clusters[0]
        solutions = first_cluster.get('solutions', [])
        if not solutions:
            print("   No solutions in cluster.")
            return False
            
        first_solution = solutions[0]
        if isinstance(first_solution, dict):
            print("   Solution is structured correctly.")
            print(f"   Solution: {first_solution.get('solution')}")
            print(f"   Cost: {first_solution.get('estimated_cost')}")
            print(f"   Tools: {first_solution.get('required_tools')}")
            
            if 'estimated_cost' in first_solution and 'required_tools' in first_solution:
                print("   SUCCESS: Cost and Tools fields present.")
                return True
            else:
                print("   FAILURE: Missing cost or tools fields.")
                return False
        else:
            print(f"   FAILURE: Solution is not a dictionary. Type: {type(first_solution)}")
            print(f"   Value: {first_solution}")
            return False

    except Exception as e:
        print(f"   Failed to get results: {e}")
        return False

if __name__ == "__main__":
    if verify():
        print("\nVerification PASSED")
    else:
        print("\nVerification FAILED")
