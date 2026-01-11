import json
import os
import uuid
from datetime import datetime, timedelta
import random

# Ensure data directory exists
os.makedirs('data', exist_ok=True)
db_path = 'data/local_db.json'

def generate_id():
    return str(uuid.uuid4())

def get_timestamp(days_ago=0):
    return (datetime.now() - timedelta(days=days_ago)).isoformat()

# 1. Mock Feedback Data
feedbacks = [
    # Student - Academics (Positive)
    {"role": "Student", "category": "course_content", "text": "The new AI curriculum is fantastic! Loving the hands-on labs.", "sentiment": "Positive", "days_ago": 1},
    {"role": "Student", "category": "course_content", "text": "Great explanation of Neural Networks in Prof. Smith's class.", "sentiment": "Positive", "days_ago": 2},
    
    # Student - Food (Negative/Critical)
    {"role": "Student", "category": "facilities", "text": "The cafeteria food hygiene is really bad. I found an insect in my meal.", "sentiment": "Negative", "days_ago": 0},
    {"role": "Student", "category": "facilities", "text": "Food poisoning cases are rising. Please check the mess kitchen immediately.", "sentiment": "Negative", "days_ago": 0},
    {"role": "Student", "category": "facilities", "text": "Mess food quality has degraded significantly this week.", "sentiment": "Negative", "days_ago": 1},

    # Faculty - Infrastructure (Neutral/Negative)
    {"role": "Faculty", "category": "facilities", "text": "Projector in Lab 3 is flickering constantly. Hinders lectures.", "sentiment": "Negative", "days_ago": 3},
    {"role": "Faculty", "category": "facilities", "text": "We need more whiteboard markers in the staff room.", "sentiment": "Neutral", "days_ago": 4},

    # Staff - Safety
    {"role": "Staff", "category": "harassment", "text": "Corridor lights near the library are out. Safety concern at night.", "sentiment": "Negative", "days_ago": 1},
    
    # Student - Exams
    {"role": "Student", "category": "exams", "text": "Exam schedule is too tight. Two major papers in one day.", "sentiment": "Negative", "days_ago": 5},
]

feedback_records = []
for f in feedbacks:
    record = {
        'id': generate_id(),
        'role': f['role'],
        'user_id': 'Anonymous',
        'user_name': 'Anonymous',
        'is_verified': False,
        'institute_id': 'Default',
        'category': f['category'],
        'text': f['text'],
        'timestamp': get_timestamp(f['days_ago']),
        'processed': True 
    }
    feedback_records.append(record)

# 2. Mock Analysis Results (Clusters)
# matching the dashboard expectation: theme, count, problem_statement, solutions[0].solution_title, .steps, .total_estimated_cost
analysis_result = {
    "id": generate_id(),
    "timestamp": get_timestamp(),
    "clusters": [
        {
            "theme": "Cafeteria Hygiene & Safety",
            "count": 12,
            "problem_statement": "Students report severe hygiene issues in the cafeteria, including foreign objects in food and suspected food poisoning incidents.",
            "solutions": [
                {
                    "solution_title": "Emergency Health Audit & Vendor Review",
                    "sentiment": "Negative",
                    "steps": [
                        "Immediate surprise inspection of kitchen facilities.",
                        "Suspend current vendor contract pending review.",
                        "Implement mandatory daily hygiene logs."
                    ],
                    "total_estimated_cost": "500"
                }
            ]
        },
        {
            "theme": "Lab Infrastructure Maintenance",
            "count": 8,
            "problem_statement": "Faculty and students are facing disruptions due to faulty projectors and lack of maintenance in Computer Labs.",
            "solutions": [
                {
                    "solution_title": "Equipment Upgrade & Rapid Repair Protocol",
                    "sentiment": "Negative",
                    "steps": [
                        "Replace bulbs in Lab 3 projectors.",
                        "Establish a 24-hour IT support ticket SLA.",
                        "Procure backup display units."
                    ],
                    "total_estimated_cost": "2,200"
                }
            ]
        },
         {
            "theme": "Curriculum Satisfaction",
            "count": 25,
            "problem_statement": "High student engagement reported in the new AI & Machine Learning specialized tracks.",
            "solutions": [
                {
                    "solution_title": "Expand Elective Offerings",
                    "sentiment": "Positive",
                    "steps": [
                        "Introduce Advanced NLP module next semester.",
                        "Organize hackathon with industry partners."
                    ],
                    "total_estimated_cost": "1,000"
                }
            ]
        }
    ]
}

# 3. Write to DB
data = {
    "feedback": feedback_records,
    "results": [analysis_result],
    "institutes": []
}

with open(db_path, 'w') as f:
    json.dump(data, f, indent=2)

print(f"Successfully seeded {len(feedback_records)} feedbacks and 1 analysis result.")
