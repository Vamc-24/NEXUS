import os
import json

# Try importing Vertex AI
try:
    import vertexai
    from vertexai.language_models import TextGenerationModel
    VERTEX_AVAILABLE = True
except ImportError:
    VERTEX_AVAILABLE = False

class LLMClient:
    def generate_problem_statement(self, texts):
        raise NotImplementedError

    def suggest_solutions(self, problem_statement):
        raise NotImplementedError

class MockLLMClient(LLMClient):
    def generate_problem_statement(self, texts):
        # ROI: Return a generic statement based on first text
        summary = "Students are expressing concerns regarding: " + texts[0][:50] + "..."
        return f"Mock Problem Statement: {summary}"

    def suggest_solutions(self, problem_statement):
        # ROI: Return detailed, high-impact solutions with Indian context (Rupees)
        text = problem_statement.lower()
        
        if "internet" in text or "wifi" in text:
            solution_title = "High-Density Campus Wi-Fi Mesh Network"
            steps = [
                "1. Conduct RF site survey to identify dead zones.",
                "2. Procure Enterprise-grade Wi-Fi 6 Access Points (Cisco/Aruba).",
                "3. Install APs in high-density areas (library, cafeteria, hostels).",
                "4. Configure bandwidth management policies to prioritize academic traffic."
            ]
            resources = {
                "Investment": "₹15,00,000 (Hardware + Cabling)",
                "Labor": "Network Engineers (Contract), IT Staff",
                "Support": "Annual Maintenance Contract (AMC)"
            }
            total_cost = "₹15,00,000 - ₹20,00,000"
            sentiment = "Negative"
            
        elif "teaching" in text or "fast" in text or "pace" in text:
            solution_title = "Hybrid Learning & Lecture Capture System"
            steps = [
                "1. Install lecture recording hardware in all major classrooms.",
                "2. Implement 'Smart Class' software for auto-uploading to LMS.",
                "3. Conduct faculty workshops on interactive teaching methods.",
                "4. Mandate 'doubt-clearing' sessions twice a week."
            ]
            resources = {
                "Investment": "₹5,00,000 (Cameras + Microphones)",
                "Labor": "IT Support for setup, Faculty time",
                "Support": "Cloud Storage Subscription"
            }
            total_cost = "₹5,00,000 (One-time) + ₹50,000/month"
            sentiment = "Neutral"

        elif "food" in text or "canteen" in text or "mess" in text:
            solution_title = "Canteen Revamp & Digital Ordering System"
            steps = [
                "1. Audit current hygiene standards and terminate underperforming vendors.",
                "2. Digitalize order taking via mobile app to reduce queues.",
                "3. Introduce subsidized nutritional meals for students.",
                "4. Form a 'Food Committee' with student representatives."
            ]
            resources = {
                "Investment": "₹2,00,000 (App Dev + Kitchen upgrades)",
                "Labor": "Kitchen Staff, App Manager",
                "Support": "Weekly health inspections"
            }
            total_cost = "₹2,00,000 - ₹5,00,000"
            sentiment = "Negative"

        else:
            solution_title = "Strategic administrative review & Infrastructure Upgrades"
            steps = [
                "1. Form a committee to investigate specific complaints.",
                "2. Allocate emergency budget for immediate repairs.",
                "3. Set up a transparent feedback tracking portal."
            ]
            resources = {
                "Investment": "₹1,00,000 (Contingency Fund)",
                "Labor": "Admin Staff",
                "Support": "Student Council"
            }
            total_cost = "₹1,00,000"
            sentiment = "Neutral"
            
        return [{
            "solution_title": solution_title,
            "steps": steps,
            "resources": resources,
            "total_estimated_cost": total_cost,
            "sentiment": sentiment
        }]

class VertexLLMClient(LLMClient):
    def __init__(self, project_id, location='us-central1'):
        if not VERTEX_AVAILABLE:
            raise RuntimeError("Vertex AI SDK not installed.")
        vertexai.init(project=project_id, location=location)
        self.model = TextGenerationModel.from_pretrained("text-bison")

    def generate_problem_statement(self, texts):
        combined_text = "\n".join([f"- {t}" for t in texts])
        prompt = f"""
        Analysis of Student Feedback:
        {combined_text}
        
        Based on the above comments, write a concise problem statement describing the main issue.
        Problem Statement:
        """
        try:
            response = self.model.predict(prompt, temperature=0.2, max_output_tokens=256)
            return response.text.strip()
        except Exception as e:
            print(f"Vertex AI Error: {e}")
            return "Error generating problem statement."

    def suggest_solutions(self, problem_statement):
        prompt = f"""
        Problem: {problem_statement}
        
        Suggest 3 concrete, actionable solutions or improvements for this issue.
        For each solution, provide:
        1. A catchy 'solution_title'.
        2. A list of 'steps' to achieve it (step-by-step).
        3. A 'resources' object containing keys: 'Investment' (Cost in Rupees), 'Labor', 'Support'.
        4. A 'total_estimated_cost' string (in Rupees, e.g., "₹50,000").
        5. A 'sentiment' string, strictly one of: "Positive", "Neutral", "Negative".
        
        Return the response AS A VALID JSON LIST of objects.
        Do not acknowledge or wrap in markdown. Just the raw JSON.
        """
        try:
            response = self.model.predict(prompt, temperature=0.4, max_output_tokens=1024)
            # Parse JSON
            text = response.text.strip()
            if text.startswith('```json'):
                text = text[7:]
            if text.endswith('```'):
                text = text[:-3]
            return json.loads(text.strip())
        except Exception as e:
            print(f"Vertex AI Error: {e}")
            return [{
                "solution_title": "Error generating solutions.",
                "steps": [],
                "resources": {},
                "total_estimated_cost": "Unknown"
            }]

def get_llm_client():
    project_id = os.environ.get('GOOGLE_CLOUD_PROJECT')
    if project_id and VERTEX_AVAILABLE:
        print(f"Using Vertex AI with project {project_id}")
        return VertexLLMClient(project_id)
    print("Using Mock LLM (Set GOOGLE_CLOUD_PROJECT env var to use Vertex AI)")
    return MockLLMClient()
