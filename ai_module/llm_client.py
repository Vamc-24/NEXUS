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
        # ROI: Return a SINGLE, high-impact solution based on the problem
        text = problem_statement.lower()
        
        cost = "Low (< $100)"
        tools = "N/A"
        
        if "internet" in text or "wifi" in text:
            solution = "Upgrade the campus Wi-Fi infrastructure with high-density access points in study areas."
            cost = "High ($10,000+)"
            tools = "Enterprise Wi-Fi Access Points, Network Controller"
        elif "teaching" in text or "fast" in text or "pace" in text:
            solution = "Implement a 'pause-and-ask' policy during lectures and provide recorded sessions for review."
            cost = "Low (Time investment)"
            tools = "Lecture Recording Software (e.g., Panopto, OBS)"
        elif "explanation" in text or "understand" in text:
            solution = "Organize supplementary tutorial sessions and peer-led study groups for complex topics."
            cost = "Medium ($500 - $2000 for tutor stipends)"
            tools = "Classroom booking system"
        elif "facilities" in text or "broken" in text or "ac" in text or "hot" in text:
            solution = "Dispatch facilities team for immediate repair and schedule preventive maintenance checks."
            cost = "Medium ($1000+ for repairs)"
            tools = "Maintenance Request System"
        elif "trees" in text or "environment" in text or "playground" in text:
             solution = "Allocate budget for green space development and outdoor student recreational areas."
             cost = "High ($5000+)"
             tools = "Landscaping tools, Outdoor furniture"
        else:
            solution = "Initiate a student-faculty joint committee to investigate and address these specific concerns."
            cost = "Low"
            tools = "Meeting room, Survey tool"
            
        return [{
            "solution": solution,
            "estimated_cost": cost,
            "required_tools": tools
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
        1. The solution description.
        2. Estimated cost (Low/Medium/High + rough amount).
        3. Required tools or resources.
        
        Return the response AS A VALID JSON LIST of objects with keys: "solution", "estimated_cost", "required_tools".
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
            return [{"solution": "Error generating solutions.", "estimated_cost": "Unknown", "required_tools": "Unknown"}]

def get_llm_client():
    project_id = os.environ.get('GOOGLE_CLOUD_PROJECT')
    if project_id and VERTEX_AVAILABLE:
        print(f"Using Vertex AI with project {project_id}")
        return VertexLLMClient(project_id)
    print("Using Mock LLM (Set GOOGLE_CLOUD_PROJECT env var to use Vertex AI)")
    return MockLLMClient()
