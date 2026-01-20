import requests

URL = "https://nexus-tbc3.onrender.com"

try:
    print(f"Checking {URL}...")
    r = requests.get(URL)
    print(f"Status Code: {r.status_code}")
    if r.status_code == 200:
        print("SUCCESS: Site is Live!")
    else:
        print(f"WARNING: Site returned {r.status_code}")
except Exception as e:
    print(f"ERROR: Could not connect. {e}")
